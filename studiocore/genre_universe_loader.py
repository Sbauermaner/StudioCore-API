# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""GenreUniverseLoader v2 — точка входа для GLOBAL GENRE UNIVERSE."""

from __future__ import annotations

from .genre_universe_extended import build_global_genre_universe_v2


def load_genre_universe():
    """Возвращает предзаполненный экземпляр GenreUniverse."""

    return build_global_genre_universe_v2()


__all__ = ["load_genre_universe"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
