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
    """Emotion inference engine (v6.4) with dynamic weight learning."""

    def __init__(self) -> None:
        """Initializes instance-level state to ensure statelessness per-request (Fix #1.1)."""
        # === 24 базовых эмоции (универсальный спектр) ===
        self.EMOTIONS = [
            "joy", "joy_bright", "happiness", "delight",  # Joy Spectrum
            "calm", "serenity", "trust",  # Calm Spectrum
            "love", "love_soft", "love_deep", "infinite_love", "healing_love", "maternal_love", "radiant_love", "longing_love", "gentle_love", "unconditional_love",  # Love Spectrum
            "sadness", "disappointment", "melancholy", "sorrow", "loneliness", "grief", "regret", "guilt", "shame",  # Sadness Spectrum
            "deep_pain", "phantom_pain", "burning_pain", "soul_pain", "silent_pain", "explosive_pain", "collapsing_pain",  # Pain Spectrum
            "rage", "rage_extreme", "aggression", "anger", "bitterness", "jealousy", "envy", "betrayal", "resentment",  # Rage Spectrum
            "fear", "anxiety", "panic", "disgust", "aversion", "confusion", "frustration",  # Fear/Conflict Spectrum
            "awe", "wonder", "hope", "relief", "admiration",  # Awe/Hope Spectrum
            "gothic_dark", "dark_poetic", "dark_romantic",  # Dark Spectrum
            "hiphop_conflict", "street_power",  # Hiphop Spectrum
            "clear_truth", "cold_truth", "sharp_truth", "brutal_honesty", "revelation", "righteous_truth",  # Truth Spectrum
            "resolve", "determination",  # Action/Resolve
            "calm_flow", "warm_pulse", "cold_pulse", "frantic", "trembling", "escalating", "descending", "pressure", "static_tension", "breathless",  # Rhythmic/Structural
            "peace", "neutral",  # Core States
        ]

        # базовые ключевые слова (instance scope)
        self.LEXICON = {
            "rage": ["убей", "бей", "гнев", "ярость", "разрывать", "сломать", "враг", "anger", "fury", "rage"],
            "rage_extreme": ["уничтожь", "смерть", "ненавижу", "истреби"],
            "sadness": ["печаль", "слёзы", "одиноко", "грусть"],
            "sorrow": ["скорбь", "горечь", "плач", "тоска", "sorrow", "weeping"],
            "loneliness": ["одиночество", "пустой", "alone", "empty", "lonely"],
            "grief": ["утрата", "потеря", "невосполним", "loss", "grief"],
            "regret": ["сожалею", "жалеть", "прошлое", "remorse", "regret"],
            "guilt": ["виноват", "вина", "ответственность", "guilty", "fault"],
            "shame": ["позор", "стыд", "унижение", "shame", "disgrace"],
            "disappointment": ["разочарование", "устал", "пустота"],
            "frustration": ["бессилие", "ярость", "frustration", "powerless"],
            "deep_pain": ["глубокая боль", "разлом", "бездна", "deep wound", "abyss"],
            "phantom_pain": ["фантомная боль", "невидимая", "phantom ache"],
            "burning_pain": ["жжение", "огонь боли", "пламя", "burning ache", "fire of sorrow"],
            "soul_pain": ["боль души", "сердце разбито", "soul ache", "heart broken"],
            "silent_pain": ["тихая боль", "немой крик", "silent scream", "mute suffering"],
            "explosive_pain": ["взрыв", "рвёт", "крик", "explosion", "tearing apart"],
            "collapsing_pain": ["рухнул", "сломлен", "обрушение", "collapsed", "broken down"],
            "love": ["люблю", "поцелуй", "ласка"],
            "love_soft": ["нежный", "ласковый", "тёплый"],
            "love_deep": ["страсть", "союз", "вечность"],
            "infinite_love": ["бесконечная любовь", "навсегда", "eternal love", "boundless"],
            "healing_love": ["исцеление", "заживет", "healing", "mend"],
            "maternal_love": ["материнский", "забота", "оберег", "motherly", "care", "guardian"],
            "radiant_love": ["сияющая любовь", "свет", "radiant", "shining"],
            "longing_love": ["тоска по любви", "ждать", "longing", "yearning"],
            "unconditional_love": ["безусловная", "без условий", "unconditional", "pure"],
            "joy": ["свет", "улыбка", "радость"],
            "happiness": ["счастье", "радостно", "веселье", "happy", "cheer"],
            "delight": ["восторг", "наслаждение", "delight", "pleasure"],
            "calm": ["спокойствие", "покой", "тишина", "calm", "stillness"],
            "serenity": ["безмятежность", "гармония", "serenity", "harmony"],
            "trust": ["доверие", "вера", "уверенность", "trust", "confidence"],
            "clear_truth": ["ясная правда", "прозрение", "clear sight", "realization"],
            "cold_truth": ["ледяное прозрение", "холодная правда", "icy clarity", "cold hard fact"],
            "sharp_truth": ["острая ясность", "болезненная правда", "sharp clarity", "painful truth"],
            "brutal_honesty": ["жестокая правда", "честность", "brutal honesty"],
            "revelation": ["озарение", "внезапно", "открытие", "epiphany", "revelation"],
            "righteous_truth": ["праведная истина", "суд", "righteous", "divine justice"],
            "fear": ["страх", "тревога", "боязнь", "fear", "anxiety", "dread"],
            "panic": ["паника", "ужас", "шок", "panic", "terror"],
            "disgust": ["отвращение", "мерзко", "противно", "disgust", "repulsive"],
            "bitterness": ["горечь", "желчь", "bitterness", "resentment", "gall"],
            "jealousy": ["ревность", "зависть", "хочу", "jealousy", "envy"],
            "betrayal": ["предательство", "измена", "удар в спину", "betrayal", "treachery"],
            "resentment": ["негодование", "обида", "злой", "indignation", "offense"],
            "resolve": ["решимость", "цель", "точно", "resolve", "purpose", "certainty"],
            "determination": ["воля", "твердо", "determination", "will", "firmly"],
            "calm_flow": ["ровный ритм", "мягкий ход", "steady tempo", "gentle flow"],
            "warm_pulse": ["тёплая волна", "мягкий бит", "warm wave", "soft pulse"],
            "cold_pulse": ["холодный ритм", "ледяной бит", "cold beat", "icy pulse"],
            "frantic": ["безумный", "крайний темп", "быстро", "frantic", "mad speed"],
            "trembling": ["дрожание", "трясет", "нервно", "trembling", "shaking", "nervous"],
            "escalating": ["нарастание", "вверх", "рост", "escalating", "rising", "upward"],
            "descending": ["спад", "вниз", "снижение", "descending", "falling", "decline"],
            "pressure": ["давление", "тяжесть", "тьма", "pressure", "heavy", "darkness"],
            "static_tension": ["серый статик", "замер", "ожидание", "gray tension", "motionless"],
            "breathless": ["задыхаясь", "без воздуха", "breathless", "gasping"],
            "gothic_dark": ["луна", "мрак", "готика", "тьма", "пан", "кровь"],
            "hiphop_conflict": ["улица", "правда", "деньги", "силой"],
            "street_power": ["бетон", "двор", "бит", "флоу"],
        }

        # индивидуальные веса (динамически обучаются, instance scope)
        self.WEIGHTS = {emotion: 1.0 for emotion in self.EMOTIONS}

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
                    vector[emotion] += 1.0 * self.WEIGHTS.get(emotion, 1.0)  # Use instance WEIGHTS

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
            self.WEIGHTS[emotion] = round(self.WEIGHTS.get(emotion, 1.0) + math.log1p(score), 5)  # Use instance WEIGHTS

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
