import re
from typing import Optional
from StudioCore_Complete_v4 import StudioCore


class PilgrimInterface:
    """
    Pilgrim Layer — пользовательская надстройка над ядром StudioCore.
    Обеспечивает:
    - автоматическую пунктуацию и очистку текста
    - разбивку на куплеты / припевы
    - добавление вокальной и жанровой структуры
    - финальную сборку текста с описанием
    """

    def __init__(self, core: StudioCore):
        self.core = core

    # -------------------------------
    # 🧹 Предобработка текста
    # -------------------------------
    def clean_text(self, text: str) -> str:
        # убираем двойные пробелы и лишние переводы строк
        text = text.replace("\r", "").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        # добавляем точку в конце строки, если нет знака
        text = re.sub(r"(?<![.!?,;:])(\n|$)", ".\n", text)
        return text.strip()

    # -------------------------------
    # 🧠 Разбиение по смысловым блокам
    # -------------------------------
    def structure_text(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        blocks = []
        current = []
        for i, line in enumerate(lines, 1):
            current.append(line)
            # каждые 4 строки → куплет / припев
            if i % 4 == 0:
                tag = "[Chorus]" if len(blocks) % 2 else "[Verse]"
                blocks.append(tag + "\n" + "\n".join(current))
                current = []
        if current:
            blocks.append("[Bridge]\n" + "\n".join(current))
        return "\n\n".join(blocks)

    # -------------------------------
    # 🎙️ Построение вокального скелета
    # -------------------------------
    def apply_vocal_style(self, genre: str, vocals: list[str]) -> str:
        """
        Возвращает аннотацию вокального исполнения под жанр и вокал.
        """
        tone_map = {
            "rock": "[Vocals: raspy + belt + emotional drive]",
            "metal": "[Vocals: growl + scream + chest resonance]",
            "pop": "[Vocals: soft + bright + mixed voice]",
            "folk": "[Vocals: natural + warm + storytelling]",
            "ambient": "[Vocals: whisper + breathy + reverb space]",
            "classical": "[Vocals: full tone + legato + vibrato]",
            "electronic": "[Vocals: processed + airy + delay]",
        }
        base = tone_map.get(genre, "[Vocals: emotional + human tone]")
        return base + "  " + " / ".join(vocals)

    # -------------------------------
    # 🔮 Финальная сборка
    # -------------------------------
    def build_from_text(self, text: str, prefer_gender: str = "auto") -> str:
        clean = self.clean_text(text)
        structured = self.structure_text(clean)
        result = self.core.analyze(clean, prefer_gender=prefer_gender)

        header = f"🎼 StudioCore Pilgrim Style Summary\n" \
                 f"Genre: {result.genre}\n" \
                 f"BPM: {result.bpm}\n" \
                 f"Tonality: {result.tonality}\n" \
                 f"Instruments: {', '.join(result.instruments)}\n" \
                 f"Vocal Style: {', '.join(result.vocals)}\n\n"

        vocal_annotation = self.apply_vocal_style(result.genre, result.vocals)
        full_text = (
            header +
            "---------------------------------------------\n" +
            f"{vocal_annotation}\n\n" +
            structured + "\n\n" +
            "---------------------------------------------\n" +
            f"🎧 Style Prompt:\n{result.prompt}\n"
        )
        return full_text
