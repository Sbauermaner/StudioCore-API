# -*- coding: utf-8 -*-
"""GLOBAL GENRE UNIVERSE v2 builder."""

from __future__ import annotations

from .genre_universe import GenreUniverse


def build_global_genre_universe_v2() -> GenreUniverse:
    """Создаёт и заполняет GenreUniverse большим, но компактным набором жанров."""

    u = GenreUniverse()

    # --- MUSIC ---
    music_genres = [
        "rock",
        "classic_rock",
        "hard_rock",
        "prog_rock",
        "post_rock",
        "math_rock",
        "gothic_rock",
        "stoner_rock",
        "indie_rock",
        "alt_rock",
        "metal",
        "heavy_metal",
        "thrash_metal",
        "death_metal",
        "black_metal",
        "doom_metal",
        "symphonic_metal",
        "gothic_metal",
        "folk_metal",
        "power_metal",
        "progressive_metal",
        "pop",
        "synthpop",
        "dream_pop",
        "art_pop",
        "k_pop",
        "j_pop",
        "hip_hop",
        "boom_bap",
        "trap",
        "drill",
        "conscious_rap",
        "horrorcore",
        "jazz",
        "bebop",
        "hard_bop",
        "cool_jazz",
        "free_jazz",
        "smooth_jazz",
        "fusion_jazz",
        "blues",
        "soul",
        "funk",
        "rnb",
        "country",
        "folk",
        "indie_folk",
        "ambient",
        "experimental",
        "noise",
        "avant_garde",
    ]
    for g in music_genres:
        u.add_music(g)

    # --- EDM ---
    edm_genres = [
        "edm",
        "house",
        "deep_house",
        "tech_house",
        "progressive_house",
        "afro_house",
        "g_house",
        "future_house",
        "techno",
        "detroit_techno",
        "acid_techno",
        "industrial_techno",
        "minimal_techno",
        "trance",
        "uplifting_trance",
        "psytrance",
        "goa_trance",
        "tech_trance",
        "progressive_trance",
        "drum_and_bass",
        "liquid_dnb",
        "neurofunk",
        "jungle",
        "techstep",
        "jump_up",
        "dubstep",
        "brostep",
        "riddim",
        "deep_dubstep",
        "hardstyle",
        "hardcore",
        "gabber",
        "idm",
        "glitch",
        "future_bass",
        "trap_edm",
        "breakbeat",
        "breaks",
        "electro",
        "synthwave",
        "vaporwave",
    ]
    for g in edm_genres:
        u.add_edm(g)

    # --- LITERATURE STYLES ---
    literature_styles = [
        "antiquity",
        "medievalism",
        "renaissance",
        "baroque",
        "classicismus",
        "romanticism",
        "realism",
        "naturalism",
        "modernism",
        "postmodernism",
        "symbolism",
        "acmeism",
        "futurism",
        "magical_realism",
        "absurdism",
        "gothic_literature",
        "science_fiction",
        "fantasy",
        "magical_epic",
        "essay",
    ]
    for g in literature_styles:
        u.add_literature_style(g)

    # --- LYRIC FORMS ---
    lyric_forms = [
        "ode",
        "elegy",
        "ballad",
        "poem",
        "sonnet",
        "epigram",
        "madrigal",
        "gazal",
        "tanka",
        "haiku",
        "free_verse",
        "blank_verse",
        "dactylic_verse",
        "villanelle",
        "sestina",
        "triolet",
        "limerick",
        "verlibre",
        "dolkink",
        "spoken_word",
    ]
    for f in lyric_forms:
        u.add_lyric_form(f)

    # --- DRAMA ---
    dramatic_genres = [
        "tragedy",
        "drama",
        "comedy",
        "tragicomedy",
        "farce",
        "vaudeville",
        "melodrama",
        "absurdist_drama",
        "grotesque",
        "historical_drama",
    ]
    for g in dramatic_genres:
        u.add_dramatic_genre(g)

    # --- COMEDY ---
    comedy_genres = [
        "satire",
        "irony",
        "sketch",
        "standup",
        "clownade",
        "buffonade",
        "parody_poem",
        "comic_verse",
        "humorous_ballad",
        "musical_parody",
    ]
    for g in comedy_genres:
        u.add_comedy_genre(g)

    # --- GOTHIC ---
    gothic_styles = [
        "gothic_rock",
        "darkwave",
        "gothic_metal",
        "deathrock",
        "ethereal_wave",
        "neoclassical_darkwave",
        "dark_ambient",
        "gothic_poetry",
        "gothic_drama",
        "gothic_cabaret",
    ]
    for g in gothic_styles:
        u.add_gothic_style(g)

    # --- ETHNIC ---
    ethnic_schools = [
        "indian_raga",
        "hindustani",
        "carnatic",
        "arabic_traditional",
        "persian_traditional",
        "turkish_traditional",
        "chinese_classical",
        "japanese_minyo",
        "african_drumming",
        "celtic_tradition",
        "slavic_folk",
        "andalusian_flamenco",
    ]
    for g in ethnic_schools:
        u.add_ethnic_school(g)

    # --- HYBRIDS ---
    hybrids = [
        ("orchestral_dnb", ["orchestral", "drum_and_bass"]),
        ("gothic_cabaret", ["gothic", "cabaret"]),
        ("cinematic_dark_folk", ["cinematic", "dark_folk"]),
        ("tribal_techno", ["tribal", "techno"]),
        ("flamenco_metal", ["flamenco", "metal"]),
        ("oriental_trap", ["oriental", "trap"]),
        ("folk_rap", ["folk", "rap"]),
        ("cinematic_orchestral", ["cinematic", "orchestral"]),
    ]
    for name, parents in hybrids:
        u.add_hybrid(name, parents=parents)

    # --- ALIASES ---
    aliases = {
        "drum and bass": "drum_and_bass",
        "dnb": "drum_and_bass",
        "DnB": "drum_and_bass",
        "транс": "trance",
        "техно": "techno",
        "хаус": "house",
        "готика": "gothic",
        "готическая поэзия": "gothic_poetry",
        "элегия": "elegy",
        "ода": "ode",
        "сонет": "sonnet",
        "драма": "drama",
        "комедия": "comedy",
        "сатирическая поэзия": "satire",
    }
    for alias, canonical in aliases.items():
        u.add_alias(alias, canonical)

    return u


__all__ = ["build_global_genre_universe_v2"]
