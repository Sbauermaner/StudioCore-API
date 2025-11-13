# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Adaptive Annotation Engine (v8 - Suno UI)
Gradio + FastAPI + Централизованное логирование
"""

import os
import sys
import traceback
import threading
import time
import io
import uvicorn # v6: ИСПРАВЛЕН NameError
import logging

# === 1. Исправление пути импорта ===
# (Нужно, если запускаем app.py из корня)
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# === 2. Активация логгера ===
# ДО импорта ядра
try:
    from studiocore.logger import setup_logging
    # Устанавливаем уровень DEBUG, чтобы видеть все
    setup_logging(level=logging.DEBUG) 
except ImportError:
    print("WARNING: studiocore.logger не найден. Используется стандартный print.")
    logging.basicConfig(level=logging.DEBUG) # Fallback

log = logging.getLogger(__name__)
log.info("Запуск app.py...")
# === Конец активации логгера ===

import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# === 3. Импорт ядра ===
try:
    from studiocore import get_core, STUDIOCORE_VERSION
    CORE = get_core()
    CORE_LOADED = True
    log.info("Ядро StudioCore успешно импортировано.")
except Exception as e:
    log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить ядро: {e}")
    log.critical(traceback.format_exc())
    CORE = None
    CORE_LOADED = False

# === 4. Инициализация FastAPI ===
log.debug("Инициализация FastAPI...")
app = FastAPI(title="StudioCore API")

# === 5. CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 6. 🎧 PUBLIC API ENDPOINT ===
# (Исправляет HTTP 404 в тестах)

class PredictRequest(BaseModel):
    """ Модель запроса для API """
    text: str
    gender: str = "auto"
    tlp: Optional[dict] = None
    overlay: Optional[dict] = None

@app.post("/api/predict")
async def api_predict(request_data: PredictRequest):
    """
    Эндпоинт, который ищут 'test_all.py' и 'auto_core_check'.
    Он принимает JSON и возвращает JSON.
    """
    log.debug(f"Входящий запрос /api/predict: {request_data.text[:50]}...")
    
    if not CORE_LOADED or CORE is None:
        log.error("API /api/predict: Ядро не загружено (Fallback).")
        return JSONResponse(
            content={"error": "⚠️ StudioCoreFallback: анализ недоступен — основное ядро не загружено."}, 
            status_code=500
        )
        
    try:
        # Сопоставляем данные из запроса с тем, что ожидает core.analyze
        result = CORE.analyze(
            request_data.text,
            preferred_gender=request_data.gender,
            overlay=request_data.overlay
        )
        
        if isinstance(result, dict) and "error" in result:
             log.warning(f"API /api/predict: Ядро вернуло ошибку: {result['error']}")
             return JSONResponse(content=result, status_code=400)
        
        # Возвращаем полный результат (тесты ожидают 'bpm' и 'style')
        log.debug("API /api/predict: Анализ успешен.")
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в /api/predict: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# === 7. SELF-CHECK ===
def auto_core_check():
    """ 
    Фоновая проверка API-эндпоинта (v4 - таймаут 20с).
    Дает серверу 5 секунд на запуск, затем пингует /api/predict.
    """
    log.debug("[Self-Check] Поток запущен, ожидание 5с...")
    time.sleep(5) 
    
    if os.environ.get("DISABLE_SELF_CHECK") == "1":
        log.info("[Self-Check] Проверка отключена (DISABLE_SELF_CHECK=1).")
        return
        
    try:
        import requests
    except ImportError:
        log.warning("[Self-Check] 'requests' не найден. Не могу выполнить самопроверку.")
        return

    log.debug("[Self-Check] Запуск самопроверки эндпоинта /api/predict...")
    api_url = "http://127.0.0.1:7860/api/predict"
    payload = {"text": "self-check test"}
    
    try:
        # v7: Таймаут 20с (для "Плана C" - быстрые словари)
        r = requests.post(api_url, json=payload, timeout=20)
        log.info(f"[Self-Check] → Статус: {r.status_code}")
        if r.status_code != 200:
             log.warning(f"[Self-Check] → Ответ: {r.text[:200]}...")
    except Exception as e:
        log.error(f"❌ Self-Check ошибка: {e}")

# Запускаем проверку в отдельном потоке
threading.Thread(target=auto_core_check, daemon=True).start()


# === 8. АНАЛИЗ ТЕКСТА (Gradio) ===

def analyze_text(text: str, gender: str = "auto"):
    """
    Основная функция анализа текста через StudioCore для UI Gradio.
    v8: Возвращает 3 строки: Summary, Suno Prompt, Annotated Text
    """
    log.debug(f"Gradio analyze_text: получено {len(text)} символов, gender={gender}")
    
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", ""

    if not CORE_LOADED or CORE is None:
        log.error("Gradio analyze_text: Ядро в режиме Fallback!")
        return "❌ Ядро не загружено (Fallback). Анализ невозможен. Проверьте логи.", "", ""

    try:
        # --- Проверка пользовательских описаний вокала ---
        overlay = {}
        voice_hint_keywords = [
            "вокал", "voice", "growl", "scream", "raspy", "мужск", "женск",
            "пескляв", "soft", "airy", "shout", "grit", "фальцет", "whisper"
        ]
        
        # v8: Улучшенная логика: ищем хинт только в ПОСЛЕДНЕЙ строке, 
        # если она в скобках или начинается с "под"
        last_line = text.strip().splitlines()[-1].strip().lower()
        if (last_line.startswith("(") and last_line.endswith(")")) or \
           last_line.startswith("под "):
            if any(k in last_line for k in voice_hint_keywords):
                overlay["voice_profile_hint"] = last_line
                log.info(f"🎙️ [UI] Обнаружено описание вокала: {overlay['voice_profile_hint']}")
        
        log.debug("Gradio -> core.analyze...")
        result = CORE.analyze(text, preferred_gender=gender, overlay=overlay or None)

        if isinstance(result, dict) and "error" in result:
            log.error(f"Gradio: Ядро вернуло ошибку: {result['error']}")
            return f"❌ Ошибка: {result['error']}", "", ""

        # --- 1. Summary ---
        style = result.get("style", {})
        vocal_form = style.get("vocal_form", "auto")
        
        summary = (
            f"✅ StudioCore {STUDIOCORE_VERSION}\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({result.get('final_gender_preference', 'auto')}) | "
            f"⏱ {result.get('bpm', '—')} BPM | "
            f"🔑 {style.get('key', 'auto')}"
        )

        # --- 2. Suno Prompt (v8) ---
        # (Объединяет Style и Lyrics)
        suno_prompt = (
            f"[STYLE PROMPT - КОПИРОВАТЬ В SUNO 'Style of Music']\n"
            f"{result.get('prompt_suno_style', 'Ошибка: prompt_suno_style не найден')}\n\n"
            f"[LYRICS PROMPT - КОПИРОВАТЬ В SUNO 'Lyrics']\n"
            f"{result.get('annotated_text_suno', 'Ошибка: annotated_text_suno не найден')}"
        )
        
        # --- 3. Аннотированный текст (для UI) ---
        annotated_text_ui = result.get("annotated_text_ui", "Ошибка: annotated_text_ui не найден")

        return (
            summary,
            suno_prompt,
            annotated_text_ui,
        )

    except Exception as e:
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в analyze_text (Gradio): {traceback.format_exc()}")
        return f"❌ Внутреннее исключение: {e}", "", ""

# === 9. INLINE TEST RUNNER ===
def run_inline_tests():
    """Выполняет тесты и возвращает stdout прямо в интерфейс."""
    log.info("=" * 30)
    log.info("🚀 ЗАПУСК ВСТРОЕННЫХ ТЕСТОВ...")
    log.info("=" * 30)
    
    buffer = io.StringIO()
    buffer.write(f"🧩 StudioCore {STUDIOCORE_VERSION} — Inline Test Session\n")
    buffer.write(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # --- Путь к скрипту test_all.py ---
    test_script_path = os.path.join(ROOT, "studiocore", "tests", "test_all.py")
    
    if not os.path.exists(test_script_path):
        log.error(f"Test runner: Файл не найден: {test_script_path}")
        buffer.write(f"❌ ОШИБКА: Не найден скрипт test_all.py\n")
        return buffer.getvalue()

    # --- Запуск test_all.py ---
    try:
        log.info(f"🚀 Running: {test_script_path}")
        buffer.write(f"🚀 Running: {test_script_path}\n\n")
        
        # Используем subprocess для захвата STDOUT и STDERR
        process = subprocess.run(
            [sys.executable, test_script_path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=180 # 3 минуты (на случай медленной загрузки ИИ)
        )
        
        # Пишем STDOUT (логи)
        if process.stdout:
            buffer.write(process.stdout)
            
        # Пишем STDERR (ошибки)
        if process.stderr:
            buffer.write("\n--- STDERR ---\n")
            buffer.write(process.stderr)

    except subprocess.TimeoutExpired:
        log.error("Test runner: ТЕСТЫ ПРЕВЫСИЛИ ТАЙМАУТ (180с)!")
        buffer.write("\n❌ КРИТИЧЕСКАЯ ОШИБКА: Тесты заняли слишком много времени (Timeout 180s).\n")
    except Exception as e:
        log.error(f"Test runner: КРИТИЧЕСКАЯ ОШИБКА: {e}")
        buffer.write(f"❌ ОШИБКА ПРИ ЗАПУСКЕ ТЕСТОВ: {e}\n{traceback.format_exc()}\n")

    log.info("🏁 ...Встроенные тесты завершены.")
    buffer.write("\n✅ Inline test session complete.\n")
    return buffer.getvalue()


# === 10. PUBLIC UI (Gradio) ===
log.debug("Инициализация Gradio UI...")
with gr.Blocks(title=f"🎧 StudioCore {STUDIOCORE_VERSION} — Public Interface") as iface_public:
    gr.Markdown(f"## 🎧 StudioCore {STUDIOCORE_VERSION}\nАдаптивный движок с тестами и логами.\n")

    with gr.Tab("🎙️ Анализ текста"):
        with gr.Row():
            text_input = gr.Textbox(
                label="Введите текст песни",
                lines=12,
                placeholder="Вставьте лирику здесь…\n\n(Подсказка: чтобы задать вокал, напишите в ПОСЛЕДНЕЙ строке, например: (под хриплый мужской вокал) или (soft female whisper))"
            )
            gender_input = gr.Radio(["auto", "male", "female"], value="auto", label="Принудительный Пол (UI)")

        analyze_button = gr.Button("🔍 Анализировать")

        # --- v8: Единый блок Suno Prompt ---
        suno_box = gr.Textbox(
            label="[StudioCore] Suno Prompt (Style + Lyrics)", 
            lines=16, 
            show_copy_button=True,
            info="Скопируйте [STYLE PROMPT] в 'Style of Music' и [LYRICS PROMPT] в 'Lyrics' в Suno."
        )

        with gr.Accordion("Показать расширенный анализ (Summary и Аннотация)", open=False):
            # v8: Кнопки копирования возвращены
            result_box = gr.Textbox(label="📊 Результат (Summary)", lines=6, show_copy_button=True)
            annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (UI)", lines=24, show_copy_button=True)

        analyze_button.click(
            fn=analyze_text,
            inputs=[text_input, gender_input],
            outputs=[result_box, suno_box, annotated_box],
        )

    with gr.Tab("🧩 Логи и тесты"):
        gr.Markdown("### Автоматическая проверка ядра StudioCore")
        run_btn = gr.Button("🚀 Запустить тесты")
        output_box = gr.Textbox(
            label="Результаты тестов (stdout/stderr)", 
            lines=30, 
            show_copy_button=True
        )
        run_btn.click(fn=run_inline_tests, inputs=None, outputs=output_box)

# === 11. MOUNT ===
log.debug("Монтирование Gradio App в FastAPI (path='/')...")
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

# === 12. RUN ===
if __name__ == "__main__":
    log.info(f"🚀 Запуск StudioCore {STUDIOCORE_VERSION} API (Inline Logs Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=7860)