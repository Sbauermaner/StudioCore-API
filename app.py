# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5 — Expressive Adaptive Engine
Truth × Love × Pain = Conscious Frequency
Memory-Safe Edition for Hugging Face Spaces (≤2 GB RAM)
"""

import os
import gradio as gr
import traceback
import importlib, subprocess, sys, threading, json, time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from studiocore import StudioCore, STUDIOCORE_VERSION

# === 💾 Memory-Safe конфигурация окружения ===
os.environ["HF_HUB_DISABLE_CACHE"] = "1"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GRADIO_TEMP_DIR"] = "/tmp"
os.environ["TRANSFORMERS_CACHE"] = "/tmp"

# === ⚙️ Проверка и установка requests ===
if importlib.util.find_spec("requests") is None:
    try:
        print("⚙️ Устанавливаю 'requests' для модулей (README, self-check)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except Exception:
        pass

try:
    import requests  # type: ignore
except Exception:
    requests = None

# === 🔄 Автосинхронизация OpenAPI ===
try:
    if os.path.exists("auto_sync_openapi.py"):
        print("🔄 Синхронизирую OpenAPI (JSON → YAML)...")
        subprocess.call([sys.executable, "auto_sync_openapi.py"])
except Exception as e:
    print("⚠️ Ошибка при автосинхронизации:", e)

# === 📘 Обновление README ===
try:
    if os.path.exists("update_readme_status.py"):
        print("🪶 Обновляю README.md...")
        import update_readme_status
        update_readme_status.update_readme()
except Exception as e:
    print("⚠️ Ошибка при обновлении README:", e)

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
        print("🧪 Self-check отключён.")
        return
    if requests is None:
        print("ℹ️ requests недоступен — пропускаю self-check.")
        return

    time.sleep(5)
    api_url = "http://0.0.0.0:7860/api/predict"
    test_text = "Вся моя жизнь — как быль или небыль, Вся моя жизнь — по краю скользить..."
    print("\n🧠 [StudioCore Self-Check]...\n")
    try:
        r = requests.post(api_url, json={"text": test_text}, timeout=25)
        if r.status_code != 200:
            print(f"❌ [Self-Check] API вернул {r.status_code}")
            return
        data = r.json()
        summary = data.get("summary", "")
        tlp_ok = any(tag in summary for tag in ["Truth", "Love", "Pain"])
        tonesync_ok = "ToneSync" in data.get("prompt_suno", "")
        ann_ok = "[" in data.get("annotated_text", "")
        status = (
            "✅ StudioCore v5 совместимо и активно."
            if all([tlp_ok, tonesync_ok, ann_ok])
            else "⚠️ Несовпадение с монолитом."
        )
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "engine_version": STUDIOCORE_VERSION,
            "status": status,
            "summary_preview": summary[:300],
        }
        # 💡 Не сохраняем файл, только вывод в лог
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as e:
        print("❌ [Self-Check] Ошибка:", e)

threading.Thread(target=auto_core_check, daemon=True).start()

# === Основной анализ ===
def analyze_text(text: str):
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""
    try:
        result = core.analyze(text)
        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        summary = (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Стиль: {result['style'].get('style', '—')}\n"
            f"Вокальная форма: {result['style'].get('vocal_form', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия ядра: {result.get('version', '—')}"
        )

        annotated_text = result.get("annotated_text") or core.annotate_text(
            text,
            result.get("overlay", {}),
            result.get("style", {}),
            result.get("vocals", []),
            result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
            result.get("emotions", {}),
            result.get("tlp", {}),
        )

        # === Генерация вокального слоя ===
        tlp = result.get("tlp", {})
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        annotated_lines = []

        def tone(idx, total):
            if idx < total * 0.25:
                return "(soft whisper)", "fragile"
            elif idx < total * 0.6:
                return "(warm mid-voice)", "balanced"
            elif love > pain and cf > 0.6:
                return "(gentle falsetto)", "open"
            else:
                return "(strong release)", "bright"

        for i, line in enumerate(lines):
            desc, tag = tone(i, len(lines))
            if i == 0:
                header = f"[Verse 1 – {desc}]"
            elif i == len(lines) - 1:
                header = f"[Outro – {desc}]"
            elif any(k in line.lower() for k in ["люб", "love", "you", "бог", "christ"]):
                header = f"[Chorus – {desc}]"
            elif "прости" in line.lower():
                header = f"[Bridge – {desc}]"
            else:
                header = f"[Verse – {desc}]"
            annotated_lines += [
                header,
                line,
                f"(tone: {tag}, Truth={truth:.2f}, Love={love:.2f}, Pain={pain:.2f}, CF={cf:.2f})",
                "",
            ]

        annotated_text = (
            "🎙️ **Core Annotation + Vocal Layer**\n\n"
            + annotated_text + "\n\n" + "\n".join(annotated_lines)
        )

        # 💾 Safe Output Buffer (≤ 0.5 MB)
        MAX_ANNOTATION_BYTES = 500_000
        if len(annotated_text.encode("utf-8")) > MAX_ANNOTATION_BYTES:
            annotated_text = (
                annotated_text[:MAX_ANNOTATION_BYTES]
                + "\n\n[... annotation truncated for memory safety ...]"
            )

        return (
            summary,
            result.get("prompt_full", "⚠️ Нет данных"),
            result.get("prompt_suno", "⚠️ Нет данных"),
            annotated_text,
        )
    except Exception as e:
        print("❌ Ошибка при анализе:\n", traceback.format_exc())
        return f"❌ Исключение: {str(e)}", "", "", ""

# === UI ===
with gr.Blocks(title="🎧 StudioCore v5 — Public Interface") as iface_public:
    gr.Markdown("### StudioCore (Public) — оптимизированная версия для Spaces.")
    gr.Interface(
        fn=analyze_text,
        inputs=gr.Textbox(label="Введите текст песни", lines=10),
        outputs=[
            gr.Textbox(label="📊 Результат анализа", lines=6),
            gr.Textbox(label="🎼 Полный промт", lines=8),
            gr.Textbox(label="🎧 Suno-промт", lines=8),
            gr.Textbox(label="🎙️ Аннотация (Vocal Layer)", lines=20),
        ],
        flagging_mode="never",
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

# === MOUNT & RUN ===
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
