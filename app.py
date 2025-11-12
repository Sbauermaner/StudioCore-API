# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Adaptive Annotation Engine (Safe Integration + Inline Logs)
Truth × Love × Pain = Conscious Frequency
Unified core loader with fallback + Gradio + FastAPI + Inline Log Viewer

ИСПРАВЛЕНИЕ (v3):
- Добавлен эндпоинт /api/predict для тестов.
- Увеличен таймаут self-check до 25с (для Inference API).
"""

import os, sys, subprocess, importlib, traceback, threading, time, io
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# === Импорт ядра ===
from studiocore import get_core, STUDIOCORE_VERSION

# === Установка requests (для self-check) ===
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
# (Эндпоинт, который ищут тесты)

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
    try:
        # Мы сопоставляем данные из запроса с тем, что ожидает core.analyze
        result = core.analyze(
            request_data.text,
            preferred_gender=request_data.gender,
            overlay=request_data.overlay
            # TLP передается через overlay, если нужно:
            # overlay={"tlp_override": request_data.tlp}
        )
        
        if isinstance(result, dict) and "error" in result:
             # Если ядро вернуло ошибку, передаем ее
             return JSONResponse(content=result, status_code=400)
        
        # Возвращаем полный результат (тесты ожидают 'bpm' и 'style')
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в /api/predict: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# === Конец API ENDPOINT ===


# === SELF-CHECK ===
def auto_core_check():
    if os.environ.get("DISABLE_SELF_CHECK") == "1" or requests is None:
        return
    time.sleep(5) # Даем серверу чуть больше времени на старт
    
    print("[Self-Check] Запуск самопроверки эндпоинта /api/predict...")
    
    try:
        # ИСПРАВЛЕНИЕ: Таймаут 25с (для Inference API)
        r = requests.post("http://127.0.0.1:7860/api/predict", json={"text": "test"}, timeout=25)
        print(f"[Self-Check] → Статус: {r.status_code}")
        if r.status_code != 200:
             print(f"[Self-Check] → Ответ: {r.text[:200]}...")
    except Exception as e:
        print(f"❌ Self-Check ошибка: {e}")

threading.Thread(target=auto_core_check, daemon=True).start()

# === АНАЛИЗ ТЕКСТА ===
def analyze_text(text: str, gender: str = "auto"):
    """Основная функция анализа текста через StudioCore."""
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        if getattr(core, "is_fallback", False):
            return (
                "⚠️ StudioCore находится в безопасном режиме (fallback). "
                "Анализ временно недоступен.", "", "", ""
            )

        # --- Проверка пользовательских описаний вокала ---
        overlay = {}
        voice_hint_keywords = [
            "вокал", "voice", "growl", "scream", "raspy", "мужск", "женск",
            "пескляв", "soft", "airy", "shout", "grit", "фальцет", "whisper"
        ]
        
        # Ищем подсказку в *последней* строке
        last_line = text.strip().split("\n")[-1].lower()
        if any(k in last_line for k in voice_hint_keywords):
            overlay["voice_profile_hint"] = last_line.strip("() ")
            print(f"🎙️ [UI] Обнаружено описание вокала: {overlay['voice_profile_hint']}")
        else:
            overlay = None

        # --- Вызов ядра ---
        result = core.analyze(text, preferred_gender=gender, overlay=overlay)

        if isinstance(result, dict) and "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        style = result.get("style", {})
        vocals = result.get("vocals", [])
        instruments = ", ".join(result.get("instruments", [])) or "no instruments"
        vocal_form = style.get("vocal_form", "auto")

        summary = (
            f"✅ StudioCore {STUDIOCORE_VERSION} (Mode: {result.get('mode', 'AUTO')})\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({result.get('preferred_gender', 'auto')}) | "
            f"🎸 {instruments} | "
            f"⏱ {result.get('bpm', '—')} BPM"
        )

        annotated_text = result.get("annotated_text", "⚠️ Аннотация не сгенерирована")
        
        # Собираем Style Prompt из уже готовых данных
        style_prompt = (
            f"[StudioCore {STUDIOCORE_VERSION} | BPM: {result.get('bpm', 'auto')}]\n"
            f"Genre: {style.get('genre', 'unknown')}\n"
            f"Vocal: {vocal_form} ({result.get('preferred_gender', 'auto')})\n"
            f"Instruments: {instruments}\n"
            f"Tone: {style.get('key', 'auto')}\n"
            f"Atmosphere: {style.get('atmosphere', 'balanced')}\n"
            f"Narrative: {style.get('narrative', 'flow')}\n"
        )

        return (
            summary,
            style_prompt,
            result.get("prompt_suno", "⚠️ Нет данных"),
            annotated_text,
        )

    except Exception:
        print("❌ Ошибка при анализе:\n", traceback.format_exc())
        return "❌ Внутреннее исключение при анализе.", "", "", ""

# === INLINE TEST RUNNER ===
def run_inline_tests():
    """Выполняет тесты и возвращает stdout прямо в интерфейс."""
    buffer = io.StringIO()
    buffer.write(f"🧩 StudioCore {STUDIOCORE_VERSION} — Inline Test Session\n")
    buffer.write(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    test_all_path = os.path.join("studiocore", "tests", "test_all.py")
    test_logic_path = os.path.join("studiocore", "tests", "test_functional_texts.py")

    try:
        buffer.write(f"🚀 Running: {test_all_path}\n")
        # Используем sys.executable для гарантии той же среды
        res1 = subprocess.run(
            [sys.executable, test_all_path],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        buffer.write(res1.stdout + "\n")
        if res1.stderr:
             buffer.write(f"--- STDERR ---\n{res1.stderr}\n")

        buffer.write(f"\n🧠 Running: {test_logic_path}\n")
        res2 = subprocess.run(
            [sys.executable, test_logic_path],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        buffer.write(res2.stdout + "\n")
        if res2.stderr:
             buffer.write(f"--- STDERR ---\n{res2.stderr}\n")

        buffer.write("✅ Inline test session complete.\n")

    except Exception as e:
        buffer.write(f"❌ Ошибка при запуске тестов: {e}\n{traceback.format_exc()}\n")

    return buffer.getvalue()


# === PUBLIC UI (Gradio) ===
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
            result_box = gr.Textbox(label="📊 Результат", lines=6)
            style_box = gr.Textbox(label="🎼 Стиль и инструменты", lines=8)

        with gr.Row():
            suno_box = gr.Textbox(label="🎧 Suno-промт (Style)", lines=8)
            annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (inline)", lines=24, show_copy_button=True)

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
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

# === RUN ===
if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Запуск StudioCore {STUDIOCORE_VERSION} API (Inline Logs Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=7860)