# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
"""Light-weight rule-based genre detector for StudioCore v6."""
from __future__ import annotations

from typing import Any, Dict, List

from studiocore.emotion_profile import EmotionVector, EmotionAggregator

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.


class GenreMatrixEngine:
    """Naïve keyword matcher that approximates classical genre families."""

    def __init__(self) -> None:
        self.matrix: Dict[str, List[str]] = {
            "lyric": [
                # классика лирики
                "лирическое",
                "элегия",
                "сонет",
                "ода",
                "эпиграмма",
                "послание",
                "романс",
                "мадригал",
                "гимн",
                # формы
                "баллада",
                "серенада",
                "кантата",
                "песня",
                # фольклор
                "частушка",
                "загадка",
                "былина",
                # поэтика
                "ямб",
                "хорей",
                "дактиль",
                "анапест",
                "амфибрахий",
            ],
            "drama": [
                "драма",
                "комедия",
                "трагедия",
                "мелодрама",
                "трагикомедия",
                "фарс",
                "водевиль",
                "скетч",
                "сценарий",
                "монолог",
                "диалог",
                "акт",
                "пьеса",
                "арка персонажа",
                "конфликт",
            ],
            "epic": [
                "эпос",
                "эпопея",
                "басня",
                "новелла",
                "повесть",
                "роман",
                "быль",
                "сказание",
                "хроника",
                "летопись",
                "миф",
                "легенда",
                "сказка",
                "притча",
            ],
            "philosophical": [
                "притча",
                "эссе",
                "афоризм",
                "манифест",
                "философское рассуждение",
                "парадокс",
            ],
            "pr_communication": [
                "объяснение",
                "осведомляющий",
                "убеждающий",
                "имиджевое сообщение",
                "заявление",
                "байлайнер",
                "кейс-стори",
                "пресс-релиз",
                "комментарий",
            ],
        }

    def detect(self, text: str, emotion_vector: EmotionVector | None = None) -> Dict[str, Any]:
        """Return a weighted map of genres inferred from ``text``."""

        lowered = text.lower()
        keyword_hits: Dict[str, List[str]] = {}
        raw_scores: Dict[str, int] = {}
        for genre, keywords in self.matrix.items():
            hits = [kw for kw in keywords if kw and kw.lower() in lowered]
            keyword_hits[genre] = hits
            raw_scores[genre] = sum(lowered.count(kw.lower()) for kw in keywords)

        total = sum(raw_scores.values()) or 1
        normalized = {genre: score / total for genre, score in raw_scores.items()}
        score = dict(normalized)

        local_emotion = (emotion_vector or EmotionVector(0.0, 0.0, 0.0, 0.0, 0.0, 1.0)).valence

        if local_emotion < -0.4:
            score["tragic"] = score.get("tragic", 0) + 0.2
        elif local_emotion > 0.4:
            score["lyrical"] = score.get("lyrical", 0) + 0.2

        total_adjusted = sum(score.values()) or 1.0
        adjusted = {genre: value / total_adjusted for genre, value in score.items()}
        dominant = max(adjusted, key=adjusted.get) if adjusted else None

        return {
            "scores": adjusted,
            "dominant": dominant,
            "keywords": keyword_hits,
        }

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )


class GenreMatrixExtended(GenreMatrixEngine):
    """Bridge keyword detection with the domain-based genre weights."""

    def evaluate(self, feature_map: Dict[str, float] | None, style_payload: Dict[str, Any] | None = None) -> str | None:
        # Folk mode override
        if style_payload and style_payload.get('_folk_mode') is True:
            return 'folk narrative ballad'
        
        if not feature_map:
            # FIX: базовый fallback — dark_country
            # (на основе анализа реальных текстов о дороге, боли и одиночестве)
            return "dark_country"
        if not any(feature_map.values()):
            # FIX: базовый fallback — dark_country
            return "dark_country"
        from .genre_weights import GenreWeightsEngine

        engine = GenreWeightsEngine()
        # NEW: нормальное разрешение жанров
        return engine.infer_genre(feature_map)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
