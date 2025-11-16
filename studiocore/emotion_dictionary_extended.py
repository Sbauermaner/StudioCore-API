# -*- coding: utf-8 -*-
"""
Большой эмоционально-стилистический словарь:
- тональность текста
- эмоциональные оттенки
- регистр речи
- драматическая насыщенность
"""
from __future__ import annotations

from typing import Dict, List


class EmotionLexiconExtended:
    """Rule-based helper that tags the text with broad emotional buckets."""

    def __init__(self) -> None:
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

        # степени драматизма
        self.drama_levels: Dict[str, List[str]] = {
            "low": ["спокойно", "тепло", "мягко"],
            "medium": ["остро", "напряженно", "тревожно"],
            "high": ["критично", "взрывно", "катастрофично"],
        }

    def get_emotion(self, text: str) -> Dict[str, bool | str]:
        lowered = text.lower()
        result = {emotion: any(word in lowered for word in words) for emotion, words in self.emotion_words.items()}
        result["drama_level"] = self._detect_drama_level(lowered)
        return result

    def _detect_drama_level(self, text: str) -> str:
        for level, keywords in self.drama_levels.items():
            if any(word in text for word in keywords):
                return level
        return "neutral"
