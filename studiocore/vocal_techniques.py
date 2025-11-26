# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
Расширенный реестр вокальных техник и типов для StudioCore.
Включает академические, популярные, джазовые, этнические, экстремальные и экспериментальные техники.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum


class VocalCategory(Enum):
    """Категории вокальных техник."""
    ACADEMIC = "academic"
    POPULAR = "popular"
    JAZZ = "jazz"
    ETHNIC = "ethnic"
    EXTREME = "extreme"
    EXPERIMENTAL = "experimental"


# =========================
# 1. АКАДЕМИЧЕСКИЙ (КЛАССИЧЕСКИЙ) ВОКАЛ
# =========================
ACADEMIC_VOCALS = {
    "soprano": [
        "soprano",
        "coloratura_soprano",
        "lyric_coloratura_soprano",
        "lyric_soprano",
        "lyric_dramatic_soprano",
        "dramatic_soprano",
        "soprano_sfogato",
    ],
    "mezzo_soprano": [
        "mezzo_soprano",
        "coloratura_mezzo_soprano",
        "lyric_mezzo_soprano",
        "dramatic_mezzo_soprano",
    ],
    "alto": [
        "contralto",
        "countertenor",
    ],
    "tenor": [
        "tenor",
        "lyric_coloratura_tenor",
        "lyric_tenor",
        "lyric_dramatic_tenor",
        "dramatic_tenor",
        "spinto_tenor",
        "heroic_tenor",
        "wagnerian_tenor",
    ],
    "baritone": [
        "baritone",
        "lyric_baritone",
        "lyric_dramatic_baritone",
        "dramatic_baritone",
        "verdi_baritone",
        "baritone_martin",
        "light_baritone",
        "cavalry_baritone",
    ],
    "bass": [
        "bass",
        "high_bass",
        "bass_cantante",
        "lyric_bass",
        "dramatic_bass",
        "bass_profundo",
        "bass_octavist",
        "subcontra_bass",
    ],
}

# =========================
# 2. ПОПУЛЯРНАЯ И ЭСТРАДНАЯ МУЗЫКА
# =========================
POPULAR_VOCALS = [
    "head_voice",
    "chest_voice",
    "mixed_voice",
    "mix",
    "belting",
    "twang",
    "speech_level_singing",
    "whistle_register",
    "falsetto",
    "reinforced_falsetto",
    "pharyngeal_voice",
]

# =========================
# 3. ДЖАЗОВЫЙ И СОУЛ-ВОКАЛ
# =========================
JAZZ_VOCALS = [
    "scat_singing",
    "vocalese",
    "crooning",
    "blue_notes",
    "bends",
    "growl",
    "jazz_growl",
    "vocal_fry_jazz",
]

# =========================
# 4. ЭТНИЧЕСКИЙ И ТРАДИЦИОННЫЙ ВОКАЛ
# =========================
ETHNIC_VOCALS = [
    "throat_singing",
    "sygyyt",
    "kargyraa",
    "khoomei",
    "ezengileer",
    "yodel",
    "cante_hondo",
    "cante_flamenco",
    "sean_nos",
    "celtic_sean_nos",
    "bulgarian_female_choir",
    "pirri",
    "pirri_it",
    "inuit_throat_games",
    "jujjo",
    "pansori",
    "qaawali",
    "raga_sangit",
    "indian_classical",
]

# =========================
# 5. ЭКСТРЕМАЛЬНЫЙ ВОКАЛ (МЕТАЛ, ПАНК, АВАНГАРД)
# =========================
EXTREME_VOCALS = [
    "clean_vocals",
    "false_cord_scream",
    "fry_scream",
    "false_cord_distortion",
    "high_false_cord_scream",
    "true_cord_scream",
    "growl",
    "death_growl",
    "guttural",
    "tunnel_throat_growl",
    "black_metal_shrieking",
    "pig_squeal",
    "bree_bree",
    "goregrind_gurgle",
    "inhale_vocals",
    "tunnel_singing",
    "harsh_vocals",
    "harsh_vocals_twang",
    "harsh_vocals_distortion",
]

# =========================
# 6. ЭКСПЕРИМЕНТАЛЬНЫЕ ТЕХНИКИ
# =========================
EXPERIMENTAL_VOCALS = [
    "overtone_singing",
    "throat_singing_modern",
    "beatboxing",
    "vocal_percussion",
    "polyphonic_overtone_singing",
    "subharmonic_singing",
    "circular_breathing_vocals",
    "multiphonics",
    "glottal_clicks",
    "tongue_clicks",
    "vocal_fry_extremes",
    "extended_vocal_techniques",
]

# =========================
# ОБЪЕДИНЕННЫЙ СПИСОК
# =========================
ALL_VOCAL_TECHNIQUES = {
    VocalCategory.ACADEMIC: ACADEMIC_VOCALS,
    VocalCategory.POPULAR: POPULAR_VOCALS,
    VocalCategory.JAZZ: JAZZ_VOCALS,
    VocalCategory.ETHNIC: ETHNIC_VOCALS,
    VocalCategory.EXTREME: EXTREME_VOCALS,
    VocalCategory.EXPERIMENTAL: EXPERIMENTAL_VOCALS,
}


# =========================
# МАППИНГ ЭМОЦИЙ → ВОКАЛЫ
# =========================
EMOTION_TO_VOCAL_MAP: Dict[str, List[Tuple[str, float]]] = {
    # Joy / Happiness
    "joy": [
        ("lyric_soprano", 0.3),
        ("falsetto", 0.4),
        ("head_voice", 0.3),
        ("bright_tone", 0.2),
    ],
    "joy_bright": [
        ("coloratura_soprano", 0.4),
        ("whistle_register", 0.3),
        ("falsetto", 0.3),
    ],
    "happiness": [
        ("lyric_tenor", 0.3),
        ("mixed_voice", 0.4),
        ("belting", 0.2),
    ],
    "delight": [
        ("soprano", 0.4),
        ("head_voice", 0.3),
        ("bright_tone", 0.3),
    ],
    
    # Calm / Serenity
    "calm": [
        ("lyric_baritone", 0.3),
        ("soft_tone", 0.4),
        ("breathy", 0.3),
    ],
    "serenity": [
        ("contralto", 0.3),
        ("head_voice", 0.4),
        ("ethereal", 0.3),
    ],
    "trust": [
        ("warm_baritone", 0.4),
        ("mixed_voice", 0.3),
        ("resonant", 0.3),
    ],
    
    # Love
    "love": [
        ("lyric_soprano", 0.3),
        ("soft_female_alto", 0.4),
        ("gentle_male_tenor", 0.3),
        ("breathy", 0.2),
    ],
    "love_soft": [
        ("contralto", 0.4),
        ("soft_tone", 0.4),
        ("close_mic", 0.2),
    ],
    "love_deep": [
        ("baritone", 0.4),
        ("chest_voice", 0.4),
        ("warm", 0.2),
    ],
    "infinite_love": [
        ("soprano", 0.3),
        ("tenor", 0.3),
        ("layered_harmonies", 0.4),
    ],
    "healing_love": [
        ("lyric_soprano", 0.4),
        ("ethereal", 0.3),
        ("angelic", 0.3),
    ],
    "maternal_love": [
        ("contralto", 0.5),
        ("warm", 0.3),
        ("soft", 0.2),
    ],
    "radiant_love": [
        ("coloratura_soprano", 0.4),
        ("bright_tone", 0.3),
        ("head_voice", 0.3),
    ],
    "longing_love": [
        ("lyric_tenor", 0.4),
        ("vibrato", 0.3),
        ("emotional", 0.3),
    ],
    "gentle_love": [
        ("mezzo_soprano", 0.4),
        ("soft", 0.4),
        ("breathy", 0.2),
    ],
    "unconditional_love": [
        ("soprano", 0.3),
        ("baritone", 0.3),
        ("choir", 0.4),
    ],
    
    # Sadness
    "sadness": [
        ("baritone", 0.4),
        ("soft", 0.3),
        ("vibrato", 0.3),
    ],
    "disappointment": [
        ("lyric_tenor", 0.4),
        ("soft_cry", 0.3),
        ("emotional", 0.3),
    ],
    "melancholy": [
        ("baritone", 0.5),
        ("soft", 0.3),
        ("warm", 0.2),
    ],
    "sorrow": [
        ("dramatic_baritone", 0.4),
        ("vibrato", 0.4),
        ("emotional", 0.2),
    ],
    "loneliness": [
        ("tenor", 0.4),
        ("soft", 0.4),
        ("distant", 0.2),
    ],
    "grief": [
        ("bass", 0.4),
        ("dramatic", 0.4),
        ("powerful", 0.2),
    ],
    "regret": [
        ("baritone", 0.4),
        ("soft", 0.3),
        ("vibrato", 0.3),
    ],
    "guilt": [
        ("tenor", 0.4),
        ("whisper", 0.3),
        ("soft", 0.3),
    ],
    "shame": [
        ("mezzo_soprano", 0.4),
        ("soft", 0.4),
        ("breathy", 0.2),
    ],
    
    # Pain
    "deep_pain": [
        ("dramatic_baritone", 0.4),
        ("rasp", 0.3),
        ("grit", 0.3),
    ],
    "phantom_pain": [
        ("contralto", 0.4),
        ("ethereal", 0.3),
        ("distant", 0.3),
    ],
    "burning_pain": [
        ("dramatic_tenor", 0.4),
        ("belting", 0.3),
        ("rasp", 0.3),
    ],
    "soul_pain": [
        ("bass", 0.4),
        ("dramatic", 0.4),
        ("powerful", 0.2),
    ],
    "silent_pain": [
        ("mezzo_soprano", 0.4),
        ("whisper", 0.3),
        ("soft", 0.3),
    ],
    "explosive_pain": [
        ("dramatic_soprano", 0.3),
        ("belting", 0.4),
        ("scream", 0.3),
    ],
    "collapsing_pain": [
        ("bass", 0.4),
        ("guttural", 0.3),
        ("low", 0.3),
    ],
    
    # Rage / Anger
    "rage": [
        ("dramatic_tenor", 0.3),
        ("harsh", 0.4),
        ("scream", 0.3),
    ],
    "rage_extreme": [
        ("death_growl", 0.4),
        ("false_cord_scream", 0.4),
        ("harsh_vocals", 0.2),
    ],
    "aggression": [
        ("baritone", 0.3),
        ("grit", 0.4),
        ("rasp", 0.3),
    ],
    "anger": [
        ("dramatic_baritone", 0.4),
        ("belting", 0.3),
        ("rasp", 0.3),
    ],
    "bitterness": [
        ("baritone", 0.4),
        ("rasp", 0.3),
        ("grit", 0.3),
    ],
    "jealousy": [
        ("tenor", 0.4),
        ("intense", 0.4),
        ("emotional", 0.2),
    ],
    "envy": [
        ("mezzo_soprano", 0.4),
        ("sharp", 0.3),
        ("intense", 0.3),
    ],
    "betrayal": [
        ("dramatic_tenor", 0.4),
        ("belting", 0.3),
        ("emotional", 0.3),
    ],
    "resentment": [
        ("baritone", 0.4),
        ("grit", 0.3),
        ("rasp", 0.3),
    ],
    
    # Fear / Anxiety
    "fear": [
        ("soprano", 0.3),
        ("whisper", 0.4),
        ("breathy", 0.3),
    ],
    "anxiety": [
        ("tenor", 0.4),
        ("breathy", 0.3),
        ("trembling", 0.3),
    ],
    "panic": [
        ("soprano", 0.4),
        ("scream", 0.4),
        ("high", 0.2),
    ],
    "disgust": [
        ("baritone", 0.4),
        ("guttural", 0.3),
        ("low", 0.3),
    ],
    "aversion": [
        ("mezzo_soprano", 0.4),
        ("sharp", 0.3),
        ("cold", 0.3),
    ],
    "confusion": [
        ("tenor", 0.4),
        ("breathy", 0.3),
        ("uncertain", 0.3),
    ],
    "frustration": [
        ("baritone", 0.4),
        ("rasp", 0.3),
        ("grit", 0.3),
    ],
    
    # Awe / Wonder
    "awe": [
        ("soprano", 0.3),
        ("ethereal", 0.4),
        ("angelic", 0.3),
    ],
    "wonder": [
        ("coloratura_soprano", 0.4),
        ("head_voice", 0.3),
        ("bright", 0.3),
    ],
    "hope": [
        ("lyric_soprano", 0.4),
        ("airy", 0.3),
        ("bright", 0.3),
    ],
    "relief": [
        ("tenor", 0.4),
        ("soft", 0.3),
        ("warm", 0.3),
    ],
    "admiration": [
        ("soprano", 0.3),
        ("baritone", 0.3),
        ("harmonious", 0.4),
    ],
    
    # Dark / Gothic
    "gothic_dark": [
        ("bass", 0.4),
        ("low_whisper", 0.3),
        ("distant_choir", 0.3),
    ],
    "dark_poetic": [
        ("baritone", 0.4),
        ("soft", 0.3),
        ("whisper", 0.3),
    ],
    "dark_romantic": [
        ("mezzo_soprano", 0.4),
        ("warm", 0.3),
        ("emotional", 0.3),
    ],
    
    # Truth
    "clear_truth": [
        ("tenor", 0.4),
        ("clear", 0.4),
        ("spoken", 0.2),
    ],
    "cold_truth": [
        ("baritone", 0.4),
        ("cold", 0.4),
        ("sharp", 0.2),
    ],
    "sharp_truth": [
        ("tenor", 0.4),
        ("sharp", 0.4),
        ("clear", 0.2),
    ],
    "brutal_honesty": [
        ("bass", 0.4),
        ("rasp", 0.3),
        ("grit", 0.3),
    ],
    "revelation": [
        ("soprano", 0.3),
        ("tenor", 0.3),
        ("powerful", 0.4),
    ],
    "righteous_truth": [
        ("baritone", 0.4),
        ("powerful", 0.3),
        ("clear", 0.3),
    ],
    
    # Resolve / Determination
    "resolve": [
        ("baritone", 0.4),
        ("powerful", 0.4),
        ("clear", 0.2),
    ],
    "determination": [
        ("tenor", 0.4),
        ("belting", 0.3),
        ("powerful", 0.3),
    ],
    
    # Rhythmic / Structural
    "calm_flow": [
        ("tenor", 0.4),
        ("soft", 0.3),
        ("flowing", 0.3),
    ],
    "warm_pulse": [
        ("baritone", 0.4),
        ("warm", 0.4),
        ("resonant", 0.2),
    ],
    "cold_pulse": [
        ("tenor", 0.4),
        ("cold", 0.4),
        ("sharp", 0.2),
    ],
    "frantic": [
        ("soprano", 0.4),
        ("fast", 0.4),
        ("intense", 0.2),
    ],
    "trembling": [
        ("tenor", 0.4),
        ("trembling", 0.4),
        ("breathy", 0.2),
    ],
    "escalating": [
        ("tenor", 0.3),
        ("baritone", 0.3),
        ("building", 0.4),
    ],
    "descending": [
        ("baritone", 0.4),
        ("bass", 0.3),
        ("falling", 0.3),
    ],
    "pressure": [
        ("baritone", 0.4),
        ("intense", 0.4),
        ("powerful", 0.2),
    ],
    "static_tension": [
        ("tenor", 0.4),
        ("held", 0.3),
        ("tension", 0.3),
    ],
    "breathless": [
        ("soprano", 0.4),
        ("fast", 0.4),
        ("intense", 0.2),
    ],
    
    # Core States
    "peace": [
        ("lyric_soprano", 0.3),
        ("soft", 0.4),
        ("ethereal", 0.3),
    ],
    "neutral": [
        ("tenor", 0.3),
        ("baritone", 0.3),
        ("balanced", 0.4),
    ],
    
    # Epic
    "epic": [
        ("soprano", 0.3),
        ("tenor", 0.3),
        ("layered_choir", 0.4),
    ],
}


def get_vocal_for_emotion(emotion: str, intensity: float = 1.0) -> List[str]:
    """
    Получить список вокальных техник для эмоции с учетом интенсивности.
    
    Args:
        emotion: Название эмоции
        intensity: Интенсивность эмоции (0.0-1.0)
    
    Returns:
        Список вокальных техник, отсортированный по релевантности
    """
    # Маппинг для новых комбинированных эмоций
    emotion_mapping = {
        "sensual_nostalgia": "love_soft",  # Мягкий, нежный вокал
        "sensual_love": "love_soft",  # Мягкий, нежный вокал
        "nostalgic_melancholy": "sadness",  # Меланхоличный вокал
        "love_tender": "love_soft",  # Нежный вокал
        "confessional": "clear_truth",  # Чистый, исповедальный вокал
        "confessional_nostalgia": "sadness",  # Меланхоличный исповедальный вокал
    }
    
    # Используем маппинг если есть
    mapped_emotion = emotion_mapping.get(emotion, emotion)
    
    techniques = EMOTION_TO_VOCAL_MAP.get(mapped_emotion, [])
    if not techniques:
        # Fallback для неизвестных эмоций
        return ["tenor", "baritone", "balanced"]
    
    # Фильтруем по интенсивности и сортируем
    filtered = [
        (tech, weight * intensity)
        for tech, weight in techniques
        if weight * intensity >= 0.15  # Минимальный порог
    ]
    
    # Сортируем по весу (убывание)
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    # Возвращаем только техники (без весов)
    return [tech for tech, _ in filtered[:3]]  # Топ-3 техники


def get_vocal_for_section(
    section_emotion: str,
    section_intensity: float,
    global_emotion: Optional[str] = None,
    genre: Optional[str] = None,
    section_name: Optional[str] = None,
) -> str:
    """
    Получить вокальную технику для секции на основе эмоций и жанра.
    
    Args:
        section_emotion: Доминирующая эмоция секции
        section_intensity: Интенсивность эмоции в секции
        global_emotion: Глобальная эмоция (опционально)
        genre: Жанр (опционально)
        section_name: Название секции (Verse, Chorus, Bridge, Outro и т.д.) для вариативности
    
    Returns:
        Строка с описанием вокальной техники для секции
    """
    techniques = get_vocal_for_emotion(section_emotion, section_intensity)
    
    # Вариативность по типу секции
    if section_name:
        section_lower = section_name.lower()
        if "verse" in section_lower:
            # Verse: более интимный, мягкий вокал
            if "tenor" in techniques[0] or "baritone" in techniques[0]:
                techniques = ["soft_tenor", "intimate_baritone", "breathy"] + techniques
        elif "chorus" in section_lower:
            # Chorus: более расширенный, эмоциональный вокал
            if "tenor" in techniques[0]:
                techniques = ["expanded_tenor", "belting", "emotional"] + techniques
            elif "final" in section_lower:
                # Final Chorus: эмоциональный пик
                techniques = ["powerful_tenor", "belting", "emotional_peak"] + techniques
        elif "bridge" in section_lower:
            # Bridge: дыхательный, напряженный вокал
            techniques = ["breathy", "tension", "emotional"] + techniques
        elif "outro" in section_lower:
            # Outro: шёпот, низкая энергия
            techniques = ["whisper", "soft", "low_energy"] + techniques
    
    # Жанровые модификации
    if genre:
        genre_lower = genre.lower()
        if "metal" in genre_lower or "rock" in genre_lower:
            if "soprano" in techniques[0] or "tenor" in techniques[0]:
                techniques = ["belting", "rasp", "grit"] + techniques
        elif "jazz" in genre_lower:
            techniques = ["scat_singing", "crooning"] + techniques
        elif "classical" in genre_lower or "orchestral" in genre_lower:
            # Приоритет академическим техникам
            academic_techs = [t for t in techniques if any(cat in t for cat in ["soprano", "tenor", "baritone", "bass", "alto"])]
            if academic_techs:
                techniques = academic_techs + techniques
    
    # Выбираем основную технику
    primary = techniques[0] if techniques else "tenor"
    
    # Формируем описание
    if len(techniques) > 1:
        return f"{primary} with {', '.join(techniques[1:3])}"
    return primary


def get_all_vocal_techniques() -> List[str]:
    """Получить полный список всех доступных вокальных техник."""
    all_techs = []
    
    # Академические
    for category, techs in ACADEMIC_VOCALS.items():
        all_techs.extend(techs)
    
    # Популярные
    all_techs.extend(POPULAR_VOCALS)
    
    # Джазовые
    all_techs.extend(JAZZ_VOCALS)
    
    # Этнические
    all_techs.extend(ETHNIC_VOCALS)
    
    # Экстремальные
    all_techs.extend(EXTREME_VOCALS)
    
    # Экспериментальные
    all_techs.extend(EXPERIMENTAL_VOCALS)
    
    return sorted(list(set(all_techs)))


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

