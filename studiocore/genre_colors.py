# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
"""
Словари цветов для жанров лирики и музыки.

Используется для сравнения цветов в цепочке анализа:
1. Цвет эмоции → Цвет жанра лирики
2. Цвет вокала → Цвет жанра музыки
"""
from __future__ import annotations
from typing import Dict, List, Any

# Цвета для лирических жанров (из GENRE_DATABASE.md)
LYRICAL_GENRE_COLORS: Dict[str, List[str]] = {
    # Основные лирические жанры
    "lyrical_song": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "lyrical_ballad": ["#D8BFD8", "#E6E6FA", "#C3B1E1"],
    "love_lyric": ["#FF7AA2"],
    "gothic_poetry": ["#2C1A2E", "#1B1B2F", "#000000"],
    "confessional_lyric": ["#4B0082", "#6C1BB1", "#5B3FA8"],
    "sensual_love": ["#C2185B", "#880E4F", "#DC143C"],
    "nostalgic_ballad": ["#D8BFD8", "#E6E6FA", "#C3B1E1"],
    "intimate_lyric": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "romantic_lyric": ["#FF7AA2"],
    "philosophical_lyric": ["#4B0082", "#6C1BB1", "#5B3FA8"],
    "tragic_lyric": ["#3E5C82"],
    "meditative_lyric": ["#40E0D0", "#E0F7FA", "#FFFFFF"],
    "author_song": ["#4B0082", "#6C1BB1", "#5B3FA8"],
    "chanson_lyric": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "elegy": ["#3E5C82"],
    "sonnet": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "ode": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "ballad_poem": ["#596E94"],
    "romance_song": ["#FF7AA2"],
    "vocal_lyric": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    
    # Классические формы (fallback к нейтральному)
    "lyric": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "lyrical_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "epigram": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "epitaph": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "hymn": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "madrigal": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "villanelle": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "triolet": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "terza_rima": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "free_verse": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "blank_verse": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "haiku": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "tanka": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "rubai": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "ghazal": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    
    # Современные формы
    "slam_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "spoken_word": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "performance_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "urban_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "minimalist_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "micro_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "instagram_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "digital_lyric": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "prose_poem": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    
    # Фольклорные формы
    "folk_lyric": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "lullaby": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "lament_song": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "ritual_song": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    
    # Авангардные формы
    "concrete_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "visual_poetry": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "absurd_lyric": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "postmodern_lyric": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
}

# Цвета для музыкальных жанров (из GENRE_DATABASE.md)
MUSIC_GENRE_COLORS: Dict[str, List[str]] = {
    # POP
    "pop": ["#FFD700", "#FFFF00", "#FFF59D"],
    "synthpop": ["#FFD700", "#FFFF00", "#FFF59D"],
    "electropop": ["#FF4E4E"],
    "dance_pop": ["#FFD700", "#FFFF00", "#FFF59D"],
    "indie_pop": ["#FFD700", "#FFFF00", "#FFF59D"],
    "art_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "dream_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "hyperpop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "teen_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "baroque_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "city_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "j_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "k_pop": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    
    # ROCK
    "rock": ["#8B0000", "#DC143C", "#FF4500"],
    "hard_rock": ["#8B0000", "#4A0000", "#2A0000"],
    "soft_rock": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "alternative_rock": ["#8B0000", "#DC143C", "#FF4500"],
    "indie_rock": ["#8B0000", "#DC143C", "#FF4500"],
    "punk_rock": ["#8B0000", "#DC143C", "#FF4500"],
    "grunge": ["#2C1A2E", "#1B1B2F", "#000000"],
    "post_rock": ["#2C1A2E", "#1B1B2F", "#000000"],
    "prog_rock": ["#8A2BE2", "#4B0082", "#FF00FF"],
    
    # METAL
    "metal": ["#2C1A2E", "#1B1B2F", "#000000"],
    "heavy_metal": ["#2C1A2E", "#1B1B2F", "#000000"],
    "death_metal": ["#2C1A2E", "#1B1B2F", "#000000"],
    "black_metal": ["#2C1A2E", "#1B1B2F", "#000000"],
    "doom_metal": ["#2C1A2E", "#1B1B2F", "#000000"],
    "thrash_metal": ["#8B0000", "#4A0000", "#2A0000"],
    
    # ELECTRONIC
    "electronic": ["#FFD700", "#FFFF00", "#FFF59D"],
    "edm": ["#FFD700", "#FFFF00", "#FFF59D"],
    "house": ["#FFD700", "#FFFF00", "#FFF59D"],
    "techno": ["#FF4E4E"],
    "trance": ["#40E0D0", "#E0F7FA", "#FFFFFF"],
    "dubstep": ["#2C1A2E", "#1B1B2F", "#000000"],
    "ambient": ["#40E0D0", "#E0F7FA", "#FFFFFF"],
    "downtempo": ["#40E0D0", "#E0F7FA", "#FFFFFF"],
    
    # JAZZ
    "jazz": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "smooth_jazz": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "bebop": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "fusion": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "latin_jazz": ["#FFD700", "#FFFF00", "#FFF59D"],
    
    # CLASSICAL
    "classical": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "orchestral": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "chamber_music": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "symphony": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    "concerto": ["#FFFFFF", "#B0BEC5", "#ECEFF1"],
    
    # CINEMATIC
    "cinematic": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "film_score": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "soundtrack": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "epic": ["#8A2BE2", "#4B0082", "#FF00FF"],
    
    # FOLK
    "folk": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "folk_rock": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "country": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "bluegrass": ["#2E8B57"],
    "celtic": ["#2E8B57"],
    
    # BLUES
    "blues": ["#4A6FA5", "#3E5C82", "#2D3A55"],
    "blues_rock": ["#4A6FA5", "#3E5C82", "#2D3A55"],
    "delta_blues": ["#4A6FA5", "#3E5C82", "#2D3A55"],
    
    # R&B / SOUL
    "r_b": ["#FF7AA2"],
    "soul": ["#FF7AA2"],
    "neo_soul": ["#FF7AA2"],
    "funk": ["#FFD700", "#FFFF00", "#FFF59D"],
    
    # HIP-HOP / RAP
    "hip_hop": ["#6C7E42", "#FF4500", "#FFBF00"],
    "rap": ["#6C7E42", "#FF4500", "#FFBF00"],
    "trap": ["#2C1A2E", "#1B1B2F", "#000000"],
    "drill": ["#2C1A2E", "#1B1B2F", "#000000"],
    
    # REGGAE
    "reggae": ["#2E8B57"],
    "dub": ["#2E8B57"],
    "dancehall": ["#FFD700", "#FFFF00", "#FFF59D"],
    
    # WORLD
    "world_music": ["#FFD700", "#FFFF00", "#FFF59D"],
    "ethnic": ["#FFD700", "#FFFF00", "#FFF59D"],
    "traditional": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    
    # EXPERIMENTAL
    "experimental": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "avant_garde": ["#8A2BE2", "#4B0082", "#FF00FF"],
    "noise": ["#2C1A2E", "#1B1B2F", "#000000"],
    
    # Лирические жанры (также музыкальные)
    "lyrical_song": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "lyrical_ballad": ["#D8BFD8", "#E6E6FA", "#C3B1E1"],
    "gothic_poetry": ["#2C1A2E", "#1B1B2F", "#000000"],
    "confessional_lyric": ["#4B0082", "#6C1BB1", "#5B3FA8"],
    "sensual_love": ["#C2185B", "#880E4F", "#DC143C"],
    "nostalgic_ballad": ["#D8BFD8", "#E6E6FA", "#C3B1E1"],
}


def get_lyrical_genre_colors(genre: str, style_payload: Dict[str, Any] | None = None) -> List[str]:
    """
    Получить цвета для лирического жанра.
    
    Args:
        genre: Название лирического жанра
        style_payload: Опциональный словарь style для проверки флагов
        
    Returns:
        Список HEX цветов для жанра
    """
    # MASTER-PATCH v3.2 — Prevent genre-based color override
    if style_payload and style_payload.get("_color_locked"):
        color_wave = style_payload.get("color_wave")
        if color_wave:
            return color_wave if isinstance(color_wave, list) else [color_wave]
    
    # If low-emotion context — force neutral palette instead of genre palette
    if style_payload and style_payload.get("_neutral_mode"):
        from .config import NEUTRAL_COLOR_WAVE
        return NEUTRAL_COLOR_WAVE

    genre_lower = genre.lower().replace(" ", "_")
    return LYRICAL_GENRE_COLORS.get(genre_lower, ["#FFFFFF", "#B0BEC5", "#ECEFF1"])


def get_music_genre_colors(genre: str, style_payload: Dict[str, Any] | None = None) -> List[str]:
    """
    Получить цвета для музыкального жанра.
    
    Args:
        genre: Название музыкального жанра
        style_payload: Опциональный словарь style для проверки флагов
        
    Returns:
        Список HEX цветов для жанра
    """
    # MASTER-PATCH v3.2 — Prevent genre-based color override
    if style_payload and style_payload.get("_color_locked"):
        color_wave = style_payload.get("color_wave")
        if color_wave:
            return color_wave if isinstance(color_wave, list) else [color_wave]
    
    # If low-emotion context — force neutral palette instead of genre palette
    if style_payload and style_payload.get("_neutral_mode"):
        from .config import NEUTRAL_COLOR_WAVE
        return NEUTRAL_COLOR_WAVE

    genre_lower = genre.lower().replace(" ", "_")
    return MUSIC_GENRE_COLORS.get(genre_lower, ["#FFFFFF", "#B0BEC5", "#ECEFF1"])


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Конвертирует HEX цвет в RGB.
    
    Args:
        hex_color: HEX цвет (например, "#FF0000")
        
    Returns:
        Кортеж (R, G, B)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(color1: str, color2: str) -> float:
    """
    Вычисляет цветовое расстояние между двумя цветами (Euclidean distance в RGB).
    
    Args:
        color1: Первый HEX цвет
        color2: Второй HEX цвет
        
    Returns:
        Расстояние (0.0 = одинаковые, больше = более разные)
    """
    try:
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        return sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)) ** 0.5
    except (ValueError, TypeError):
        return 1000.0  # Большое расстояние для невалидных цветов


def compare_colors(target_color: str, color_list: List[str]) -> float:
    """
    Сравнивает целевой цвет со списком цветов и возвращает минимальное расстояние.
    
    Args:
        target_color: Целевой HEX цвет
        color_list: Список HEX цветов для сравнения
        
    Returns:
        Минимальное расстояние (0.0 = точное совпадение)
    """
    if not color_list:
        return 1000.0
    return min(color_distance(target_color, c) for c in color_list)


def find_matching_lyrical_genre_by_color(target_color: str) -> tuple[str, float]:
    """
    Находит лирический жанр с наиболее похожим цветом.
    
    Args:
        target_color: Целевой HEX цвет
        
    Returns:
        Кортеж (жанр, расстояние)
    """
    # GLOBAL PATCH: отключен fallback на lyrical_song
    best_genre = None  # "lyrical_song"
    best_distance = 1000.0
    
    for genre, colors in LYRICAL_GENRE_COLORS.items():
        distance = compare_colors(target_color, colors)
        if distance < best_distance:
            best_distance = distance
            best_genre = genre
    
    return (best_genre, best_distance)


def find_matching_music_genre_by_color(target_color: str) -> tuple[str, float]:
    """
    Находит музыкальный жанр с наиболее похожим цветом.
    
    Args:
        target_color: Целевой HEX цвет
        
    Returns:
        Кортеж (жанр, расстояние)
    """
    # GLOBAL PATCH: отключен fallback на lyrical_song
    best_genre = None  # "lyrical_song"
    best_distance = 1000.0
    
    for genre, colors in MUSIC_GENRE_COLORS.items():
        distance = compare_colors(target_color, colors)
        if distance < best_distance:
            best_distance = distance
            best_genre = genre
    
    return (best_genre, best_distance)


def aggregate_colors(
    tlp_color: str | None = None,
    emotion_color: str | None = None,
    lyrical_genre_color: str | None = None,
    vocal_colors: List[str] | None = None,
    music_genre_color: str | None = None,
) -> List[str]:
    """
    Агрегирует все цвета из цепочки анализа в общий color_wave.
    
    Args:
        tlp_color: Цвет из TLP
        emotion_color: Цвет эмоции
        lyrical_genre_color: Цвет жанра лирики
        vocal_colors: Цвета вокала (список)
        music_genre_color: Цвет жанра музыки
        
    Returns:
        Список агрегированных цветов
    """
    aggregated = []
    
    # Добавляем цвета в порядке приоритета
    if tlp_color:
        aggregated.append(tlp_color)
    if emotion_color and emotion_color not in aggregated:
        aggregated.append(emotion_color)
    if lyrical_genre_color and lyrical_genre_color not in aggregated:
        aggregated.append(lyrical_genre_color)
    if vocal_colors:
        for vc in vocal_colors:
            if vc and vc not in aggregated:
                aggregated.append(vc)
    if music_genre_color and music_genre_color not in aggregated:
        aggregated.append(music_genre_color)
    
    # Если нет цветов, возвращаем нейтральный
    if not aggregated:
        return ["#FFFFFF", "#B0BEC5", "#ECEFF1"]
    
    # Ограничиваем до 5-7 цветов для читаемости
    return aggregated[:7]


# Маппинг цветов эмоций к BPM и Key (из GENRE_DATABASE.md и EMOTION_COLOR_MAP)
EMOTION_COLOR_TO_BPM: Dict[str, tuple[int, int, int]] = {
    # LOVE цвета → лирические BPM (60-100)
    "#FF7AA2": (70, 100, 85),  # love
    "#FFC0CB": (60, 100, 80),  # love_soft, lyrical_song
    "#FFB6C1": (60, 100, 80),  # love_soft
    "#FFE4E1": (60, 100, 80),  # love_soft
    "#C2185B": (70, 95, 82),   # love_deep, sensual_love
    "#880E4F": (70, 95, 82),   # love_deep
    "#DC143C": (70, 95, 82),   # love_deep
    
    # PAIN/GOTHIC цвета → низкие BPM (50-80)
    "#2C1A2E": (50, 80, 65),   # gothic_poetry
    "#1B1B2F": (50, 80, 65),   # gothic_poetry
    "#000000": (50, 80, 65),   # gothic_poetry
    "#2F1B25": (50, 80, 65),   # pain
    "#0A1F44": (50, 80, 65),   # pain
    "#8B0000": (50, 80, 65),   # rage_extreme
    "#111111": (50, 80, 65),   # dark
    
    # TRUTH цвета → средние BPM (60-90)
    "#4B0082": (60, 90, 75),   # truth, confessional_lyric
    "#6C1BB1": (60, 90, 75),   # truth
    "#5B3FA8": (60, 90, 75),   # truth
    "#AEE3FF": (60, 90, 75),   # clear_truth
    "#6DA8C8": (60, 90, 75),   # cold_truth
    
    # JOY цвета → высокие BPM (100-140)
    "#FFD93D": (100, 140, 120),  # joy, pop
    "#FFD700": (100, 140, 120),  # joy_bright
    "#FFFF00": (100, 140, 120),  # joy_bright
    "#FFF59D": (100, 140, 120),  # joy_bright
    
    # PEACE цвета → средние BPM (50-100)
    "#40E0D0": (50, 100, 80),   # peace, meditative_lyric
    "#E0F7FA": (50, 100, 80),   # peace
    "#FFFFFF": (50, 100, 80),   # peace, neutral
    "#9FD3FF": (50, 100, 80),   # calm_flow
    "#8FC1E3": (50, 100, 80),   # calm
    
    # SORROW цвета → низкие BPM (50-80)
    "#3E5C82": (50, 80, 65),   # sorrow, elegy
    "#4A6FA5": (50, 80, 65),   # sadness
    "#596E94": (50, 80, 65),   # melancholy, ballad_poem
    
    # NOSTALGIA цвета → средние BPM (60-85)
    "#D8BFD8": (60, 85, 72),   # nostalgia, nostalgic_ballad
    "#E6E6FA": (60, 85, 72),   # nostalgia
    "#C3B1E1": (60, 85, 72),   # nostalgia
    
    # EPIC цвета → средние BPM (70-100)
    "#8A2BE2": (70, 100, 85),  # epic, ode
    "#FF00FF": (70, 100, 85),  # epic
}

EMOTION_COLOR_TO_KEY: Dict[str, List[str]] = {
    # LOVE цвета → major ключи
    "#FF7AA2": ["C major", "G major", "A major", "E major", "D major"],  # love_lyric
    "#FFC0CB": ["C major", "G major", "A minor", "D minor", "F major"],  # lyrical_song
    "#FFB6C1": ["C major", "G major", "A minor", "F major"],  # intimate_lyric
    "#FFE4E1": ["C major", "G major", "A minor", "F major"],  # chanson_lyric
    "#C2185B": ["C major", "G major", "D major", "A major", "E major"],  # sensual_love
    "#880E4F": ["C major", "G major", "D major", "A major", "E major"],  # sensual_love
    "#DC143C": ["C major", "G major", "D major", "A major", "E major"],  # sensual_love
    
    # PAIN/GOTHIC цвета → minor ключи
    "#2C1A2E": ["D minor", "A minor", "E minor", "B minor", "G minor"],  # gothic_poetry
    "#1B1B2F": ["D minor", "A minor", "E minor", "B minor", "G minor"],  # gothic_poetry
    "#000000": ["D minor", "A minor", "E minor", "B minor", "G minor"],  # gothic_poetry
    "#2F1B25": ["D minor", "A minor", "E minor", "B minor"],  # pain
    "#0A1F44": ["D minor", "A minor", "E minor", "B minor"],  # pain
    "#8B0000": ["D minor", "A minor", "E minor", "B minor"],  # rage_extreme
    "#111111": ["D minor", "A minor", "E minor", "B minor"],  # dark
    
    # TRUTH цвета → minor ключи (исповедальность)
    "#4B0082": ["C minor", "G minor", "A minor", "F minor", "D minor"],  # confessional_lyric
    "#6C1BB1": ["C minor", "G minor", "A minor", "F minor", "D minor"],  # truth
    "#5B3FA8": ["C minor", "G minor", "A minor", "F minor", "D minor"],  # truth
    "#AEE3FF": ["C minor", "G minor", "A minor", "F minor", "D minor"],  # clear_truth
    "#6DA8C8": ["C minor", "G minor", "A minor", "F minor", "D minor"],  # cold_truth
    
    # JOY цвета → major ключи
    "#FFD93D": ["C major", "G major", "A minor", "F major", "D major"],  # pop
    "#FFD700": ["C major", "G major", "A minor", "F major"],  # synthpop
    "#FFFF00": ["C major", "G major", "A minor", "F major"],  # dance_pop
    "#FFF59D": ["C major", "G major", "A minor", "F major"],  # indie_pop
    
    # PEACE цвета → major/minor ключи
    "#40E0D0": ["C major", "F major", "A minor", "D minor"],  # meditative_lyric
    "#E0F7FA": ["C major", "F major", "A minor", "D minor"],  # peace
    "#FFFFFF": ["C major", "A minor"],  # neutral
    "#9FD3FF": ["C major", "F major", "A minor", "D minor"],  # calm_flow
    "#8FC1E3": ["C major", "F major", "A minor", "D minor"],  # calm
    
    # SORROW цвета → minor ключи
    "#3E5C82": ["D minor", "A minor", "E minor", "G minor"],  # elegy
    "#4A6FA5": ["D minor", "A minor", "E minor", "B minor"],  # sadness
    "#596E94": ["A minor", "D minor", "E minor", "G minor", "C minor"],  # ballad_poem
    
    # NOSTALGIA цвета → minor ключи
    "#D8BFD8": ["A minor", "D minor", "E minor", "G minor", "C minor"],  # nostalgic_ballad
    "#E6E6FA": ["A minor", "D minor", "E minor", "G minor", "C minor"],  # nostalgic_ballad
    "#C3B1E1": ["A minor", "D minor", "E minor", "G minor", "C minor"],  # nostalgic_ballad
    
    # EPIC цвета → major ключи
    "#8A2BE2": ["C major", "G major", "D major", "A major"],  # ode
    "#FF00FF": ["C major", "G major", "D major", "A major"],  # epic
}


def get_bpm_from_emotion_color(emotion_color: str) -> tuple[int, int, int] | None:
    """
    Получить BPM (min, max, default) из цвета эмоции.
    
    Args:
        emotion_color: HEX цвет эмоции
        
    Returns:
        Кортеж (min_bpm, max_bpm, default_bpm) или None
    """
    return EMOTION_COLOR_TO_BPM.get(emotion_color)


def get_key_from_emotion_color(emotion_color: str) -> List[str] | None:
    """
    Получить список предпочтительных ключей из цвета эмоции.
    
    Args:
        emotion_color: HEX цвет эмоции
        
    Returns:
        Список ключей или None
    """
    return EMOTION_COLOR_TO_KEY.get(emotion_color)


def find_matching_music_genre_by_bpm_key(
    target_bpm: int,
    target_key: str,
    genre_bpm_ranges: Dict[str, tuple[int, int, int]] | None = None,
    genre_keys: Dict[str, List[str]] | None = None,
) -> tuple[str, float]:
    """
    Находит музыкальный жанр с наиболее подходящими BPM и Key.
    
    Args:
        target_bpm: Целевой BPM
        target_key: Целевой Key
        genre_bpm_ranges: Словарь жанр → (min_bpm, max_bpm, default_bpm)
        genre_keys: Словарь жанр → список ключей
        
    Returns:
        Кортеж (жанр, оценка совпадения 0.0-1.0)
    """
    if not genre_bpm_ranges:
        genre_bpm_ranges = {}
    if not genre_keys:
        genre_keys = {}
    
    # GLOBAL PATCH: отключен fallback на lyrical_song
    best_genre = None  # "lyrical_song"
    best_score = 0.0
    
    for genre in MUSIC_GENRE_COLORS.keys():
        score = 0.0
        
        # Проверяем BPM
        if genre in genre_bpm_ranges:
            min_bpm, max_bpm, default_bpm = genre_bpm_ranges[genre]
            if min_bpm <= target_bpm <= max_bpm:
                # BPM в диапазоне - полный балл
                score += 0.5
            else:
                # BPM вне диапазона - частичный балл на основе близости
                distance = min(abs(target_bpm - min_bpm), abs(target_bpm - max_bpm), abs(target_bpm - default_bpm))
                score += max(0.0, 0.5 - (distance / 100.0))  # Штраф за расстояние
        
        # Проверяем Key
        if genre in genre_keys:
            genre_key_list = genre_keys[genre]
            if target_key in genre_key_list:
                # Key совпадает - полный балл
                score += 0.5
            else:
                # Key не совпадает - частичный балл на основе похожести
                # Упрощенная проверка: major/minor совпадение
                target_mode = "major" if "major" in target_key.lower() else "minor"
                genre_modes = [k.split()[1].lower() if len(k.split()) > 1 else "major" for k in genre_key_list]
                if target_mode in genre_modes:
                    score += 0.25  # Частичное совпадение по mode
        
        if score > best_score:
            best_score = score
            best_genre = genre
    
    return (best_genre, best_score)

