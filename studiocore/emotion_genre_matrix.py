# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Emotion→Genre bias matrix (Variant A: Emotion is stronger than text)."""

from __future__ import annotations

from typing import Dict

_GENRES = (
    "rock_metal",
    "hip_hop",
    "jazz",
    "edm",
    "orchestral",
    "chanson",
    "gothic",
    "folk",
    "pop",
)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def compute_genre_bias(emotion_vector: Dict[str, float]) -> Dict[str, float]:
    """Translate a 7-axis emotion vector into macro-genre biases.

    Biases are normalised to ``[0.0, 1.0]`` and start from a neutral baseline of
    ``1.0``.  Variant A rules intentionally allow strong emotional signals to
    dominate textual routing.
    """

    bias = {genre: 1.0 for genre in _GENRES}
    vector = emotion_vector or {}

    anger = float(vector.get("anger", 0.0))
    sadness = float(vector.get("sadness", 0.0))
    awe = float(vector.get("awe", 0.0))
    joy = float(vector.get("joy", 0.0))
    pain = float(vector.get("pain", 0.0))
    love = float(vector.get("love", 0.0))

    # anger ↑ metal/industrial/hip-hop, ↓ jazz/folk/pop
    # На основе базы: HARD (rock/metal) - преимущественно minor, быстрый BPM
    bias["rock_metal"] += 0.65 * anger  # Увеличено: более сильная связь
    bias["hip_hop"] += 0.55 * anger  # Увеличено
    bias["jazz"] -= 0.45 * anger  # Усилено вычитание: jazz только major
    bias["folk"] -= 0.35 * anger  # Усилено
    bias["pop"] -= 0.35 * anger  # Усилено

    # sadness ↑ gothic/darkwave/neofolk, ↓ EDM/pop
    # На основе базы: CINEMATIC - преимущественно minor, медленный BPM
    bias["gothic"] += 0.60 * sadness  # Увеличено
    bias["folk"] += 0.28 * sadness  # Слегка увеличено
    bias["edm"] -= 0.38 * sadness  # Усилено: EDM очень быстрый (134.9 BPM)
    bias["pop"] -= 0.28 * sadness  # Слегка увеличено

    # awe ↑ orchestral/cinematic, ↓ hip-hop/edm
    # На основе базы: CINEMATIC - преимущественно minor, медленный BPM (80.0)
    # Цвета epic/awe: #8A2BE2, #4B0082, #FF00FF, #40E0D0 → cinematic жанры
    bias["orchestral"] += 0.70 * awe  # Увеличено
    bias["hip_hop"] -= 0.28 * awe  # Слегка усилено
    bias["edm"] -= 0.22 * awe  # Слегка усилено
    # Дополнительный boost для cinematic при высоком awe (цвета epic указывают на cinematic)
    if awe > 0.5:
        bias["orchestral"] += 0.18 * (awe - 0.5)  # Дополнительный boost для высокого awe

    # joy ↑ pop/funk/electronic, ↓ gothic/doom
    # На основе базы: POP/EDM - быстрый BPM, преимущественно major
    # Цвета joy: #FFD93D, #FFD700, #FFFF00, #FFF59D → electronic/pop жанры
    bias["pop"] += 0.60 * joy  # Увеличено
    bias["edm"] += 0.38 * joy  # Увеличено
    bias["gothic"] -= 0.45 * joy  # Усилено: gothic преимущественно minor
    # Дополнительный boost для pop/edm при высоком joy (цвета joy указывают на pop/electronic)
    if joy > 0.5:
        bias["pop"] += 0.15 * (joy - 0.5)  # Дополнительный boost для высокого joy
        bias["edm"] += 0.12 * (joy - 0.5)  # Дополнительный boost для высокого joy

    # pain ↑ darkwave/gothic, ↓ pop
    # На основе базы: GOTHIC - преимущественно minor, медленный BPM
    bias["gothic"] += 0.55 * pain  # Увеличено
    bias["pop"] -= 0.50 * pain  # Усилено: pop преимущественно major

    # love ↑ ballad/folk, ↓ metal
    # На основе базы: LYRICAL/SOFT - преимущественно major, медленный/средний BPM
    # Цвета love: #FF7AA2, #FFC0CB, #FFB6C1, #FFE4E1, #C2185B → lyrical/soft жанры
    bias["folk"] += 0.45 * love  # Увеличено
    bias["chanson"] += 0.25 * love  # Увеличено
    bias["rock_metal"] -= 0.40 * love  # Усилено: rock_metal преимущественно minor
    # Дополнительный boost для lyrical жанров (цвета love указывают на лирику)
    if love > 0.5:
        bias["chanson"] += 0.15 * (love - 0.5)  # Дополнительный boost для высокого love

    normalized = {genre: round(_clamp(value), 3) for genre, value in bias.items()}
    return normalized


__all__ = ["compute_genre_bias"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
