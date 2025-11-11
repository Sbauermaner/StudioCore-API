# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Adaptive Annotation Engine (Safe Integration)
Truth × Love × Pain = Conscious Frequency
Unified core loader with fallback + Gradio + FastAPI + AutoTests
"""

import os, sys, subprocess, importlib, traceback, threading, time
import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# === Импорт ядра (с безопасной обёрткой) ===
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

# === Автосинхронизация OpenAPI (если есть скрипт) ===
try:
    if os.path.exists("auto_sync_openapi.py"):
        subprocess.call([sys.executable, "auto_sync_openapi.py"])
except Exception as e:
    print("⚠️ Ошибка OpenAPI sync:", e)

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

        result = core.analyze(text, preferred_gender=gender)
        if isinstance(result, dict) and "error" in result:
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

        annotated_text = result.get("annotated_text")
        if not annotated_text and hasattr(core, "annotate_text"):
            annotated_text = core.annotate_text(
                text,
                result.get("overlay", {}),
                style,
                vocals,
                result.get("bpm") or getattr(core, "rhythm", None).bpm_from_density(text) or 120,
                result.get("emotions", {}),
                result.get("tlp", {}),
            )

        style_prompt = (
            f"[StudioCore {STUDIOCORE_VERSION} | BPM: {result.get('bpm', 'auto')}]\n"
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
with gr.Blocks(title=f"🎧 StudioCore {STUDIOCORE_VERSION} — Public Interface") as iface_public:
    gr.Markdown(f"## 🎧 StudioCore {STUDIOCORE_VERSION}\nПубличная версия без логов.\n")

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

    analyze_button.click(
        fn=analyze_text,
        inputs=[text_input, gender_input],
        outputs=[result_box, style_box, suno_box, annotated_box],
    )


# === API ===
@app.get("/status")
async def status():
    return JSONResponse(
        content={
            "status": "ok",
            "engine": "StudioCore",
            "ready": not getattr(core, "is_fallback", False),
            "version": STUDIOCORE_VERSION,
        }
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
                "style_prompt": style_prompt,
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

    print(f"🚀 Запуск StudioCore {STUDIOCORE_VERSION} API...")

    # ==========================================================
    # 🧩 Auto Integrity + Functional Logic Tests
    # ==========================================================
    def run_integrity_and_functional_tests():
        time.sleep(2)
        print("\n🧩 Auto-Running StudioCore Full System Test...")
        res1 = os.system("python3 studiocore/tests/test_all.py > test_log.txt 2>&1")
        if res1 == 0:
            print("✅ test_all.py — системные тесты успешно завершены.")
        else:
            print("⚠️ Ошибка в test_all.py — см. test_log.txt")

        print("\n🧠 Running Functional Text Logic Test...")
        res2 = os.system("python3 studiocore/tests/test_functional_texts.py > test_logic.txt 2>&1")
        if res2 == 0:
            print("✅ test_functional_texts.py — функциональная логика пройдена.")
        else:
            print("⚠️ Ошибка в функциональном тесте — см. test_logic.txt.")

        print("\n📁 Логи сохранены в файлы:")
        print("   • test_log.txt   — системные тесты")
        print("   • test_logic.txt — проверка смысловой логики анализа\n")

    threading.Thread(target=run_integrity_and_functional_tests, daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=7860)
