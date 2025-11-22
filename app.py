# -*- coding: utf-8 -*-
import gradio as gr
from studiocore.core_v6 import StudioCoreV6

engine = StudioCoreV6()

def analyze_text(x: str):
    try:
        result = engine.analyze(x)
        fanf = result.get("fanf", {})
        diag = result.get("diagnostics", {})

        return (
            fanf.get("style_prompt", ""),
            fanf.get("lyrics_prompt", ""),
            fanf.get("ui_text", ""),
            fanf.get("summary", ""),
            diag
        )
    except Exception as e:
        return ("", "", "", "", {"error": str(e)})

with gr.Blocks() as demo:
    gr.Markdown("# StudioCore IMMORTAL v7.0 · Analysis Space")

    inp = gr.Textbox(label="Input text", lines=10)

    out_style = gr.Textbox(label="Style Prompt")
    out_lyrics = gr.Textbox(label="Lyrics Prompt")
    out_ui = gr.Textbox(label="UI Text")
    out_summary = gr.Textbox(label="Summary")
    out_diag = gr.JSON(label="Diagnostics v8.0")

    btn = gr.Button("Analyze")

    btn.click(
        analyze_text,
        inputs=[inp],
        outputs=[out_style, out_lyrics, out_ui, out_summary, out_diag]
    )

demo.launch()
