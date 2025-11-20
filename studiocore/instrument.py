# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Instrumentation utilities required by the Codex specification."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence


_DEFAULT_LIBRARY: Sequence[str] = (
    "grand piano",
    "warm pad",
    "cinematic strings",
    "electric guitar",
    "analog bass",
    "orchestral percussion",
    "ethereal choir",
    "lofi kit",
    "modular synth",
)


@dataclass(frozen=True)
class InstrumentPick:
    """Light-weight data container for instrument recommendations."""

    instruments: List[str]
    confidence: float
    rationale: str


class InstrumentLibrary:
    """Simple heuristic instrument selector used by the v6 logical engines."""

    def __init__(self) -> None:
        self._defaults = list(_DEFAULT_LIBRARY)

    def list_defaults(self) -> List[str]:
        """Return a copy of the default instrument catalogue."""

        return list(self._defaults)

    def suggest_for_energy(self, energy: float) -> InstrumentPick:
        """Return a set of instruments that loosely match the energy value."""

        energy = max(0.0, min(1.0, energy))
        if energy < 0.25:
            instruments = ["grand piano", "ethereal choir", "warm pad"]
            rationale = "Calm atmosphere — focus on sustained harmonics."
        elif energy < 0.55:
            instruments = ["grand piano", "cinematic strings", "analog bass"]
            rationale = "Mid-energy narrative — blend organic and synthetic layers."
        elif energy < 0.8:
            instruments = ["electric guitar", "analog bass", "lofi kit"]
            rationale = "Energetic core — emphasise rhythm section."
        else:
            instruments = ["modular synth", "orchestral percussion", "electric guitar"]
            rationale = "High-energy climax — accentuate percussive hits."

        return InstrumentPick(instruments, round(0.6 + energy * 0.4, 3), rationale)

    def extend_palette(self, seed: Iterable[str]) -> List[str]:
        """Merge seed suggestions with the default library preserving order."""

        seen = set()
        palette: List[str] = []
        for name in list(seed) + self._defaults:
            if name not in seen:
                palette.append(name)
                seen.add(name)
        return palette


def _ensure_emotion_profile(emotions: Dict[str, float]) -> Dict[str, float]:
    if not emotions:
        return {"peace": 1.0}
    total = sum(emotions.values())
    if total <= 0:
        return {"peace": 1.0}
    return {key: value / total for key, value in emotions.items()}


def instrument_selection(
    *,
    genre: str | None = None,
    energy: float | None = None,
    mood: str | None = None,
    reference_palette: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Select a small collection of instruments suitable for the track skeleton."""

    library = InstrumentLibrary()
    base = reference_palette or []
    energy = 0.5 if energy is None else max(0.0, min(1.0, energy))
    suggestion = library.suggest_for_energy(energy)
    palette = library.extend_palette(base)

    if genre:
        genre_low = genre.lower()
        if "rock" in genre_low:
            palette = library.extend_palette(["electric guitar", "live drums"])
        elif "hip" in genre_low or "rap" in genre_low:
            palette = library.extend_palette(["808 bass", "drum machine", "vinyl crackle"])
        elif "edm" in genre_low or "electronic" in genre_low:
            palette = library.extend_palette(["sidechained pad", "super saw", "fm bass"])
        elif "cinematic" in genre_low or "score" in genre_low:
            palette = library.extend_palette(["cinematic brass", "granular textures"])

    if mood and "melanch" in mood.lower():
        palette = library.extend_palette(["felt piano", "solo cello"])

    return {
        "selected": suggestion.instruments,
        "palette": palette,
        "confidence": suggestion.confidence,
        "rationale": suggestion.rationale,
        "energy": energy,
    }


def instrument_based_on_emotion(
    emotions: Dict[str, float],
    *,
    base_palette: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Map dominant emotions to characteristic instruments."""

    emotions = _ensure_emotion_profile(emotions)
    dominant = max(emotions, key=emotions.get)
    mapping = {
        "joy": ["acoustic guitar", "hand percussion", "bright piano"],
        "sadness": ["felt piano", "solo violin", "soft pads"],
        "anger": ["distorted guitar", "aggressive synth", "drums"],
        "fear": ["dissonant strings", "processed vocals", "sub bass"],
        "epic": ["orchestral brass", "taiko ensemble", "choir"]
    }
    palette = mapping.get(dominant, ["ambient piano", "textured pad"])
    library = InstrumentLibrary()
    merged = library.extend_palette(list(base_palette or []) + palette)
    mood_descriptor = f"Dominant emotion '{dominant}' routed to {', '.join(palette)}."

    return {
        "dominant_emotion": dominant,
        "emotions": emotions,
        "suggested": palette,
        "palette": merged,
        "explanation": mood_descriptor,
    }


def instrument_based_on_voice(
    voice_profile: str | None,
    *,
    target_energy: float | None = None,
) -> Dict[str, Any]:
    """Suggest supporting instruments that complement the detected voice style."""

    voice_profile = (voice_profile or "neutral").lower()
    target_energy = 0.5 if target_energy is None else max(0.0, min(1.0, target_energy))
    library = InstrumentLibrary()

    if "whisper" in voice_profile or "soft" in voice_profile:
        instruments = ["felt piano", "subtle pads", "field recordings"]
        rationale = "Soft voice detected — emphasise intimate textures."
    elif "grit" in voice_profile or "rasp" in voice_profile or "growl" in voice_profile:
        instruments = ["distorted guitar", "hybrid drums", "analog bass"]
        rationale = "Gritty vocals — balance with solid rhythm section."
    elif "choir" in voice_profile or "ensemble" in voice_profile:
        instruments = ["orchestral strings", "grand piano", "cymbal swells"]
        rationale = "Ensemble vocals — support with lush harmonic beds."
    else:
        instruments = library.suggest_for_energy(target_energy).instruments
        rationale = "Neutral voice — rely on energy-aligned library selection."

    palette = library.extend_palette(instruments)
    return {
        "voice_profile": voice_profile,
        "suggested": instruments,
        "palette": palette,
        "rationale": rationale,
        "energy": target_energy,
    }


def instrument_color_sync(
    color_profile: Dict[str, Any],
    *,
    base_palette: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Produce instrument accents that reflect the tonal color palette."""

    palette_map = {
        "red": ["analog brass", "distorted leads"],
        "orange": ["warm electric piano", "percussion loops"],
        "golden": ["dulcimer", "acoustic guitar"],
        "green": ["organic percussion", "flute"],
        "blue": ["choral pad", "shimmer guitar"],
        "violet": ["granular synth", "wide pad"],
    }

    base_color = (color_profile.get("primary_color") or "").split(" ")[0].lower()
    accents = palette_map.get(base_color, ["textures", "atmospheric pad"])
    library = InstrumentLibrary()
    palette = library.extend_palette(list(base_palette or []) + accents)

    return {
        "primary_color": color_profile.get("primary_color"),
        "accent_color": color_profile.get("accent_color"),
        "accents": accents,
        "palette": palette,
        "confidence": 0.7,
        "rationale": f"Mapped tonal color '{base_color or 'neutral'}' to accent instruments.",
    }


def instrument_rhythm_sync(
    bpm: float,
    *,
    rhythm_profile: Sequence[float] | None = None,
) -> Dict[str, Any]:
    """Adapt percussion choices to the rhythmic profile."""

    bpm = max(60.0, min(200.0, float(bpm)))
    rhythm_profile = list(rhythm_profile or [])
    if bpm < 80:
        groove = "downtempo"
        toolkit = ["brush kit", "upright bass", "ambient percussion"]
    elif bpm < 110:
        groove = "mid-groove"
        toolkit = ["studio kit", "rhodes piano", "subtle shakers"]
    elif bpm < 140:
        groove = "uptempo"
        toolkit = ["tight drums", "synth bass", "plucked synth"]
    else:
        groove = "high-energy"
        toolkit = ["hard-hitting drums", "sidechain pad", "risers"]

    movement = 0.0
    if rhythm_profile:
        max_curve = max(rhythm_profile)
        min_curve = min(rhythm_profile)
        if max_curve > min_curve:
            movement = round((max_curve - min_curve) / max_curve, 3)

    return {
        "bpm": bpm,
        "groove": groove,
        "toolkit": toolkit,
        "movement": movement,
        "confidence": 0.65,
        "rationale": f"Rhythm profile suggests {groove} percussion bed.",
    }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
