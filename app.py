# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Adaptive Annotation Engine
v5: Внедрен централизованный логгер (studiocore.logger)
"""

import os, sys, subprocess, importlib, traceback, threading, time, io
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging # <-- 1. Импортируем logging

# === 2. Импортируем и АКТИВИРУЕМ наш логгер ===
from studiocore.logger import setup_logging
setup_logging()
# === Логирование активировано ===

# Получаем наш логгер (он уже настроен)
log = logging.getLogger(__name__)

# === Импорт ядра ===
# (Импорты ядра должны идти ПОСЛЕ настройки логгера)
try:
    from studiocore import get_core, STUDIOCORE_VERSION
except ImportError as e:
    log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА ЯДРА: {e}")
    log.critical("Убедитесь, что все зависимости установлены и нет синтаксических ошибок.")
    sys.exit(1)


# === Установка requests (для self-check) ===
# (Этот блок остается без изменений)
if importlib.util.find_spec("requests") is None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except Exception:
        pass
try:
    import requests  # type: ignore
except Exception:
    requests = None

# === Инициализация ядра и FastAPI ===
log.info("Инициализация ядра StudioCore...")
core = get_core()
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
# (Этот блок остается без изменений)

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
        log.debug(f"API /api/predict успешно вернул результат.")
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        log.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в /api/predict: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# === Конец API ENDPOINT ===


# === SELF-CHECK ===
def auto_core_check():
    if os.environ.get("DISABLE_SELF_CHECK") == "1" or requests is None:
        return
    time.sleep(3)
    log.debug("[Self-Check] Запуск самопроверки эндпоинта /api/predict...")
    try:
        # Увеличиваем таймаут до 20 секунд (на случай медленного запуска)
        r = requests.post("http://127.0.0.1:7860/api/predict", json={"text": "test"}, timeout=20)
        log.info(f"[Self-Check] → Статус: {r.status_code}")
        if r.status_code != 200:
             log.warning(f"[Self-Check] → Ответ: {r.text[:100]}...")
    except Exception as e:
        log.error(f"❌ Self-Check ошибка: {e}")

threading.Thread(target=auto_core_check, daemon=True).start()

# === АНАЛИЗ ТЕКСТА ===
def analyze_text(text: str, gender: str = "auto"):
    """Основная функция анализа текста через StudioCore."""
    log.debug(f"Gradio analyze_text: получено {len(text)} символов, gender={gender}")
    if not text.strip():
        log.warning("Gradio analyze_text: получен пустой текст.")
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        if getattr(core, "is_fallback", False):
            log.error("Gradio analyze_text: Ядро в режиме Fallback!")
            return (
                "⚠️ StudioCore находится в безопасном режиме (fallback). "
                "Анализ временно недоступен.", "", "", ""
            )

        # --- Проверка пользовательских описаний вокала ---
        overlay = {}
        # (Логика voice_profile_hint остается без изменений)
        # ...
        if any(k in text.lower() for k in [
            "вокал", "voice", "growl", "scream", "raspy", "мужск", "женск",
            "пескляв", "soft", "airy", "shout", "grit", "фальцет", "whisper"
        ]):
            overlay["voice_profile_hint"] = text.split("\n")[-1].strip()
            log.info(f"🎙️ [UI] Обнаружено описание вокала: {overlay['voice_profile_hint']}")
        else:
            overlay = None

        # --- Вызов ядра ---
        log.debug("Gradio analyze_text: Вызов core.analyze...")
        result = core.analyze(text, preferred_gender=gender, overlay=overlay)

        if isinstance(result, dict) and "error" in result:
            log.error(f"Gradio analyze_text: Ядро вернуло ошибку: {result['error']}")
            return f"❌ Ошибка: {result['error']}", "", "", ""

        # (Остальная часть функции analyze_text остается без изменений)
        # ...

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

        annotated_text = result.get("annotated_text")
        if not annotated_text and hasattr(core, "annotate_text"):
            log.debug("Gradio analyze_text: Вызов core.annotate_text (fallback)...")
            annotated_text = core.annotate_text(
                text,
                result.get("overlay", {}),
                style,
                vocals,
                result.get("bpm") or getattr(core, "rhythm", None).bpm_from_density(text) or 120,
                result.get("emotions", {}),
                result.get("tlp", {}),
            )
        
        style_prompt = result.get("prompt_suno_style", "⚠️ Нет данных")
        
        log.debug("Gradio analyze_text: Анализ завершен, возврат в UI.")
        return (
            summary,
            style_prompt, # prompt_suno_style
            result.get("prompt_suno_lyrics", "⚠️ Нет данных"), # prompt_suno_lyrics
            annotated_text,
        )

    except Exception:
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в analyze_text (UI): {traceback.format_exc()}")
        return "❌ Внутреннее исключение при анализе.", "", "", ""

# === INLINE TEST RUNNER ===
def run_inline_tests():
    """Выполняет тесты и возвращает stdout прямо в интерфейс."""
    log.info("=" * 30)
    log.info("🚀 ЗАПУСК ВСТРОЕННЫХ ТЕСТОВ...")
    log.info("=" * 30)
    buffer = io.StringIO()
    # Направляем логгер также в buffer
    test_log_handler = logging.StreamHandler(buffer)
    test_log_handler.setFormatter(logging.Formatter(
        "[%(name)s.%(funcName)s:%(lineno)d] - %(message)s"
    ))
    logging.getLogger().addHandler(test_log_handler)

    buffer.write(f"🧩 StudioCore {STUDIOCORE_VERSION} — Inline Test Session\n")
    buffer.write(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    try:
        buffer.write("🚀 Running: studiocore/tests/test_all.py\n\n")
        # Мы используем os.system, но логирование уже перехватит stdout/stderr
        # благодаря setup_logging()
        
        # Создаем временные файлы для вывода, чтобы точно его захватить
        test_all_out = "tmp_test_all_out.txt"
        
        # Запускаем test_all.py и перенаправляем ЕГО stdout/stderr в файл
        os.system(f"python3 studiocore/tests/test_all.py > {test_all_out} 2>&1")
        
        with open(test_all_out, "r", encoding="utf-8", errors="ignore") as f:
            buffer.write(f.read() + "\n")
        os.remove(test_all_out) # Чистим за собой

        # ---
        
        buffer.write("\n🧠 Running: studiocore/tests/test_functional_texts.py\n\n")
        test_func_out = "tmp_test_func_out.txt"
        
        os.system(f"python3 studiocore/tests/test_functional_texts.py > {test_func_out} 2>&1")
        
        with open(test_func_out, "r", encoding="utf-8", errors="ignore") as f:
            buffer.write(f.read() + "\n")
        os.remove(test_func_out) # Чистим за собой


        buffer.write("✅ Inline test session complete.\n")

    except Exception as e:
        buffer.write(f"❌ Ошибка при запуске тестов: {e}\n")
        log.error(f"❌ Ошибка при запуске тестов: {e}")

    # Удаляем наш временный обработчик логов
    logging.getLogger().removeHandler(test_log_handler)
    log.info("🏁 ...Встроенные тесты завершены.")
    return buffer.getvalue()

# === PUBLIC UI (Gradio) ===
# (Этот блок остается без изменений, за исключением имен вывода)
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
            style_box = gr.Textbox(label="🎼 Стиль и инструменты (Style Prompt)", lines=8)

        with gr.Row():
            suno_box = gr.Textbox(label="🎧 Suno-промт (Lyrics)", lines=8)
            annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (inline)", lines=24)

        analyze_button.click(
            fn=analyze_text,
            inputs=[text_input, gender_input],
            # Обновляем имена вывода, чтобы соответствовать analyze_text
            outputs=[result_box, style_box, suno_box, annotated_box],
        )

    with gr.Tab("🧩 Логи и тесты"):
        gr.Markdown("### Автоматическая проверка ядра StudioCore")
        run_btn = gr.Button("🚀 Запустить тесты")
        output_box = gr.Textbox(label="Результаты тестов", lines=30, show_copy_button=True)
        run_btn.click(fn=run_inline_tests, inputs=None, outputs=output_box)

# === MOUNT ===
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

# === RUN ===
if __name__ == "__main__":
    import uvicorn
    log.info(f"🚀 Запуск StudioCore {STUDIOCORE_VERSION} API (Inline Logs Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=7860)