import gradio as gr
import traceback
from studiocore import StudioCore

# === Инициализация ядра ===
core = StudioCore()

# === Основная функция анализа ===
def analyze_text(text: str):
    """
    Выполняет полный анализ текста через ядро StudioCore.
    Возвращает:
    1. краткий результат (жанр, BPM, философия),
    2. полный промт,
    3. Suno-промт,
    4. аннотированный текст.
    """
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""

    try:
        result = core.analyze(text)

        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        summary = (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Стиль: {result['style'].get('style', '—')}\n"
            f"Вокальная форма: {result['style'].get('vocal_form', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия: {result.get('version', '—')}"
        )

        annotated = []
        overlay = result.get("overlay", {}).get("sections", [])
        for sec in overlay:
            annotated.append(
                f"[{sec['section']} – {sec['mood']}, focus={sec['focus']}] "
                f"(intensity={sec['intensity']})"
            )
        annotated_text = "\n".join(annotated) if annotated else "⚠️ Аннотация не найдена."

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


# === Проверка статуса ядра ===
def check_status():
    """Проверка состояния движка (healthcheck)."""
    return {"status": "ok", "engine": "StudioCore v5", "ready": True}


# === Создаём интерфейсы ===
iface_predict = gr.Interface(
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
    api_name="/predict",
)

iface_status = gr.Interface(
    fn=check_status,
    inputs=None,
    outputs="json",
    api_name="/status",
)

# === Объединяем оба интерфейса в одно приложение ===
# Hugging Face Spaces поддерживает только один .launch()
app = gr.mount_gradio_app(iface_predict, path="/")
app = gr.mount_gradio_app(iface_status, path="/status", parent=app)

# === Запуск сервера (Hugging Face / Docker) ===
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)