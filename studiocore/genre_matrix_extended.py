"""Light-weight rule-based genre detector for StudioCore v6."""
from __future__ import annotations

from typing import Any, Dict, List

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

    def detect(self, text: str) -> Dict[str, Any]:
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
        dominant = max(raw_scores, key=raw_scores.get) if raw_scores else None

        return {
            "scores": normalized,
            "dominant": dominant,
            "keywords": keyword_hits,
        }


class GenreMatrixExtended(GenreMatrixEngine):
    """Bridge keyword detection with the domain-based genre weights."""

    def evaluate(self, feature_map: Dict[str, float] | None) -> str | None:
        if not feature_map:
            return None
        if not any(feature_map.values()):
            return None
        from .genre_weights import GenreWeightsEngine

        engine = GenreWeightsEngine()
        return engine.infer_genre(feature_map)
