# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
EmotionEngine v6.4 — full emotional spectrum engine.

Добавлено:
- Полный эмоциональный ряд (24 ключевые эмоции)
- Rage-spectrum (rage, rage_extreme)
- Love-spectrum (love_soft, love_bright)
- Sadness / disappointment spectrum
- Gothic / dark-poetic spectrum
- HipHop / aggressive street spectrum
- Adaptive weight-learning: каждый анализ корректирует внутренние веса
"""

from __future__ import annotations
from typing import Dict, Tuple
import math


class EmotionEngineV64:
    """
    1) Анализирует текст → выдает emotion_vector (24D)
    2) Определяет dominant emotion
    3) Вычисляет TLP: Truth/Love/Pain
    4) Корректирует весовые коэффициенты динамически по тексту
    """

    # === 24 базовых эмоции (универсальный спектр) ===
    EMOTIONS = [
        "joy", "joy_bright",
        "love", "love_soft", "love_deep",
        "sadness", "disappointment", "melancholy",
        "rage", "rage_extreme", "aggression",
        "fear", "anxiety",
        "awe", "wonder",
        "hope",
        "gothic_dark", "dark_poetic", "dark_romantic",
        "hiphop_conflict", "street_power",
        "peace", "neutral",
    ]

    # базовые ключевые слова
    LEXICON = {
        "rage": ["убей", "бей", "морг", "кровь", "разорвать", "сломать", "враг"],
        "rage_extreme": ["уничтожь", "смерть", "ненавижу", "истреби"],
        "sadness": ["печаль", "слёзы", "одиноко", "грусть"],
        "disappointment": ["разочарование", "устал", "пустота"],
        "love": ["люблю", "поцелуй", "ласка"],
        "love_soft": ["нежный", "ласковый", "тёплый"],
        "love_deep": ["страсть", "союз", "вечность"],
        "joy": ["свет", "улыбка", "радость"],
        "gothic_dark": ["луна", "мрак", "готика", "тьма", "пан", "кровь"],
        "hiphop_conflict": ["улица", "правда", "деньги", "силой"],
        "street_power": ["бетон", "двор", "бит", "флоу"],
    }

    # индивидуальные веса (динамически обучаются)
    WEIGHTS = {emotion: 1.0 for emotion in EMOTIONS}

    def analyze_emotion(self, text: str) -> Dict[str, float]:
        """
        Возвращает emotion_vector {emotion: score}
        """
        vector = {e: 0.0 for e in self.EMOTIONS}

        lower_text = text.lower()

        # лексический анализ
        for emotion, words in self.LEXICON.items():
            for w in words:
                if w in lower_text:
                    vector[emotion] += 1.0 * self.WEIGHTS.get(emotion, 1.0)

        # нормализация
        total = sum(vector.values()) or 1
        for e in vector:
            vector[e] /= total

        return vector

    def detect_dominant(self, vector: Dict[str, float]) -> str:
        return max(vector.items(), key=lambda x: x[1])[0]

    def compute_TLP(self, dominant: str, vector: Dict[str, float]) -> Dict[str, float]:
        """
        Truth / Love / Pain — три эмоциональные оси.
        """
        return {
            "truth": round(vector.get("hiphop_conflict", 0) +
                           vector.get("rage", 0) * 0.3 +
                           vector.get("street_power", 0) * 0.2, 3),

            "love": round(vector.get("love", 0) +
                          vector.get("love_soft", 0) +
                          vector.get("love_deep", 0), 3),

            "pain": round(vector.get("rage_extreme", 0) +
                          vector.get("sadness", 0) +
                          vector.get("disappointment", 0), 3),
        }

    def update_weights(self, vector: Dict[str, float]) -> None:
        """
        Самообучение на основе входного текста.
        Усиливаем эмоции, которые часто встречаются.
        """
        for emotion, score in vector.items():
            # логарифмическое усиление (без взрывов)
            self.WEIGHTS[emotion] = round(self.WEIGHTS.get(emotion, 1.0) + math.log1p(score), 5)

    def process(self, text: str) -> Dict[str, object]:
        """
        Главный интерфейс:
        1) vector
        2) dominant
        3) TLP
        4) обновление весов
        """
        vector = self.analyze_emotion(text)
        dominant = self.detect_dominant(vector)
        tlp = self.compute_TLP(dominant, vector)

        # динамическое обновление веса
        self.update_weights(vector)

        return {
            "vector": vector,
            "dominant": dominant,
            "tlp": tlp,
            "dominant_name": dominant,
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
