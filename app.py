import gradio as gr
from StudioCore_Complete_v4 import StudioCore

core = StudioCore()

def analyze_lyrics(lyrics, prefer_gender):
    result = core.analyze(lyrics, prefer_gender=prefer_gender)
    return result.prompt

demo = gr.Interface(
    fn=analyze_lyrics,
    inputs=[gr.Textbox(label="Lyrics"), gr.Dropdown(choices=["auto", "male", "female"], label="Prefer Gender")],
    outputs="text",
    title="StudioCore API"
)

if __name__ == "__main__":
    demo.launch()
