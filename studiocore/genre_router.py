from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class GenreContext:
    emotion: str
    bpm: float
    key: str
    mode: str
    rhyme_density: float
    narrative_pressure: float
    pain: float
    valence: float
    arousal: float


class DynamicGenreRouter:
    """
    Stateless router from Emotion + BPM + structure → macro-genre.

    ВАЖНО:
    - не хранит глобального состояния
    - не кэширует результаты
    - основывается ТОЛЬКО на переданном result.
    """

    def build_context(self, result: Dict[str, Any]) -> GenreContext:
        bpm = float(result.get("bpm", {}).get("estimate") or 0.0)
        key = str(result.get("style", {}).get("key") or "auto")
        mode = "minor" if "m" in key.lower() else "major"

        integrity = result.get("integrity", {}) or {}
        rhyme_density = float(integrity.get("rhyme_density") or 0.0)
        narrative_pressure = float(integrity.get("narrative_pressure") or 0.0)

        tlp = result.get("tlp", {}) or {}
        pain = float(tlp.get("pain") or 0.0)
        valence = float(tlp.get("valence") or 0.0)
        arousal = float(tlp.get("arousal") or 0.0)

        emotion = str(result.get("emotion", {}).get("label") or result.get("_emotion_label") or "neutral")

        return GenreContext(
            emotion=emotion,
            bpm=bpm,
            key=key,
            mode=mode,
            rhyme_density=rhyme_density,
            narrative_pressure=narrative_pressure,
            pain=pain,
            valence=valence,
            arousal=arousal,
        )

    # --- SCORE HELPERS -----------------------------------------------------

    def _score_rock_metal(self, ctx: GenreContext) -> float:
        score = 0.0
        if ctx.emotion in ("rage", "dark", "epic"):
            score += 0.6
        if ctx.mode == "minor":
            score += 0.2
        if ctx.bpm >= 130:
            score += 0.2
        return score

    def _score_hip_hop(self, ctx: GenreContext) -> float:
        score = 0.0
        if 75 <= ctx.bpm <= 110:
            score += 0.4
        if ctx.narrative_pressure > 0.6:
            score += 0.3
        if ctx.rhyme_density > 0.6:
            score += 0.3
        return score

    def _score_jazz(self, ctx: GenreContext) -> float:
        score = 0.0
        if 80 <= ctx.bpm <= 140:
            score += 0.3
        if ctx.emotion in ("melancholic", "hope"):
            score += 0.4
        if ctx.valence > 0.1 and ctx.arousal < 0.7:
            score += 0.3
        return score

    def _score_edm(self, ctx: GenreContext) -> float:
        score = 0.0
        if 118 <= ctx.bpm <= 140:
            score += 0.4
        if ctx.emotion in ("epic", "hope"):
            score += 0.3
        if ctx.rhyme_density < 0.4:
            score += 0.3
        return score

    def _score_orchestral(self, ctx: GenreContext) -> float:
        score = 0.0
        if ctx.emotion in ("epic", "hope", "melancholic"):
            score += 0.5
        if ctx.narrative_pressure > 0.7:
            score += 0.3
        return score

    def _score_chanson(self, ctx: GenreContext) -> float:
        score = 0.0
        if ctx.narrative_pressure > 0.7 and ctx.bpm < 110:
            score += 0.4
        if ctx.emotion in ("melancholic", "dark"):
            score += 0.3
        if ctx.rhyme_density > 0.5:
            score += 0.3
        return score

    def _score_gothic(self, ctx: GenreContext) -> float:
        score = 0.0
        if ctx.emotion == "dark":
            score += 0.6
        if ctx.mode == "minor":
            score += 0.2
        if 60 <= ctx.bpm <= 130:
            score += 0.2
        return score

    def _score_folk(self, ctx: GenreContext) -> float:
        score = 0.0
        if ctx.emotion in ("hope", "melancholic"):
            score += 0.3
        if ctx.bpm < 120:
            score += 0.3
        if ctx.narrative_pressure > 0.5:
            score += 0.4
        return score

    def _score_pop(self, ctx: GenreContext) -> float:
        score = 0.0
        if 90 <= ctx.bpm <= 130:
            score += 0.4
        if ctx.valence > 0.2 and ctx.pain < 0.5:
            score += 0.4
        if ctx.rhyme_density >= 0.4:
            score += 0.2
        return score

    # --- PUBLIC API --------------------------------------------------------

    def route(self, result: Dict[str, Any]) -> Tuple[str, str]:
        """
        Возвращает (macro_genre, reason).

        НЕ ПЕРЕПИСЫВАЕТ явно заданный жанр пользователем:
        - если result["style"]["genre"] не "auto" и не пустой — оставляем.
        """
        style_block = result.get("style", {}) or {}
        user_genre = style_block.get("genre")

        if user_genre and str(user_genre).lower() not in ("auto", "unknown", ""):
            return str(user_genre), "user_override"

        ctx = self.build_context(result)

        scores = {
            "rock_metal": self._score_rock_metal(ctx),
            "hip_hop": self._score_hip_hop(ctx),
            "jazz": self._score_jazz(ctx),
            "edm": self._score_edm(ctx),
            "orchestral": self._score_orchestral(ctx),
            "chanson": self._score_chanson(ctx),
            "gothic": self._score_gothic(ctx),
            "folk": self._score_folk(ctx),
            "pop": self._score_pop(ctx),
        }

        macro_genre = max(scores.items(), key=lambda kv: kv[1])[0]
        return macro_genre, "dynamic_router"
