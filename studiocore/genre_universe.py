# -*- coding: utf-8 -*-
"""
GenreUniverse v2 — единый реестр жанров StudioCore.

* Сохраняет обратную совместимость с v1 (публичные сигнатуры).
* Добавляет отдельные коллекции для музыкальных/EDM/литературных/драматических
  и гибридных форм.
* Поддерживает alias-map для синонимов (включая русскоязычные варианты).
"""

from __future__ import annotations
from typing import Dict, List


class GenreUniverse:
    """Глобальный реестр жанров и форм искусства."""

    def __init__(self) -> None:
        # Базовые категории
        self.music_genres: List[str] = []
        self.edm_genres: List[str] = []
        self.lyric_forms: List[str] = []
        self.literature_styles: List[str] = []
        self.dramatic_genres: List[str] = []
        self.comedy_genres: List[str] = []
        self.gothic_styles: List[str] = []
        self.ethnic_schools: List[str] = []
        self.hybrids: List[str] = []
        self.alias_map: Dict[str, str] = {}

        # Совместимость с v1
        self.music: List[str] = self.music_genres
        self.literature: List[str] = self.literature_styles
        self.stage: List[str] = self.dramatic_genres
        self.comedy: List[str] = self.comedy_genres

    # === UTILS ===
    @staticmethod
    def _canonical(name: str) -> str:
        return name.strip().lower().replace(" ", "_").replace("-", "_")

    def add_alias(self, alias: str, canonical: str) -> None:
        self.alias_map[self._canonical(alias)] = self._canonical(canonical)

    def _add_unique(self, collection: List[str], name: str) -> str:
        canonical = self._canonical(name)
        if canonical not in collection:
            collection.append(canonical)
        # каждый зарегистрированный жанр сам себе алиас
        self.add_alias(canonical, canonical)
        return canonical

    # === MUSIC ===
    def add_music(self, name: str, **meta) -> None:  # meta сохраняем для совместимости
        self._add_unique(self.music_genres, name)

    # === EDM ===
    def add_edm(self, name: str, **meta) -> None:
        self._add_unique(self.edm_genres, name)

    def add_electronic(self, genre: str) -> None:  # v1 совместимость
        self.add_edm(genre)

    # === LITERATURE ===
    def add_literature_style(self, name: str, **meta) -> None:
        self._add_unique(self.literature_styles, name)

    def add_literature(self, genre: str) -> None:  # v1 совместимость
        self.add_literature_style(genre)

    # === LYRIC FORMS ===
    def add_lyric_form(self, form: str, **meta) -> None:
        self._add_unique(self.lyric_forms, form)

    # === DRAMA ===
    def add_dramatic_genre(self, name: str, **meta) -> None:
        self._add_unique(self.dramatic_genres, name)

    def add_drama(self, form: str) -> None:  # v1 совместимость
        self.add_dramatic_genre(form)

    # === COMEDY ===
    def add_comedy_genre(self, name: str, **meta) -> None:
        self._add_unique(self.comedy_genres, name)

    def add_comedy(self, form: str) -> None:  # v1 совместимость
        self.add_comedy_genre(form)

    # === GOTHIC ===
    def add_gothic_style(self, name: str, **meta) -> None:
        self._add_unique(self.gothic_styles, name)

    # === ETHNIC ===
    def add_ethnic_school(self, name: str, region: str = "", **meta) -> None:
        canonical = self._add_unique(self.ethnic_schools, name)
        if region:
            self.add_alias(region + "_" + canonical, canonical)

    def add_ethnic(self, name: str) -> None:  # v1 совместимость
        self.add_ethnic_school(name)

    # === HYBRID ===
    def add_hybrid(self, name: str, parents: List[str] | None = None, **meta) -> None:
        self._add_unique(self.hybrids, name)
        if parents:
            for p in parents:
                self.add_alias(f"{p}_{name}", name)

    # === ALIAS / RESOLVE ===
    def resolve(self, name: str) -> str:
        canonical = self._canonical(name)
        return self.alias_map.get(canonical, canonical)

    # === DOMAIN DETECTION ===
    def detect_domain(self, name: str) -> Dict[str, str]:
        canonical = self.resolve(name)
        domain = "unknown"
        subdomain = ""
        gtype = "unknown"

        if canonical in self.edm_genres:
            domain, subdomain, gtype = "music", "edm", "edm"
        elif canonical in self.music_genres:
            domain, subdomain, gtype = "music", "music", "music"
        elif canonical in self.lyric_forms:
            domain, subdomain, gtype = "literature", "lyric_form", "lyric_forms"
        elif canonical in self.literature_styles:
            domain, subdomain, gtype = "literature", "literature", "literature"
        elif canonical in self.dramatic_genres:
            domain, subdomain, gtype = "drama", "drama", "drama"
        elif canonical in self.comedy_genres:
            domain, subdomain, gtype = "comedy", "comedy", "comedy"
        elif canonical in self.gothic_styles:
            domain, subdomain, gtype = "gothic", "gothic", "gothic"
        elif canonical in self.ethnic_schools:
            domain, subdomain, gtype = "ethnic", "ethnic", "ethnic"
        elif canonical in self.hybrids:
            domain, subdomain, gtype = "hybrid", "hybrid", "hybrid"

        return {"domain": domain, "subdomain": subdomain, "type": gtype, "canonical": canonical}

    def list_all(self) -> Dict[str, List[str]]:
        return {
            "music_genres": list(self.music_genres),
            "edm_genres": list(self.edm_genres),
            "lyric_forms": list(self.lyric_forms),
            "literature_styles": list(self.literature_styles),
            "dramatic_genres": list(self.dramatic_genres),
            "comedy_genres": list(self.comedy_genres),
            "gothic_styles": list(self.gothic_styles),
            "ethnic_schools": list(self.ethnic_schools),
            "hybrids": list(self.hybrids),
        }
