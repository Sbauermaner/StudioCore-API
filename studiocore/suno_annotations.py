"""Helpers that produce Suno-safe annotations according to the Codex rules."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence


class SunoAnnotationEngine:
    """Wrap annotations with English parenthesised commands."""

    def build_suno_safe_annotations(self, sections: Sequence[str], diagnostics: Dict[str, Any]) -> List[str]:
        headers = self.generate_section_headers(sections)
        annotations = []
        for idx, header in enumerate(headers):
            meta = [header]
            meta.extend(self.attach_bpm_and_fracture_commands(diagnostics, idx))
            meta.extend(self.attach_vocal_and_instrumental_commands(diagnostics, idx))
            meta.extend(self.insert_parenthesized_commands(diagnostics.get("commands", {}), idx))
            annotations.append(" ".join(meta))
        return self.protect_annotations_from_lyrics(annotations)

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
