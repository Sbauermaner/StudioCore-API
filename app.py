import gradio as gr
from StudioCore_Complete_v4 import StudioCore

core = StudioCore()

def analyze_lyrics(lyrics, prefer_gender):
    result = core.analyze(lyrics, prefer_gender=prefer_gender)
    return (
        result.prompt,
        result.genre,
        result.bpm,
        result.tonality,
        result.tlp,
        result.emotions,
        result.resonance
    )

demo = gr.Interface(
    fn=analyze_lyrics,
    inputs=[gr.Textbox(label="Lyrics"), gr.Dropdown(choices=["auto", "male", "female"], label="Prefer Gender")],
    outputs=[
        gr.Textbox(label="Prompt"),
        gr.Textbox(label="Genre"),
        gr.Textbox(label="BPM"),
        gr.Textbox(label="Tonality"),
        gr.Textbox(label="TLP"),
        gr.Textbox(label="Emotions"),
        gr.Textbox(label="Resonance")
    ],
    title="StudioCore API"
)

if __name__ == "__main__":
    demo.launch()
