# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


KEY_COLOR_PALETTE: Dict[str, str] = {
    "red": "#FF0000",
    "orange-red": "#FF4500",
    "golden": "#DAA520",
    "amber": "#FFBF00",
    "yellow": "#FFFF00",
    "green": "#2E8B57",
    "turquoise": "#40E0D0",
    "blue": "#1E90FF",
    "indigo": "#4B0082",
    "violet": "#8A2BE2",
    "magenta": "#FF00FF",
    "crimson": "#DC143C",
    "white": "#FFFFFF",
}


EMOTION_COLOR_MAP: Dict[str, List[str]] = {
    # --- Rhythmic/Structural States (New) ---
    "calm_flow": ["#9FD3FF"],
    "warm_pulse": ["#F5B56B"],
    "cold_pulse": ["#4D7EA8"],
    "frantic": ["#FF4E4E"],
    "trembling": ["#A8A6FF"],
    "escalating": ["#E06C75"],
    "descending": ["#7A6D6F"],
    "pressure": ["#332F2F"],
    "static_tension": ["#645A5A"],
    "breathless": ["#8BB9E3"],
    # --- Deep Pain Spectrum (New) ---
    "deep_pain": ["#2A0000"],
    "phantom_pain": ["#3A1A1A"],
    "burning_pain": ["#660000"],
    "soul_pain": ["#400021"],
    "silent_pain": ["#2E1A27"],
    "explosive_pain": ["#7F0000"],
    "collapsing_pain": ["#1A0000"],
    # --- Deep Love Spectrum (New) ---
    "infinite_love": ["#FF6FA8"],
    "healing_love": ["#FF9CCB"],
    "maternal_love": ["#FFB7DA"],
    "radiant_love": ["#FFD1E8"],
    "longing_love": ["#E88AB7"],
    "gentle_love": ["#FFCEDA"],
    "unconditional_love": ["#FFA3C4"],
    # --- Deep Truth Spectrum (New) ---
    "clear_truth": ["#AEE3FF"],
    "cold_truth": ["#6DA8C8"],
    "sharp_truth": ["#3A5E73"],
    "brutal_honesty": ["#1A3F56"],
    "revelation": ["#8FE1FF"],
    "righteous_truth": ["#0099CC"],
    # --- Core Emotions (Overridden with new values) ---
    "truth": [KEY_COLOR_PALETTE["indigo"], "#6C1BB1", "#5B3FA8"],
    "love": ["#FF7AA2"],
    "pain": [KEY_COLOR_PALETTE["crimson"], "#2F1B25", "#0A1F44"],
    "joy": ["#FFD93D"],
    "sadness": ["#5A6A86"],
    "anger": ["#D62828"],
    "fear": ["#4B3F72"],
    # --- Detailed Negative Emotions (New/Overridden) ---
    "sorrow": ["#3E5C82"],
    "loneliness": ["#475674"],
    "grief": ["#2D3A55"],
    "regret": ["#55637A"],
    "guilt": ["#4C4F6B"],
    "shame": ["#735D78"],
    "anxiety": ["#8CA6DB"],
    "panic": ["#001A33"],
    "disgust": ["#4E6D39"],
    "aversion": ["#5E7D4C"],
    "confusion": ["#8EA3B7"],
    "frustration": ["#C75146"],
    "rage": ["#990000"],
    "bitterness": ["#733131"],
    "jealousy": ["#629A49"],
    "envy": ["#6BAD49"],
    "betrayal": ["#764C6D"],
    "resentment": ["#923D3D"],
    "resolve": ["#DDB27F"],
    "determination": ["#C78E4A"],
    # --- Detailed Positive Emotions (New/Overridden) ---
    "happiness": ["#FFE97F"],
    "delight": ["#FFF2A6"],
    "serenity": ["#A8D8FF"],
    "calm": ["#8FC1E3"],
    "hope": ["#A9F04E"],
    "trust": ["#8FE6C2"],
    "affection": ["#FF9EBF"],
    "compassion": ["#FFADC7"],
    "warmth": ["#F7B267"],
    "admiration": ["#DDB3F8"],
    "relief": ["#B8E986"],
    # --- Base/Cluster Emotions (Retained original/V6.4) ---
    "peace": ["#8FD3FE"],
    "epic": [KEY_COLOR_PALETTE["violet"], "#4B0082", KEY_COLOR_PALETTE["magenta"]],
    "awe": [KEY_COLOR_PALETTE["turquoise"], "#7DF9FF", "#C0C0C0"],
    "neutral": [KEY_COLOR_PALETTE["white"], "#B0BEC5", "#ECEFF1"],
    "nostalgia": ["#FFD1A1"],
    "irony": ["#800080", KEY_COLOR_PALETTE["magenta"], "#C71585"],
    "conflict": [KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["amber"], KEY_COLOR_PALETTE["crimson"]],
    "joy_bright": ["#FFD700", KEY_COLOR_PALETTE["yellow"], "#FFF59D"],
    "love_soft": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "love_deep": ["#C2185B", "#880E4F", KEY_COLOR_PALETTE["crimson"]],
    "disappointment": ["#708090", "#A9A9A9", "#6C6C6C"],
    "melancholy": ["#5A6A86"],
    "rage_extreme": ["#8B0000", "#4A0000", "#2A0000"],
    "aggression": ["#8B0000", KEY_COLOR_PALETTE["crimson"], KEY_COLOR_PALETTE["orange-red"]],
    "wonder": ["#7DF9FF", KEY_COLOR_PALETTE["turquoise"], "#E0FFFF"],
    "gothic_dark": ["#2C1A2E", "#1B1B2F", "#000000"],
    "dark_poetic": ["#2C1A2E", "#3F2A44", "#1B1B2F"],
    "dark_romantic": ["#4A192C", "#2C0F1A", "#6A1B3F"],
    "hiphop_conflict": ["#6C7E42", KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["amber"]],
    "street_power": ["#8B4513", "#FF8C00", KEY_COLOR_PALETTE["amber"]],
    "dark": ["#111111", "#2F2F2F", "#0B0B0B"],
    "melancholic": ["#4B5D67", "#243447", "#1A2633"],
    "epic_cluster": [KEY_COLOR_PALETTE["violet"], "#4B0082", KEY_COLOR_PALETTE["magenta"]],
    "hope_cluster": ["#9ACD32", KEY_COLOR_PALETTE["turquoise"], "#C5E1A5"],
    "neutral_cluster": ["#B0BEC5", "#CFD8DC", "#ECEFF1"],
}


def _normalize_emotion_key(name: str | None) -> str:
    return (name or "").strip().lower()


def get_emotion_colors(emotion: str, *, default: List[str] | None = None) -> List[str]:
    key = _normalize_emotion_key(emotion)
    if key in EMOTION_COLOR_MAP:
        return EMOTION_COLOR_MAP[key]
    return default or EMOTION_COLOR_MAP["neutral"]


@dataclass
class ColorResolution:
    colors: List[str]
    source: str  # "tlp_rules" / "emotion_map" / "fallback"


class ColorEngineAdapter:
    """
    Лёгкая адаптация ColorEngine к результату анализа:
    — читает result["tlp"] и result["emotion"]
    — создает color_wave: список hex-цветов
    — не вмешивается в внутреннюю работу ColorEngine

    Это прослойка: безопасна, не хранит состояния, не ломает пайплайн.
    """

    def resolve_color_wave(self, result: Dict[str, Any]) -> ColorResolution:
        # MASTER-PATCH v3.1 — Neutral Mode Color Override
        # If style already locked color (road narrative, neutral mode), freeze output
        style_payload = result.get("style", {})
        if style_payload and style_payload.get("_color_locked"):
            color_wave = style_payload.get("color_wave")
            if color_wave:
                return ColorResolution(colors=color_wave, source="locked_override")
        
        from .config import (
            NEUTRAL_COLOR_WAVE,
            LOW_EMOTION_TLP_PAIN_MAX,
            LOW_EMOTION_TLP_TRUTH_MIN,
        )
        
        tlp = result.get("tlp", {}) or {}
        emo = result.get("emotion", {}) or {}
        
        # Безопасное извлечение профиля эмоций
        if isinstance(emo, dict) and "profile" in emo:
            emo_profile = emo.get("profile", {})
        else:
            emo_profile = emo if isinstance(emo, dict) else {}
        
        # MASTER-PATCH v3.1: проверка на low-emotion по TLP (приоритет)
        pain = float(tlp.get("pain", 0.0))
        truth = float(tlp.get("truth", 0.0))
        if pain <= LOW_EMOTION_TLP_PAIN_MAX and truth >= LOW_EMOTION_TLP_TRUTH_MIN:
            # Проверяем также по эмоциям
            if self._is_low_emotion_profile(emo_profile):
                # Устанавливаем нейтральный цвет и блокируем его
                if style_payload:
                    style_payload["color_wave"] = NEUTRAL_COLOR_WAVE
                    style_payload["_color_locked"] = True
                return ColorResolution(colors=NEUTRAL_COLOR_WAVE, source="neutral_profile")
        
        scores: Dict[str, float] = {
            "truth": float(tlp.get("truth", 0.0)),
            "love": float(tlp.get("love", 0.0)),
            "pain": float(tlp.get("pain", 0.0)),
        }

        for name, value in emo_profile.items():
            try:
                scores[_normalize_emotion_key(name)] = float(value)
            except (TypeError, ValueError):
                continue

        filtered_scores = {k: v for k, v in scores.items() if v is not None}
        if not filtered_scores:
            # NEW: строим wave на основе эмоций
            colors = self._build_from_emotions(emo_profile)
            return ColorResolution(colors=colors, source="emotion_based_fallback")

        # MASTER-PATCH v3: если TLP указывает на low-emotion, но filtered_scores не пуст,
        # все равно проверяем эмоции и применяем нейтральный цвет
        if pain <= LOW_EMOTION_TLP_PAIN_MAX and truth >= LOW_EMOTION_TLP_TRUTH_MIN:
            if self._is_low_emotion_profile(emo_profile):
                return ColorResolution(colors=NEUTRAL_COLOR_WAVE, source="neutral_profile")

        dominant = max(filtered_scores, key=filtered_scores.get)
        colors = get_emotion_colors(dominant)
        
        # Folk mode color override
        if style_payload.get('_folk_mode') is True:
            return ColorResolution(colors=['#6B4F2A', '#C89D66'], source="folk_mode")
        
        # MASTER-PATCH v6.0: ColorEngine v3 для гибридных жанров
        genre_label = style_payload.get("genre", "")
        if genre_label and "hybrid" in str(genre_label).lower():
            hybrid_colors = self._resolve_hybrid_colors(genre_label, colors, style_payload)
            if hybrid_colors:
                return ColorResolution(colors=hybrid_colors, source="hybrid_genre")
        
        # нормальная ветка
        return ColorResolution(
            colors=colors,
            source="emotion_map",
        )
    
    def _resolve_hybrid_colors(self, genre_label: str, base_colors: List[str], style_payload: Dict[str, Any]) -> List[str] | None:
        """
        MASTER-PATCH v6.0: ColorEngine v3 — разрешение гибридных цветов.
        
        Смешивает базовые палитры для каждого домена в гибридном жанре.
        
        Args:
            genre_label: Жанровый лейбл (может быть гибридным)
            base_colors: Базовые цвета
            style_payload: Style payload с флагами
            
        Returns:
            Смешанные цвета или None
        """
        # Проверяем флаги (НЕ нарушаем флаги из v3.4)
        if style_payload.get("_color_locked"):
            return None  # Не меняем заблокированный цвет
        
        if style_payload.get("_neutral_mode"):
            from .config import NEUTRAL_COLOR_WAVE
            return NEUTRAL_COLOR_WAVE  # Используем нейтральный цвет
        
        # Парсим genre_label для извлечения доменов
        genre_lower = str(genre_label).lower()
        domains = []
        
        if "folk" in genre_lower or "ballad" in genre_lower:
            domains.append("folk")
        if "cinematic" in genre_lower or "orchestral" in genre_lower:
            domains.append("cinematic")
        if "hiphop" in genre_lower or "rap" in genre_lower:
            domains.append("hiphop")
        if "edm" in genre_lower or "electronic" in genre_lower:
            domains.append("electronic")
        if "dark" in genre_lower or "country" in genre_lower:
            domains.append("dark_country")
        
        if len(domains) < 2:
            # Не гибрид или только один домен
            return None
        
        # Базовые палитры для каждого домена
        domain_palettes = {
            "folk": ["#6B4F2A", "#C89D66", "#8B7355"],
            "cinematic": ["#4B0082", "#6A5ACD", "#9370DB"],
            "hiphop": ["#8B4513", "#FF8C00", "#FFA500"],
            "electronic": ["#00CED1", "#20B2AA", "#48D1CC"],
            "dark_country": ["#1F2A3A", "#C58B3A", "#3E5C82"]
        }
        
        # Собираем цвета из всех доменов
        all_colors = []
        for domain in domains:
            if domain in domain_palettes:
                all_colors.extend(domain_palettes[domain])
        
        if not all_colors:
            return None
        
        # Смешиваем: берем первый цвет из каждого домена и усредняем остальные
        # Упрощенный подход: берем первые 2 цвета из разных доменов
        unique_colors = []
        seen = set()
        for color in all_colors:
            if color not in seen:
                unique_colors.append(color)
                seen.add(color)
                if len(unique_colors) >= 2:
                    break
        
        # Если получилось меньше 2 цветов, дополняем базовыми
        while len(unique_colors) < 2:
            if base_colors:
                for bc in base_colors:
                    if bc not in unique_colors:
                        unique_colors.append(bc)
                        break
            else:
                unique_colors.append("#888888")  # Fallback
        
        return unique_colors[:2]  # Возвращаем максимум 2 цвета
    
    def _is_low_emotion_profile(self, emotions: dict) -> bool:
        """
        Примитивный детектор нейтрального профиля по эмоциям.
        Используем, если нет прямого доступа к TLP.
        """
        if not emotions:
            return True
        
        sadness = emotions.get("sadness", 0.0)
        sorrow = emotions.get("sorrow", 0.0)
        anger = emotions.get("anger", 0.0)
        fear = emotions.get("fear", 0.0)
        peace = emotions.get("peace", 0.0)
        joy = emotions.get("joy", 0.0)
        
        # Низкая боль/негатив при ощутимом мире → нейтральный/спокойный профиль
        negative = sadness + sorrow + anger + fear
        
        if negative <= 0.15 and peace >= 0.4 and joy <= 0.4:
            return True
        
        return False

    def _build_from_emotions(self, emotions: Dict[str, Any]) -> List[str]:
        """Строит color wave на основе эмоций, если нет TLP данных."""
        # MASTER-PATCH v3.1:
        # Apply neutral color wave if detected low-emotion profile
        if self._is_low_emotion_profile(emotions):
            from .config import NEUTRAL_COLOR_WAVE
            return NEUTRAL_COLOR_WAVE
        
        from .config import NEUTRAL_COLOR_WAVE
        
        if not emotions:
            return get_emotion_colors("neutral")
        
        # MASTER-PATCH v2: Road narrative color wave
        sorrow = float(emotions.get("sorrow", 0.0))
        determination = float(emotions.get("determination", 0.0))
        sensual = float(emotions.get("sensual", 0.0))
        
        # Road narrative: глубокий синий + выгоревший янтарь
        if sorrow > 0.4 and determination > 0.2 and sensual < 0.3:
            return ["#1F2A3A", "#C58B3A"]
        
        # Находим доминирующую эмоцию
        numeric_emotions = {k: float(v) for k, v in emotions.items() if isinstance(v, (int, float))}
        if not numeric_emotions:
            return get_emotion_colors("neutral")
        
        dominant = max(numeric_emotions, key=numeric_emotions.get)
        return get_emotion_colors(dominant)

    def resolve(self, style: Dict[str, Any]) -> List[str] | None:
        """
        HARD LOCK: if style contains road narrative palette, do not override.
        Returns color_wave from style if _color_locked is True, otherwise None.
        """
        # HARD LOCK: if style contains road narrative palette, do not override
        if style.get("_color_locked"):
            return style.get("color_wave")
        
        # existing logic...
        return None


# ============================================================================
# Color_Formula Functions (StudioCore Formulas Implementation)
# ============================================================================

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Конвертирует HEX цвет в RGB."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Конвертирует RGB в HEX цвет."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def blend(color1: str, color2: str, factor: float) -> str:
    """
    Смешивает два цвета по формуле: result = color1 * (1 - factor) + color2 * factor
    
    Args:
        color1: Первый HEX цвет
        color2: Второй HEX цвет
        factor: Коэффициент смешивания (0.0 = color1, 1.0 = color2)
        
    Returns:
        Смешанный HEX цвет
    """
    factor = max(0.0, min(1.0, factor))
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    rgb_result = tuple(int(r1 * (1 - factor) + r2 * factor) for r1, r2 in zip(rgb1, rgb2))
    return rgb_to_hex(rgb_result)


def gradient(colors: List[str], weights: List[float] | None = None) -> List[str]:
    """
    Создает градиент из списка цветов с весами.
    
    Args:
        colors: Список HEX цветов
        weights: Список весов (если None, равномерное распределение)
        
    Returns:
        Список цветов градиента
    """
    if not colors:
        return []
    if len(colors) == 1:
        return colors
    
    if weights is None:
        weights = [1.0 / len(colors)] * len(colors)
    
    # Нормализуем веса
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0 / len(colors)] * len(colors)
    else:
        weights = [w / total_weight for w in weights]
    
    # Создаем градиент путем смешивания соседних цветов
    gradient_colors = []
    for i in range(len(colors) - 1):
        gradient_colors.append(colors[i])
        # Смешиваем с следующим цветом
        if i < len(colors) - 1:
            mixed = blend(colors[i], colors[i + 1], weights[i + 1] if i + 1 < len(weights) else 0.5)
            gradient_colors.append(mixed)
    
    gradient_colors.append(colors[-1])
    return gradient_colors


def soften(color: str, factor: float) -> str:
    """
    Смягчает цвет, смешивая с белым.
    
    Args:
        color: HEX цвет
        factor: Коэффициент смягчения (0.0 = без изменений, 1.0 = белый)
        
    Returns:
        Смягченный HEX цвет
    """
    return blend(color, "#FFFFFF", factor)


def warm_shift(color: str, factor: float) -> str:
    """
    Делает цвет теплее, добавляя оранжевый оттенок.
    
    Args:
        color: HEX цвет
        factor: Коэффициент теплого сдвига (0.0 = без изменений, 1.0 = оранжевый)
        
    Returns:
        Теплый HEX цвет
    """
    warm_color = "#FFA500"  # Orange
    return blend(color, warm_color, factor)


def saturate(color: str, factor: float) -> str:
    """
    Увеличивает насыщенность цвета.
    
    Args:
        color: HEX цвет
        factor: Коэффициент насыщения (0.0 = без изменений, 1.0 = максимальная насыщенность)
        
    Returns:
        Насыщенный HEX цвет
    """
    rgb = hex_to_rgb(color)
    # Увеличиваем насыщенность, отдаляя от серого
    gray = sum(rgb) // 3
    rgb_result = tuple(
        int(c + (c - gray) * factor) if c != gray else c
        for c in rgb
    )
    # Ограничиваем значения
    rgb_result = tuple(max(0, min(255, c)) for c in rgb_result)
    return rgb_to_hex(rgb_result)


def darken(color: str, factor: float) -> str:
    """
    Затемняет цвет.
    
    Args:
        color: HEX цвет
        factor: Коэффициент затемнения (0.0 = без изменений, 1.0 = черный)
        
    Returns:
        Затемненный HEX цвет
    """
    return blend(color, "#000000", factor)


def fade(color: str, factor: float) -> str:
    """
    Затухает цвет, смешивая с прозрачным (белым для HEX).
    
    Args:
        color: HEX цвет
        factor: Коэффициент затухания (0.0 = без изменений, 1.0 = белый)
        
    Returns:
        Затухающий HEX цвет
    """
    return blend(color, "#FFFFFF", factor)


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
