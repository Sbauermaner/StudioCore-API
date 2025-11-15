"""Logical engine helpers used by the StudioCore v6 compatibility layer.

The Codex specification expects a wide collection of logical engines.  The
implementations below provide light-weight, deterministic heuristics that can
run in restricted environments while still producing structured data.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from statistics import mean
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .emotion import AutoEmotionalAnalyzer
from .instrument import (
    InstrumentLibrary,
    instrument_based_on_emotion as _instrument_based_on_emotion,
    instrument_based_on_voice as _instrument_based_on_voice,
    instrument_color_sync as _instrument_color_sync,
    instrument_rhythm_sync as _instrument_rhythm_sync,
    instrument_selection as _instrument_selection,
)
from .rhythm import LyricMeter
from .text_utils import extract_sections, normalize_text_preserve_symbols
from .tone import ToneSyncEngine
from .user_override_manager import UserOverrideManager

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
_COMMAND_RE = re.compile(r"\[(?P<name>[A-Z_]+)\s*:?\s*(?P<value>[^\]]+)\]")
_VOWEL_RE = re.compile(r"[aeiouyаеёиоуыэюя]", re.I)


def _split_sentences(text: str) -> List[str]:
    if not text.strip():
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text)


def _section_texts(text: str) -> List[str]:
    structured = extract_sections(text)
    if structured:
        sections = []
        for section in structured:
            lines = [ln.strip() for ln in section.get("lines", []) if ln.strip()]
            if lines:
                sections.append("\n".join(lines))
        if sections:
            return sections
    chunks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    return chunks or ([text.strip()] if text.strip() else [])


class TextStructureEngine:
    """Detect song sections and structural anchors."""

    KEYWORDS = {
        "intro": ("intro", "интро", "вступ", "opening"),
        "verse": ("verse", "куплет", "strofa"),
        "prechorus": ("pre-chorus", "prechorus", "преприпев"),
        "chorus": ("chorus", "припев", "hook", "refrain"),
        "bridge": ("bridge", "бридж", "middle"),
        "outro": ("outro", "финал", "ending"),
    }

    def __init__(self) -> None:
        self._last_sections: List[str] = []

    def auto_section_split(self, text: str) -> List[str]:
        sections = _section_texts(text)
        self._last_sections = sections
        return list(sections)

    def _ensure_sections(self, text: str, sections: Sequence[str] | None = None) -> List[str]:
        if sections is not None:
            return list(sections)
        if self._last_sections:
            return list(self._last_sections)
        return self.auto_section_split(text)

    def _resolve_section(self, label: str, text: str, sections: Sequence[str] | None, fallback_index: int) -> Dict[str, Any]:
        sections = self._ensure_sections(text, sections)
        if not sections:
            return {"label": label, "index": None, "text": "", "confidence": 0.0}

        keywords = self.KEYWORDS.get(label, ())
        match_index = None
        for idx, section in enumerate(sections):
            low = section.lower()
            if any(token in low for token in keywords):
                match_index = idx
                break
        if match_index is None:
            match_index = min(fallback_index, len(sections) - 1)
            confidence = 0.4
        else:
            confidence = 0.75

        return {
            "label": label,
            "index": match_index,
            "text": sections[match_index],
            "confidence": round(confidence, 3),
        }

    def detect_intro(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("intro", text, sections, 0)

    def detect_verse(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("verse", text, sections, 0 if len(self._ensure_sections(text, sections)) == 1 else 1)

    def detect_prechorus(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("prechorus", text, sections, 1)

    def detect_chorus(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("chorus", text, sections, 1)

    def detect_bridge(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("bridge", text, sections, max(len(self._ensure_sections(text, sections)) - 2, 0))

    def detect_outro(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        return self._resolve_section("outro", text, sections, max(len(self._ensure_sections(text, sections)) - 1, 0))

    def detect_meta_pause(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        sections = self._ensure_sections(text, sections)
        pause_locations: List[int] = []
        for idx, section in enumerate(sections):
            if "..." in section or "(pause" in section.lower() or "[pause" in section.lower():
                pause_locations.append(idx)
        confidence = 0.8 if pause_locations else 0.2
        return {"count": len(pause_locations), "locations": pause_locations, "confidence": confidence}

    def detect_zero_pulse(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        sections = self._ensure_sections(text, sections)
        zero_sections: List[int] = []
        for idx, section in enumerate(sections):
            if not section.strip() or "[silence]" in section.lower():
                zero_sections.append(idx)
        return {
            "has_zero_pulse": bool(zero_sections),
            "locations": zero_sections,
            "confidence": 0.9 if zero_sections else 0.3,
        }


class EmotionEngine:
    """High-level wrapper above the heuristic emotional analyzers."""

    def __init__(self) -> None:
        self._analyzer = AutoEmotionalAnalyzer()

    def emotion_detection(self, text: str) -> Dict[str, float]:
        return self._analyzer.analyze(text)

    def emotion_intensity_curve(self, text: str) -> List[float]:
        sentences = _split_sentences(text)
        if not sentences:
            return []
        curve: List[float] = []
        for sentence in sentences:
            scores = self._analyzer.analyze(sentence)
            intensity = sum(scores.values())
            curve.append(round(intensity, 3))
        return curve

    def emotion_pivot_points(self, text: str, *, intensity_curve: Sequence[float] | None = None) -> List[int]:
        curve = list(intensity_curve or self.emotion_intensity_curve(text))
        if not curve:
            return []
        indexed = sorted(enumerate(curve), key=lambda item: item[1], reverse=True)
        return [idx for idx, _ in indexed[:3]]

    def secondary_emotion_detection(self, text: str | Dict[str, float]) -> Dict[str, float]:
        if isinstance(text, dict):
            scores = dict(text)
        else:
            scores = self._analyzer.analyze(text)
        if not scores:
            return {}
        dominant = max(scores, key=scores.get)
        return {k: round(v, 3) for k, v in scores.items() if k != dominant}

    def emotion_conflict_map(self, text: str | Dict[str, float]) -> Dict[str, Any]:
        if isinstance(text, dict):
            scores = dict(text)
        else:
            scores = self._analyzer.analyze(text)
        if not scores:
            return {"conflict": 0.0, "primary": None, "secondary": None}
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        primary, primary_value = ordered[0]
        secondary, secondary_value = ordered[1] if len(ordered) > 1 else (None, 0.0)
        conflict = round(abs(primary_value - secondary_value), 3)
        return {"primary": primary, "secondary": secondary, "conflict": conflict}


class ColorEmotionEngine:
    """Translate emotions into colour palettes."""

    COLOR_MAP = {
        "joy": "golden",
        "sadness": "deep blue",
        "anger": "crimson",
        "fear": "ashen gray",
        "peace": "soft white",
        "epic": "violet flare",
        "awe": "iridescent teal",
    }

    def assign_color_by_emotion(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        if not emotions:
            return {"primary_color": "neutral white", "confidence": 0.2}
        dominant = max(emotions, key=emotions.get)
        color = self.COLOR_MAP.get(dominant, "ambient silver")
        return {"primary_color": color, "accent_color": "prism glow", "confidence": round(emotions[dominant], 3)}

    def generate_color_wave(self, emotions: Dict[str, float], *, steps: int = 5) -> List[str]:
        if not emotions:
            return ["neutral white" for _ in range(steps)]
        ordered = sorted(emotions.items(), key=lambda item: item[1], reverse=True)
        palette = [self.COLOR_MAP.get(name, name) for name, _ in ordered]
        if len(palette) >= steps:
            return palette[:steps]
        while len(palette) < steps:
            palette.append(palette[-1])
        return palette

    def color_transition_map(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        wave = self.generate_color_wave(emotions)
        transitions = []
        for idx in range(len(wave) - 1):
            transitions.append({"from": wave[idx], "to": wave[idx + 1], "blend": 0.5})
        return {"transitions": transitions, "palette": wave}


class VocalEngine:
    """Extracts rough vocal characteristics from the lyrics."""

    def detect_voice_gender(self, text: str) -> str:
        tokens = [t.lower() for t in _words(text)]
        feminine = sum(tokens.count(pronoun) for pronoun in ("she", "her", "она", "её"))
        masculine = sum(tokens.count(pronoun) for pronoun in ("he", "him", "он", "его"))
        if feminine > masculine:
            return "female"
        if masculine > feminine:
            return "male"
        return "neutral"

    def detect_voice_type(self, text: str) -> str:
        sentences = _split_sentences(text)
        if not sentences:
            return "narration"
        avg_length = mean(len(sentence.split()) for sentence in sentences)
        if avg_length <= 6:
            return "spoken"
        if avg_length <= 12:
            return "lyrical"
        return "melismatic"

    def detect_voice_tone(self, text: str) -> str:
        energy = sum(ch in "!?" for ch in text)
        softness = sum(ch in "…" for ch in text)
        if energy > softness * 2:
            return "intense"
        if softness > energy:
            return "soft"
        return "balanced"

    def detect_vocal_style(self, text: str, *, voice_type: str | None = None, voice_tone: str | None = None) -> str:
        voice_type = voice_type or self.detect_voice_type(text)
        voice_tone = voice_tone or self.detect_voice_tone(text)
        if voice_type == "spoken":
            return "spoken-word"
        if voice_tone == "intense":
            return "belting"
        if voice_tone == "soft":
            return "breathy"
        return "lyrical"

    def vocal_dynamics_map(self, sections: Sequence[str]) -> Dict[str, float]:
        dynamics: Dict[str, float] = {}
        if not sections:
            return dynamics
        for idx, section in enumerate(sections):
            emphasis = sum(1 for ch in section if ch.isupper())
            exclaims = section.count("!")
            ellipsis = section.count("…")
            score = 0.4 + 0.1 * exclaims + 0.05 * emphasis - 0.05 * ellipsis
            dynamics[f"section_{idx + 1}"] = round(max(0.0, score), 3)
        return dynamics

    def vocal_intensity_curve(self, dynamics: Dict[str, float]) -> List[float]:
        return [dynamics[key] for key in sorted(dynamics.keys())]


class BreathingEngine:
    """Estimate breathing points using simple heuristics."""

    def _lines(self, text: str) -> List[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def detect_inhale_points(self, text: str) -> List[int]:
        lines = self._lines(text)
        inhale_points: List[int] = []
        for idx, line in enumerate(lines):
            if len(line.split()) >= 12 or line.endswith((";", ":")):
                inhale_points.append(idx)
        return inhale_points

    def detect_short_breath(self, text: str) -> List[int]:
        lines = self._lines(text)
        return [idx for idx, line in enumerate(lines) if len(line.split()) <= 4]

    def detect_broken_breath(self, text: str) -> List[int]:
        lines = self._lines(text)
        broken = []
        for idx, line in enumerate(lines):
            if "--" in line or "—" in line:
                broken.append(idx)
        return broken

    def detect_spasms(self, text: str) -> List[int]:
        lines = self._lines(text)
        return [idx for idx, line in enumerate(lines) if "?!" in line or "!!" in line]

    def detect_emotional_breathing(self, text: str, emotions: Dict[str, float] | None = None) -> Dict[str, Any]:
        emotions = emotions or {}
        inhale = self.detect_inhale_points(text)
        spasms = self.detect_spasms(text)
        return {
            "inhale_points": inhale,
            "spasm_points": spasms,
            "emotional_weight": emotions,
            "intensity": round(min(1.0, len(spasms) * 0.1 + emotions.get("anger", 0) * 0.5), 3),
        }

    def breath_to_emotion_sync(self, text: str, emotions: Dict[str, float]) -> Dict[str, Any]:
        inhale = self.detect_inhale_points(text)
        short = self.detect_short_breath(text)
        density = len(inhale) / max(1, len(short))
        dominant = max(emotions, key=emotions.get) if emotions else "neutral"
        return {
            "breath_density": round(density, 3),
            "dominant_emotion": dominant,
            "sync_score": round(min(1.0, emotions.get(dominant, 0) + density * 0.1), 3),
        }


class BPMEngine:
    """Expose BPM-related helpers from the lyric meter."""

    def __init__(self) -> None:
        self._meter = LyricMeter()

    def text_bpm_estimation(self, text: str) -> int:
        analysis = self._meter.analyze(normalize_text_preserve_symbols(text))
        return int(round(analysis.get("global_bpm", 120.0)))

    def emotion_bpm_mapping(self, emotions: Dict[str, float], *, base_bpm: int | None = None) -> Dict[str, Any]:
        if not emotions:
            return {"map": {}, "target_bpm": base_bpm or 120, "target_energy": 0.5}
        base = float(base_bpm or 120)
        mapping: Dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0
        for emotion, weight in emotions.items():
            shift = (weight - 0.3) * 40
            mapping[emotion] = round(base + shift, 1)
            weighted_sum += mapping[emotion] * weight
            total_weight += weight
        target_bpm = round(weighted_sum / max(total_weight, 1e-6), 1)
        target_energy = round(min(1.0, max(0.0, (target_bpm - 90) / 80)), 3)
        return {"map": mapping, "target_bpm": target_bpm, "target_energy": target_energy}

    def meaning_bpm_curve(self, sections: Sequence[str], *, base_bpm: int | None = None) -> List[float]:
        if not sections:
            return []
        base = float(base_bpm or 120)
        curve: List[float] = []
        for section in sections:
            words = _words(section)
            syllables = sum(len(_VOWEL_RE.findall(word)) for word in words)
            density = syllables / max(1, len(words))
            curve.append(round(base + (density - 3) * 8, 2))
        return curve

    def breathing_bpm_integration(self, breathing: Dict[str, Any], base_bpm: int) -> Dict[str, Any]:
        inhale = breathing.get("inhale_points", [])
        spasm = breathing.get("spasm_points", [])
        modifier = len(spasm) * 2 - len(inhale)
        adjusted = max(60.0, base_bpm + modifier)
        return {
            "base_bpm": base_bpm,
            "adjusted_bpm": round(adjusted, 1),
            "breathing_modifier": modifier,
        }

    def poly_rhythm_detection(self, bpm_curve: Sequence[float]) -> Dict[str, Any]:
        if not bpm_curve:
            return {"has_poly_rhythm": False, "variance": 0.0}
        variance = max(bpm_curve) - min(bpm_curve)
        return {"has_poly_rhythm": variance > 15.0, "variance": round(variance, 2)}


class MeaningVelocityEngine:
    """Estimate semantic speed and fractures between sections."""

    def semantic_shift_detection(self, sections: Sequence[str]) -> Dict[str, Any]:
        shifts: List[Dict[str, Any]] = []
        for idx in range(1, len(sections)):
            prev_words = Counter(_words(sections[idx - 1]))
            current_words = Counter(_words(sections[idx]))
            if not prev_words or not current_words:
                overlap = 0.0
            else:
                common = sum((prev_words & current_words).values())
                total = sum((prev_words | current_words).values())
                overlap = common / max(total, 1)
            shifts.append({"index": idx, "overlap": round(overlap, 3)})
        return {"shifts": shifts}

    def meaning_acceleration(self, curve: Sequence[float]) -> List[float]:
        acceleration: List[float] = []
        for idx in range(1, len(curve)):
            acceleration.append(round(curve[idx] - curve[idx - 1], 3))
        return acceleration

    def meaning_fracture_detection(self, shifts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        fractures = [shift for shift in shifts if shift.get("overlap", 0.0) < 0.15]
        return {"fractures": fractures, "count": len(fractures)}

    def meaning_curve_generation(self, sections: Sequence[str]) -> List[float]:
        if not sections:
            return []
        curve: List[float] = []
        for section in sections:
            unique_words = len(set(_words(section)))
            total_words = len(_words(section)) or 1
            curve.append(round(unique_words / total_words, 3))
        return curve


class TonalityEngine:
    """Provide basic tonal reasoning for the v6 pipeline."""

    def __init__(self) -> None:
        self._tone = ToneSyncEngine()

    def mode_detection(self, emotions: Dict[str, float], tlp: Dict[str, float]) -> Dict[str, Any]:
        love = emotions.get("joy", 0) + emotions.get("peace", 0)
        sadness = emotions.get("sadness", 0)
        anger = emotions.get("anger", 0)
        if sadness > max(love, anger):
            mode = "minor"
        elif anger > love:
            mode = "modal"
        else:
            mode = "major"
        confidence = round(max(love, sadness, anger), 3)
        return {"mode": mode, "confidence": confidence, "tlp_cf": tlp.get("conscious_frequency")}

    def major_minor_classifier(self, sections: Sequence[str], mode: str) -> str:
        if not sections:
            return mode
        melancholy_lines = sum("""sad""" in section.lower() or """тоск""" in section.lower() for section in sections)
        if melancholy_lines > len(sections) // 2:
            return "minor"
        if any("rise" in section.lower() or "свет" in section.lower() for section in sections):
            return "major"
        return mode

    def section_key_selection(self, sections: Sequence[str], mode: str) -> List[str]:
        keys = []
        palette = ["C", "G", "D", "A", "E", "B", "F#", "C#"]
        for idx, section in enumerate(sections):
            seed = sum(ord(ch) for ch in section) + idx
            key = palette[seed % len(palette)]
            keys.append(f"{key} {mode}")
        return keys

    def modal_shift_detection(self, section_keys: Sequence[str]) -> Dict[str, Any]:
        if not section_keys:
            return {"shifts": [], "count": 0}
        shifts = []
        for idx in range(1, len(section_keys)):
            prev = section_keys[idx - 1]
            current = section_keys[idx]
            if prev != current:
                shifts.append({"index": idx, "from": prev, "to": current})
        return {"shifts": shifts, "count": len(shifts)}

    def key_transition_curve(self, section_keys: Sequence[str]) -> List[str]:
        return list(section_keys)


class InstrumentationEngine:
    """Bridge the convenience helpers from :mod:`studiocore.instrument`."""

    def __init__(self) -> None:
        self._library = InstrumentLibrary()

    def instrument_selection(self, **kwargs: Any) -> Dict[str, Any]:
        return _instrument_selection(**kwargs)

    def instrument_based_on_emotion(self, emotions: Dict[str, float], **kwargs: Any) -> Dict[str, Any]:
        return _instrument_based_on_emotion(emotions, **kwargs)

    def instrument_based_on_voice(self, voice_profile: str | None, **kwargs: Any) -> Dict[str, Any]:
        return _instrument_based_on_voice(voice_profile, **kwargs)

    def instrument_color_sync(self, color_profile: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        return _instrument_color_sync(color_profile, **kwargs)

    def instrument_rhythm_sync(self, bpm: float, **kwargs: Any) -> Dict[str, Any]:
        return _instrument_rhythm_sync(bpm, **kwargs)


class REM_Synchronizer:
    """Coordinate cross-layer alignment for REM (Rhythmic Emotional Matrix)."""

    def detect_layer_conflicts(
        self,
        structure: Dict[str, Any],
        bpm_curve: Sequence[float],
        instrumentation: Dict[str, Any],
    ) -> Dict[str, Any]:
        sections = structure.get("sections", [])
        conflict_notes: List[str] = []
        level = 0.0
        if sections and bpm_curve and len(sections) != len(bpm_curve):
            level += 0.3
            conflict_notes.append("BPM curve length differs from section count.")
        energy = instrumentation.get("energy", 0.5)
        if energy > 0.8 and bpm_curve and min(bpm_curve) < 90:
            level += 0.4
            conflict_notes.append("High instrumental energy with slow tempo segments.")
        return {
            "has_conflict": level > 0.0,
            "conflict_level": round(level, 2),
            "notes": conflict_notes,
        }

    def resolve_layer_conflicts(self, conflicts: Dict[str, Any]) -> Dict[str, Any]:
        if not conflicts.get("has_conflict"):
            return {"actions": ["No adjustments required."], "status": "stable"}
        actions = [
            "Re-balance percussion energy",
            "Adjust arrangement dynamics",
        ]
        return {"actions": actions, "status": "mitigated"}

    def assign_dominant_layer(self, *, structure: Dict[str, Any], emotion: Dict[str, Any]) -> Dict[str, Any]:
        sections = structure.get("sections", [])
        dominant_emotion = max(emotion.get("profile", {"peace": 1.0}), key=emotion.get("profile", {"peace": 1.0}).get)
        if len(sections) >= 4 and dominant_emotion in {"joy", "epic"}:
            layer = "rhythm"
        elif dominant_emotion in {"sadness", "fear"}:
            layer = "melody"
        else:
            layer = "harmonic"
        return {"layer": layer, "rationale": f"Dominant emotion '{dominant_emotion}'"}

    def align_layers_for_final_output(
        self,
        structure: Dict[str, Any],
        instrumentation: Dict[str, Any],
        tonality: Dict[str, Any],
    ) -> Dict[str, Any]:
        section_keys = tonality.get("section_keys", [])
        return {
            "sections": structure.get("sections", []),
            "instrument_palette": instrumentation.get("palette", []),
            "section_keys": section_keys,
        }


class ZeroPulseEngine:
    """Handle silent segments that should be preserved in the arrangement."""

    def detect_zero_pulse(self, text: str) -> Dict[str, Any]:
        sections = _section_texts(text)
        zero_sections = [idx for idx, section in enumerate(sections) if not section.strip() or "[silence]" in section.lower()]
        return {"has_zero_pulse": bool(zero_sections), "sections": zero_sections}

    def vacuum_beat_state(self, text: str) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        state = "active" if zero["has_zero_pulse"] else "inactive"
        return {"state": state, "count": len(zero["sections"])}

    def silence_as_emotion(self, text: str, emotions: Dict[str, float]) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        peace = emotions.get("peace", 0.0)
        return {
            "aligned_emotion": "peace" if peace >= 0.3 else "neutral",
            "zero_pulse_sections": zero["sections"],
        }

    def silence_as_transition(self, text: str) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        transitions = [
            {"from": idx, "to": idx + 1, "type": "silence-gap"}
            for idx in zero["sections"]
        ]
        return {"transitions": transitions}


class CommandInterpreter:
    """Parse inline commands that control arrangement parameters."""

    def detect_commands_in_text(self, text: str) -> List[Dict[str, Any]]:
        commands: List[Dict[str, Any]] = []
        for match in _COMMAND_RE.finditer(text):
            commands.append(
                {
                    "type": match.group("name").lower(),
                    "value": match.group("value").strip(),
                    "raw": match.group(0),
                    "position": match.start(),
                }
            )
        return commands

    def _extract_command(self, commands: Iterable[Dict[str, Any]], names: Sequence[str]) -> Dict[str, Any] | None:
        for command in commands:
            if command.get("type") in names:
                return command
        return None

    def execute_bpm_commands(self, commands: Iterable[Dict[str, Any]], base_bpm: int | None = None) -> Dict[str, Any]:
        command = self._extract_command(commands, ["bpm", "tempo"])
        if not command:
            return {"bpm": base_bpm}
        try:
            value = float(command["value"])
        except ValueError:
            return {"bpm": base_bpm, "error": "invalid_value"}
        return {"bpm": int(round(value)), "source": command["raw"]}

    def execute_key_commands(self, commands: Iterable[Dict[str, Any]], default_key: str | None = None) -> Dict[str, Any]:
        command = self._extract_command(commands, ["key", "scale"])
        if not command:
            return {"key": default_key}
        return {"key": command["value"], "source": command["raw"]}

    def execute_rhythm_commands(self, commands: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        command = self._extract_command(commands, ["rhythm", "groove"])
        if not command:
            return {"rhythm": None}
        return {"rhythm": command["value"], "source": command["raw"]}

    def execute_emotion_commands(self, commands: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        command = self._extract_command(commands, ["emotion", "mood"])
        if not command:
            return {"emotion": None}
        return {"emotion": command["value"], "source": command["raw"]}


class StyleEngine:
    """Assemble stylistic guidance for the arrangement and prompts."""

    GENRE_MAP = {
        "joy": "indie pop",
        "sadness": "ambient ballad",
        "anger": "industrial rock",
        "fear": "cinematic darkwave",
        "peace": "neo-classical",
        "epic": "epic orchestral",
    }

    def genre_selection(self, emotions: Dict[str, float], tlp: Dict[str, float]) -> str:
        if not emotions:
            return "ambient"
        dominant = max(emotions, key=emotions.get)
        return self.GENRE_MAP.get(dominant, "experimental")

    def mood_selection(self, emotions: Dict[str, float], tlp: Dict[str, float]) -> str:
        cf = tlp.get("conscious_frequency", 0.5)
        if cf > 0.7:
            return "uplifting"
        if cf < 0.4:
            return "melancholic"
        return "reflective"

    def instrumentation_style(self, instrumentation: Dict[str, Any]) -> str:
        palette = instrumentation.get("selected") or instrumentation.get("toolkit") or []
        return ", ".join(palette) if palette else "minimal instrumentation"

    def vocal_style(self, vocal: Dict[str, Any]) -> str:
        profile = vocal.get("style", "lyrical")
        tone = vocal.get("tone", "balanced")
        return f"{tone} {profile}"

    def visual_style(self, color_profile: Dict[str, Any]) -> str:
        return f"{color_profile.get('primary_color', 'neutral light')} with {color_profile.get('accent_color', 'soft accents')}"

    def tone_style(self, tonality: Dict[str, Any]) -> str:
        return f"{tonality.get('mode', 'major')} mood, keys {', '.join(tonality.get('section_keys', []))}"

    def final_style_prompt_build(self, *, genre: str, mood: str, instrumentation: str, vocal: str, visual: str, tone: str) -> str:
        return (
            f"Genre: {genre}; Mood: {mood}; Vocals: {vocal}; Instruments: {instrumentation}; "
            f"Visuals: {visual}; Tonality: {tone}."
        )


class UserOverrideEngine:
    """Bridge between overrides and the logical engine payloads."""

    def resolve_bpm(self, manager: UserOverrideManager, auto_bpm: float | None) -> float | None:
        return manager.resolve_bpm(auto_bpm)

    def apply_to_rhythm(self, rhythm_payload: Dict[str, Any], manager: UserOverrideManager) -> Dict[str, Any]:
        return manager.apply_to_rhythm(rhythm_payload)

    def apply_to_style(self, style_payload: Dict[str, Any], manager: UserOverrideManager) -> Dict[str, Any]:
        return manager.apply_to_style(style_payload)

    def apply_to_vocals(self, vocal_payload: Dict[str, Any], manager: UserOverrideManager) -> Dict[str, Any]:
        return manager.apply_to_vocals(vocal_payload)


class UserAdaptiveSymbiosisEngine:
    """Merge user intent with automatically generated layers."""

    def collect_user_params(self, manager: UserOverrideManager) -> Dict[str, Any]:
        return manager.debug_summary()

    def merge_user_with_auto_core(self, manager: UserOverrideManager, auto_payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(auto_payload)
        merged["user"] = self.collect_user_params(manager)
        return merged

    def recalculate_rhythm_under_user_settings(
        self, manager: UserOverrideManager, rhythm_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return manager.apply_to_rhythm(rhythm_payload)

    def recalculate_tone_under_user_settings(
        self, manager: UserOverrideManager, tonality_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = dict(tonality_payload)
        if manager.overrides.key:
            payload["manual_key"] = manager.overrides.key
            payload["mode"] = payload.get("mode") or "user"
        return payload

    def recalculate_vocals_under_user_settings(
        self, manager: UserOverrideManager, vocal_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return manager.apply_to_vocals(vocal_payload)

    def recalculate_instrumental_under_user_settings(
        self, manager: UserOverrideManager, instrumentation_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = dict(instrumentation_payload)
        if manager.overrides.instrumentation:
            payload["palette"] = list(manager.overrides.instrumentation)
            payload["source"] = "user"
        return payload

    def build_final_symbiosis_state(
        self,
        manager: UserOverrideManager,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        rhythm = self.recalculate_rhythm_under_user_settings(manager, payload.get("bpm", {}))
        tone = self.recalculate_tone_under_user_settings(manager, payload.get("tonality", {}))
        vocal = self.recalculate_vocals_under_user_settings(manager, payload.get("vocal", {}))
        instrumentation = self.recalculate_instrumental_under_user_settings(manager, payload.get("instrumentation", {}))
        merged = self.merge_user_with_auto_core(manager, payload)
        merged.update(
            {
                "rhythm": rhythm,
                "tonality": tone,
                "vocal": vocal,
                "instrumentation": instrumentation,
            }
        )
        return merged


class LyricsAnnotationEngine:
    """Produce lightweight annotations for UI or downstream exporters."""

    def add_vocal_annotations(self, sections: Sequence[str], vocal: Dict[str, Any]) -> List[Dict[str, Any]]:
        intensity_curve = vocal.get("intensity_curve", [])
        annotations: List[Dict[str, Any]] = []
        for idx, section in enumerate(sections):
            intensity = intensity_curve[idx] if idx < len(intensity_curve) else vocal.get("average_intensity", 0.5)
            annotations.append({"section": idx, "type": "vocal", "intensity": round(float(intensity), 3)})
        return annotations

    def add_breath_annotations(self, sections: Sequence[str], breathing: Dict[str, Any]) -> List[Dict[str, Any]]:
        inhale = set(breathing.get("inhale_points", []))
        return [
            {"section": idx, "type": "breath", "marker": "inhale" if idx in inhale else "flow"}
            for idx in range(len(sections))
        ]

    def add_tonal_annotations(self, sections: Sequence[str], tonality: Dict[str, Any]) -> List[Dict[str, Any]]:
        keys = tonality.get("section_keys", [])
        return [
            {"section": idx, "type": "tonality", "key": keys[idx] if idx < len(keys) else tonality.get("mode")}
            for idx in range(len(sections))
        ]

    def add_emotional_annotations(self, sections: Sequence[str], emotions: Dict[str, Any]) -> List[Dict[str, Any]]:
        profile = emotions.get("profile", {})
        dominant = max(profile, key=profile.get) if profile else "neutral"
        return [
            {"section": idx, "type": "emotion", "dominant": dominant}
            for idx in range(len(sections))
        ]

    def add_rhythm_annotations(self, sections: Sequence[str], bpm_curve: Sequence[float]) -> List[Dict[str, Any]]:
        return [
            {"section": idx, "type": "rhythm", "bpm": bpm_curve[idx] if idx < len(bpm_curve) else None}
            for idx in range(len(sections))
        ]


class FinalCompiler:
    """Merge logical engine outputs into a convenient response payload."""

    def merge_all_layers(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = {
            "engine": "StudioCoreV6",
            "legacy": payload.get("legacy"),
            "structure": payload.get("structure"),
            "emotion": payload.get("emotion"),
            "color": payload.get("color"),
            "vocal": payload.get("vocal"),
            "breathing": payload.get("breathing"),
            "bpm": payload.get("bpm"),
            "meaning": payload.get("meaning"),
            "tonality": payload.get("tonality"),
            "instrumentation": payload.get("instrumentation"),
            "rem": payload.get("rem"),
            "zero_pulse": payload.get("zero_pulse"),
            "style": payload.get("style"),
            "commands": payload.get("commands"),
        }
        return merged

    def generate_final_structure(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sections = payload.get("structure", {}).get("sections", [])
        return {
            "section_count": len(sections),
            "sections": sections,
            "intro": payload.get("structure", {}).get("intro"),
            "chorus": payload.get("structure", {}).get("chorus"),
            "outro": payload.get("structure", {}).get("outro"),
        }

    def generate_final_prompt(self, payload: Dict[str, Any]) -> str:
        style = payload.get("style", {})
        return style.get("prompt", "")

    def generate_final_annotations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return payload.get("annotations", {})

    def consistency_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if not payload.get("structure", {}).get("sections"):
            issues.append("Structure lacks sections")
        if not payload.get("emotion", {}).get("profile"):
            issues.append("Emotion profile missing")
        if not payload.get("style", {}).get("prompt"):
            issues.append("Style prompt missing")
        return {"issues": issues, "is_consistent": not issues}
