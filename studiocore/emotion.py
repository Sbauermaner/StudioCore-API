# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engines (v15 - Имена ИСПРАВЛЕНЫ)
Быстрый эвристический анализ (не ИИ) + Расширенные словари v3.
"""

import re
import math
from typing import Dict, Any
import logging

from studiocore.emotion_profile import EmotionVector, EmotionAggregator

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.

# Получаем логгер для этого модуля
log = logging.getLogger(__name__)

# === Весовые карты ===
PUNCT_WEIGHTS = {"!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1}
EMOJI_WEIGHTS = {ch: 0.5 for ch in "❤💔💖🔥😭😢✨🌌🌅🌙🌈☀⚡💫"}


# =====================================================
# 💠 Truth × Love × Pain Engine (v3 Словари)
# =====================================================
class TruthLovePainEngine: # <-- v15: Оригинальное имя
    """Balances TLP axes using expanded v3 dictionaries."""

    # v3 - Расширенные словари с "корнями"
    TRUTH_WORDS = [
        "правд", "истин", "честн", "смысл", "знан", "позна", "созна", # ru
        "мудро", "осозна", "голос", "суть", "reason", "судьб",
        "truth", "honest", "real", "meaning", "wisdom", "soul", "mind", # en
        "see", "know", "understand", "realize", "reflect"
    ]

    LOVE_WORDS = [
        "люб", "нежн", "сердц", "забот", "свет", "тепл", "солнц", "жизн", # ru
        "мир", "надежд", "вер", "добр", "друг", "вмест", "простит", "дом",
        "love", "care", "unity", "light", "heart", "peace", "hope", "faith", # en
        "warm", "sun", "life", "friend", "together", "forgive", "home", "kind"
    ]

    PAIN_WORDS = [
        "боль", "страда", "мук", "горе", "плач", "слез", "рана", "потер", # ru
        "ненави", "гнев", "зл", "яд", "лож", "тьм", "мрак", "смерт", "крик",
        "холод", "пусто", "один", "тоск", "пепел", "кров", "воин", "бо", # (бой, боль...)
        "страх", "ужас", "тревог", "тону", "камен", "груз", "обман", "рухн",
        "pain", "hate", "fear", "lie", "dark", "death", "anger", "cry", "cold", # en
        "war", "suffer", "grief", "loss", "scream", "alone", "empty", "blood",
        "broken", "fall", "lost", "scared"
    ]

    def __init__(self):
        # Компилируем регекспы один раз для скорости
        self.TRUTH = re.compile(r"(" + "|".join(self.TRUTH_WORDS) + r")", re.I)
        self.LOVE = re.compile(r"(" + "|".join(self.LOVE_WORDS) + r")", re.I)
        self.PAIN = re.compile(r"(" + "|".join(self.PAIN_WORDS) + r")", re.I)
        log.debug(f"TLP Engine (v15) инициализирован с {len(self.TRUTH_WORDS)}+{len(self.LOVE_WORDS)}+{len(self.PAIN_WORDS)} словами.")

    def analyze(self, text: str) -> Dict[str, float]:
        log.debug(f"Вызов функции: TruthLovePainEngine.analyze")
        s = text.lower()

        truth_hits = len(self.TRUTH.findall(s))
        love_hits = len(self.LOVE.findall(s))
        pain_hits = len(self.PAIN.findall(s))

        total = truth_hits + love_hits + pain_hits

        log.debug(f"TLP хиты: T={truth_hits}, L={love_hits}, P={pain_hits}, Total={total}")

        if total == 0:
            # Если нет TLP слов, вычисляем "частоту" (CF)
            word_count = len(re.findall(r"[a-zа-яё]+", s))
            cf = 1.0 - min(1.0, word_count / 100.0) * 0.5
            truth, love, pain = 0.0, 0.0, 0.0
        else:
            # Нормализация
            truth = truth_hits / total
            love = love_hits / total
            pain = pain_hits / total

            # Гармония (Love, Truth) против Диссонанса (Pain)
            harmony = (love + truth) / 2
            dissonance = pain

            # CF = (Гармония - Диссонанс) + 0.5 (базовая линия)
            cf = max(0.0, min(1.0, (harmony - dissonance * 0.5 + 0.5)))

        result = {
            "truth": round(truth, 3),
            "love": round(love, 3),
            "pain": round(pain, 3),
            "conscious_frequency": round(cf, 3),
        }
        log.debug(f"TLP результат: {result}")
        return result

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )


# =====================================================
# 💫 AutoEmotionalAnalyzer (v3 Словари)
# =====================================================
class AutoEmotionalAnalyzer: # <-- v15: Оригинальное имя
    """Heuristic emotion-field classifier (v15, +Logging)."""

    EMO_FIELDS = {
        "joy": ["joy", "happy", "laugh", "смех", "рад", "улыб", "счаст", "весел", "hope", "bright", "солнц"],
        "sadness": ["sad", "печал", "груст", "слез", "плач", "cry", "lonely", "утрат", "страда", "тоск", "один"],
        "anger": ["anger", "rage", "злост", "гнев", "ярост", "fight", "burn", "ненави", "крик", "воин"],
        "fear": ["fear", "страх", "ужас", "паник", "тревог", "боят", "scared"],
        "peace": ["мир", "тишин", "calm", "still", "тихо", "равновес", "спокой", "умиротвор"],
        "epic": ["epic", "велич", "геро", "легенд", "immortal", "battle", "rise", "бог", "судьб", "огон", "шторм", "неб", "гимн"],
        "awe": ["восторг", "awe", "wow", "чудо", "вдохнов", "удив", "прекрас"],
        "neutral": [] # Остается пустым
    }

    def __init__(self):
        self.LEXICON = {}
        for field, tokens in self.EMO_FIELDS.items():
            if tokens:
                # v13: Компилируем регекспы для *корней* слов (быстрее и точнее)
                self.LEXICON[field] = re.compile(r"(" + "|".join(tokens) + r")", re.I)
        log.debug(f"AutoEmotionalAnalyzer (v15) инициализирован.")

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        if not scores:
            return {}
        max_score = max(scores.values()) if scores else 0
        try:
            exps = {k: math.exp(v - max_score) for k, v in scores.items()}
        except OverflowError:
            log.warning("Softmax Overflow. Используется линейная нормализация.")
            total = sum(v for v in scores.values() if v > 0) or 1.0
            return {k: max(0, v) / total for k, v in scores.items()}

        total = sum(exps.values()) or 1.0
        return {k: exps[k] / total for k in scores}

    def analyze(self, text: str) -> Dict[str, float]:
        log.debug(f"Вызов функции: AutoEmotionalAnalyzer.analyze")
        s = text.lower()

        # 1️⃣ Энергия пунктуации и эмодзи
        punct_energy = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in s)
        emoji_energy = sum(EMOJI_WEIGHTS.get(ch, 0.0) for ch in s)
        energy = min(1.0, (punct_energy + emoji_energy) ** 0.7)
        log.debug(f"Энергия пунктуации/эмодзи: {energy:.2f}")

        # 2️⃣ Подсчёт совпадений по токенам
        scores: Dict[str, float] = {}
        total_hits = 0
        for field, pattern in self.LEXICON.items():
            hits = len(pattern.findall(s))
            scores[field] = float(hits)
            total_hits += hits

        log.debug(f"Хиты по эмоциям (raw): {scores}")

        # 3️⃣ Усиление (Amplification)
        if energy > 0.1 and total_hits > 0:
            for field in scores:
                scores[field] *= (1 + energy ** 2)
            log.debug(f"Хиты по эмоциям (усиленные): {scores}")

        # 4️⃣ Нормализация (softmax)
        normalized = self._softmax(scores)

        # 5️⃣ Если сигналов нет — вернуть фоновое спокойствие
        if total_hits == 0 or all(v < 0.05 for v in normalized.values()):
            log.debug("Сигналы эмоций не найдены. Возврат 'peace'.")
            normalized = {"peace": 0.6, "joy": 0.3, "neutral": 0.1}

        # 6. Очистка (убираем 'neutral' и нули)
        final_scores = {k: round(v, 3) for k, v in normalized.items() if k != "neutral" and v > 0.001}
        log.debug(f"Результат EMO (финал): {final_scores}")
        return final_scores

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )

