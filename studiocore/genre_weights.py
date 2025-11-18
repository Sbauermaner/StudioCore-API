# -*- coding: utf-8 -*-
"""
GenreWeightsEngine v2 — Domain-Based Classification
Rock/Metal/Rap/DnB больше не падают в lyrical adaptive.
Лирика/Cinematic больше не конфликтуют с Hard-доменом.
Совместимо с RDE, TLP, Rhythm, Tone, Section Intelligence.
"""

from __future__ import annotations
from typing import Dict


class GenreWeightsEngine:
    """Domain-driven genre selection based on StudioCore feature map."""

    def __init__(self) -> None:
        # === Domain mapping ===
        self.genre_domain = {
            # HARD
            "rock": "hard",
            "alt_rock": "hard",
            "hard_rock": "hard",
            "metal": "hard",
            "metalcore": "hard",
            "nu_metal": "hard",
            "rap": "hard",
            "trap": "hard",
            "hip_hop": "hard",
            "dnb": "hard",
            "industrial": "hard",

            # SOFT
            "lyrical": "soft",
            "ballad": "soft",
            "poetic": "soft",
            "cinematic": "soft",
            "epic": "soft",
            "folk": "soft",
            "indie": "soft",
        }

        # === Feature weights ===
        self.domain_feature_weights = {
            "hard": {
                "sai": 0.28,
                "power": 0.24,
                "rhythm_density": 0.16,
                "edge": 0.16,
                "harmonic_lumen_minor": 0.10,
                "structure_tension": 0.06,
            },
            "soft": {
                "narrative_pressure": 0.26,
                "emotional_gradient": 0.24,
                "harmonic_lumen_major": 0.16,
                "cinematic_spread": 0.14,
                "vocal_intention": 0.10,
                "structure_tension": 0.10,
            },
        }

        # === Thresholds ===
        self.domain_thresholds = {
            "hard": 0.45,
            "soft": 0.50,
        }

        self.fallback_by_domain = {
            "hard": "rock",
            "soft": "lyrical",
        }

    def score_genres(self, features: Dict[str, float]) -> Dict[str, float]:
        """Raw weights for each genre."""
        scores = {}
        for genre, domain in self.genre_domain.items():
            score = 0.0
            for feat, w in self.domain_feature_weights[domain].items():
                score += features.get(feat, 0.0) * w
            scores[genre] = score
        return scores

    def infer_genre(self, features: Dict[str, float]) -> str:
        scores = self.score_genres(features)

        best = {
            "hard": {"genre": None, "score": 0.0},
            "soft": {"genre": None, "score": 0.0},
        }

        for genre, score in scores.items():
            domain = self.genre_domain[genre]
            if score > best[domain]["score"]:
                best[domain] = {"genre": genre, "score": score}

        candidates = {}
        for domain in ["hard", "soft"]:
            g = best[domain]["genre"]
            s = best[domain]["score"]
            if g and s >= self.domain_thresholds[domain]:
                candidates[g] = s

        if candidates:
            return max(candidates.items(), key=lambda kv: kv[1])[0]

        # fallback
        if best["hard"]["score"] >= best["soft"]["score"]:
            return self.fallback_by_domain["hard"]
        return self.fallback_by_domain["soft"]
