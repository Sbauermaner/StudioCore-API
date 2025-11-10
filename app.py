# -*- coding: utf-8 -*-
"""
🎧 StudioCore v4.3–v5 — Expressive Adaptive Engine
Truth × Love × Pain = Conscious Frequency
"""

import gradio as gr
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from studiocore import StudioCore, STUDIOCORE_VERSION

# === Инициализация ядра ===
core = StudioCore()
app = FastAPI(title="StudioCore API")

# === 🔎 Автоматическая проверка ядра после старта ===
import threading, requests, json, time
from datetime import datetime

def auto_core_check():
    """Выполняет внутренний self-check ядра после старта Space."""
    time.sleep(5)  # ждём пока API поднимется
    api_url = "http://0.0.0.0:7860/api/predict"
    test_text = """Вся моя жизнь — как быль или небыль,
Вся моя жизнь — по краю скользить.
Но я молю открыть в сердце двери,
Я так хочу твоей женщиной быть…"""

    print("\n🧠 [StudioCore Self-Check] Запуск теста совместимости...\n")
    try:
        r = requests.post(api_url, json={"text": test_text}, timeout=30)
        if r.status_code != 200:
            print(f"❌ [Self-Check] API вернул {r.status_code}: {r.text}")
            return
        data = r.json()
        summary = data.get("summary", "")
        annotated = data.get("annotated_text", "")
        tlp_ok = any(tag in summary for tag in ["Truth", "Love", "Pain"])
        tonesync_ok = "ToneSync" in data.get("prompt_suno", "")
        ann_ok = "[" in annotated

        print("📊 Жанр и стиль:", "OK" if "Жанр" in summary or "Genre" in summary else "⚠️ нет")
        print("🩵 TLP:", "OK" if tlp_ok else "⚠️ нет")
        print("🎨 ToneSync:", "OK" if tonesync_ok else "⚠️ нет")
        print("🎙️ Аннотация:", "OK" if ann_ok else "⚠️ нет")

        status = (
            "✅ StudioCore v5 совместимо и активно."
            if all([tlp_ok, tonesync_ok, ann_ok])
            else "⚠️ Проверка выявила неполное совпадение с монолитом."
        )
        print("\n" + status)

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "summary": summary[:400],
            "has_tlp": tlp_ok,
            "has_tonesync": tonesync_ok,
            "annotated_preview": "\n".join(annotated.splitlines()[:6]),
        }
        with open("startup_selfcheck_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("📁 Self-check report сохранён → startup_selfcheck_report.json\n")

    except Exception as e:
        print("❌ [Self-Check] Ошибка при тесте:", e)

# Запуск в фоне, чтобы не мешать Gradio
threading.Thread(target=auto_core_check, daemon=True).start()


# === Основная функция анализа ===
def analyze_text(text: str):
    """Основная функция анализа текста."""
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

        if result.get("annotated_text"):
            annotated_text = result["annotated_text"]
        else:
            annotated_text = core.annotate_text(
                text,
                result.get("overlay", {}),
                result.get("style", {}),
                result.get("vocals", []),
                result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
                result.get("emotions", {}),
                result.get("tlp", {}),
            )

        # --- VOCAL ANNOTATION LAYER ---
        tlp = result.get("tlp", {})
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        annotated_lines = []

        def describe_tone(idx, total):
            if idx < total * 0.25:
                tone_desc = "(soft whisper, emotional intro, close-mic vocal)"
                tone_tag = "fragile, intimate, trembling"
            elif idx < total * 0.6:
                tone_desc = "(warm mid-voice, storytelling tone, slight tension)"
                tone_tag = "balanced, grounded, expressive"
            elif love > pain and cf > 0.6:
                tone_desc = "(gentle falsetto mixed with vibrato, tender resonance)"
                tone_tag = "open, lyrical, emotional"
            else:
                tone_desc = "(strong emotional release, warm full voice, slight cry in tone)"
                tone_tag = "bright, soaring, cathartic"
            return tone_desc, tone_tag

        for i, line in enumerate(lines):
            tone_desc, tone_tag = describe_tone(i, len(lines))
            if i == 0:
                header = f"[Verse 1 – {tone_desc}]"
            elif i == len(lines) - 1:
                header = f"[Outro – {tone_desc}]"
            elif "люб" in line.lower() or "you" in line.lower():
                header = f"[Chorus – {tone_desc}]"
            else:
                header = f"[Verse – {tone_desc}]"

            tone_line = (
                f"(tone: {tone_tag}, "
                f"Truth={truth:.2f}, Love={love:.2f}, Pain={pain:.2f}, CF={cf:.2f})"
            )
            annotated_lines += [header, line, tone_line, ""]

        annotated_text = (
            "🎙️ **Core Annotation + Vocal Layer**\n\n"
            + annotated_text
            + "\n\n"
            + "\n".join(annotated_lines)
        )

        return (
            summary,
            result.get("prompt_full", "⚠️ Нет данных"),
            result.get("prompt_suno", "⚠️ Нет данных"),
            annotated_text,
        )

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Ошибка при анализе:\n", tb)
        return f"❌ Исключение: {str(e)}", "", "", ""


# === Gradio-интерфейс ===
iface = gr.Interface(
    fn=analyze_text,
    inputs=gr.Textbox(
        label="Введите текст песни, стихотворения или манифеста",
        lines=10,
        placeholder="Например: Под серым небом я шёл один, дождь шептал забытые имена..."
    ),
    outputs=[
        gr.Textbox(label="📊 Результат анализа", lines=6),
        gr.Textbox(label="🎼 Полный промт (Full Prompt)", lines=8),
        gr.Textbox(label="🎧 Suno-промт (до 1000 символов)", lines=8),
        gr.Textbox(label="🎙️ Вокально-эмоциональная аннотация (Vocal Layer)", lines=20)
    ],
    title="🎧 StudioCore v4.3–v5 — Expressive Adaptive Engine",
    description="AI-движок анализа эмоций, структуры и вокальной выразительности текста.\nФормула ядра: Truth × Love × Pain = Conscious Frequency.",
)

# === Healthcheck ===
@app.get("/status")
async def status():
    return JSONResponse(content={"status": "ok", "engine": "StudioCore", "ready": True})

# === Version endpoint ===
@app.get("/version")
async def version_info():
    return JSONResponse(
        content={
            "status": "ok",
            "engine": "StudioCore",
            "version": STUDIOCORE_VERSION,
            "signature": core.__class__.__name__,
        }
    )

# === API endpoint ===
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
            }
        )
    except Exception as e:
        print("❌ Ошибка API /api/predict:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

# === Монтируем Gradio ===
app = gr.mount_gradio_app(app, iface, path="/")

# === Запуск ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
