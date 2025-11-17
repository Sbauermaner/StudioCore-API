# -*- coding: utf-8 -*-
"""GenreWeightsEngine v1.1 — весовая классификация жанров."""
from __future__ import annotations

from typing import Any, Dict, List
from .emotion_dictionary_extended import EmotionLexiconExtended


class GenreWeightsEngine:
    """Approximate poetic/dramatic genre classifier based on structural cues."""

    def __init__(self) -> None:

        # Весовые профили жанров
        self.genre_profiles: Dict[str, Dict[str, float]] = {
            "лирика": {
                "structure_weight": 0.40,
                "emotion_weight": 0.35,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.10,
            },
            "элегия": {
                "structure_weight": 0.30,
                "emotion_weight": 0.50,
                "lexicon_weight": 0.10,
                "narrative_weight": 0.10,
            },
            "романс": {
                "structure_weight": 0.35,
                "emotion_weight": 0.45,
                "lexicon_weight": 0.10,
                "narrative_weight": 0.10,
            },
            "ода": {
                "structure_weight": 0.30,
                "emotion_weight": 0.30,
                "lexicon_weight": 0.25,
                "narrative_weight": 0.15,
            },
            "поэма": {
                "structure_weight": 0.25,
                "emotion_weight": 0.20,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.40,
            },
            "притча": {
                "structure_weight": 0.20,
                "emotion_weight": 0.20,
                "lexicon_weight": 0.20,
                "narrative_weight": 0.40,
            },
            "басня": {
                "structure_weight": 0.20,
                "emotion_weight": 0.15,
                "lexicon_weight": 0.35,
                "narrative_weight": 0.30,
            },
            "драма": {
                "structure_weight": 0.10,
                "emotion_weight": 0.40,
                "lexicon_weight": 0.20,
                "narrative_weight": 0.30,
            },
            "трагедия": {
                "structure_weight": 0.15,
                "emotion_weight": 0.45,
                "lexicon_weight": 0.15,
                "narrative_weight": 0.25,
            },
            "комедия": {
                "structure_weight": 0.15,
                "emotion_weight": 0.30,
                "lexicon_weight": 0.35,
                "narrative_weight": 0.20,
            },
        }

        # Паттерны жанровой лексики
        self.genre_keywords: Dict[str, List[str]] = {
            "лирика": ["сердце", "луна", "ночь", "тихий", "шёпот"],
            "элегия": ["скорбь", "прах", "минувшее", "тень", "вечность"],
            "романс": ["поцелуй", "огонь", "любимый", "струны", "танго"],
            "ода": ["слава", "триумф", "бог", "герой", "глас"],
            "поэма": ["странник", "дорога", "битва", "меч", "кровь"],
            "притча": ["учитель", "ученик", "мудрец", "урок", "истина"],
            "басня": ["мораль", "зверь", "лиса", "ворона", "поученье"],
            "драма": ["сцена", "акт", "герой", "диалог", "пауза"],
            "трагедия": ["рок", "гибель", "фатальный", "плач", "жертва"],
            "комедия": ["смех", "шут", "курьёз", "ирония", "фарс"],
        }

        # Маркеры повествовательной структуры
        self.narrative_markers = {
            "dialogue": ("—", " - ", ":"),
            "conflict": ("конфликт", "спор", "битва", "война", "столкновение"),
            "moral": ("мораль", "урок", "вывод"),
        }

        self.emotion_lexicon = EmotionLexiconExtended()

    # -------------------------------
    # STRUCTURE METRICS
    # -------------------------------

    def _rhyme_score(self, text: str) -> float:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if len(lines) < 2:
            return 0.0

        rhymes = 0
        for current, following in zip(lines, lines[1:]):
            if (
                len(current) > 3
                and len(following) > 3
                and current[-2:] == following[-2:]
            ):
                rhymes += 1

        return rhymes / len(lines)

    def _structure_score(self, text: str) -> float:
        lengths = [len(line) for line in text.split("\n") if line.strip()]
        if not lengths:
            return 0.0

        avg_length = sum(lengths) / len(lengths)
        variance = sum(abs(length - avg_length) for length in lengths)

        return 1.0 - min(1.0, variance / 300)

    # -------------------------------
    # EMOTION METRICS
    # -------------------------------

    def _emotion_score(self, tags: Dict[str, Any]) -> float:
        emotions = tags.get("emotions", {})
        if not isinstance(emotions, dict):
            emotions = {}

        hit_count = sum(
            1 for value in emotions.values()
            if isinstance(value, bool) and value
        )

        drama_bonus = {
            "high": 0.4,
            "medium": 0.25,
            "low": 0.1,
        }.get(tags.get("drama_level"), 0.0)

        intensity = tags.get("intensity")
        if not isinstance(intensity, (int, float)):
            intensity = 0.0

        if hit_count == 0 and drama_bonus == 0.0 and intensity == 0.0:
            return 0.0

        normalized_hits = hit_count / max(len(self.emotion_lexicon.emotion_words), 1)
        base = normalized_hits * 3

        return min(1.0, base + drama_bonus + intensity * 0.5)

    # -------------------------------
    # LEXICON METRICS
    # -------------------------------

    def _lexicon_score(self, text: str, genre: str) -> float:
        keywords = self.genre_keywords.get(genre, [])
        if not keywords:
            return 0.0

        lowered = text.lower()
        hits = sum(lowered.count(keyword) for keyword in keywords)
        unique_hits = sum(1 for keyword in keywords if keyword in lowered)

        score = (hits * 0.6 + unique_hits * 0.4) / max(len(keywords), 1)
        return min(1.0, score)

    # -------------------------------
    # NARRATIVE METRICS
    # -------------------------------

    def _narrative_score(self, text: str, register: str | None = None) -> float:
        lowered = text.lower()

        dialogue_hits = sum(lowered.count(m) for m in self.narrative_markers["dialogue"])
        conflict_hits = sum(lowered.count(m) for m in self.narrative_markers["conflict"])
        moral_hits = sum(lowered.count(m) for m in self.narrative_markers["moral"])

        raw_score = dialogue_hits * 0.2 + conflict_hits * 0.3 + moral_hits * 0.5

        register_bonus = {
            "formal": 0.05,
            "poetic": 0.08,
        }.get(register, 0.0)

        return min(1.0, raw_score + register_bonus)

    # -------------------------------
    # FINAL PREDICTION
    # -------------------------------

    def predict(self, text: str) -> Dict[str, float]:
        tags = self.emotion_lexicon.get_emotion(text)

        rhyme = self._rhyme_score(text)
        structure = self._structure_score(text)
        structure_combo = (rhyme + structure) / 2

        emotion = self._emotion_score(tags)
        narrative = self._narrative_score(text, tags.get("register"))

        predictions: Dict[str, float] = {}

        for genre, weights in self.genre_profiles.items():
            lexicon = self._lexicon_score(text, genre)
            score = (
                structure_combo * weights["structure_weight"]
                + emotion * weights["emotion_weight"]
                + lexicon * weights["lexicon_weight"]
                + narrative * weights["narrative_weight"]
            )
            predictions[genre] = round(score, 4)

        return dict(sorted(predictions.items(), key=lambda i: i[1], reverse=True))
