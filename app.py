import gradio as gr
from studiocore import StudioCore

core = StudioCore()

def analyze_text(text):
    if not text.strip():
        return "Введите текст для анализа."

    try:
        result = core.analyze(text)
        if not result or "prompt" not in result:
            return "⚠️ Анализ не завершён: ядро не вернуло результат."
        return result["prompt"]

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("❌ Ошибка при анализе:\n", tb)
        return f"❌ Ошибка: {str(e)}"

demo = gr.Interface(
    fn=analyze_text,
    inputs=gr.Textbox(label="Введите текст песни или стихотворения", lines=8, placeholder="Например: Мир, любовь, путь…"),
    outputs=gr.Textbox(label="Сгенерированный Suno prompt"),
    title="🎧 StudioCore v4.3 — Expressive Adaptive Engine",
    description="AI-движок анализа эмоций и структуры текста (Truth × Love × Pain = Conscious Frequency)"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
