import re
from typing import Dict, Any

# Весовые карты пунктуации и эмоций
PUNCT_WEIGHTS = {
    "!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1
}
EMOJI_WEIGHTS = {ch: 0.5 for ch in "❤💔💖🔥😭😢✨🌌🌅🌙🌈☀⚡💫"}

class TruthLovePainEngine:
    """
    Deep analyzer of Truth × Love × Pain balance.
    Uses contextual and linguistic cues instead of raw counts.
    """

    POSITIVE = ["love", "care", "unity", "truth", "light", "heart", "peace", "hope",
                "любов", "сердц", "мир", "надежд", "истин", "свет", "добро"]
    NEGATIVE = ["pain", "hate", "fear", "lie", "dark", "death", "anger", "cry", "cold",
                "страд", "боль", "ненав", "лож", "тьм", "смерт", "гнев", "слез", "холод"]

    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        words = re.findall(r"[a-zа-яё]+", s)
        n = max(1, len(words))

        # Оцениваем контекст через долю позитивных / негативных слов
        pos_hits = sum(1 for w in words if any(p in w for p in self.POSITIVE))
        neg_hits = sum(1 for w in words if any(nv in w for nv in self.NEGATIVE))

        polarity = (pos_hits - neg_hits) / n
        positivity = pos_hits / n
        negativity = neg_hits / n

        truth = max(0.0, min(1.0, positivity * (1.0 - negativity)))
        love = max(0.0, min(1.0, (positivity * 2.5 + polarity + 0.1)))
        pain = max(0.0, min(1.0, (negativity * 2.2 - polarity * 0.5 + 0.05)))

        # Conscious Frequency — уравновешенность 3 осей
        cf = 1.0 - abs(truth - love) - abs(love - pain) * 0.3
        cf = max(0.0, min(cf, 1.0))

        return {
            "truth": round(truth, 3),
            "love": round(love, 3),
            "pain": round(pain, 3),
            "conscious_frequency": round(cf, 3)
        }


class AutoEmotionalAnalyzer:
    """
    Emotion classifier with contextual weighting.
    Detects emotional fields (joy, sadness, anger, fear, peace, epic)
    based on linguistic polarity, punctuation, and energy density.
    """

    EMO_FIELDS = {
        "joy": ["joy", "happy", "laugh", "счаст", "рад", "улыб", "благ", "hope", "bright"],
        "sadness": ["sad", "печаль", "грусть", "слез", "cry", "lonely", "утрата"],
        "anger": ["anger", "rage", "злость", "гнев", "ярость", "fight", "burn"],
        "fear": ["fear", "страх", "ужас", "паник", "тревог"],
        "peace": ["мир", "тишин", "calm", "still", "тихо", "равновес"],
        "epic": ["epic", "велич", "геро", "monument", "легенд", "immortal"]
    }

    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        scores = {}

        # Энергия текста по пунктуации
        punct_intensity = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in s)
        emoji_intensity = sum(EMOJI_WEIGHTS.get(ch, 0.0) for ch in s)
        energy = min(1.0, (punct_intensity + emoji_intensity) * 0.5)

        for field, tokens in self.EMO_FIELDS.items():
            hits = sum(1 for t in tokens if t in s)
            weight = hits * (1 + energy)
            scores[field] = weight

        # нормализация
        total = sum(scores.values()) or 1.0
        normalized = {k: v / total for k, v in scores.items()}

        # добавляем “background” для пустых текстов
        if total < 0.2:
            normalized["peace"] = 0.6
            normalized["joy"] = 0.4

        return normalized
