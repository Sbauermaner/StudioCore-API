# -*- coding: utf-8 -*-
"""
app.py — Gradio interface for StudioCore v4.3
Author: Bauer Synesthetic Studio
"""

import gradio as gr
from studiocore import StudioCore

# --- инициализация ядра ---
core = StudioCore()

def analyze_lyrics(text: str, author_style: str = "", gender: str = "auto"):
    """Обёртка для вызова StudioCore.analyze()"""
    if not text.strip():
        return "❗ Введите текст для анализа.", {}
    result = core.analyze(text, author_style=author_style, preferred_gender=gender)
    return result["prompt"], result

# --- интерфейс ---
demo = gr.Interface(
    fn=analyze_lyrics,
    inputs=[
        gr.Textbox(label="Введите текст песни", lines=10, placeholder="[Verse] ... [Chorus] ..."),
        gr.Textbox(label="Авторский стиль (опционально)"),
        gr.Radio(["auto", "male", "female", "duet", "choir"], label="Тип вокала", value="auto")
    ],
    outputs=[
        gr.Textbox(label="🎵 Сгенерированный Suno-prompt"),
        gr.JSON(label="🔍 Подробный анализ StudioCore")
    ],
    title="🎧 StudioCore v4.3 — Expressive Adaptive Engine",
    description="AI-ядро для анализа текста и генерации музыкальных промтов Suno",
    theme="soft",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
