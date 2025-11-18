# -*- coding: utf-8 -*-
"""
GenreUniverse v1.0 — базовый контейнер глобальных жанров.

Эта структура является тем, что наполняет genre_universe_loader.py:
музыкальные жанры, лирические формы, театральные формы, кино, комедия,
этно-жанры и любые будущие категории.
"""

from __future__ import annotations
from typing import List


class GenreUniverse:
    """Глобальный реестр жанров и форм искусства."""

    def __init__(self) -> None:
        # Храним всё в простых категориях
        self.music: List[str] = []
        self.literature: List[str] = []
        self.lyric_forms: List[str] = []
        self.stage: List[str] = []
        self.comedy: List[str] = []

    # === MUSIC ===
    def add_music(self, genre: str) -> None:
        if genre not in self.music:
            self.music.append(genre)

    # === LITERATURE ===
    def add_literature(self, genre: str) -> None:
        if genre not in self.literature:
            self.literature.append(genre)

    # === LYRIC FORMS ===
    def add_lyric_form(self, form: str) -> None:
        if form not in self.lyric_forms:
            self.lyric_forms.append(form)

    # === CINEMA / THEATRE / STAGE ===
    def add_stage(self, form: str) -> None:
        if form not in self.stage:
            self.stage.append(form)

    # === COMEDY / HUMOR ===
    def add_comedy(self, form: str) -> None:
        if form not in self.comedy:
            self.comedy.append(form)
