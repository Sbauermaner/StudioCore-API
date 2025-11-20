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
GenreUniverse v2 — единый реестр жанров StudioCore.

* Сохраняет обратную совместимость с v1 (публичные сигнатуры).
* Добавляет отдельные коллекции для музыкальных/EDM/литературных/драматических
  и гибридных форм.
* Поддерживает alias-map для синонимов (включая русскоязычные варианты).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set


class GenreUniverse:
    """Глобальный реестр жанров и форм искусства."""

    def __init__(self) -> None:
        # Базовые категории
        self.music_genres: List[str] = []
        self.edm_styles: List[str] = []
        self.lyric_forms: List[str] = []
        self.literary_schools: List[str] = []
        self.dramatic_genres: List[str] = []
        self.comedy_forms: List[str] = []
        self.gothic_directions: List[str] = []
        self.ethnic_music_schools: List[str] = []
        self.hybrids: List[str] = []
        self.alias_map: Dict[str, str] = {}
        self.tags: Dict[str, Set[str]] = {}

        # Совместимость с v1
        self.music: List[str] = self.music_genres
        self.literature_styles: List[str] = self.literary_schools
        self.literature: List[str] = self.literary_schools
        self.stage: List[str] = self.dramatic_genres
        self.comedy_genres: List[str] = self.comedy_forms
        self.edm_genres: List[str] = self.edm_styles
        self.gothic_styles: List[str] = self.gothic_directions
        self.ethnic_schools: List[str] = self.ethnic_music_schools

    # === UTILS ===
    @staticmethod
    def _canonical(name: str) -> str:
        return name.strip().lower().replace(" ", "_").replace("-", "_")

    def add_alias(self, alias: str, canonical: str) -> None:
        self.alias_map[self._canonical(alias)] = self._canonical(canonical)

    def _add_unique(self, collection: List[str], name: str, tags: Optional[Set[str]] = None) -> str:
        canonical = self._canonical(name)
        if canonical not in collection:
            collection.append(canonical)
        # каждый зарегистрированный жанр сам себе алиас
        self.add_alias(canonical, canonical)
        if tags:
            self.tags.setdefault(canonical, set()).update({self._canonical(tag) for tag in tags})
        return canonical

    # === MUSIC ===
    def add_music(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:  # meta сохраняем для совместимости
        self._add_unique(self.music_genres, name, set(tags or []))

    # === EDM ===
    def add_edm(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.edm_styles, name, set(tags or []))

    def add_electronic(self, genre: str) -> None:  # v1 совместимость
        self.add_edm(genre)

    # === LITERATURE ===
    def add_literature_style(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.literary_schools, name, set(tags or []))

    def add_literature(self, genre: str) -> None:  # v1 совместимость
        self.add_literature_style(genre)

    # === LYRIC FORMS ===
    def add_lyric_form(self, form: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.lyric_forms, form, set(tags or []))

    # === DRAMA ===
    def add_dramatic_genre(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.dramatic_genres, name, set(tags or []))

    def add_drama(self, form: str) -> None:  # v1 совместимость
        self.add_dramatic_genre(form)

    # === COMEDY ===
    def add_comedy_genre(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.comedy_forms, name, set(tags or []))

    def add_comedy(self, form: str) -> None:  # v1 совместимость
        self.add_comedy_genre(form)

    # === GOTHIC ===
    def add_gothic_style(self, name: str, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.gothic_directions, name, set(tags or []))

    # === ETHNIC ===
    def add_ethnic_school(self, name: str, region: str = "", tags: Optional[List[str]] = None, **meta) -> None:
        canonical = self._add_unique(self.ethnic_music_schools, name, set(tags or []))
        if region:
            self.add_alias(region + "_" + canonical, canonical)

    def add_ethnic(self, name: str) -> None:  # v1 совместимость
        self.add_ethnic_school(name)

    # === HYBRID ===
    def add_hybrid(self, name: str, components: Optional[List[str]] = None, tags: Optional[List[str]] = None, **meta) -> None:
        self._add_unique(self.hybrids, name, set(tags or []))
        if components:
            for p in components:
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

        if canonical in self.edm_styles:
            domain, subdomain, gtype = "music", "edm", "edm"
        elif canonical in self.music_genres:
            domain, subdomain, gtype = "music", "music", "music"
        elif canonical in self.lyric_forms:
            domain, subdomain, gtype = "literature", "lyric_form", "lyric_forms"
        elif canonical in self.literary_schools:
            domain, subdomain, gtype = "literature", "literature", "literature"
        elif canonical in self.dramatic_genres:
            domain, subdomain, gtype = "drama", "drama", "drama"
        elif canonical in self.comedy_forms:
            domain, subdomain, gtype = "comedy", "comedy", "comedy"
        elif canonical in self.gothic_directions:
            domain, subdomain, gtype = "gothic", "gothic", "gothic"
        elif canonical in self.ethnic_music_schools:
            domain, subdomain, gtype = "ethnic", "ethnic", "ethnic"
        elif canonical in self.hybrids:
            domain, subdomain, gtype = "hybrid", "hybrid", "hybrid"

        return {"domain": domain, "subdomain": subdomain, "type": gtype, "canonical": canonical}

    def list_all(self) -> Dict[str, List[str]]:
        return {
            "music_genres": list(self.music_genres),
            "edm_styles": list(self.edm_styles),
            "lyric_forms": list(self.lyric_forms),
            "literary_schools": list(self.literary_schools),
            "dramatic_genres": list(self.dramatic_genres),
            "comedy_forms": list(self.comedy_forms),
            "gothic_directions": list(self.gothic_directions),
            "ethnic_music_schools": list(self.ethnic_music_schools),
            "hybrids": list(self.hybrids),
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
