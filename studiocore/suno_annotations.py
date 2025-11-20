"""Helpers that produce Suno-safe annotations according to the Codex rules."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence


class SunoAnnotationEngine:
    """Wrap annotations with English parenthesised commands."""

    def build_suno_safe_annotations(self, sections: Sequence[str], diagnostics: Dict[str, Any]) -> List[str]:
        headers = self.generate_section_headers(sections)
        annotations = []
        payload = {
            "legacy": diagnostics.get("legacy", {}),
            "out": diagnostics,
        }
        for header in headers:
            annotations.append(self.build_annotation(payload, section_label=header))
        return self.protect_annotations_from_lyrics(annotations)

    def build_annotation(self, payload: Dict[str, Any], section_label: str = "Section") -> str:
        legacy = payload.get("legacy", {}) if isinstance(payload.get("legacy"), dict) else {}
        out = payload.get("out", {}) if isinstance(payload.get("out"), dict) else {}
        style = legacy.get("style", {}) if isinstance(legacy.get("style"), dict) else {}

        genre = style.get("genre") or "auto"
        mood = style.get("mood") or "auto"
        energy = style.get("energy") or "auto"
        arrangement = style.get("arrangement") or "auto"
        bpm_source = legacy.get("bpm") if isinstance(legacy, dict) else None
        if bpm_source is None:
            bpm_source = out.get("bpm", {}).get("estimate") if isinstance(out.get("bpm"), dict) else None
        key = style.get("key") or "auto"

        bpm_label = bpm_source if bpm_source is not None else "auto"
        try:
            bpm_label = int(bpm_label)
        except Exception:
            bpm_label = bpm_label

        return f"[{section_label} - AUTO - {mood}, {energy}, {arrangement}, BPM≈{bpm_label}] (Genre={genre}, Key={key})"

    def protect_annotations_from_lyrics(self, annotations: Sequence[str]) -> List[str]:
        return [f"({item})" if not item.startswith("(") else item for item in annotations]

    def insert_parenthesized_commands(self, command_payload: Dict[str, Any], index: int) -> List[str]:
        detected = command_payload.get("detected", []) if isinstance(command_payload, dict) else []
        result = []
        for cmd in detected:
            raw = cmd.get("raw") if isinstance(cmd, dict) else None
            if raw:
                result.append(f"({raw})")
        return result[:2]

    def generate_section_headers(self, sections: Sequence[str]) -> List[str]:
        headers = []
        labels = ("Intro", "Verse", "Pre-Chorus", "Chorus", "Bridge", "Outro")
        for idx in range(len(sections)):
            headers.append(f"{labels[idx % len(labels)]} {idx + 1}")
        return headers

    def attach_bpm_and_fracture_commands(self, diagnostics: Dict[str, Any], index: int) -> List[str]:
        bpm = diagnostics.get("bpm", {}).get("estimate") if isinstance(diagnostics.get("bpm"), dict) else None
        fractures = diagnostics.get("instrumentation", {}).get("fractures") if isinstance(diagnostics.get("instrumentation"), dict) else []
        result = []
        if bpm:
            result.append(f"(BPM ~ {int(bpm)})")
        if fractures and index in fractures:
            result.append("(BPM Fracture)")
        return result

    def attach_vocal_and_instrumental_commands(self, diagnostics: Dict[str, Any], index: int) -> List[str]:
        vocal = diagnostics.get("vocal", {}) if isinstance(diagnostics.get("vocal"), dict) else {}
        instrumentation = diagnostics.get("instrumentation", {}).get("palette") if isinstance(diagnostics.get("instrumentation"), dict) else []
        result = []
        if vocal.get("style"):
            result.append(f"(Vocal: {vocal['style']})")
        if instrumentation:
            result.append(f"(Instruments IN: {instrumentation[index % len(instrumentation)]})")
        return result
