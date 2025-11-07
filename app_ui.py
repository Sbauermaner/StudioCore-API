import gradio as gr
import requests

API_URL = "https://sbauer8-studiocore-api.hf.space/analyze-lite"

def analyze_lyrics(lyrics, gender, hint):
    headers = {"Content-Type": "text/plain"}
    data = lyrics
    try:
        resp = requests.post(API_URL, headers=headers, data=data.encode("utf-8"))
        if resp.status_code == 200:
            return resp.text
        else:
            return f"Ошибка: {resp.status_code}\n{resp.text}"
    except Exception as e:
        return f"Ошибка соединения: {str(e)}"

iface = gr.Interface(
    fn=analyze_lyrics,
    inputs=[
        gr.Textbox(label="Вставь лирику", lines=12, placeholder="Введите текст песни..."),
        gr.Radio(["auto","male","female","duet","choir"], label="Предпочт. вокал", value="auto"),
        gr.Dropdown(["auto","rock","pop","folk","ambient","classical","metal","electronic"], label="Подсказка жанра", value="auto")
    ],
    outputs=gr.Textbox(label="Результат"),
    title="StudioCore Pilgrim — Лирика → Скелет + Style Prompt",
    description="Вставь свою лирику в любое формате и нажми «Анализировать». Ядро StudioCore Pilgrim создаст структурированный текст и подберёт стиль для Suno."
)

iface.launch(server_port=7860, server_name="0.0.0.0")