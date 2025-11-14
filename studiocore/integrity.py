# -*- coding: utf-8 -*-
"""
StudioCore v6 — Integrity Scan Engine
Проверяет структурную и эмоциональную целостность текста.
"""

import re
from statistics import mean
from typing import Dict, Any
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine


class IntegrityScanEngine:
    """Анализирует форму, эмоции, TLP и психолингвистическую симметрию."""

    def _symmetry_index(self, lines):
        if not lines:
            return 0.0
        lengths = [len(l.strip()) for l in lines if l.strip()]
        if len(lengths) < 2:
            return 1.0
        mean_len = mean(lengths)
        variance = mean(abs(l - mean_len) for l in lengths) / max(1, mean_len)
        return round(1.0 - min(1.0, variance), 3)

    def _punct_density(self, text: str) -> float:
        punct = len(re.findall(r"[!?.,;:…—–]", text))
        return round(punct / max(1, len(text)) * 10, 3)

    def _harmonic_coherence(self, tlp: Dict[str, float]) -> float:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        diff = abs(t - l) + abs(l - p) + abs(t - p)
        return round(1.0 - min(1.0, diff * 0.6), 3)

    def analyze(self, text: str) -> Dict[str, Any]:
        lines = [l for l in text.split("\n") if l.strip()]
        words = re.findall(r"[^\s]+", text)
        sents = re.split(r"[.!?]+", text)

        form = {
            "word_count": len(words),
            "sentence_count": len([s for s in sents if s.strip()]),
            "mean_sentence_length": round(len(words) / max(1, len(sents)), 2),
            "punctuation_density": self._punct_density(text),
            "symmetry_index": self._symmetry_index(lines),
        }

        # эмоции и оси TLP
        emo = AutoEmotionalAnalyzer().analyze(text)
        tlp = TruthLovePainEngine().analyze(text)
        harmonic_coherence = self._harmonic_coherence(tlp)

        # рефлексия — присутствие «я», «мы», «они»
        ref_words = set(
            "i me my myself я мне меня сам себя думаю чувствую знаю понимаю "
            "мы наш нас together united мы все".split()
        )
        tokens = set(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()))
        reflection = len(tokens & ref_words) / max(1, len(tokens))
        ego_density = len([w for w in tokens if w in {"я", "i", "my", "me"}]) / max(1, len(tokens))
        collective_focus = len([w for w in tokens if w in {"мы", "наш", "together"}]) / max(1, len(tokens))

        integrity_score = round(
            0.4 * form["symmetry_index"]
            + 0.3 * harmonic_coherence
            + 0.2 * (1 - abs(emo.get("anger", 0) - emo.get("peace", 0)))
            + 0.1 * (1 - abs(ego_density - collective_focus)),
            3,
        )

        return {
            "form": form,
            "essence": {"emotions": emo, "tlp": tlp, "harmonic_coherence": harmonic_coherence},
            "reflection": {
                "self_awareness": round(reflection, 3),
                "ego_density": round(ego_density, 3),
                "collective_focus": round(collective_focus, 3),
            },
            "integrity_score": integrity_score,
        }
