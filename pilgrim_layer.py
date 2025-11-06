# pilgrim_layer.py
# Pilgrim Interface Layer — адаптер между пользователем и StudioCore

import re
from StudioCore_Complete_v4 import StudioCore, normalize_text_preserve_symbols

class PilgrimInterface:
    def __init__(self):
        self.core = StudioCore()

    # -------------------------------
    # ТЕКСТОВЫЙ ПРЕПРОЦЕССОР
    # -------------------------------
    def auto_punctuate(self, text: str) -> str:
        """Автоматическая пунктуация и нормализация текста"""
        text = text.replace("\r", "").replace("\n", " ").strip()
        text = re.sub(r"\s+", " ", text)
        if not re.search(r"[.!?…]$", text):
            text += "."
        text = re.sub(r"\s+([,.;!?])", r"\1", text)

        def capitalize_after_punctuation(match):
            return match.group(1) + match.group(2).upper()
        text = re.sub(r"([.!?]\s+)([a-zа-яё])", capitalize_after_punctuation, text)

        sentences = re.split(r"(?<=[.!?])\s+", text)
        text = "\n".join(sentences)
        return text.strip()

    # -------------------------------
    # ГЛАВНЫЙ ИНТЕРФЕЙСНЫЙ МЕТОД
    # -------------------------------
    def process(self, text: str, author_style: str = None, gender: str = "auto"):
        """Главный метод: принимает «сырую» лирику, анализирует и возвращает style prompt"""
        if not text or not text.strip():
            return {"error": "Empty lyrics input."}

        clean = normalize_text_preserve_symbols(text)
        punctuated = self.auto_punctuate(clean)

        result = self.core.analyze(punctuated, prefer_gender=gender, author_style=author_style)

        return {
            "clean_lyrics": punctuated,
            "genre": result.genre,
            "bpm": result.bpm,
            "tonality": result.tonality,
            "vocals": result.vocals,
            "instruments": result.instruments,
            "prompt": result.prompt,
            "tlp": result.tlp,
            "emotions": result.emotions,
            "resonance": result.resonance,
            "integrity": result.integrity,
            "tonesync": result.tonesync
        }
