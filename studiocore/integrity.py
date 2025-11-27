# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
StudioCore v5 — Integrity Scan Engine
Проверяет структурную и эмоциональную целостность текста.
"""

import re
from statistics import mean
from typing import Dict, Any, Optional
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine


class IntegrityScanEngine:
    """Анализирует форму, эмоции, TLP и психолингвистическую симметрию."""

    def _symmetry_index(self, lines):
        if not lines:
            return 0.0
        lengths = [len(line.strip()) for line in lines if line.strip()]
        if len(lengths) < 2:
            return 1.0
        mean_len = mean(lengths)
        variance = mean(abs(item - mean_len) for item in lengths) / max(1, mean_len)
        return round(1.0 - min(1.0, variance), 3)

    def _punct_density(self, text: str) -> float:
        punct = len(re.findall(r"[!?.,;:…—–]", text))
        return round(punct / max(1, len(text)) * 10, 3)

    def _harmonic_coherence(self, tlp: Dict[str, float]) -> float:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)  # noqa: E741
        diff = abs(t - l) + abs(l - p) + abs(t - p)  # noqa: E741
        return round(1.0 - min(1.0, diff * 0.6), 3)

    def analyze(
        self, 
        text: str,
        # Task 2.2: Добавлены опциональные параметры для устранения повторных анализов
        emotions: Optional[Dict[str, float]] = None,
        tlp: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        lines = [line for line in text.split("\n") if line.strip()]
        words = re.findall(r"[^\s]+", text)
        sents = re.split(r"[.!?]+", text)

        form = {
            "word_count": len(words),
            "sentence_count": len([s for s in sents if s.strip()]),
            "mean_sentence_length": round(len(words) / max(1, len(sents)), 2),
            "punctuation_density": self._punct_density(text),
            "symmetry_index": self._symmetry_index(lines),
        }

        # Task 2.2: Используем переданные emotions и tlp вместо создания новых экземпляров
        if emotions is None:
            emo = AutoEmotionalAnalyzer().analyze(text)
        else:
            emo = emotions
        
        if tlp is None:
            tlp_local = TruthLovePainEngine().analyze(text)
        else:
            tlp_local = tlp
        
        harmonic_coherence = self._harmonic_coherence(tlp_local)

        # рефлексия — присутствие «я», «мы», «они»
        ref_words = set(
            "i me my myself я мне меня сам себя думаю чувствую знаю понимаю мы наш нас together united мы все".split()
        )
        tokens = set(re.findall(r"[a - zA - Zа - яА - ЯёЁ]+", text.lower()))
        reflection = len(tokens & ref_words) / max(1, len(tokens))
        ego_density = len([w for w in tokens if w in {"я", "i", "my", "me"}]) / max(
            1, len(tokens)
        )
        collective_focus = len(
            [w for w in tokens if w in {"мы", "наш", "together"}]
        ) / max(1, len(tokens))

        integrity_score = round(
            0.4 * form["symmetry_index"]
            + 0.3 * harmonic_coherence
            + 0.2 * (1 - abs(emo.get("anger", 0) - emo.get("peace", 0)))
            + 0.1 * (1 - abs(ego_density - collective_focus)),
            3,
        )

        return {
            "form": form,
            "essence": {
                "emotions": emo,
                "tlp": tlp_local,
                "harmonic_coherence": harmonic_coherence,
            },
            "reflection": {
                "self_awareness": round(reflection, 3),
                "ego_density": round(ego_density, 3),
                "collective_focus": round(collective_focus, 3),
            },
            "integrity_score": integrity_score,
        }


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
