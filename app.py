# -*- coding: utf-8 -*-
"""
🎧 StudioCore v4.3–v5 — Expressive Adaptive Engine
Truth × Love × Pain = Conscious Frequency
"""

import gradio as gr
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from studiocore import StudioCore

# === Инициализация ядра ===
core = StudioCore()
app = FastAPI(title="StudioCore API")

# === Основная функция анализа ===
def analyze_text(text: str):
    """
    Основная функция анализа текста.
    Возвращает: summary, full_prompt, suno_prompt, annotated_text
    """
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        result = core.analyze(text)

        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        # --- Краткое резюме анализа ---
        summary = (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Стиль: {result['style'].get('style', '—')}\n"
            f"Вокальная форма: {result['style'].get('vocal_form', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия: {result.get('version', '—')}"
        )

        # --- Автоматическая аннотация текста с секциями ---
        overlay = result.get("overlay", {}).get("sections", [])
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        annotated_lines = []
        section_index = 0

        # обработка повторяющихся секций (например, Chorus x2)
        repeat_map = {}
        for sec in overlay:
            key = sec["section"].lower().strip()
            repeat_map[key] = repeat_map.get(key, 0) + 1

        for i, line in enumerate(lines):
            if section_index < len(overlay):
                sec = overlay[section_index]
                sec_name = sec["section"].lower().strip()

                # если секция повторяется — добавляем x2, x3...
                repeat_suffix = ""
                if repeat_map.get(sec_name, 0) > 1:
                    count = repeat_map[sec_name]
                    repeat_suffix = f" x{count}"
                    repeat_map[sec_name] = 0  # чтобы не повторять надпись повторно

                tag = (
                    f"[{sec['section']} – {sec['mood']}, focus={sec['focus']}] "
                    f"(intensity={sec['intensity']}){repeat_suffix}"
                )
                annotated_lines.append(tag)
                section_index += 1

            annotated_lines.append(line)

        # если секций меньше строк — добавляем остаток
        if len(lines) > len(overlay):
            annotated_lines.extend(lines[len(overlay):])

        annotated_text = "\n".join(annotated_lines) if annotated_lines else "⚠️ Аннотация не найдена."

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
        gr.Textbox(label="📜 Автоматическая аннотация (структура секций)", lines=15)
    ],
    title="🎧 StudioCore v4.3–v5 — Expressive Adaptive Engine",
    description="AI-движок анализа эмоций, структуры и смысловой архитектуры текста.\nФормула ядра: Truth × Love × Pain = Conscious Frequency.",
)

# === Healthcheck endpoint для GPT Builder ===
@app.get("/status")
async def status():
    """Healthcheck для GPT Builder и Hugging Face."""
    return JSONResponse(content={"status": "ok", "engine": "StudioCore v5", "ready": True})


# === API endpoint /api/predict (для GPT Builder, cURL, Python, JS) ===
@app.post("/api/predict")
async def predict_api(request: Request):
    """Реальный JSON API для интеграций."""
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


# === Монтируем Gradio-интерфейс в FastAPI ===
app = gr.mount_gradio_app(app, iface, path="/")

# === Запуск ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
