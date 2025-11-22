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
GenreWeightsEngine v3.0 — Multi-Domain

Домены:
- hard       (rock/metal/rap/агрессия)
- electronic (edm/techno/trance/dnb/etc.)
- jazz       (jazz/swing/bebop/nu_jazz/etc.)
- lyrical    (поэтическая/песенная лирика, включая комическую)
- cinematic  (score, epic, trailer)
- comedy     (комедийная музыка/пародии)
- soft       (спокойные жанры: folk/ambient/lofi/etc.)

Работает на feature map из core_v6:
features = {
    "sai", "power", "rhythm_density", "edge",
    "narrative_pressure", "emotional_gradient",
    "hl_minor", "hl_major",
    "cinematic_spread", "vocal_intention",
    "structure_tension", "swing_ratio",
    "jazz_complexity", "electronic_pressure",
    "lyrical_emotion_score", "comedy_factor",
}
"""

from __future__ import annotations
from typing import Dict, Any

from .genre_registry import GlobalGenreRegistry
from .genre_universe_loader import load_genre_universe


class GenreWeightsEngine:
    """Многодоменный жанровый классификатор."""

    def __init__(self) -> None:
        self.registry = GlobalGenreRegistry()
        self.universe = load_genre_universe()

        # === 1. Домен → веса признаков ===
        self.domain_feature_weights: Dict[str, Dict[str, float]] = {
            "hard": {
                "sai": 0.22,
                "power": 0.22,
                "rhythm_density": 0.16,
                "edge": 0.16,
                "hl_minor": 0.14,
                "structure_tension": 0.10,
            },
            "electronic": {
                "electronic_pressure": 0.24,
                "rhythm_density": 0.20,
                "power": 0.16,
                "structure_tension": 0.10,
                "hl_minor": 0.10,
                "hl_major": 0.10,
                "cinematic_spread": 0.10,
                "poetic_density": -0.12,
                "lyric_form_weight": -0.14,
            },
            "jazz": {
                "jazz_complexity": 0.26,
                "swing_ratio": 0.22,
                "rhythm_density": 0.14,
                "hl_minor": 0.14,
                "hl_major": 0.14,
                "emotional_gradient": 0.10,
            },
            "lyrical": {
                "narrative_pressure": 0.22,
                "lyrical_emotion_score": 0.28,
                "emotional_gradient": 0.16,
                "hl_major": 0.12,
                "hl_minor": 0.10,
                "vocal_intention": 0.12,
                "poetic_density": 0.18,
                "lyric_form_weight": 0.22,
                "gothic_factor": 0.06,
                "dramatic_weight": 0.06,
            },
            "cinematic": {
                "cinematic_spread": 0.28,
                "power": 0.16,
                "emotional_gradient": 0.18,
                "structure_tension": 0.14,
                "hl_minor": 0.12,
                "hl_major": 0.12,
                "dramatic_weight": 0.18,
                "darkness_level": 0.12,
            },
            "comedy": {
                "comedy_factor": 0.40,
                "lyrical_emotion_score": 0.20,
                "narrative_pressure": 0.20,
                "hl_major": 0.10,
                "vocal_intention": 0.10,
            },
            "soft": {
                "narrative_pressure": 0.24,
                "emotional_gradient": 0.22,
                "hl_major": 0.20,
                "power": 0.10,
                "rhythm_density": 0.10,
                "structure_tension": 0.14,
                "poetic_density": 0.12,
            },
        }

        # === 2. Порог по доменам ===
        self.domain_thresholds: Dict[str, float] = {
            "hard": 0.45,
            "electronic": 0.45,
            "jazz": 0.45,
            "lyrical": 0.50,
            "cinematic": 0.50,
            "comedy": 0.40,
            "soft": 0.50,
        }

        # === 3. Fallback жанр по домену ===
        self.fallback_by_domain: Dict[str, str] = {
            "hard": "rock",
            "electronic": "edm",
            "jazz": "jazz",
            "lyrical": "lyrical_song",
            "cinematic": "cinematic",
            "comedy": "comedy_rock",
            "soft": "folk",
        }

        self.genre_profiles: Dict[str, Dict[str, float]] = getattr(self, "genre_profiles", {})
        self.genre_profiles.update(
            {
                "баллада": {
                    "structure_weight": 0.35,
                    "emotion_weight": 0.40,
                    "lexicon_weight": 0.15,
                    "narrative_weight": 0.10,
                },
                "ода": {
                    "structure_weight": 0.30,
                    "emotion_weight": 0.35,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.10,
                },
                "сонет": {
                    "structure_weight": 0.45,
                    "emotion_weight": 0.30,
                    "lexicon_weight": 0.15,
                    "narrative_weight": 0.10,
                },
                "притча": {
                    "structure_weight": 0.25,
                    "emotion_weight": 0.25,
                    "lexicon_weight": 0.20,
                    "narrative_weight": 0.30,
                },
                "реп_текст": {
                    "structure_weight": 0.20,
                    "emotion_weight": 0.40,
                    "lexicon_weight": 0.30,
                    "narrative_weight": 0.10,
                },
                "spoken_word": {
                    "structure_weight": 0.20,
                    "emotion_weight": 0.45,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.10,
                },
                "верлибр": {
                    "structure_weight": 0.15,
                    "emotion_weight": 0.45,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.15,
                },
            }
        )

        self._universe_domain_cache: Dict[str, List[str]] = {}

    # ---------- Внутренняя логика ----------

    def _domain_for_genre(self, genre: str) -> str | None:
        for domain, genres in self.registry.domains.items():
            if genre in genres:
                return domain
        return None

    def _genres_for_domain(self, domain: str) -> List[str]:
        """Возвращает жанры для домена из GLOBAL GENRE UNIVERSE."""

        if domain in self._universe_domain_cache:
            return self._universe_domain_cache[domain]

        u = self.universe
        if domain == "electronic":
            base = u.edm_genres + [
                g for g in u.music_genres
                if any(k in g for k in (
                    "edm", "techno", "trance", "dnb", "drum_and_bass",
                    "dubstep", "house", "bass", "synth", "wave", "electro",
                    "idm", "break", "rave",
                ))
            ]
        elif domain == "hard":
            base = [
                g for g in u.music_genres
                if any(k in g for k in (
                    "rock", "metal", "punk", "core", "rap", "hip_hop",
                    "drill", "trap", "hard",
                ))
            ]
        elif domain == "jazz":
            base = [g for g in u.music_genres if any(k in g for k in ("jazz", "swing", "bop"))]
        elif domain == "lyrical":
            base = u.lyric_forms + u.literature_styles
        elif domain == "comedy":
            base = u.comedy_genres
        elif domain == "cinematic":
            base = [g for g in u.hybrids if "cinematic" in g or "orchestral" in g]
            base += [g for g in u.music_genres if "cinematic" in g or "score" in g]
        elif domain == "soft":
            base = [
                g for g in u.music_genres
                if any(k in g for k in (
                    "folk", "ambient", "lofi", "chill", "dream", "soft", "ballad"
                ))
            ]
        else:
            base = []

        normalized = list(dict.fromkeys(base))  # сохраняем порядок
        self._universe_domain_cache[domain] = normalized or self.registry.domains.get(domain, [])
        return self._universe_domain_cache[domain]

    def score_domains(self, features: Dict[str, float]) -> Dict[str, float]:
        """Сырые веса по доменам."""
        scores: Dict[str, float] = {}
        for domain, weights in self.domain_feature_weights.items():
            s = 0.0
            for feat, w in weights.items():
                value = features.get(feat, 0.0)
                s += value * w
            scores[domain] = s

        poetic = features.get("poetic_density", 0.0)
        gothic = features.get("gothic_factor", 0.0)
        dramatic = features.get("dramatic_weight", 0.0)
        lyric = features.get("lyric_form_weight", poetic)

        scores["lyrical"] = scores.get("lyrical", 0.0) + (poetic * 0.2) + (lyric * 0.25)
        scores["cinematic"] = scores.get("cinematic", 0.0) + (dramatic * 0.15) + (gothic * 0.1)
        scores["electronic"] = max(0.0, scores.get("electronic", 0.0) - (poetic * 0.25 + gothic * 0.2 + dramatic * 0.1))
        return scores

    def infer_domain(self, features: Dict[str, float]) -> str:
        """Определяет домен, с которым работаем."""
        domain_scores = self.score_domains(features)

        # отфильтровать по порогу
        candidates = {
            d: s for d, s in domain_scores.items()
            if s >= self.domain_thresholds.get(d, 0.0)
        }
        if candidates:
            return max(candidates.items(), key=lambda kv: kv[1])[0]

        # fallback: берём домен с максимальной "сырой" энергией
        return max(domain_scores.items(), key=lambda kv: kv[1])[0]

    def infer_genre(self, features: Dict[str, float]) -> str:
        """
        Главный метод:
        - определяет домен
        - внутри домена выбирает конкретный жанр
        - если ничего не набрало порога — fallback
        """
        domain = self.infer_domain(features)
        domain_genres = self._genres_for_domain(domain) or self.registry.domains.get(domain, [])

        # Если домен пустой — fallback
        if not domain_genres:
            return self.fallback_by_domain.get(domain, "cinematic")

        # Простейший выбор: пока всем жанрам внутри домена
        # отдаём один и тот же доменный скор (можно уточнить позже
        # по дополнительным признакам).
        domain_score = self.score_domains(features)[domain]
        threshold = self.domain_thresholds.get(domain, 0.0)

        if domain_score < threshold:
            return self.fallback_by_domain.get(domain, "cinematic")

        # Для начала выбираем "главный" жанр домена — первый.
        # Позже можно сделать тонкую дифференциацию по поджанрам.
        selected = domain_genres[0]

        poetic = features.get("poetic_density", 0.0)
        lyric = features.get("lyric_form_weight", poetic)
        gothic = features.get("gothic_factor", 0.0)

        if domain == "electronic" and (poetic > 0.35 or lyric > 0.35 or gothic > 0.25):
            return "lyrical_song"

        return selected

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
