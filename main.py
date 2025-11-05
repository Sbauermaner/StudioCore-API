import gradio as gr
import subprocess, threading

def run_api():
    subprocess.run(["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"])

threading.Thread(target=run_api).start()

def info():
    return "✅ StudioCore API running.\nUse POST /analyze"

gr.Interface(fn=info, inputs=[], outputs="text", title="StudioCore API").launch()
