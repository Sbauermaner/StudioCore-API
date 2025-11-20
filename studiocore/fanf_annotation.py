"""FANF cinematic annotation engine.

This module builds three synchronized outputs:
- annotated_text_fanf: cinematic, richly formatted output for internal use
- annotated_text_ui: concise UI-friendly annotation
- annotated_text_suno: Suno-safe annotation with FANF cues

The engine is intentionally defensive: missing fields are tolerated and
fallback placeholders are used so the pipeline never breaks downstream
formatters.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence


def _safe(value: Any, default: str = "—") -> str:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return str(round(value, 3)) if isinstance(value, float) else str(value)
    if isinstance(value, str):
        return value or default
    return str(value) or default


def _first(iterable: Iterable[str], default: str = "—") -> str:
    for item in iterable:
        if item:
            return str(item)
    return default


@dataclass
class FANFAnnotation:
    annotated_text_fanf: str
    annotated_text_ui: str
    annotated_text_suno: str
    choir_active: bool
    cinematic_header: str
    resonance_header: str


class FANFAnnotationEngine:
    """Constructs FANF cinematic annotations with dynamic choir logic."""

    CHOIR_KEYWORDS = (
        "sacred",
        "cathedral",
        "tragic",
        "dramatic",
        "elevated",
        "epic",
        "solemn",
        "hymn",
        "prayer",
        "monastery",
        "spiritual",
        "litany",
        "anthem",
        "возвыш",
        "траг",
        "сакрал",
        "храм",
        "молит",
        "катедрал",
    )

    INTIMATE_KEYWORDS = (
        "whisper",
        "intimate",
        "minimal",
        "bedroom",
        "lofi",
        "fragile",
        "tender",
        "ласк",
        "шепот",
        "шёпот",
        "тих",
        "минимал",
    )

    def build_annotations(
        self,
        text: str,
        sections: Sequence[str],
        analysis: Dict[str, Any] | None,
    ) -> FANFAnnotation:
        if not isinstance(sections, list):
            sections = list(sections.values()) if isinstance(sections, dict) else list(sections or [])
        analysis = analysis or {}
        emotion = analysis.get("emotion", {})
        bpm = analysis.get("bpm", {})
        tonality = analysis.get("tonality", {})
        style = analysis.get("style", {})
        tlp = analysis.get("tlp", {})
        zero_pulse = analysis.get("zero_pulse", {})
        color_wave = analysis.get("color", {}).get("wave") if isinstance(analysis.get("color"), dict) else None
        instrumentation = analysis.get("instrumentation", {})
        rde = analysis.get("rde", {})

        choir_active = self._should_add_choir(text, emotion)
        cinematic_header = self._build_cinematic_header(style, bpm, tonality, tlp)
        resonance_header = self._build_resonance_header(instrumentation, choir_active)

        section_descriptors = self._build_sections(sections, bpm, tonality, emotion)

        annotations = self._compose_annotation(
            cinematic_header,
            resonance_header,
            section_descriptors,
            zero_pulse,
            color_wave,
            tonality,
            rde,
            choir_active,
        )

        ui_annotation = self._build_ui_annotation(
            cinematic_header,
            section_descriptors,
            choir_active,
            color_wave,
        )

        suno_annotation = self._build_suno_annotation(
            cinematic_header,
            resonance_header,
            section_descriptors,
            choir_active,
        )

        return FANFAnnotation(
            annotated_text_fanf=annotations,
            annotated_text_ui=ui_annotation,
            annotated_text_suno=suno_annotation,
            choir_active=choir_active,
            cinematic_header=cinematic_header,
            resonance_header=resonance_header,
        )

    # Internal helpers -------------------------------------------------
    def _should_add_choir(self, text: str, emotion: Dict[str, Any]) -> bool:
        text_lower = text.lower()
        sadness_score = 0.0
        if isinstance(emotion, dict):
            profile = emotion.get("profile", {}) if isinstance(emotion.get("profile"), dict) else {}
            sadness_score = float(profile.get("sadness") or emotion.get("sadness") or 0.0)

        keyword_trigger = any(token in text_lower for token in (
            "chorus",
            "choir",
            "prayer",
            "echo",
            "stone",
            "gothic",
            "cathedral",
        ))

        return sadness_score > 0.55 or keyword_trigger

    def _build_cinematic_header(
        self, style: Dict[str, Any], bpm: Dict[str, Any], tonality: Dict[str, Any], tlp: Dict[str, Any]
    ) -> str:
        genre = _safe(style.get("genre")) if isinstance(style, dict) else "—"
        mood = _safe(style.get("mood")) if isinstance(style, dict) else "—"
        bpm_val = _safe(bpm.get("estimate"), "120") if isinstance(bpm, dict) else "120"
        key = _safe(tonality.get("mode"), "auto") if isinstance(tonality, dict) else "auto"
        anchor = _first(tonality.get("section_keys", []), "C") if isinstance(tonality, dict) else "C"
        freq = _safe(tlp.get("base_hz", tlp.get("base_frequency", 432)), "432") if isinstance(tlp, dict) else "432"
        consciousness = _safe(tlp.get("consciousness_level", tlp.get("consciousness", 0.72)), "0.72")

        return (
            f"[GenreFusion: {genre} / {mood} | BPM: {bpm_val} | Key/Mode: {anchor} {key} | "
            f"A={freq} Hz | Conscious Frequency: {consciousness}]"
        )

    def _build_resonance_header(self, instrumentation: Dict[str, Any], choir_active: bool) -> str:
        palette = instrumentation.get("palette") if isinstance(instrumentation, dict) else []
        primary_instruments = ", ".join(palette) if palette else "adaptive blend"
        fx = instrumentation.get("selection", {}).get("fx") if isinstance(instrumentation.get("selection", {}), dict) else None
        fx_block = fx or "bells, whispers, stone hall" if choir_active else "micro fx & air"
        atmosphere = instrumentation.get("emotion", {}).get("atmosphere") if isinstance(instrumentation.get("emotion"), dict) else None
        texture = instrumentation.get("voice", {}).get("style") if isinstance(instrumentation.get("voice"), dict) else "solo voice"

        choir_label = "ChoirLayers active" if choir_active else "Solo/duet focus"
        return (
            f"[VocalTexture: {texture} + {choir_label} | ChoirLayers + InstrumentBlend: {primary_instruments} | "
            f"FX: {fx_block} | Atmosphere: {_safe(atmosphere, 'wide space')} ]"
        )

    def _build_sections(
        self,
        sections: Sequence[str],
        bpm: Dict[str, Any],
        tonality: Dict[str, Any],
        emotion: Dict[str, Any],
    ) -> List[str]:
        labels = [
            "Intro",
            "Verse 1",
            "Pre-Chorus",
            "Chorus",
            "Bridge",
            "Final Chorus",
            "Outro",
        ]
        bpm_val = _safe(bpm.get("estimate"), "120") if isinstance(bpm, dict) else "120"
        modal_shifts_raw = tonality.get("modal_shifts") if isinstance(tonality, dict) else []
        modal_shifts = (
            list(modal_shifts_raw.values())
            if isinstance(modal_shifts_raw, dict)
            else list(modal_shifts_raw or [])
        )
        emotion_profile = emotion.get("profile", {}) if isinstance(emotion, dict) else {}
        intensity_raw = emotion.get("curve", []) if isinstance(emotion, dict) else []
        intensity = list(intensity_raw.values()) if isinstance(intensity_raw, dict) else list(intensity_raw or [])

        descriptors = []
        for idx, section in enumerate(list(sections or [])):
            label = labels[idx] if idx < len(labels) else f"Section {idx + 1}"
            tone = _first(modal_shifts[idx:idx + 1], "stable") if modal_shifts else "stable"
            height = round(intensity[idx] * 100) if idx < len(intensity) else 50
            color_hint = _first(emotion_profile.keys(), "emotion blend") if emotion_profile else "emotion blend"
            descriptors.append(f"[{label}: Rhythm~{bpm_val} | Mode: {tone} | Intensity: {height}% | ColorWave: {color_hint}]")

        if not descriptors:
            descriptors.append("[Intro: Adaptive entry | Rhythm~120 | Mode: stable | Intensity: 50% | ColorWave: neutral]")
        return descriptors

    def _compose_annotation(
        self,
        cinematic_header: str,
        resonance_header: str,
        sections: Sequence[str],
        zero_pulse: Dict[str, Any],
        color_wave: Any,
        tonality: Dict[str, Any],
        rde: Dict[str, Any],
        choir_active: bool,
    ) -> str:
        zero_map = zero_pulse.get("structure_hint") if isinstance(zero_pulse, dict) else None
        zero_line = f"ZeroPulse: {_safe(zero_map, 'none')}"
        resonance_map = f"Resonance map: {_safe(tonality.get('modal_shifts', []), 'stable')}"
        rde_line = f"RDE: {_safe(rde.get('state', rde.get('dominant_axis', 'balanced')))}"
        choir_line = "ChoirLayers: enabled" if choir_active else "ChoirLayers: off"
        color_line = f"ColorWave: {_safe(color_wave, 'adaptive gradient')}"

        body = "\n".join(sections)
        tail = " | ".join([zero_line, color_line, resonance_map, rde_line, choir_line])

        return f"{cinematic_header}\n{resonance_header}\n{body}\n{tail}"

    def _build_ui_annotation(
        self,
        cinematic_header: str,
        sections: Sequence[str],
        choir_active: bool,
        color_wave: Any,
    ) -> str:
        sections_block = "\n".join(sections)
        choir_state = "with emotional choir lift" if choir_active else "intimate vocal focus"
        return (
            f"{cinematic_header}\nUI Pathway ({choir_state})\n"
            f"Sections:\n{sections_block}\nColorWave → {_safe(color_wave, 'adaptive')}"
        )

    def _build_suno_annotation(
        self,
        cinematic_header: str,
        resonance_header: str,
        sections: Sequence[str],
        choir_active: bool,
    ) -> str:
        choir_tag = "(ChoirLayers ON)" if choir_active else "(No choir)"
        section_line = " ".join(sections)
        return f"{cinematic_header} {resonance_header} {section_line} {choir_tag}"

