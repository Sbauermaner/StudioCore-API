# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
Emotion Profile v1 — единый формат эмоций для StudioCore.

Вводит базовые структуры:
- EmotionVector: профиль эмоции строки/фразы/блока
- EmotionAggregator: глобальное усреднение эмоции текста + локальные "spike" пики
"""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Dict, List, Sequence


@dataclass
class EmotionVector:
    truth: float  # T ∈ [0, 1]
    love: float  # L ∈ [0, 1]
    pain: float  # P ∈ [0, 1]
    valence: float  # V ∈ [-1, 1]
    arousal: float  # A ∈ [0, 1]
    weight: float = 1.0  # вес строки в агрегации

    @staticmethod
    def average(vectors: Sequence["EmotionVector"]) -> "EmotionVector":
        if not vectors:
            return EmotionVector(0.0, 0.0, 0.0, 0.0, 0.0, 1.0)

        total_weight = sum(v.weight for v in vectors) or 1.0
        t = sum(v.truth * v.weight for v in vectors) / total_weight
        l = sum(v.love * v.weight for v in vectors) / total_weight
        p = sum(v.pain * v.weight for v in vectors) / total_weight
        v_mean = sum(v.valence * v.weight for v in vectors) / total_weight
        a = sum(v.arousal * v.weight for v in vectors) / total_weight
        weight = sum(v.weight for v in vectors) / len(vectors)
        return EmotionVector(t, l, p, v_mean, a, weight).clipped()

    def clipped(self) -> "EmotionVector":
        def clip(x: float, lo: float, hi: float) -> float:
            return max(lo, min(hi, x))

        return EmotionVector(
            truth=clip(self.truth, 0.0, 1.0),
            love=clip(self.love, 0.0, 1.0),
            pain=clip(self.pain, 0.0, 1.0),
            valence=clip(self.valence, -1.0, 1.0),
            arousal=clip(self.arousal, 0.0, 1.0),
            weight=max(self.weight, 0.0),
        )

    def to_dict(self) -> Dict[str, float]:
        return asdict(self.clipped())


class EmotionAggregator:
    @staticmethod
    def aggregate(vectors: Sequence[EmotionVector]) -> EmotionVector:
        if not vectors:
            return EmotionVector(0, 0, 0, 0, 0, 1)

        total_weight = sum(max(v.weight, 0.0) for v in vectors) or 1.0

        t = sum(v.truth * v.weight for v in vectors) / total_weight
        l = sum(v.love * v.weight for v in vectors) / total_weight
        p = sum(v.pain * v.weight for v in vectors) / total_weight
        v_mean = sum(v.valence * v.weight for v in vectors) / total_weight
        a = sum(v.arousal * v.weight for v in vectors) / total_weight

        return EmotionVector(t, l, p, v_mean, a, total_weight).clipped()

    @staticmethod
    def spikes(
        vectors: Sequence[EmotionVector], global_vector: EmotionVector
    ) -> List[float]:
        spikes = []
        for v in vectors:
            dv_t = abs(v.truth - global_vector.truth)
            dv_l = abs(v.love - global_vector.love)
            dv_p = abs(v.pain - global_vector.pain)
            dv_v = abs(v.valence - global_vector.valence)
            dv_a = abs(v.arousal - global_vector.arousal)
            spikes.append(dv_t + dv_l + dv_p + dv_v + dv_a)
        return spikes


# === END OF FILE ===
