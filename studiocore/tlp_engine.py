# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""Public wrapper for the Truth × Love × Pain engine."""

import hashlib
import math
from typing import Any, Dict, List, Tuple, Optional

from .config import DEFAULT_CONFIG

from studiocore.emotion_profile import EmotionVector

from .emotion import TruthLovePainEngine as _TruthLovePainEngine


def _harmonic_mean(x: float, y: float, z: float) -> float:
    """Return harmonic mean with zero - protection fallback."""

    if x <= 0.01 or y <= 0.01 or z <= 0.01:
        return (x + y + z) / 3.0

    return 3.0 / (1.0 / x + 1.0 / y + 1.0 / z)


class TruthLovePainEngine(_TruthLovePainEngine):
    """Adds convenience helpers on top of the base TLP engine."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Task 8.1: Hash-based cache to prevent re-analyzing the same text multiple times
        self._cache: Dict[str, Dict[str, Any]] = {}

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Task 13.1: Override analyze() to add hash-based caching.
        This prevents re-analyzing the same text when analyze() is called directly.
        """
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            # Return cached result
            return self._cache[text_hash].copy()
        
        # Call parent analyze() and cache the result
        profile = super().analyze(text)
        self._cache[text_hash] = profile.copy()
        return profile

    def describe(self, text: str) -> Dict[str, Any]:
        # Task 8.1: Use hash-based cache to prevent re-analyzing the same text
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            profile = self._cache[text_hash].copy()
        else:
            profile = self.analyze(text)
            # Cache the result using hash
            self._cache[text_hash] = profile.copy()
        ordered: List[Tuple[str, float]] = sorted(
            profile.items(), key=lambda item: item[1], reverse=True
        )
        dominant = ordered[0][0] if ordered else "truth"
        profile["dominant_axis"] = dominant
        profile["balance"] = round(
            (profile.get("truth", 0.0) + profile.get("love", 0.0))
            - profile.get("pain", 0.0),
            3,
        )
        return profile

    def truth_score(self, text: str, profile: Optional[Dict[str, Any]] = None) -> float:
        # Task 8.1: Accept optional profile argument or use hash-based cache
        if profile is not None:
            return float(profile.get("truth", 0.0))
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            return float(self._cache[text_hash].get("truth", 0.0))
        profile = self.analyze(text)
        # Cache the result using hash
        self._cache[text_hash] = profile.copy()
        return float(profile.get("truth", 0.0))

    def love_score(self, text: str, profile: Optional[Dict[str, Any]] = None) -> float:
        # Task 8.1: Accept optional profile argument or use hash-based cache
        if profile is not None:
            return float(profile.get("love", 0.0))
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            return float(self._cache[text_hash].get("love", 0.0))
        profile = self.analyze(text)
        # Cache the result using hash
        self._cache[text_hash] = profile.copy()
        return float(profile.get("love", 0.0))

    def pain_score(self, text: str, profile: Optional[Dict[str, Any]] = None) -> float:
        # Task 8.1: Accept optional profile argument or use hash-based cache
        if profile is not None:
            return float(profile.get("pain", 0.0))
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            return float(self._cache[text_hash].get("pain", 0.0))
        profile = self.analyze(text)
        # Cache the result using hash
        self._cache[text_hash] = profile.copy()
        return float(profile.get("pain", 0.0))

    def tlp_vector(
        self, text: str, emotion_matrix: Dict[str, float]
    ) -> Dict[str, float]:
        """Return normalized TLP axis."""
        low = text.lower()

        truth_score = 0.0
        love_score = 0.0
        pain_score = 0.0

        # Простые эвристики (можно расширять)
        truth_keywords = (
            "правда",
            "честно",
            "искренне",
            "правдивый",
            "honest",
            "truth",
        )
        love_keywords = ("любовь", "люблю", "сердце", "обнимаю", "love", "dear")
        pain_keywords = ("боль", "страдание", "рана", "кровь", "слёзы", "pain", "hurt")

        for w in truth_keywords:
            if w in low:
                truth_score += 1.0
        for w in love_keywords:
            if w in low:
                love_score += 1.0
        for w in pain_keywords:
            if w in low:
                pain_score += 1.0

        # Эмоции подмешиваем к осям
        love_score += (
            emotion_matrix.get("joy", 0.0) * 0.6 + emotion_matrix.get("hope", 0.0) * 0.4
        )
        pain_score += (
            emotion_matrix.get("sadness", 0.0) * 0.6
            + emotion_matrix.get("anger", 0.0) * 0.4
        )

        # Нормализация
        maximum = max(truth_score, love_score, pain_score, 1e-6)
        truth = truth_score / maximum
        love = love_score / maximum
        pain = pain_score / maximum

        cmin = DEFAULT_CONFIG.TLP_CLAMP_MIN
        cmax = DEFAULT_CONFIG.TLP_CLAMP_MAX

        tlp = {
            "truth": float(min(cmax, max(cmin, truth))),
            "love": float(min(cmax, max(cmin, love))),
            "pain": float(min(cmax, max(cmin, pain))),
        }
        tlp["conscious_frequency"] = max(
            0.0,
            min(1.0, round(_harmonic_mean(tlp["truth"], tlp["love"], tlp["pain"]), 4)),
        )
        tlp["dominant_axis"] = max(
            ("truth", "love", "pain"), key=lambda axis: tlp[axis]
        )
        values = (tlp["truth"], tlp["love"], tlp["pain"])
        mean = sum(values) / 3.0
        tlp["balance"] = round(math.sqrt(sum((v - mean) ** 2 for v in values) / 3.0), 4)
        return tlp

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Calculates dynamic Valence and Arousal based on TLP scores.
        """
        # Task 8.1: Use hash-based cache to prevent re-analyzing the same text
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            profile = self._cache[text_hash].copy()
        else:
            profile = self.analyze(text)
            # Cache the result using hash
            self._cache[text_hash] = profile.copy()
        truth = profile.get("truth", 0.0)
        love = profile.get("love", 0.0)
        pain = profile.get("pain", 0.0)
        weight = profile.get("conscious_frequency", 0.5)

        # Valence (V): Positivity / Negativity (Love - Pain). Clamped to [-1,
        # 1].
        valence = love - pain

        # Arousal (A): Intensity / Energy (Average of all axes). Clamped to [0,
        # 1].
        arousal = (love + pain + truth) / 3.0

        return EmotionVector(
            truth=truth,
            love=love,
            pain=pain,
            valence=valence,
            arousal=arousal,
            weight=weight,
            extra={},
        )


__all__ = ["TruthLovePainEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
