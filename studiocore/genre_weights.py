# -*- coding: utf-8 -*-
"""GenreWeightsEngine v1.0 — весовая классификация жанров."""
from __future__ import annotations

from typing import Dict


class GenreWeightsEngine:
    """Approximate poetic/dramatic genre classifier based on structural cues."""

    def __init__(self) -> None:
        self.genre_profiles: Dict[str, Dict[str, float]] = {
            "лирика": {
                "structure_weight": 0.40,
                "emotion_weight": 0.35,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.10,
            },
            "элегия": {
                "structure_weight": 0.30,
                "emotion_weight": 0.50,
                "lexicon_weight": 0.10,
                "narrative_weight": 0.10,
            },
            "романс": {
                "structure_weight": 0.35,
                "emotion_weight": 0.45,
                "lexicon_weight": 0.10,
                "narrative_weight": 0.10,
            },
            "ода": {
                "structure_weight": 0.30,
                "emotion_weight": 0.30,
                "lexicon_weight": 0.25,
                "narrative_weight": 0.15,
            },
            "поэма": {
                "structure_weight": 0.25,
                "emotion_weight": 0.20,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.40,
            },
            "притча": {
                "structure_weight": 0.20,
                "emotion_weight": 0.20,
                "lexicon_weight": 0.20,
                "narrative_weight": 0.40,
            },
            "басня": {
                "structure_weight": 0.20,
                "emotion_weight": 0.15,
                "lexicon_weight": 0.35,
                "narrative_weight": 0.30,
            },
            "драма": {
                "structure_weight": 0.10,
                "emotion_weight": 0.40,
                "lexicon_weight": 0.20,
                "narrative_weight": 0.30,
            },
            "трагедия": {
                "structure_weight": 0.15,
                "emotion_weight": 0.45,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.25,
            },
            "комедия": {
                "structure_weight": 0.15,
                "emotion_weight": 0.30,
                "lexicon_weight": 0.35,
                "narrative_weight": 0.20,
            },
        }

    def _rhyme_score(self, text: str) -> float:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if len(lines) < 2:
            return 0.0
        rhymes = 0
        for current, following in zip(lines, lines[1:]):
            if len(current) > 3 and len(following) > 3 and current[-2:] == following[-2:]:
                rhymes += 1
        return rhymes / len(lines)

    def _structure_score(self, text: str) -> float:
        lengths = [len(line) for line in text.split("\n") if line.strip()]
        if not lengths:
            return 0.0
        avg_length = sum(lengths) / len(lengths)
        variance = sum(abs(length - avg_length) for length in lengths)
        return 1.0 - min(1.0, variance / 300)

    def predict(self, text: str) -> Dict[str, float]:
        rhyme = self._rhyme_score(text)
        structure = self._structure_score(text)

        predictions: Dict[str, float] = {}
        for genre, weights in self.genre_profiles.items():
            score = (
                rhyme * weights["structure_weight"]
                + structure * weights["structure_weight"]
                + weights["emotion_weight"] * 0.5
            )
            predictions[genre] = round(score, 4)

        return dict(sorted(predictions.items(), key=lambda item: item[1], reverse=True))
