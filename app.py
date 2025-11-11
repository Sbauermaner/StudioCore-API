# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2 — Adaptive Annotation Engine
Truth × Love × Pain = Conscious Frequency
Enhanced adaptive output with vocal gender, style, and instruments
"""

import os, sys, subprocess, importlib, traceback, threading, time
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from studiocore import StudioCore, STUDIOCORE_VERSION

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

# === Автосинхронизация OpenAPI (если есть скрипт) ===
try:
    if os.path.exists("auto_sync_openapi.py"):
        subprocess.call([sys.executable, "auto_sync_openapi.py"])
except Exception as e:
    print("⚠️ Ошибка OpenAPI sync:", e)

# === Инициализация ядра и FastAPI ===
core = StudioCore()
app = FastAPI(title="StudioCore API")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SELF-CHECK ===
def auto_core_check():
    if os.environ.get("DISABLE_SELF_CHECK") == "1" or requests is None:
        return
    time.sleep(3)
    try:
        r = requests.post("http://0.0.0.0:7860/api/predict", json={"text": "test"}, timeout=10)
        print(f"[Self-Check] → {r.status_code}")
    except Exception as e:
        print("❌ Self-Check error:", e)

threading.Thread(target=auto_core_check, daemon=True).start()


# === АНАЛИЗ ТЕКСТА (адаптивная аннотация) ===
def analyze_text(text: str, gender: str = "auto"):
    """
    Возвращает:
        summary, style_prompt, prompt_suno, annotated_inline
    """
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        result = core.analyze(text, preferred_gender=gender)
        if isinstance(result, dict) and "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        style = result.get("style", {})
        vocals = result.get("vocals", [])
        instruments = ", ".join(result.get("instruments", [])) or "no instruments"
        vocal_form = style.get("vocal_form", "auto")

        # --- краткий summary ---
        summary = (
            f"✅ StudioCore v5.2\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({gender}) | "
            f"🎸 {instruments} | "
            f"⏱ {result.get('bpm', '—')} BPM"
        )

        # --- аннотированный текст (от ядра) ---
        annotated_text = result.get("annotated_text")
        if not annotated_text:
            # fallback — на случай, если ядро не вернуло строку
            annotated_text = core.annotate_text(
                text,
                result.get("overlay", {}),
                style,
                vocals,
                result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
                result.get("emotions", {}),
                result.get("tlp", {}),
            )

        # --- компактный style-prompt (не лирика!) ---
        style_prompt = (
            f"[StudioCore v5.2 | BPM: {result.get('bpm', 'auto')}]\n"
            f"Genre: {style.get('genre', 'unknown')}\n"
            f"Vocal: {vocal_form} ({gender})\n"
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


# === PUBLIC UI (Gradio) ===
with gr.Blocks(title="🎧 StudioCore v5.2 — Public Interface") as iface_public:
    gr.Markdown("## 🎧 StudioCore v5.2\nПубличная версия без логов.\n")

    with gr.Row():
        text_input = gr.Textbox(label="Введите текст песни", lines=12, placeholder="Вставьте лирику здесь…")
        gender_input = gr.Radio(["auto", "male", "female"], value="auto", label="Пол вокала (Gender)")

    analyze_button = gr.Button("🔍 Анализировать")

    with gr.Row():
        result_box = gr.Textbox(label="📊 Результат", lines=6)
        style_box = gr.Textbox(label="🎼 Стиль и инструменты", lines=8)

    with gr.Row():
        suno_box = gr.Textbox(label="🎧 Suno-промт (Style)", lines=8)
        annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (inline)", lines=24)

    # Важно: передаем 2 входа → 4 выхода (исправляет ошибку “needed: 2, got: 1”)
    analyze_button.click(
        fn=analyze_text,
        inputs=[text_input, gender_input],
        outputs=[result_box, style_box, suno_box, annotated_box],
    )


# === API ===
@app.get("/status")
async def status():
    return JSONResponse(
        content={"status": "ok", "engine": "StudioCore", "ready": True, "version": STUDIOCORE_VERSION}
    )

@app.post("/api/predict")
async def predict_api(request: Request):
    try:
        payload = await request.json()
        text = payload.get("text", "")
        gender = payload.get("gender", "auto")
        summary, style_prompt, suno, annotated = analyze_text(text, gender)
        return JSONResponse(
            content={
                "summary": summary,
                "style_prompt": style_prompt,   # компактный style prompt (≤1000)
                "prompt_suno": suno,            # адаптивный suno prompt из adapter.py
                "annotated_text": annotated,    # полный аннотированный текст
                "engine_version": STUDIOCORE_VERSION,
                "gender": gender,
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# === MOUNT ===
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")


# === RUN ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
