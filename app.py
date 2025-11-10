# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5 — Compressed Adaptive Engine
Truth × Love × Pain = Conscious Frequency
Optimized for Hugging Face (low RAM, compressed annotated output)
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

# === АНАЛИЗ ТЕКСТА (с компрессией) ===
def analyze_text(text: str):
    """Полный анализ с интеллектуальным сжатием (до 100k символов, ~0.3 KB вывода)."""
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""
    try:
        result = core.analyze(text)
        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        # --- краткий summary ---
        summary = (
            f"✅ StudioCore v5\n"
            f"🎭 {result['style'].get('genre', '—')} | "
            f"🎵 {result['style'].get('style', '—')} | "
            f"🎙 {result['style'].get('vocal_form', '—')} | "
            f"⏱ {result.get('bpm', '—')} BPM | "
            f"🧠 {result.get('philosophy', '—')}"
        )

        # --- аннотация ---
        annotated_text = result.get("annotated_text") or core.annotate_text(
            text,
            result.get("overlay", {}),
            result.get("style", {}),
            result.get("vocals", []),
            result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
            result.get("emotions", {}),
            result.get("tlp", {}),
        )

        # --- очистка ---
        annotated_text = " ".join(annotated_text.split())
        if len(annotated_text) > 100000:
            annotated_text = annotated_text[:100000]

        # --- уплотнение структуры ---
        annotated_text = (
            annotated_text.replace("(tone:", "[")
            .replace("Truth=", "T=")
            .replace("Love=", "L=")
            .replace("Pain=", "P=")
            .replace("CF=", "CF=")
            .replace(")", "]")
        )

        # --- лёгкое адаптивное сжатие ---
        lines = annotated_text.split()
        preview = " ".join(lines[:80])  # первые 80 токенов
        tail = " ".join(lines[-30:]) if len(lines) > 120 else ""
        annotated_compressed = (
            f"🎙️ **Annotation (compressed 0.3 KB view)**\n\n"
            + preview
            + ("\n\n... " + tail if tail else "")
        )

        return (
            summary,
            result.get("prompt_full", "⚠️ Нет данных"),
            result.get("prompt_suno", "⚠️ Нет данных"),
            annotated_compressed,
        )

    except Exception as e:
        print("❌ Ошибка при анализе:\n", traceback.format_exc())
        return f"❌ Исключение: {str(e)}", "", "", ""

# === PUBLIC UI ===
with gr.Blocks(title="🎧 StudioCore v5 — Public Interface") as iface_public:
    gr.Markdown("### StudioCore (Public)\nПубличная версия без логов.")
    gr.Interface(
        fn=analyze_text,
        inputs=gr.Textbox(label="Введите текст песни", lines=10),
        outputs=[
            gr.Textbox(label="📊 Результат", lines=6),
            gr.Textbox(label="🎼 Полный промт", lines=8),
            gr.Textbox(label="🎧 Suno-промт", lines=8),
            gr.Textbox(label="🎙️ Аннотация (сжата)", lines=20),
        ],
        flagging_mode="never",
    )

# === ADMIN UI ===
def password_gate(password):
    if password == "Timofej151106":
        return gr.update(visible=False), gr.update(visible=True), ""
    return gr.update(visible=True), gr.update(visible=False), "❌ Неверный пароль"

with gr.Blocks(title="🎧 StudioCore Admin") as iface_admin:
    gr.Markdown("## 🔐 Вход в панель StudioCore")
    pwd = gr.Textbox(label="Пароль", type="password")
    err = gr.Markdown("")
    btn = gr.Button("Войти")
    admin_panel = gr.Group(visible=False)
    with admin_panel:
        gr.Interface(
            fn=analyze_text,
            inputs=gr.Textbox(label="Введите текст", lines=10),
            outputs=[
                gr.Textbox(label="📊 Результат", lines=6),
                gr.Textbox(label="🎼 Полный промт", lines=8),
                gr.Textbox(label="🎧 Suno-промт", lines=8),
                gr.Textbox(label="🎙️ Вокальная аннотация (сжата)", lines=20),
            ],
            flagging_mode="manual",
        )
    btn.click(password_gate, inputs=pwd, outputs=[pwd, admin_panel, err])

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
        summary, full, suno, annotated = analyze_text(text)
        return JSONResponse(
            content={
                "summary": summary,
                "prompt_full": full,
                "prompt_suno": suno,
                "annotated_text": annotated,
                "engine_version": STUDIOCORE_VERSION,
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# === MOUNT ===
iface_public.queue()
iface_admin.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")
app = gr.mount_gradio_app(app, iface_admin, path="/admin")

# === RUN ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
