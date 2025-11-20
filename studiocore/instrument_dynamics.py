# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Instrument dynamics mapping required by the StudioCore Codex."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence


class InstrumentalDynamicsEngine:
    """Maps section energy, BPM and emotion to dynamic cues."""

    def section_instrument_density_map(self, sections: Sequence[str], palette: Sequence[str] | None = None) -> List[Dict[str, Any]]:
        density_map: List[Dict[str, Any]] = []
        palette = list(palette or [])
        for idx, section in enumerate(sections):
            token_count = len(section.split()) or 1
            density = min(1.0, token_count / 120)
            density_map.append(
                {
                    "section": idx,
                    "density": round(density, 3),
                    "suggested_layer": palette[idx % len(palette)] if palette else None,
                }
            )
        return density_map

    def apply_bpm_to_instrumental_feel(self, bpm_payload: Dict[str, Any], palette: Sequence[str] | None = None) -> Dict[str, Any]:
        bpm = bpm_payload.get("estimate") or 100
        feel = "laid_back" if bpm < 90 else "energetic" if bpm > 130 else "balanced"
        return {
            "bpm": bpm,
            "feel": feel,
            "palette_bias": list(palette or [])[:4],
        }

    def apply_emotion_to_instrumental_intensity(self, emotion_payload: Dict[str, Any]) -> Dict[str, Any]:
        profile = emotion_payload.get("profile") or {}
        dominant = max(profile, key=profile.get) if profile else "peace"
        intensity = 0.3 if dominant in {"peace", "sadness"} else 0.8
        return {"dominant": dominant, "intensity": intensity}

    def detect_instrumental_fracture_points(self, bpm_curve: Sequence[float]) -> List[int]:
        fractures: List[int] = []
        for idx in range(len(bpm_curve) - 1):
            if abs(bpm_curve[idx] - bpm_curve[idx + 1]) > 20:
                fractures.append(idx + 1)
        return fractures

    def instrumental_zero_pulse_alignment(self, zero_pulse_payload: Dict[str, Any], sections: Sequence[str]) -> Dict[str, Any]:
        hints = zero_pulse_payload.get("analysis", {})
        silence_sections = [idx for idx, section in enumerate(sections) if "(silence)" in section.lower()]
        return {
            "zero_pulse": hints,
            "sections": silence_sections,
        }

    def map_instruments_to_structure(
        self,
        sections: Sequence[str],
        palette: Sequence[str] | None,
        bpm_payload: Dict[str, Any],
        emotion_payload: Dict[str, Any],
        zero_pulse_payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        palette = list(palette or [])
        density = self.section_instrument_density_map(sections, palette)
        bpm_feel = self.apply_bpm_to_instrumental_feel(bpm_payload, palette)
        emotion_intensity = self.apply_emotion_to_instrumental_intensity(emotion_payload)
        fractures = self.detect_instrumental_fracture_points(bpm_payload.get("curve", []) or [])
        zero = self.instrumental_zero_pulse_alignment(zero_pulse_payload or {}, sections)
        mapping: List[Dict[str, Any]] = []
        for idx, section in enumerate(sections):
            mapping.append(
                {
                    "section": idx,
                    "instrument": palette[idx % len(palette)] if palette else None,
                    "density": density[idx]["density"] if idx < len(density) else 0.5,
                    "fracture": idx in fractures,
                }
            )
        return {
            "density": density,
            "bpm": bpm_feel,
            "emotion": emotion_intensity,
            "fractures": fractures,
            "zero_pulse": zero,
            "mapping": mapping,
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
