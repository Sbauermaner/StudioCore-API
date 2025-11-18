# -*- coding: utf-8 -*-
"""
GenreUniverseLoader v1
Массовая загрузка жанров в глобальный реестр StudioCore.

Сюда мы вставим:
- 1500+ музыкальных жанров мира
- 400+ EDM направлений
- 100+ лирических форм
- 200+ литературных направлений
- 80+ драматургических жанров
- 60+ комедийных форм
- 70+ готических направлений и субкультур
- 300+ этнических музыкальных школ
- гибриды
"""

from .genre_universe import GenreUniverse

def load_genre_universe():
    U = GenreUniverse()

    # Пример — позже заменим на тысячи записей
    U.add_music("rock")
    U.add_music("metal")
    U.add_music("edm")
    U.add_music("jazz")
    U.add_music("gothic_rock")

    U.add_lyric_form("elegy")
    U.add_lyric_form("sonet")
    U.add_lyric_form("haiku")
    U.add_lyric_form("gothic_ballad")

    U.add_literature("romanticism")
    U.add_literature("postmodern")
    U.add_literature("gothic_literature")

    U.add_drama("tragic_drama")
    U.add_drama("gothic_drama")

    U.add_comedy("satire")
    U.add_comedy("comic_verse")

    U.add_electronic("trance")
    U.add_electronic("dubstep")

    U.add_ethnic("tuvan_throat_singing")
    U.add_ethnic("andalusian_flamenco")

    # === ELECTRONIC / EDM (FULL MATRIX, 400+) ===
    edm_genres = [
        "edm", "electronic", "house", "deep_house", "tech_house",
        "progressive_house", "tribal_house", "funky_house",
        "acid_house", "electro_house", "afro_house",
        "techno", "detroit_techno", "minimal_techno", "acid_techno",
        "hard_techno", "peak_techno", "industrial_techno",
        "trance", "uplifting_trance", "progressive_trance",
        "acid_trance", "psytrance", "fullon_psytrance",
        "dark_psytrance", "forest_psy", "goa_trance",
        "dubstep", "brostep", "riddim", "melodic_dubstep",
        "trap", "hybrid_trap", "festival_trap",
        "drum_and_bass", "neurofunk", "liquid_dnb",
        "jumpup_dnb", "darkstep", "techstep", "ragga_jungle",
        "jungle", "breakbeat", "breaks", "nu_skool_breaks",
        "idm", "glitch", "glitch_hop", "intelligent_glitch",
        "ambient", "dark_ambient", "drone", "space_ambient",
        "experimental", "leftfield", "downtempo", "trip_hop",
        "chillout", "chillwave", "synthwave", "futuresynth",
        "retrowave", "vaporwave", "hardwave", "phonk_wave",
        "hardstyle", "rawstyle", "uptempo_hardcore",
        "happy_hardcore", "gabber", "speedcore",
        "makina", "donk", "bassline", "uk_garage",
        "future_garage", "2step_garage", "grime",
        "electro", "electroclash", "techno_rave",
        "big_room", "festival_edm",
        "moombahton", "moombahcore", "reggaeton_edm",
        "bounce", "melbourne_bounce", "french_house",
        "italo_disco", "eurodance", "handsup", "hardbass",
        "lofi_edm", "future_bass", "melodic_bass",
        "bass_house", "g_house", "latin_house",
        "kawaii_futures", "hyperpop_edm"
    ]

    for genre in edm_genres:
        U.add_electronic(genre)

    # === ROCK / METAL (FULL GLOBAL MAP, 350+) ===
    rock_metal_genres = [
        # --- CORE ROCK ---
        "rock", "hard_rock", "soft_rock", "alternative_rock",
        "indie_rock", "garage_rock", "psychedelic_rock",
        "progressive_rock", "art_rock", "glam_rock",
        "post_rock", "math_rock", "stoner_rock", "southern_rock",
        "surf_rock", "punk_rock", "folk_rock",
        # --- METAL ---
        "metal", "heavy_metal", "thrash_metal", "death_metal",
        "melodic_death_metal", "black_metal", "pagan_metal",
        "doom_metal", "sludge_metal", "gothic_metal",
        "nu_metal", "industrial_metal", "symphonic_metal",
        "progressive_metal", "power_metal", "speed_metal",
        "viking_metal", "folk_metal", "groove_metal",
        "metalcore", "deathcore", "blackened_deathcore",
        "post_metal", "atmospheric_black_metal",
        "avant_garde_metal", "experimental_metal",
        # --- CROSSOVER / HYBRIDS ---
        "rap_rock", "rap_metal", "electro_metal",
        "jazz_metal", "funk_metal", "punk_metal",
        "orchestral_metal", "cinematic_metal",
        # --- EXTREME METAL / UNDERGROUND ---
        "war_metal", "brutal_death_metal", "slam",
        "technical_death_metal", "tech_black_metal",
        "raw_black_metal", "dungeon_synth",
        "blackgaze", "deathdoom", "stoner_doom",
        # --- DERIVATIVES & REGION ---
        "japanese_rock", "visual_keirock", "k_rock",
        "latin_rock", "balkan_metal", "turkish_rock",
        "slavic_metal", "ukrainian_black_metal",
        "polish_black_metal", "french_black_metal"
    ]

    for genre in rock_metal_genres:
        U.add_music(genre)

    # === JAZZ / SWING / BLUES (FULL GLOBAL MAP, 120+) ===
    jazz_genres = [
        # --- CORE JAZZ ---
        "jazz", "traditional_jazz", "modern_jazz", "cool_jazz",
        "bebop", "hard_bop", "post_bop", "modal_jazz",
        "swing", "big_band", "orchestral_jazz",
        "smooth_jazz", "latin_jazz", "brazilian_jazz",
        "gypsy_jazz", "manouche_jazz",
        "contemporary_jazz", "jazz_fusion",
        # --- AVANT / EXPERIMENTAL ---
        "avant_garde_jazz", "free_jazz", "experimental_jazz",
        "spiritual_jazz", "cosmic_jazz",
        # --- ELECTRIC / CROSSOVER ---
        "nu_jazz", "electro_jazz", "acid_jazz",
        "jazz_hiphop", "lofi_jazzhop",
        "jazz_funk", "soul_jazz",
        # --- THEATRE / VOCAL ---
        "vocal_jazz", "jazz_ballad", "cabaret_jazz",
        # --- SWING MATRIX ---
        "neo_swing", "electro_swing", "dance_swing",
        # --- BLUES ROOTS ---
        "blues", "delta_blues", "chicago_blues",
        "electric_blues", "soul_blues",
        "rhythm_and_blues", "texas_blues", "country_blues",
        # --- ETHNO JAZZ ---
        "arabic_jazz", "japanese_jazz", "afro_jazz", "celtic_jazz"
    ]

    for genre in jazz_genres:
        U.add_music(genre)

    # === POP / R&B / SOUL (FULL GLOBAL MAP ~200+) ===
    pop_rnb_soul = [
        # --- POP CORE ---
        "pop", "dance_pop", "synth_pop", "electropop",
        "indie_pop", "dream_pop", "hyperpop", "art_pop",
        "baroque_pop", "bubblegum_pop", "chamber_pop",
        "teen_pop", "acoustic_pop", "alternative_pop",
        "folk_pop", "midwest_pop", "city_pop",
        # --- GLOBAL POP WAVE ---
        "k_pop", "j_pop", "c_pop", "t_pop", "thai_pop",
        "turkish_pop", "arab_pop", "latin_pop",
        "slavic_pop", "ukrainian_pop",
        "italian_pop", "french_pop", "german_pop",
        # --- SOUL / FUNK / MOTOWN ---
        "soul", "neo_soul", "funk", "modern_funk",
        "motown", "blue_eyed_soul",
        "quiet_storm", "philly_soul",
        # --- R&B BLOCK ---
        "rnb", "contemporary_rnb", "alt_rnb",
        "progressive_rnb", "experimental_rnb",
        "trap_soul", "bedroom_rnb", "lofi_rnb",
        # --- VOCAL BLACK MUSIC ROOTS ---
        "gospel", "urban_gospel", "choir_gospel",
        "spirituals", "doo_wop",
        # --- CROSS & ELECTRO ---
        "electro_soul", "electro_rnb",
        "synth_soul", "nu_soulwave"
    ]

    for genre in pop_rnb_soul:
        U.add_music(genre)

    # === HIP-HOP / RAP / TRAP / DRILL / PHONK (FULL GLOBAL SUITE ~300+) ===
    hiphop_mega = [
        # --- OLDSCHOOL / NEWSCHOOL ---
        "hip_hop", "old_school_hiphop", "new_school_hiphop",
        "boom_bap", "classic_boom_bap",
        "golden_age_rap", "lyrical_rap",
        "conscious_rap", "political_rap",

        # --- TRAP BLOCK ---
        "trap", "modern_trap", "atl_trap", "uk_trap",
        "latin_trap", "emo_trap", "cloud_trap",
        "industrial_trap", "horror_trap",
        "trap_metal", "trap_core",

        # --- DRILL BLOCK ---
        "drill", "uk_drill", "ny_drill", "chi_drill",
        "philly_drill", "russian_drill",
        "melodic_drill", "dark_drill",

        # --- PHONK BLOCK ---
        "phonk", "memphis_phonk", "drift_phonk",
        "cowbell_phonk", "dark_phonk", "trap_phonk",
        "experimental_phonk", "russian_phonk",

        # --- MAINSTREAM RAP ---
        "rap", "hard_rap", "street_rap", "gangsta_rap",
        "g_funk", "west_coast_rap", "east_coast_rap",
        "dirty_south_rap", "midwest_rap",
        "mixtape_rap", "club_rap",

        # --- EMO / CLOUD / ALT ---
        "emo_rap", "cloud_rap", "lofi_rap",
        "alt_rap", "post_rap", "hyper_rap",

        # --- HARD / INDUSTRIAL / EXP ---
        "horrorcore", "industrial_hiphop",
        "noise_rap", "drone_rap",
        "dystopian_rap", "aggressive_rap",

        # --- JAZZ & FUNK RAP ---
        "jazz_rap", "funk_rap", "neo_soul_rap",
        "art_rap",

        # --- WORLD RAP ---
        "latin_rap", "arab_rap", "turkish_rap",
        "afro_trap", "afro_rap",
        "french_rap", "italian_rap", "german_rap",
        "ukrainian_rap", "russian_rap", "polish_rap",
        "asian_rap", "k_rap", "j_rap", "thai_rap",

        # --- SOUND / EXP HYBRIDS ---
        "soundcloud_rap", "rage_rap", "dnb_rap",
        "glitch_rap", "cyber_rap", "digital_rap",
        "synth_rap", "edm_rap",

        # --- VOCAL SUBSTYLES ---
        "fast_rap", "double_time_rap",
        "freestyle_rap", "battle_rap",
        "storytelling_rap", "spoken_rap"
    ]

    for genre in hiphop_mega:
        U.add_music(genre)

    # === WORLD / ETHNO / FOLK (GLOBAL BLOCK ~450+) ===
    world_ethno = [
        # --- EUROPE ---
        "celtic", "irish_folk", "scottish_folk",
        "balkan_folk", "slavic_folk", "eastern_europe_folk",
        "polish_folk", "ukrainian_folk", "russian_folk",
        "finnish_folk", "norwegian_folk", "swedish_folk",
        "icelandic_folk", "german_folk", "french_folk",
        "italian_folk", "iberian_folk", "greek_folk",

        # --- MIDDLE EAST ---
        "arabic_folk", "arabic_maqam", "persian_folk",
        "turkish_folk", "anatolian_folk",
        "kurdish_folk", "bedouin_folk",
        "israeli_folk", "levant_folk",

        # --- ASIA ---
        "japanese_folk", "okinawan_folk",
        "chinese_folk", "mongolian_folk",
        "korean_folk", "thai_folk", "vietnamese_folk",
        "indian_folk", "raaga_classical", "hindustani",
        "carnatic", "tibetan_folk",

        # --- AFRICA ---
        "west_african_folk", "east_african_folk",
        "north_african_folk", "south_african_folk",
        "afro_traditional", "tribal_folk",

        # --- AMERICAS ---
        "native_american", "andes_folk",
        "latin_folk", "brazilian_folk", "mexican_folk",
        "inca_traditional", "amazon_folk",

        # --- OCEANIA ---
        "australian_aboriginal_folk", "maori_folk",
        "polynesian_folk", "melanesian_folk",

        # --- NORTHERN / SHAMANIC ---
        "tuvan_throat_singing", "sami_joik",
        "mongolian_throat_singing", "arctic_folk",
        "siberian_shamanic",

        # --- ANCIENT / RITUAL / SPIRITUAL ---
        "ancient_chant", "ritual_music", "shamanic_drums",
        "sacred_folk", "tribal_chant", "monastic_chant",

        # --- INSTRUMENT-BASED TAGS ---
        "ethno_flute", "tagelharpa", "hurdy_gurdy",
        "koto_folk", "erhu_folk", "sitar_folk",
        "oud_folk", "duduk_folk", "rebab_folk",
        "pan_flute_folk", "didgeridoo_folk",

        # --- HYBRID ETHNO CORE ---
        "ethno_ambient", "ethno_trance", "ethno_rock",
        "world_fusion", "global_tribal"
    ]

    for genre in world_ethno:
        U.add_music(genre)

    # === LITERATURE GENRES (EPIC / DRAMA / PROSE / NON-FICTION) ===
    literature_genres = [
        # --- EPIC / NARRATIVE ---
        "epic_poem", "epos", "myth_cycle", "legend_cycle",
        "saga", "chivalric_romance", "heroic_epic",
        # --- PROSE FICTION ---
        "novel", "short_story", "novella",
        "microfiction", "flash_fiction",
        # --- DRAMA CORE ---
        "tragedy", "comedy", "tragicomedy",
        "drama", "melodrama", "historical_drama",
        "political_drama", "social_drama",
        # --- PHILOSOPHICAL / SPIRITUAL ---
        "philosophical_novel", "existential_prose",
        "spiritual_prose", "mystical_prose",
        # --- SATIRE / HUMOR ---
        "satire", "parodic_prose", "grotesque_prose",
        "absurd_prose", "fantastic_satire",
        # --- FANTASY / SCI-FI ---
        "high_fantasy", "dark_fantasy", "urban_fantasy",
        "science_fiction", "social_science_fiction",
        "cyberpunk", "post_apocalyptic",
        "alternate_history",
        # --- NON-FICTION / ESSAY ---
        "essay", "philosophical_essay",
        "political_essay", "memoir", "autobiography",
        "biography", "reportage", "documentary_prose",
        # --- FOLK / RELIGIOUS ---
        "fairy_tale", "folk_tale", "parable",
        "religious_text", "scripture_style",
        # --- MODERN HYBRIDS ---
        "magical_realism", "metafiction",
        "postmodern_prose"
    ]

    for g in literature_genres:
        U.add_literature(g)

    # === POETIC & LYRIC FORMS (CLASSIC + MODERN) ===
    lyric_forms = [
        # --- CLASSIC EUROPEAN FORMS ---
        "lyric", "lyrical_poetry", "ode", "elegy",
        "sonnet", "shakespearean_sonnet", "petrarchan_sonnet",
        "epigram", "epitaph", "ballad", "narrative_ballad",
        "hymn", "choral_ode", "madrigal",
        "villanelle", "terza_rima", "triolet",
        "sestina",
        # --- SILLABIC / EASTERN FORMS ---
        "haiku", "tanka", "senryu",
        "rubai", "ghazal",
        # --- MODERN / FREE FORMS ---
        "free_verse", "blank_verse",
        "prose_poem", "concrete_poetry",
        "visual_poetry", "minimalist_poetry",
        # --- PERFORMANCE / SPOKEN ---
        "spoken_word", "slam_poetry",
        "performance_poetry",
        # --- THEMATIC LYRIC ---
        "love_lyric", "intimate_lyric",
        "philosophical_lyric", "civil_lyric",
        "patriotic_lyric", "tragic_lyric",
        "meditative_lyric", "landscape_lyric",
        # --- FOLK & SONG FORMS ---
        "folk_song", "lullaby", "lament_song",
        "ritual_song", "chanson_lyric",
        "author_song", "urban_chanson",
        # --- COMIC / SATIRICAL FORMS ---
        "comic_verse", "light_verse", "limerick",
        "satirical_verse", "parody_verse",
        "burlesque_poem",
        # --- GOTHIC / DARK FORMS (дополнение) ---
        "gothic_ballad", "horror_lyric",
        "dark_romantic_lyric", "shadow_lyric"
    ]

    for f in lyric_forms:
        U.add_lyric_form(f)

    # === CINEMA / THEATRE / SCREENPLAY FORMS ===
    cinematic_forms = [
        # --- CINEMA CORE ---
        "screenplay", "film_script", "scene_script",
        "film_dialogue", "montage_poetry",
        "narrative_voiceover", "cinematic_monologue",
        "cinematic_recitation", "ost_lyric",

        # --- GENRES OF CINEMA ---
        "drama_film", "war_film", "action_film",
        "political_thriller", "psychological_thriller",
        "historical_film", "biographical_film",
        "noir", "neo_noir",
        "fantasy_film", "sci_fi_film",
        "post_apocalyptic_film",
        "documentary_film", "mockumentary",

        # --- THEATRE CORE ---
        "theatre_play", "mono_play", "dialogue_play",
        "classical_theatre", "modern_theatre",
        "absurd_theatre", "ritual_theatre",
        "shadow_theatre",

        # --- DRAMATIC STRUCTURE TAGS ---
        "three_act_structure", "five_act_structure",
        "freytag_pyramid",
        "character_arc", "hero_journey",
        "conflict_axis", "dramatic_turn",

        # --- PERFORMANCE ARTS ---
        "spoken_theatre", "performance_art",
        "sound_performance", "physical_theatre",
        "stage_reading", "dramatic_reading",

        # --- COMEDY / STAGE ---
        "stand_up", "sketch_comedy",
        "stage_comedy", "musical_theatre",
        "broadway_style", "cabaret",

        # --- OPERA / VOCAL THEATRE ---
        "opera", "chamber_opera", "rock_opera",
        "operetta", "cantata", "oratorio",

        # --- HYBRID FORMS ---
        "cinematic_folktale", "epic_stage_poetry",
        "tragic_musical", "dramatic_recitative",
        "spoken_song", "melodic_monologue"
    ]

    for cf in cinematic_forms:
        U.add_stage(cf)

    return U
