# -*- coding: utf-8 -*-
"""
Большой эмоционально-стилистический словарь:
- тональность текста
- эмоциональные оттенки
- регистр речи
- драматическая насыщенность
"""
from __future__ import annotations

from typing import Any, Dict, List


class EmotionLexiconExtended:
    """Rule-based helper that tags the text with broad emotional buckets."""

    def __init__(self) -> None:
        # Основные эмоциональные категории
        self.emotion_words: Dict[str, List[str]] = {
            "love": ["люблю", "любовь", "нежность", "ласка", "страсть"],
            "sadness": ["грусть", "печаль", "слёзы", "уныние", "одиночество"],
            "anger": ["злость", "ярость", "крик", "ненависть", "вспышка"],
            "fear": ["страх", "опасение", "тревога", "дрожь", "паника"],
            "hope": ["надежда", "верю", "свет", "утро", "рассвет"],
            "calm": ["спокойствие", "тишина", "умиротворение", "мир"],
            "nostalgia": ["память", "вспоминаю", "давно", "прошлое"],
            "irony": ["ирония", "смешно", "сарказм", "насмешка"],
            "conflict": ["конфликт", "спор", "борьба", "разрыв"],
        }

        # Степени драматизма
        self.drama_levels: Dict[str, List[str]] = {
            "low": ["спокойно", "тепло", "мягко"],
            "medium": ["остро", "напряженно", "тревожно"],
            "high": ["критично", "взрывно", "катастрофично"],
        }

        # Речевые регистры
        self.speech_registers: Dict[str, List[str]] = {
            "formal": ["уважаемый", "прошение", "обращаюсь", "господин"],
            "colloquial": ["эй", "чувак", "ладно", "ну да", "ага"],
            "poetic": ["о мой", "очи", "сердцу", "внемли", "владыка"],
        }

        # Тональные маркеры
        self.tone_markers: Dict[str, List[str]] = {
            "solemn": ["торжественно", "величие", "венец", "сияние"],
            "rebellious": ["бунт", "революция", "сопротивление", "не покорюсь"],
            "meditative": ["тишина", "дыхание", "покой", "медленно"],
        }

        # Интенсивность выражения
        self.intensity_markers: Dict[str, List[str]] = {
            "high": ["буря", "огонь", "кровь", "кричу", "шторм"],
            "medium": ["искры", "дрожь", "пульс", "порыв"],
            "low": ["шёпот", "тихо", "лёгкий", "мягкий"],
        }

    def get_emotion(self, text: str) -> Dict[str, Any]:
        lowered = text.lower()

        buckets = {
            emotion: any(word in lowered for word in words)
            for emotion, words in self.emotion_words.items()
        }

        return {
            "emotions": buckets,
            "register": self._detect_register(lowered),
            "tone": self._detect_tone(lowered),
            "drama_level": self._detect_drama_level(lowered),
            "intensity": self._estimate_intensity(lowered),
        }

    def _detect_drama_level(self, text: str) -> str:
        for level, keywords in self.drama_levels.items():
            if any(word in text for word in keywords):
                return level
        return "neutral"

    def _detect_register(self, text: str) -> str:
        for register, keywords in self.speech_registers.items():
            if any(word in text for word in keywords):
                return register
        return "neutral"

    def _detect_tone(self, text: str) -> str:
        for tone, keywords in self.tone_markers.items():
            if any(word in text for word in keywords):
                return tone
        return "neutral"

    def _estimate_intensity(self, text: str) -> float:
        high_hits = sum(text.count(word) for word in self.intensity_markers["high"])
        medium_hits = sum(text.count(word) for word in self.intensity_markers["medium"])
        low_hits = sum(text.count(word) for word in self.intensity_markers["low"])

        punctuation_bonus = min(text.count("!") / 5, 1.0) * 0.2
        base = high_hits * 0.3 + medium_hits * 0.15 + low_hits * 0.05

        return round(min(1.0, base + punctuation_bonus), 3)
