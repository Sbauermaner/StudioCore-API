# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
GenreWeightsEngine v3.0 — Multi - Domain

Домены:
- hard       (rock / metal / rap / агрессия)
- electronic (edm / techno / trance / dnb / etc.)
- jazz       (jazz / swing / bebop / nu_jazz / etc.)
- lyrical    (поэтическая / песенная лирика, включая комическую)
- cinematic  (score, epic, trailer)
- comedy     (комедийная музыка / пародии)
- soft       (спокойные жанры: folk / ambient / lofi / etc.)

Работает на feature map из core_v6:
features = {
    "sai", "power", "rhythm_density", "edge",
    "narrative_pressure", "emotional_gradient",
    "hl_minor", "hl_major",
    "cinematic_spread", "vocal_intention",
    "structure_tension", "swing_ratio",
    "jazz_complexity", "electronic_pressure",
    "lyrical_emotion_score", "comedy_factor",
}
"""

from typing import Dict, List, Optional

from .genre_registry import GlobalGenreRegistry
from .genre_universe_loader import load_genre_universe


class GenreWeightsEngine:
    """Многодоменный жанровый классификатор."""

    def __init__(self) -> None:
        self.registry = GlobalGenreRegistry()
        self.universe = load_genre_universe()

        # === 1. Домен → веса признаков (выровнены на основе GENRE_DATABASE.json) ===
        # Статистика из базы данных:
        # - LYRICAL: Major: 30, Minor: 6, Средний BPM: 78.2 (медленный, преимущественно major)
        # - HARD: Major: 11, Minor: 63, Средний BPM: 128.8 (быстрый, преимущественно minor)
        # - ELECTRONIC: Major: 21, Minor: 14, Средний BPM: 134.9 (очень быстрый, смешанный)
        # - JAZZ: Major: 20, Minor: 0, Средний BPM: 116.8 (средний, только major)
        # - CINEMATIC: Major: 1, Minor: 10, Средний BPM: 80.0 (медленный, преимущественно minor)
        # - SOFT: Major: 12, Minor: 1, Средний BPM: 91.9 (средний, преимущественно major)
        raw_weights: Dict[str, Dict[str, float]] = {
            "hard": {
                # Преимущественно minor (63 vs 11), быстрый BPM (128.8)
                "sai": 0.24,
                "power": 0.24,
                "rhythm_density": 0.18,
                "edge": 0.18,
                "hl_minor": 0.16,  # Увеличено: 63 minor vs 11 major
                "structure_tension": 0.12,
            },
            "electronic": {
                # Очень быстрый BPM (134.9), смешанный mode (21 major, 14
                # minor)
                "electronic_pressure": 0.26,
                "rhythm_density": 0.22,
                "power": 0.18,
                "structure_tension": 0.12,
                "hl_minor": 0.11,
                "hl_major": 0.11,  # Сбалансировано: 21 major, 14 minor
                "cinematic_spread": 0.10,
                "poetic_density": -0.14,  # Усилено: электроника не должна быть лирической
                "lyric_form_weight": -0.16,  # Усилено
            },
            "jazz": {
                # Только major (20 vs 0), средний BPM (116.8)
                "jazz_complexity": 0.28,
                "swing_ratio": 0.24,
                "rhythm_density": 0.16,
                "hl_minor": 0.08,  # Снижено: только major
                "hl_major": 0.20,  # Увеличено: только major
                "emotional_gradient": 0.12,
            },
            "lyrical": {
                # Преимущественно major (30 vs 6), медленный BPM (78.2)
                "narrative_pressure": 0.24,
                "lyrical_emotion_score": 0.30,  # Увеличено: главный признак
                "emotional_gradient": 0.18,
                "hl_major": 0.16,  # Увеличено: 30 major vs 6 minor
                "hl_minor": 0.08,  # Снижено
                "vocal_intention": 0.14,
                "poetic_density": 0.20,
                "lyric_form_weight": 0.24,  # Увеличено: важный признак
                "gothic_factor": 0.04,  # Снижено: не основной признак
                "dramatic_weight": 0.08,
            },
            "cinematic": {
                # Преимущественно minor (10 vs 1), медленный BPM (80.0)
                "cinematic_spread": 0.30,
                "power": 0.18,
                "emotional_gradient": 0.20,
                "structure_tension": 0.16,
                "hl_minor": 0.18,  # Увеличено: 10 minor vs 1 major
                "hl_major": 0.06,  # Снижено
                "dramatic_weight": 0.20,
                "darkness_level": 0.14,
            },
            "comedy": {
                "comedy_factor": 0.42,
                "lyrical_emotion_score": 0.22,
                "narrative_pressure": 0.22,
                "hl_major": 0.12,
                "vocal_intention": 0.12,
            },
            "soft": {
                # Преимущественно major (12 vs 1), средний BPM (91.9)
                "narrative_pressure": 0.26,
                "emotional_gradient": 0.24,
                "hl_major": 0.22,  # Увеличено: 12 major vs 1 minor
                "hl_minor": 0.04,  # Снижено
                "power": 0.08,
                "rhythm_density": 0.08,
                "structure_tension": 0.16,
                "poetic_density": 0.14,
            },
        }

        # Нормализация весов: гарантируем, что отрицательные веса зажаты, и
        # опционально нормализуем суммы
        self.domain_feature_weights: Dict[str, Dict[str, float]] = {}
        for domain, weights in raw_weights.items():
            normalized_weights: Dict[str, float] = {}
            # Зажимаем отрицательные веса (они используются для вычитания, но
            # должны быть в разумных пределах)
            for feat, w in weights.items():
                # Отрицательные веса допустимы (для вычитания), но зажимаем их
                # в разумные пределы
                normalized_weights[feat] = (
                    max(-0.5, min(0.5, w)) if w < 0 else max(0.0, min(1.0, w))
                )
            self.domain_feature_weights[domain] = normalized_weights

        # === 2. Порог по доменам (выровнены на основе статистики базы данных) ===
        self.domain_thresholds: Dict[str, float] = {
            "hard": 0.48,  # Увеличен: более строгий отбор для hard жанров
            "electronic": 0.46,  # Слегка увеличен
            "jazz": 0.44,  # Слегка снижен: jazz более специфичен
            "lyrical": 0.52,  # Увеличен: лирика требует более высокого порога
            "cinematic": 0.50,  # Без изменений
            "comedy": 0.38,  # Снижен: комедия более гибкая
            "soft": 0.50,  # Без изменений
        }

        # === 3. Fallback жанр по домену ===
        self.fallback_by_domain: Dict[str, str] = {
            "hard": "rock",
            "electronic": "edm",
            "jazz": "jazz",
            "lyrical": "lyrical_song",
            "cinematic": "cinematic",
            "comedy": "comedy_rock",
            "soft": "folk",
        }

        self.genre_profiles: Dict[str, Dict[str, float]] = getattr(
            self, "genre_profiles", {}
        )
        self.genre_profiles.update(
            {
                "баллада": {
                    "structure_weight": 0.35,
                    "emotion_weight": 0.40,
                    "lexicon_weight": 0.15,
                    "narrative_weight": 0.10,
                },
                "ода": {
                    "structure_weight": 0.30,
                    "emotion_weight": 0.35,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.10,
                },
                "сонет": {
                    "structure_weight": 0.45,
                    "emotion_weight": 0.30,
                    "lexicon_weight": 0.15,
                    "narrative_weight": 0.10,
                },
                "притча": {
                    "structure_weight": 0.25,
                    "emotion_weight": 0.25,
                    "lexicon_weight": 0.20,
                    "narrative_weight": 0.30,
                },
                "реп_текст": {
                    "structure_weight": 0.20,
                    "emotion_weight": 0.40,
                    "lexicon_weight": 0.30,
                    "narrative_weight": 0.10,
                },
                "spoken_word": {
                    "structure_weight": 0.20,
                    "emotion_weight": 0.45,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.10,
                },
                "верлибр": {
                    "structure_weight": 0.15,
                    "emotion_weight": 0.45,
                    "lexicon_weight": 0.25,
                    "narrative_weight": 0.15,
                },
            }
        )

        self._universe_domain_cache: Dict[str, List[str]] = {}

    # ---------- Внутренняя логика ----------

    def _domain_for_genre(self, genre: str) -> Optional[str]:
        for domain, genres in self.registry.domains.items():
            if genre in genres:
                return domain
        return None

    def _genres_for_domain(self, domain: str) -> List[str]:
        """Возвращает жанры для домена из GLOBAL GENRE UNIVERSE."""

        if domain in self._universe_domain_cache:
            return self._universe_domain_cache[domain]

        u = self.universe
        if domain == "electronic":
            base = u.edm_genres + [
                g
                for g in u.music_genres
                if any(
                    k in g
                    for k in (
                        "edm",
                        "techno",
                        "trance",
                        "dnb",
                        "drum_and_bass",
                        "dubstep",
                        "house",
                        "bass",
                        "synth",
                        "wave",
                        "electro",
                        "idm",
                        "break",
                        "rave",
                    )
                )
            ]
        elif domain == "hard":
            base = [
                g
                for g in u.music_genres
                if any(
                    k in g
                    for k in (
                        "rock",
                        "metal",
                        "punk",
                        "core",
                        "rap",
                        "hip_hop",
                        "drill",
                        "trap",
                        "hard",
                    )
                )
            ]
        elif domain == "jazz":
            base = [
                g
                for g in u.music_genres
                if any(k in g for k in ("jazz", "swing", "bop"))
            ]
        elif domain == "lyrical":
            base = u.lyric_forms + u.literature_styles
        elif domain == "comedy":
            base = u.comedy_genres
        elif domain == "cinematic":
            base = [g for g in u.hybrids if "cinematic" in g or "orchestral" in g]
            base += [g for g in u.music_genres if "cinematic" in g or "score" in g]
        elif domain == "soft":
            base = [
                g
                for g in u.music_genres
                if any(
                    k in g
                    for k in (
                        "folk",
                        "ambient",
                        "lofi",
                        "chill",
                        "dream",
                        "soft",
                        "ballad",
                    )
                )
            ]
        else:
            base = []

        normalized = list(dict.fromkeys(base))  # сохраняем порядок
        self._universe_domain_cache[domain] = normalized or self.registry.domains.get(
            domain, []
        )
        return self._universe_domain_cache[domain]

    def score_domains(self, features: Dict[str, float]) -> Dict[str, float]:
        """Сырые веса по доменам."""
        scores: Dict[str, float] = {}
        for domain, weights in self.domain_feature_weights.items():
            s = 0.0
            for feat, w in weights.items():
                # Зажимаем значение признака в [0.0, 1.0] для безопасности
                value = max(0.0, min(1.0, float(features.get(feat, 0.0))))
                # Веса уже нормализованы в __init__, но дополнительная проверка
                # не помешает
                safe_weight = max(-0.5, min(0.5, w)) if w < 0 else max(0.0, min(1.0, w))
                s += value * safe_weight
            scores[domain] = s

        poetic = features.get("poetic_density", 0.0)
        gothic = features.get("gothic_factor", 0.0)
        dramatic = features.get("dramatic_weight", 0.0)
        lyric = features.get("lyric_form_weight", poetic)

        # === ЦВЕТОВАЯ КОРРЕКЦИЯ НА ОСНОВЕ ЭМОЦИЙ ===
        # Получаем цветовую информацию из feature_map (если доступна)
        color_info = features.get("color_profile", {}) or {}
        primary_color = color_info.get("primary_color") or ""
        dominant_emotion = features.get("dominant_emotion", "")

        # Маппинг цветов эмоций к доменам (на основе GENRE_DATABASE.json)
        color_to_domain_boost = {
            # LOVE цвета → lyrical
            "#FF7AA2": ("lyrical", 0.15),  # love
            "#FFC0CB": ("lyrical", 0.12),  # love_soft
            "#FFB6C1": ("lyrical", 0.12),  # love_soft
            "#FFE4E1": ("lyrical", 0.12),  # love_soft
            "#C2185B": ("lyrical", 0.18),  # love_deep
            "#880E4F": ("lyrical", 0.18),  # love_deep
            # PAIN / GOTHIC цвета → hard
            "#DC143C": ("hard", 0.12),  # pain / crimson
            "#2F1B25": ("hard", 0.15),  # pain
            "#0A1F44": ("hard", 0.15),  # pain
            "#2C1A2E": ("hard", 0.18),  # gothic_dark
            "#1B1B2F": ("hard", 0.18),  # gothic_dark
            "#000000": ("hard", 0.20),  # gothic_dark
            "#111111": ("hard", 0.16),  # dark
            "#8B0000": ("hard", 0.18),  # rage_extreme
            # TRUTH цвета → lyrical / cinematic
            "#4B0082_lyrical": ("lyrical", 0.15),  # truth
            "#6C1BB1": ("lyrical", 0.15),  # truth
            "#5B3FA8": ("lyrical", 0.15),  # truth
            "#AEE3FF": ("cinematic", 0.12),  # clear_truth
            "#6DA8C8": ("cinematic", 0.12),  # cold_truth
            # JOY цвета → electronic / pop
            "#FFD93D": ("electronic", 0.15),  # joy
            "#FFD700": ("electronic", 0.18),  # joy_bright
            "#FFFF00": ("electronic", 0.18),  # joy_bright
            "#FFF59D": ("electronic", 0.15),  # joy_bright
            # PEACE цвета → soft
            "#40E0D0": ("soft", 0.15),  # peace
            "#E0F7FA": ("soft", 0.12),  # peace
            "#9FD3FF": ("soft", 0.12),  # calm_flow
            "#8FC1E3": ("soft", 0.10),  # calm
            # EPIC цвета → cinematic
            "#8A2BE2": ("cinematic", 0.20),  # epic
            "#4B0082_cinematic": ("cinematic", 0.18),  # epic (также truth)
            "#FF00FF": ("cinematic", 0.18),  # epic
            # NOSTALGIA цвета → lyrical
            "#D8BFD8": ("lyrical", 0.12),  # nostalgia
            "#E6E6FA": ("lyrical", 0.12),  # nostalgia
            "#C3B1E1": ("lyrical", 0.12),  # nostalgia
            # SORROW цвета → lyrical
            "#3E5C82": ("lyrical", 0.15),  # sorrow
            "#4A6FA5": ("lyrical", 0.12),  # sadness
            "#596E94": ("lyrical", 0.12),  # melancholy
            # WARM цвета → soft / jazz
            "#F5B56B": ("soft", 0.12),  # warm_pulse
            "#F7B267": ("soft", 0.10),  # warmth
        }

        # Применяем цветовую коррекцию
        if primary_color and primary_color in color_to_domain_boost:
            domain, boost = color_to_domain_boost[primary_color]
            scores[domain] = scores.get(domain, 0.0) + boost

        # Также учитываем доминирующую эмоцию по имени
        emotion_to_domain_boost = {
            "love": ("lyrical", 0.20),
            "love_soft": ("lyrical", 0.18),
            "love_deep": ("lyrical", 0.22),
            "pain": ("hard", 0.18),
            "gothic_dark": ("hard", 0.20),
            "dark": ("hard", 0.16),
            "truth": ("lyrical", 0.15),
            "joy": ("electronic", 0.18),
            "joy_bright": ("electronic", 0.20),
            "peace": ("soft", 0.15),
            "calm_flow": ("soft", 0.12),
            "epic": ("cinematic", 0.20),
            "nostalgia": ("lyrical", 0.12),
            "sorrow": ("lyrical", 0.15),
            "sadness": ("lyrical", 0.12),
            "melancholy": ("lyrical", 0.12),
            "rage": ("hard", 0.18),
            "rage_extreme": ("hard", 0.20),
            "anger": ("hard", 0.16),
        }

        if dominant_emotion and dominant_emotion in emotion_to_domain_boost:
            domain, boost = emotion_to_domain_boost[dominant_emotion]
            scores[domain] = scores.get(domain, 0.0) + boost

        # Выровненные веса на основе базы данных:
        # - LYRICAL: преимущественно major, медленный BPM - усилен poetic и lyric
        scores["lyrical"] = (
            scores.get("lyrical", 0.0) + (poetic * 0.22) + (lyric * 0.28)
        )
        # - CINEMATIC: преимущественно minor, медленный BPM - усилен dramatic
        scores["cinematic"] = (
            scores.get("cinematic", 0.0) + (dramatic * 0.18) + (gothic * 0.12)
        )
        # - ELECTRONIC: очень быстрый BPM, не должен быть лирическим - усилено вычитание
        scores["electronic"] = max(
            0.0,
            scores.get("electronic", 0.0)
            - (poetic * 0.28 + gothic * 0.22 + dramatic * 0.12),
        )
        return scores

    def infer_domain(self, features: Dict[str, float]) -> str:
        """Определяет домен, с которым работаем."""
        domain_scores = self.score_domains(features)

        # отфильтровать по порогу
        candidates = {
            d: s
            for d, s in domain_scores.items()
            if s >= self.domain_thresholds.get(d, 0.0)
        }
        if candidates:
            return max(candidates.items(), key=lambda kv: kv[1])[0]

        # fallback: берём домен с максимальной "сырой" энергией
        return max(domain_scores.items(), key=lambda kv: kv[1])[0]

    def infer_genre(self, features: Dict[str, float]) -> str:
        """
        Главный метод:
        - определяет домен
        - внутри домена выбирает конкретный жанр
        - если ничего не набрало порога — fallback
        """
        domain = self.infer_domain(features)
        domain_genres = self._genres_for_domain(domain) or self.registry.domains.get(
            domain, []
        )

        # Если домен пустой — fallback
        if not domain_genres:
            return self.fallback_by_domain.get(domain, "cinematic")

        # Простейший выбор: пока всем жанрам внутри домена
        # отдаём один и тот же доменный скор (можно уточнить позже
        # по дополнительным признакам).
        domain_score = self.score_domains(features)[domain]
        threshold = self.domain_thresholds.get(domain, 0.0)

        if domain_score < threshold:
            # FIX: базовый fallback — dark_country
            # (на основе анализа реальных текстов о дороге, боли и одиночестве)
            return "dark_country"

        # Для начала выбираем "главный" жанр домена — первый.
        # Позже можно сделать тонкую дифференциацию по поджанрам.
        selected = domain_genres[0]

        poetic = features.get("poetic_density", 0.0)
        features.get("lyric_form_weight", poetic)  # Reserved for future use
        features.get("gothic_factor", 0.0)  # Reserved for future use

        # Task 16.2: Removed disabled code block (if False:) to eliminate pass statement
        # Previous code: fallback to "lyrical_song" was disabled via GLOBAL PATCH
        # This block was never executed, so it's been removed for code clarity

        # NEW: нормальное разрешение жанров
        return selected


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
