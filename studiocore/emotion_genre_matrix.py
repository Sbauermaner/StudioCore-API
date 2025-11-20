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
    bias["rock_metal"] += 0.6 * anger
    bias["hip_hop"] += 0.5 * anger
    bias["jazz"] -= 0.4 * anger
    bias["folk"] -= 0.3 * anger
    bias["pop"] -= 0.3 * anger

    # sadness ↑ gothic/darkwave/neofolk, ↓ EDM/pop
    bias["gothic"] += 0.55 * sadness
    bias["folk"] += 0.25 * sadness
    bias["edm"] -= 0.35 * sadness
    bias["pop"] -= 0.25 * sadness

    # awe ↑ orchestral/cinematic, ↓ hip-hop/edm
    bias["orchestral"] += 0.65 * awe
    bias["hip_hop"] -= 0.25 * awe
    bias["edm"] -= 0.2 * awe

    # joy ↑ pop/funk/electronic, ↓ gothic/doom
    bias["pop"] += 0.55 * joy
    bias["edm"] += 0.35 * joy
    bias["gothic"] -= 0.4 * joy

    # pain ↑ darkwave/gothic, ↓ pop
    bias["gothic"] += 0.5 * pain
    bias["pop"] -= 0.45 * pain

    # love ↑ ballad/folk, ↓ metal
    bias["folk"] += 0.4 * love
    bias["chanson"] += 0.2 * love
    bias["rock_metal"] -= 0.35 * love

    normalized = {genre: round(_clamp(value), 3) for genre, value in bias.items()}
    return normalized


__all__ = ["compute_genre_bias"]
