import gradio as gr
import traceback
from studiocore import StudioCore

# === Инициализация ядра ===
core = StudioCore()

# === Основная функция анализа ===
def analyze_text(text: str):
    """
    Выполняет полный анализ текста через ядро StudioCore.
    Возвращает два промта: полный и сжатый (для Suno).
    """
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", ""

    try:
        result = core.analyze(text)

        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", ""

        return (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия: {result.get('version', '—')}",
            result.get("prompt_full", "⚠️ Нет данных"),
            result.get("prompt_suno", "⚠️ Нет данных")
        )

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ Ошибка при анализе:\n", tb)
        return f"❌ Исключение: {str(e)}", "", ""

# === Интерфейс Gradio ===
demo = gr.Interface(
    fn=analyze_text,
    inputs=gr.Textbox(
        label="Введите текст песни или стихотворения",
        lines=10,
        placeholder="Например: Под серым небом я шёл один, дождь шептал забытые имена..."
    ),
    outputs=[
        gr.Textbox(label="📊 Результат анализа", lines=6),
        gr.Textbox(label="🎼 Полный промт (Full Prompt)", lines=8),
        gr.Textbox(label="🎧 Suno-промт (до 1000 символов)", lines=8)
    ],
    title="🎧 StudioCore v4.3–v5 — Expressive Adaptive Engine",
    description="AI-движок анализа эмоций и структуры текста (Truth × Love × Pain = Conscious Frequency)"
)

# === Запуск сервера (для Hugging Face / Docker) ===
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
