# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2 — Adaptive Annotation Engine
Truth × Love × Pain = Conscious Frequency
Enhanced adaptive output with vocal gender, style, and instruments
"""

import os, sys, subprocess, importlib, traceback, threading, json, time
from datetime import datetime
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from studiocore import StudioCore, STUDIOCORE_VERSION

# === Установка requests ===
if importlib.util.find_spec("requests") is None:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except Exception:
        pass
try:
    import requests  # type: ignore
except Exception:
    requests = None

# === Автосинхронизация OpenAPI ===
try:
    if os.path.exists("auto_sync_openapi.py"):
        subprocess.call([sys.executable, "auto_sync_openapi.py"])
except Exception as e:
    print("⚠️ Ошибка OpenAPI sync:", e)

# === Инициализация ядра ===
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
    if os.environ.get("DISABLE_SELF_CHECK") == "1":
        return
    if requests is None:
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
    """Полный анализ текста с генерацией inline-аннотации и адаптацией под пол вокала."""
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""
    try:
        result = core.analyze(text, preferred_gender=gender)
        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        # --- краткий summary ---
        style = result.get("style", {})
        vocals = result.get("vocals", [])
        instruments = ", ".join(result.get("instruments", [])) or "no instruments"
        vocal_form = style.get("vocal_form", "auto")

        summary = (
            f"✅ StudioCore v5.2\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({gender}) | "
            f"🎸 {instruments} | "
            f"⏱ {result.get('bpm', '—')} BPM"
        )

        # --- аннотация ---
        annotated_text = result.get("annotated_text") or core.annotate_text(
            text,
            result.get("overlay", {}),
            style,
            vocals,
            result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
            result.get("emotions", {}),
            result.get("tlp", {}),
        )

        # === Inline-аннотация ===
        try:
            sections = result.get("sections", [])
            inline_lines = []
            for section in sections:
                mood = section.get("emotion", "neutral")
                tone = section.get("tone", "mid")
                phrasing = core.vocals.map_emotion_to_english(mood, tone)
                inline_lines.append(f"[{section.get('name','Verse')} – {phrasing}]")
                inline_lines.append(section.get("text", "").strip())
                inline_lines.append("")
            annotated_inline = "\n".join(inline_lines) if inline_lines else annotated_text
        except Exception:
            annotated_inline = annotated_text

        # --- ограничение размера ---
        if len(annotated_inline) > 100000:
            annotated_inline = annotated_inline[:100000] + "\n\n⚠️ [Truncated]"

        # --- style-prompt для Suno ---
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
            annotated_inline,
        )

    except Exception as e:
        print("❌ Ошибка при анализе:\n", traceback.format_exc())
        return f"❌ Исключение: {str(e)}", "", "", ""


# === PUBLIC UI (Gradio) ===
with gr.Blocks(title="🎧 StudioCore v5.2 — Public Interface") as iface_public:
    gr.Markdown("## 🎧 StudioCore v5.2\nПубличная версия без логов.\n")

    with gr.Row():
        text_input = gr.Textbox(label="Введите текст песни", lines=10, placeholder="Введите текст...")
        gender_input = gr.Radio(["auto", "male", "female"], value="auto", label="Пол вокала (Gender)")

    analyze_button = gr.Button("🔍 Анализировать")

    with gr.Row():
        result_box = gr.Textbox(label="📊 Результат", lines=6)
        style_box = gr.Textbox(label="🎼 Стиль и инструменты", lines=8)

    with gr.Row():
        suno_box = gr.Textbox(label="🎧 Suno-промт", lines=8)
        annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (inline)", lines=20)

    analyze_button.click(
        fn=analyze_text,
        inputs=[text_input, gender_input],
        outputs=[result_box, style_box, suno_box, annotated_box],
    )


# === API ===
@app.post("/api/predict")
async def predict_api(request: Request):
    try:
        payload = await request.json()
        text = payload.get("text", "")
        gender = payload.get("gender", "auto")
        summary, full, suno, annotated = analyze_text(text, gender)
        return JSONResponse(
            content={
                "summary": summary,
                "prompt_full": full,
                "prompt_suno": suno,
                "annotated_text": annotated,
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
