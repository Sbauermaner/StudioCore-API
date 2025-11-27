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
GenreMetaMatrix v1.0 — доменная матрица жанров для StudioCore.

Задача:
- взять список жанров, которые распознал парсер / ядро,
- классифицировать их по крупным доменам (rock, metal, edm, jazz, hiphop, pop,
  world, cinema, comedy, lyric, literature, stage, gothic, etc.),
- посчитать веса по доменам,
- вернуть структуру, готовую для включения в feature_map.

Использование:
    matrix = GenreMetaMatrix()
    domain_weights = matrix.compute_domain_weights(["gothic_metal", "dark_ambient", "latin_rap"])
    # domain_weights -> {"metal": 0.34, "gothic": 0.34, "ambient": 0.16, "hiphop": 0.16, "latin": 0.16}

Дальше:
    feature_map["genre_domains"] = domain_weights
"""

from __future__ import annotations
from typing import Dict, List


class GenreMetaMatrix:
    """Доменно - ориентированная матрица жанров."""

    def __init__(self) -> None:
        # Простейшая сигнатура доменов.
        # Можно расширять без ломки логики.
        self.domain_keywords: Dict[str, List[str]] = {
            "rock": ["rock", "punk", "grunge", "emo"],
            "metal": ["metal", "core", "doom", "sludge"],
            "jazz": ["jazz", "swing", "bebop", "bop"],
            "blues": ["blues"],
            "edm": [
                "edm",
                "house",
                "techno",
                "trance",
                "dubstep",
                "dnb",
                "breakbeat",
                "synthwave",
                "ambient",
                "drone",
                "wave",
            ],
            "hiphop": ["hiphop", "hip_hop", "rap", "trap", "drill", "phonk"],
            "pop": ["pop", "city_pop", "dance_pop", "k_pop", "j_pop", "rnb"],
            "soul_funk": ["soul", "funk", "motown", "gospel"],
            "world": ["folk", "ethno", "world", "traditional"],
            "cinema": ["film", "ost", "cinematic", "score"],
            "theatre": ["theatre", "opera", "operetta", "stage", "broadway"],
            "comedy": ["comedy", "humor", "parody", "satire", "burlesque", "clown"],
            "gothic": ["gothic", "darkwave", "occult", "ritual", "witch"],
            "literature": ["novel", "epic", "saga", "essay", "memoir"],
            "lyric": [
                "lyric",
                "sonnet",
                "ode",
                "elegy",
                "haiku",
                "ballad",
                "villanelle",
                "free_verse",
                "slam",
            ],
        }

    def _match_domains_for_genre(self, genre: str) -> List[str]:
        """Возвращает список доменов, к которым относится данный жанр."""
        g = genre.lower()
        matched: List[str] = []
        for domain, keys in self.domain_keywords.items():
            for key in keys:
                if key in g:
                    matched.append(domain)
                    break
        return matched

    def compute_domain_weights(self, genres: List[str]) -> Dict[str, float]:
        """
        Принимает список жанров (уже распознанных ядром),
        возвращает нормированные веса доменов.
        """
        raw_counts: Dict[str, float] = {}

        for g in genres:
            domains = self._match_domains_for_genre(g)
            if not domains:
                # если жанр не узнали — относим к 'unknown' домену
                raw_counts.setdefault("unknown", 0.0)
                raw_counts["unknown"] += 1.0
                continue

            share = 1.0 / len(domains)
            for d in domains:
                raw_counts.setdefault(d, 0.0)
                raw_counts[d] += share

        # Нормализация в [0..1]
        total = sum(raw_counts.values()) or 1.0
        normalized = {d: v / total for d, v in raw_counts.items()}

        return normalized


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
