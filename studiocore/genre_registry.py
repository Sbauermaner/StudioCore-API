# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
GlobalGenreRegistry v1.0

Единый реестр жанров для StudioCore:
- музыкальные жанры (rock/metal/edm/jazz/world/etc.)
- лирические жанры (классика + современная поэзия)
- комические жанры (музыка + лирика)
- домены (hard/electronic/jazz/lyrical/cinematic/comedy/soft)
- композиторские/режиссёрские профили (score / directing modes)

Этот модуль НЕ привязан к Suno напрямую, это справочник для ядра.
"""

from __future__ import annotations
from typing import Dict, List


class GlobalGenreRegistry:
    """Глобальный реестр жанров и доменов StudioCore."""

    def __init__(self) -> None:
        # === 1. Музыкальные жанры (укрупнённый, но широкий список) ===
        # Можно расширять, но базовый набор покрывает 95% реального мира.
        self.music_genres: List[str] = [
            # POP
            "pop", "synthpop", "electropop", "dance_pop", "art_pop", "dream_pop",
            "indie_pop", "hyperpop", "teen_pop", "baroque_pop", "city_pop",
            "j_pop", "k_pop", "c_pop", "latin_pop", "french_pop", "schlager",

            # ROCK
            "rock", "hard_rock", "soft_rock", "alt_rock", "indie_rock",
            "garage_rock", "psychedelic_rock", "post_rock", "prog_rock",
            "space_rock", "surf_rock", "glam_rock", "math_rock", "blues_rock",
            "folk_rock", "country_rock", "southern_rock", "gothic_rock",
            "emo_rock", "midwest_emo", "post_grunge", "arena_rock",
            "rock_n_roll",

            # METAL
            "heavy_metal", "power_metal", "thrash_metal", "speed_metal",
            "death_metal", "black_metal", "doom_metal", "gothic_metal",
            "folk_metal", "viking_metal", "pagan_metal", "melodic_death_metal",
            "prog_metal", "djent", "metalcore", "deathcore", "grindcore",
            "industrial_metal", "nu_metal", "sludge_metal", "groove_metal",
            "alt_metal", "avantgarde_metal", "drone_metal", "symphonic_metal",

            # PUNK
            "punk", "pop_punk", "hardcore_punk", "post_punk", "skate_punk",
            "emo_punk", "garage_punk", "crust_punk", "anarcho_punk", "oi_punk",

            # HIP-HOP / RAP
            "hip_hop", "boom_bap", "trap", "drill", "gangsta_rap",
            "conscious_rap", "jazz_rap", "trip_hop", "lofi_hip_hop",
            "alt_hip_hop", "rap_rock", "rap_metal", "cloud_rap", "phonk",
            "drift_phonk", "grime", "uk_drill", "horrorcore",

            # EDM / ELECTRONIC / CLUB
            "edm", "house", "deep_house", "tech_house", "progressive_house",
            "electro_house", "bass_house", "tropical_house", "piano_house",
            "slap_house", "g_house", "melodic_house", "uk_house",

            "trance", "progressive_trance", "uplifting_trance", "vocal_trance",
            "psytrance", "goa_trance", "hard_trance", "tech_trance",

            "techno", "minimal_techno", "acid_techno", "hard_techno",
            "industrial_techno", "dub_techno", "detroit_techno",

            "drum_and_bass", "jungle", "liquid_dnb", "neurofunk", "jump_up",
            "techstep", "atmospheric_dnb", "darkstep",

            "dubstep", "brostep", "riddim", "chillstep", "deep_dubstep",
            "future_bass", "hybrid_trap", "wonky", "trapstep",

            "breakbeat", "big_beat", "uk_garage", "speed_garage", "breakcore",
            "2step", "electro", "electroclash", "digital_hardcore",

            # AMBIENT / EXPERIMENTAL / SYNTH
            "ambient", "dark_ambient", "space_ambient", "drone",
            "downtempo", "chillout", "psybient", "idm", "electronica",
            "glitch", "glitch_hop",

            "synthwave", "retrowave", "outrun", "darksynth", "chillwave",
            "vaporwave", "future_garage", "dreamwave", "cyberwave",

            # HARD DANCE / RAVE
            "hardstyle", "rawstyle", "hardcore", "happy_hardcore", "gabber",
            "terrorcore", "speedcore", "jumpstyle", "rave",

            # JAZZ
            "jazz", "vocal_jazz", "smooth_jazz", "swing", "bebop", "hard_bop",
            "cool_jazz", "modal_jazz", "free_jazz", "fusion_jazz",
            "jazz_funk", "nu_jazz", "contemporary_jazz", "jazz_ballad",
            "latin_jazz", "bossa_nova", "gypsy_jazz", "ragtime", "dixieland",
            "acid_jazz", "electro_swing", "jazz_hip_hop", "jazz_lofi",

            # CLASSICAL / SCORE / COMPOSER
            "classical", "baroque", "romantic", "modern_classical",
            "neo_classical", "film_score", "orchestral_score", "chamber_music",
            "solo_piano", "ballet_score", "opera", "minimalism",

            # CINEMATIC
            "cinematic", "epic_orchestral", "hybrid_orchestral",
            "dark_orchestral", "trailer_music", "emotional_score",
            "horror_score", "fantasy_score", "sci_fi_score",

            # WORLD / ETHNO (сжатый набор)
            "world_music", "flamenco", "arabic_music", "persian_music",
            "klezmer", "balkan_folk", "afrobeat", "reggae", "dub", "ska",
            "salsa", "tango", "samba", "cumbia", "mariachi", "bollywood_pop",

            # FOLK / COUNTRY / BLUES
            "folk", "indie_folk", "dark_folk", "pagan_folk",
            "country", "country_pop", "bluegrass", "americana",
            "blues", "delta_blues", "chicago_blues", "electric_blues",

            # R&B / SOUL / FUNK
            "rnb", "neo_soul", "soul", "funk", "motown",

            # LO-FI / CHILL
            "lofi", "lofi_jazz", "lofi_hip_hop", "chillhop", "study_beats",
            "sleepcore",

            # HYBRIDS (для ядра)
            "orchestral_trap", "orchestral_dnb", "orchestral_dubstep",
            "electro_rock", "edm_rock", "jazz_metal", "jazz_rap",
            "cinematic_rap", "cinematic_trap"
        ]

        # === 2. Лирические жанры (включая комические формы) ===
        self.lyrical_genres: List[str] = [
            # классика
            "lyric", "lyrical_poetry", "elegy", "ode", "sonnet", "epigram",
            "epitaph", "ballad_poem", "hymn", "madrigal", "villanelle",
            "triolet", "terza_rima", "free_verse", "blank_verse", "haiku",
            "tanka", "rubai", "ghazal",

            # тематическая лирика
            "love_lyric", "intimate_lyric", "romantic_lyric",
            "confessional_lyric", "philosophical_lyric",
            "landscape_lyric", "spiritual_lyric", "civic_lyric",
            "patriotic_lyric", "tragic_lyric", "meditative_lyric",

            # музыкально-лирические формы
            "lyrical_song", "lyrical_ballad", "vocal_lyric", "romance_song",
            "author_song", "chanson_lyric",

            # современная поэзия
            "slam_poetry", "spoken_word", "performance_poetry",
            "urban_poetry", "minimalist_poetry", "micro_poetry",
            "instagram_poetry", "digital_lyric", "prose_poem",

            # фольклор
            "folk_lyric", "lullaby", "lament_song", "ritual_song",

            # авангард
            "concrete_poetry", "visual_poetry", "absurd_lyric",
            "postmodern_lyric",
        ]

        # === 3. Комические лирические формы (как «комиксы» и сатира) ===
        self.comedic_lyrical_genres: List[str] = [
            "comic_verse", "light_verse", "satirical_poetry",
            "parody_poem", "humorous_ballad", "limmerick", "burlesque_poem",
            "ironic_monologue", "standup_poetry", "comic_spoken_word",
        ]

        # === 4. Комические музыкальные жанры ===
        self.comedic_music_genres: List[str] = [
            "comedy_rock", "parody_rock", "novelty_song",
            "musical_theatre", "cabaret", "vaudeville",
            "comic_opera", "parody_pop", "satirical_song",
        ]

        # === 5. Композиторские и режиссёрские профили ===
        self.composer_profiles: List[str] = [
            "film_composer", "game_composer", "orchestral_composer",
            "minimalist_composer", "jazz_arranger", "songwriter",
        ]

        self.director_profiles: List[str] = [
            "cinematic_director", "music_video_director",
            "montage_style", "one_take_style", "trailer_directing",
        ]

        # === 6. Домены (для GenreWeightsEngine) ===
        self.domains: Dict[str, List[str]] = {
            "hard": [
                "rock", "hard_rock", "alt_rock", "metalcore", "heavy_metal",
                "thrash_metal", "nu_metal", "death_metal", "black_metal",
                "punk", "hardcore_punk", "rap_metal", "rap_rock",
                "drill", "trap", "phonk", "grime",
            ],
            "electronic": [
                "edm", "house", "techno", "trance", "drum_and_bass",
                "jungle", "dubstep", "future_bass", "synthwave", "retrowave",
                "darksynth", "vaporwave", "glitch", "idm", "lofi", "chillhop",
            ],
            "jazz": [
                "jazz", "vocal_jazz", "smooth_jazz", "swing", "bebop",
                "hard_bop", "cool_jazz", "fusion_jazz", "jazz_funk",
                "nu_jazz", "jazz_ballad", "latin_jazz", "bossa_nova",
                "gypsy_jazz", "jazz_hip_hop", "jazz_lofi",
            ],
            "lyrical": self.lyrical_genres + self.comedic_lyrical_genres,
            "cinematic": [
                "cinematic", "epic_orchestral", "hybrid_orchestral",
                "film_score", "orchestral_score", "trailer_music",
                "emotional_score", "horror_score", "fantasy_score",
            ],
            "comedy": self.comedic_music_genres,
            "soft": [
                "folk", "indie_folk", "acoustic_pop", "ballad_pop",
                "world_music", "ambient", "chillout", "lofi_jazz",
            ],
        }

    # Вспомогательные методы можно расширять позже
