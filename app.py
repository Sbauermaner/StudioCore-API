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

# === Основная функция анализа ===
def analyze_text(text: str):
    """
    Основная функция анализа текста.
    Возвращает: summary, full_prompt, suno_prompt, annotated_text (дополнение)
    """
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        # --- Запуск основного анализа ядра ---
        result = core.analyze(text)
        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        # --- Краткое резюме ---
        summary = (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Стиль: {result['style'].get('style', '—')}\n"
            f"Вокальная форма: {result['style'].get('vocal_form', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия ядра: {result.get('version', '—')}"
        )

        # --- Проверяем аннотацию ядра ---
        if result.get("annotated_text"):
            annotated_text = result["annotated_text"]
        else:
            # fallback-аннотация через ядро с передачей эмоций и TLP
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
            """Адаптивное описание вокала в зависимости от эмоций и позиции."""
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

            annotated_lines.append(header)
            annotated_lines.append(line)
            annotated_lines.append(tone_line)
            annotated_lines.append("")

        # --- Комбинированная аннотация ---
        annotated_text = (
            "🎙️ **Core Annotation + Vocal Layer**\n\n"
            + annotated_text
            + "\n\n"
            + "\n".join(annotated_lines)
        )

        # --- Возврат ---
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

# === Healthcheck endpoint ===
@app.get("/status")
async def status():
    return JSONResponse(content={"status": "ok", "engine": "StudioCore", "ready": True})

# === Version endpoint (верификация ядра) ===
@app.get("/version")
async def version_info():
    """
    Проверка версии активного ядра (для CI/CD и HuggingFace Space)
    """
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

# === Монтируем Gradio-интерфейс ===
app = gr.mount_gradio_app(app, iface, path="/")

# === Запуск ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
