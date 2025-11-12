# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engines
Truth × Love × Pain and AutoEmotionalAnalyzer (v5-adaptive)

ИСПРАВЛЕНИЕ v2: Расширены словари TLP и EMO для
корректного распознавания 'страх', 'жизнь', 'солнце' и т.д.
"""

import re
import math
from typing import Dict, Any

# === Весовые карты ===
PUNCT_WEIGHTS = {"!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1}
EMOJI_WEIGHTS = {ch: 0.5 for ch in "❤💔💖🔥😭😢✨🌌🌅🌙🌈☀⚡💫"}


# =====================================================
# 💠 Truth × Love × Pain Engine
# =====================================================
class TruthLovePainEngine:
    """Balances three archetypal axes: Truth, Love, Pain → Conscious Frequency."""

    # ИСПРАВЛЕНО v2: Добавлены 'жизн', 'душ', 'солнц', 'простит', 'человек'
    POSITIVE = [
        "love", "care", "unity", "truth", "light", "heart", "peace", "hope", "faith", "sun", "life",
        "любов", "сердц", "мир", "надежд", "истин", "свет", "добро", "вер",
        "жизн", "душ", "солнц", "простит", "человек"
    ]
    # ИСПРАВЛЕНО v2: Добавлены 'страх', 'убил', 'рушит', 'войн' (дубль)
    NEGATIVE = [
        "pain", "hate", "fear", "lie", "dark", "death", "anger", "cry", "cold", "war", "lost", "empty",
        "страд", "боль", "ненав", "лож", "тьм", "смерт", "гнев", "слез", "холод", "войн",
        "страх", "убил", "рушит", "пустот"
    ]

    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        words = re.findall(r"[a-zа-яё]+", s)
        n = max(1, len(words))

        pos_hits = sum(1 for w in words if any(p in w for p in self.POSITIVE))
        neg_hits = sum(1 for w in words if any(nv in w for nv in self.NEGATIVE))

        positivity = pos_hits / n
        negativity = neg_hits / n
        polarity = positivity - negativity

        truth = max(0.0, min(1.0, positivity * (1.0 - negativity)))
        love = max(0.0, min(1.0, (positivity * 2.4 + polarity * 0.8)))
        # ИСПРАВЛЕНО v2: Увеличен множитель боли, чтобы он был более значимым
        pain = max(0.0, min(1.0, (negativity * 2.5 - polarity * 0.6 + 0.05)))

        # Conscious Frequency = гармония трёх осей
        cf = 1.0 - (abs(truth - love) + abs(love - pain) * 0.35 + abs(truth - pain) * 0.25)
        cf = max(0.0, min(cf, 1.0))

        return {
            "truth": round(truth, 3),
            "love": round(love, 3),
            "pain": round(pain, 3),
            "conscious_frequency": round(cf, 3),
        }


# =====================================================
# 💫 AutoEmotionalAnalyzer
# =====================================================
class AutoEmotionalAnalyzer:
    """Heuristic emotion-field classifier (v5-adaptive)."""

    EMO_FIELDS = {
        # ИСПРАВЛЕНО v2: Добавлена 'надежд'
        "joy": ["joy", "happy", "laugh", "смех", "рад", "улыб", "благ", "hope", "bright", "надежд"],
        # ИСПРАВЛЕНО v2: Добавлены 'боль', 'один'
        "sadness": ["sad", "печаль", "грусть", "слез", "cry", "lonely", "утрата", "страд", "боль", "один"],
        "anger": ["anger", "rage", "злость", "гнев", "ярость", "fight", "burn"],
        "fear": ["fear", "страх", "ужас", "паник", "тревог"],
        "peace": ["мир", "тишин", "calm", "still", "тихо", "равновес", "спокой"],
        "epic": ["epic", "велич", "геро", "легенд", "immortal", "battle", "rise"],
        "awe": ["восторг", "awe", "wow", "чудо", "вдохнов"],
        "neutral": []
    }

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        exps = {k: math.exp(v) for k, v in scores.items()}
        total = sum(exps.values()) or 1.0
        return {k: exps[k] / total for k in scores}

    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()

        # 1️⃣ Энергия пунктуации и эмодзи
        punct_energy = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in s)
        emoji_energy = sum(EMOJI_WEIGHTS.get(ch, 0.0) for ch in s)
        energy = min(1.0, (punct_energy + emoji_energy) ** 0.7)

        # 2️⃣ Подсчёт совпадений по токенам
        scores: Dict[str, float] = {}
        for field, tokens in self.EMO_FIELDS.items():
            # ИСПРАВЛЕНО v2: Используем поиск по подстроке (re.search)
            # Это позволяет найти "страх" в "страха"
            try:
                pattern = r"|".join(re.escape(t) for t in tokens)
                if not pattern:
                    hits = 0
                else:
                    hits = len(re.findall(pattern, s))
            except re.error:
                hits = 0 # На случай, если в токене ошибка regex
                
            # energy² делает пик эмоций ощутимее при сильных текстах
            scores[field] = hits * (1 + energy ** 2)

        # 3️⃣ Нормализация (softmax)
        normalized = self._softmax(scores)

        # 4️⃣ Если сигналов нет — вернуть фоновое спокойствие
        if all(v < 0.05 for v in normalized.values()):
            normalized = {"peace": 0.6, "joy": 0.3, "neutral": 0.1}

        return normalized