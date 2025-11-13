# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Adaptive Annotation Engine (v6 - uvicorn ИСПРАВЛЕН)
"""

import os, sys, subprocess, importlib, traceback, threading, time, io
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn # <-- ИСПРАВЛЕНИЕ: Этот импорт был потерян

# === 1. АКТИВАЦИЯ ЛОГГЕРА ===
try:
    from studiocore.logger import setup_logging
    setup_logging()
except ImportError:
    print("WARNING: studiocore.logger не найден. Используется стандартный print.")
    pass

import logging
log = logging.getLogger(__name__)
log.info("Запуск app.py...")
# === Конец активации логгера ===


# === Импорт ядра ===
try:
    from studiocore import get_core, STUDIOCORE_VERSION
    core = get_core()
    CORE_LOADED = True
    log.info("Ядро StudioCore успешно импортировано.")
except Exception as e:
    log.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить ядро StudioCore.")
    log.error(traceback.format_exc())
    from studiocore import StudioCoreFallback
    core = StudioCoreFallback()
    CORE_LOADED = False
    STUDIOCORE_VERSION = "FALLBACK"


# === Установка requests (для self-check) ===
if importlib.util.find_spec("requests") is None:
    try:
        log.warning("Зависимость 'requests' не найдена. Попытка установить...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except Exception:
        log.error("Не удалось установить 'requests'. Self-check будет отключен.")
        pass
try:
    import requests
except Exception:
    requests = None


# === Инициализация FastAPI ===
log.debug("Инициализация FastAPI...")
app = FastAPI(title="StudioCore API")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 🎧 PUBLIC API ENDPOINT ===

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
    log.debug(f"Входящий запрос /api/predict: {request_data.text[:20]}...")
    
    if not CORE_LOADED:
        log.error("API /api/predict вызван, но ядро в режиме Fallback.")
        return JSONResponse(
            content={"error": "⚠️ StudioCoreFallback: анализ недоступен — основное ядро не загружено."}, 
            status_code=500
        )
        
    try:
        # Мы сопоставляем данные из запроса с тем, что ожидает core.analyze
        result = core.analyze(
            request_data.text,
            preferred_gender=request_data.gender,
            overlay=request_data.overlay
        )
        
        if isinstance(result, dict) and "error" in result:
             # Если ядро вернуло ошибку, передаем ее
             log.warning(f"Ядро вернуло ошибку: {result['error']}")
             return JSONResponse(content=result, status_code=400)
        
        # Возвращаем полный результат (тесты ожидают 'bpm' и 'style')
        log.debug("API /api/predict: Успешный ответ 200 OK")
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        log.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в /api/predict: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# === Конец API ENDPOINT ===


# === SELF-CHECK ===
def auto_core_check():
    if os.environ.get("DISABLE_SELF_CHECK") == "1" or requests is None:
        log.info("[Self-Check] Проверка отключена (DISABLE_SELF_CHECK=1 или 'requests' не найден).")
        return
    
    time.sleep(3) # Даем uvicorn время на запуск
    log.debug("[Self-Check] Запуск самопроверки эндпоинта /api/predict...")
    
    api_url = "http://127.0.0.1:7860/api/predict"
    payload = {"text": "self-check test"}
    
    try:
        # v7: Таймаут 20с (для "Плана C" - быстрые словари)
        r = requests.post(api_url, json=payload, timeout=20) 
        log.info(f"[Self-Check] → Статус: {r.status_code}")
        if r.status_code != 200:
             log.warning(f"[Self-Check] → Ответ: {r.text[:100]}...")
    except Exception as e:
        log.error(f"❌ Self-Check ошибка: {e}")

# Запускаем self-check в отдельном потоке
threading.Thread(target=auto_core_check, daemon=True).start()


# === АНАЛИЗ ТЕКСТА (Gradio UI) ===
def analyze_text(text: str, gender: str = "auto"):
    """Основная функция анализа текста через StudioCore (для UI)."""
    log.debug(f"Gradio analyze_text: получено {len(text)} символов, gender={gender}")
    
    if not text.strip():
        log.warning("Gradio analyze_text: Пустой ввод.")
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        if not CORE_LOADED:
            log.error("Gradio analyze_text: Ядро в режиме Fallback!")
            return "❌ ОШИБКА: Ядро не загружено (см. лог).", "", "", ""

        # --- Проверка пользовательских описаний вокала ---
        overlay = {}
        voice_hint_keywords = [
            "вокал", "voice", "growl", "scream", "raspy", "мужск", "женск",
            "пескляв", "soft", "airy", "shout", "grit", "фальцет", "whisper"
        ]
        if any(k in text.lower() for k in voice_hint_keywords):
            overlay["voice_profile_hint"] = text.split("\n")[-1].strip()
            log.info(f"🎙️ [UI] Обнаружено описание вокала: {overlay['voice_profile_hint']}")
        else:
            overlay = None

        # --- Вызов ядра ---
        log.debug("Gradio -> core.analyze...")
        result = core.analyze(text, preferred_gender=gender, overlay=overlay)

        if isinstance(result, dict) and "error" in result:
            log.error(f"Gradio: Ядро вернуло ошибку: {result['error']}")
            return f"❌ Ошибка: {result['error']}", "", "", ""

        style = result.get("style", {})
        vocals = result.get("vocals", [])
        instruments = ", ".join(result.get("instruments", [])) or "no instruments"
        vocal_form = style.get("vocal_form", "auto")

        summary = (
            f"✅ StudioCore {STUDIOCORE_VERSION}\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({gender}) | "
            f"🎸 {instruments} | "
            f"⏱ {result.get('bpm', '—')} BPM"
        )
        
        # prompt_suno_style (Style) и prompt_suno_lyrics (Lyrics)
        style_prompt = result.get("prompt_suno_style", "⚠️ Нет данных")
        suno_lyrics_prompt = result.get("prompt_suno_lyrics", "⚠️ Нет данных")
        annotated_text = result.get("annotated_text", "⚠️ Нет данных")

        log.debug("Gradio: Анализ завершен, возврат в UI.")
        return (
            summary,
            style_prompt,
            suno_lyrics_prompt, # Возвращаем вокальный промпт
            annotated_text,
        )

    except Exception:
        log.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в analyze_text (Gradio): {traceback.format_exc()}")
        return "❌ Внутреннее исключение при анализе (см. лог).", "", "", ""

# === INLINE TEST RUNNER ===
def run_inline_tests():
    """Выполняет тесты и возвращает stdout прямо в интерфейс."""
    
    log.info("=" * 30)
    log.info("🚀 ЗАПУСК ВСТРОЕННЫХ ТЕСТОВ...")
    log.info("=" * 30)
    
    # Используем StringIO для перехвата вывода от os.system
    buffer = io.StringIO()
    
    # Перенаправляем stdout/stderr в буфер
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = buffer
    sys.stderr = buffer
    
    # Заголовки
    buffer.write(f"🧩 StudioCore {STUDIOCORE_VERSION} — Inline Test Session\n")
    buffer.write(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    try:
        # --- Запуск test_all.py ---
        buffer.write("🚀 Running: studiocore/tests/test_all.py\n\n")
        # Создаем процесс и ждем его завершения
        # Используем sys.executable для гарантии использования того же python
        process1 = subprocess.Popen(
            [sys.executable, "studiocore/tests/test_all.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        stdout1, _ = process1.communicate()
        buffer.write(stdout1 + "\n\n")

        # --- Запуск test_functional_texts.py ---
        buffer.write("🧠 Running: studiocore/tests/test_functional_texts.py\n\n")
        process2 = subprocess.Popen(
            [sys.executable, "studiocore/tests/test_functional_texts.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        stdout2, _ = process2.communicate()
        buffer.write(stdout2 + "\n\n")

        buffer.write("✅ Inline test session complete.\n")

    except Exception as e:
        buffer.write(f"❌ Ошибка при запуске subprocess: {e}\n")
        buffer.write(traceback.format_exc())
    
    finally:
        # ОБЯЗАТЕЛЬНО возвращаем stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    log.info("🏁 ...Встроенные тесты завершены.")
    
    return buffer.getvalue()


# === PUBLIC UI (Gradio) ===
log.debug("Инициализация Gradio UI...")
with gr.Blocks(title=f"🎧 StudioCore {STUDIOCORE_VERSION} — Public Interface") as iface_public:
    gr.Markdown(f"## 🎧 StudioCore {STUDIOCORE_VERSION}\nАдаптивный движок с тестами и логами.\n")

    with gr.Tab("🎙️ Анализ текста"):
        with gr.Row():
            text_input = gr.Textbox(
                label="Введите текст песни (внизу можно добавить описание вокала)",
                lines=12,
                placeholder="Вставьте лирику здесь…\n\nПример: (под хриплый мужской вокал, с криками)"
            )
            gender_input = gr.Radio(["auto", "male", "female"], value="auto", label="Пол вокала (Gender)")

        analyze_button = gr.Button("🔍 Анализировать")

        with gr.Row():
            result_box = gr.Textbox(label="📊 Результат (Summary)", lines=6)
            style_box = gr.Textbox(label="🎼 Suno [Style of Music] Prompt", lines=8, show_copy_button=True)

        with gr.Row():
            suno_box = gr.Textbox(label="🎤 Suno [Lyrics] Prompt (Vocal)", lines=8, show_copy_button=True)
            annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (inline)", lines=24)

        analyze_button.click(
            fn=analyze_text,
            inputs=[text_input, gender_input],
            outputs=[result_box, style_box, suno_box, annotated_box],
        )

    with gr.Tab("🧩 Логи и тесты"):
        gr.Markdown("### Автоматическая проверка ядра StudioCore")
        run_btn = gr.Button("🚀 Запустить тесты")
        output_box = gr.Textbox(label="Результаты тестов", lines=30, show_copy_button=True)
        run_btn.click(fn=run_inline_tests, inputs=None, outputs=output_box)

# === MOUNT ===
log.debug("Монтирование Gradio App в FastAPI (path='/')...")
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

# === RUN ===
if __name__ == "__main__":
    log.info(f"🚀 Запуск StudioCore {STUDIOCORE_VERSION} API (Inline Logs Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=7860)