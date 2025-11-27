# -*- coding: utf - 8 -*-
"""
GenreUniverseLoader v2
Массовая загрузка жанров в глобальный реестр StudioCore.

Цель:
- Подготовить каркас под 1500+ музыкальных жанров
- 400+ EDM - направлений
- 100+ лирических форм
- 200+ литературных направлений
- 80+ драматургических жанров
- 60+ комедийных форм
- 70+ готических направлений и субкультур
- 300+ этнических музыкальных школ
- гибридные и экспериментальные стили

В этом модуле задаются только базовые выборки и структура.
Реальное наполнение можно расширять патчами без изменения ядра.
"""

from __future__ import annotations

from typing import Iterable

from .genre_universe import GenreUniverse


def _bulk_add(items: Iterable[str], add_fn) -> None:
    for name in items:
        add_fn(name.strip())


def load_genre_universe() -> GenreUniverse:
    """Инициализирует и заполняет GenreUniverse базовыми наборами жанров.

    Функция stateless: всегда создаёт новый объект и возвращает его.
    """
    U = GenreUniverse()

    # === BASE MUSIC GENRES (примерное ядро, далее расширяется патчами) ===
    music_genres = [
        "rock",
        "metal",
        "progressive_rock",
        "progressive_metal",
        "hard_rock",
        "punk_rock",
        "post_punk",
        "indie_rock",
        "alternative_rock",
        "pop",
        "synth_pop",
        "art_pop",
        "electronic",
        "ambient",
        "drone",
        "industrial",
        "trip_hop",
        "hip_hop",
        "rap",
        "trap",
        "drill",
        "boom_bap",
        "lofi_hip_hop",
        "jazz",
        "swing",
        "bebop",
        "fusion",
        "blues",
        "soul",
        "funk",
        "rnb",
        "gospel",
        "reggae",
        "ska",
        "dub",
        "country",
        "folk",
        "neofolk",
        "world_music",
        "classical",
        "baroque",
        "romantic_era",
        "modern_classical",
        "film_score",
        "orchestral_epic",
        "gothic_rock",
        "darkwave",
        "post_rock",
    ]

    # === EDM SUBGENRES (скелет под 400+ направлений) ===
    edm_subgenres = [
        "edm",
        "house",
        "deep_house",
        "progressive_house",
        "electro_house",
        "tech_house",
        "trance",
        "uplifting_trance",
        "psytrance",
        "goa_trance",
        "hardstyle",
        "dubstep",
        "brostep",
        "future_bass",
        "drum_and_bass",
        "liquid_dnb",
        "neurofunk",
        "jungle",
        "techno",
        "minimal_techno",
        "melodic_techno",
        "idm",
        "glitch",
        "breakbeat",
        "breakcore",
        "hardcore_techno",
    ]

    # === LYRIC FORMS (поэзия, песенные формы) ===
    lyric_forms = [
        "лирика",
        "элегия",
        "романс",
        "баллада",
        "ода",
        "сонет",
        "эпиграмма",
        "послание",
        "притча",
        "поэма",
        "поэтический_монолог",
        "панегирик",
        "сатирическое_стихотворение",
        "гимн",
        "колыбельная",
        "народная_песня",
        "шансона",
        "реп_текст",
        "spoken_word",
        "slam_poetry",
        "верлибр",
    ]

    # === LITERARY GENRES ===
    literary_genres = [
        "роман",
        "повесть",
        "рассказ",
        "новелла",
        "эссе",
        "очерк",
        "дневник",
        "мемуары",
        "античная_драма",
        "миф",
        "легенда",
        "сказка",
        "антиутопия",
        "утопия",
        "фэнтези",
        "научная_фантастика",
        "мистика",
        "ужасы",
        "детектив",
        "триллер",
        "психологический_роман",
        "философский_роман",
    ]

    # === DRAMA GENRES ===
    dramatic_genres = [
        "трагедия",
        "комедия",
        "драма",
        "трагикомедия",
        "farce",
        "sketch_comedy",
        "монодрама",
        "пьеса_в_стихах",
        "музыкальная_драма",
        "мюзикл",
        "опера",
        "оперетта",
        "водевиль",
    ]

    # === COMEDY FORMS ===
    comedy_forms = [
        "сатирическая_комедия",
        "лирическая_комедия",
        "черная_комедия",
        "романтическая_комедия",
        "стэнд_ап",
        "скетч",
        "импровизация",
        "пародия",
        "гротеск",
        "фарс",
    ]

    # === GOTHIC / DARK SUBCULTURES ===
    gothic_subcultures = [
        "gothic_rock",
        "darkwave",
        "ethereal_wave",
        "post_punk_goth",
        "industrial_goth",
        "doom_metal",
        "black_metal",
        "symphonic_metal",
        "gothic_metal",
        "dark_ambient",
        "ritual_ambient",
    ]

    # === ETHNIC SCHOOLS (примерный каркас) ===
    ethnic_schools = [
        "celtic_folk",
        "irish_folk",
        "ukrainian_folk",
        "balkan_folk",
        "slavic_folk",
        "arabic_classical",
        "persian_classical",
        "indian_classical_hindustani",
        "indian_classical_carnatic",
        "chinese_traditional",
        "japanese_traditional",
        "afrobeat",
        "latin_folk",
        "flamenco",
        "tango_traditional",
    ]

    # === HYBRID / EXPERIMENTAL ===
    hybrid_genres = [
        "cinematic_trap",
        "orchestral_rap",
        "folk_trap",
        "dark_folk_electronic",
        "post_classical_ambient",
        "neo_classical",
        "synthwave",
        "darksynth",
        "vaporwave",
        "chillwave",
    ]

    _bulk_add(music_genres, U.add_music)
    _bulk_add(edm_subgenres, U.add_music)
    _bulk_add(lyric_forms, U.add_lyric_form)
    _bulk_add(literary_genres, U.add_literature_style)
    _bulk_add(dramatic_genres, U.add_drama)
    _bulk_add(comedy_forms, U.add_comedy)
    _bulk_add(gothic_subcultures, U.add_gothic_style)
    _bulk_add(ethnic_schools, U.add_ethnic)
    _bulk_add(hybrid_genres, U.add_hybrid)

    return U
