# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Helpers that produce Suno-safe annotations according to the Codex rules."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence


class EmotionDrivenSunoAdapter:
    """
    Converts global_emotion_curve + section_emotions into dynamic Suno-style annotations.
    Does NOT pick genre/BPM/key — only musical behavior (intensity, instruments, vocals).
    """

    def __init__(self, text: str, sections: Sequence[Dict[str, Any]], emotion_curve: Dict[str, Any]):
        self.text = text
        self.sections = list(sections or [])
        self.emotion_curve = emotion_curve or {}

    def build(self) -> Dict[str, Any]:
        style = self._resolve_style()
        vocal_profile = self._resolve_vocal_profile()
        instrumentation = self._resolve_instrumentation()
        section_annotations = self._build_section_annotations()

        return {
            "style": style,
            "vocal_profile": vocal_profile,
            "instrumentation": instrumentation,
            "section_annotations": section_annotations,
        }

    # --- Internal helpers ---
    def _resolve_style(self) -> str:
        cluster = (self.emotion_curve or {}).get("dominant_cluster") or ""
        table = {
            "rage": "dark metal / industrial adaptive",
            "despair": "darkwave / gothic cinematic",
            "tender": "lyrical ballad / neoclassical",
            "hope": "ambient uplifting / orchestral light",
            "narrative": "poetic acoustic / indie narrative",
        }
        return table.get(cluster, "adaptive hybrid")

    def _resolve_vocal_profile(self) -> str:
        tlp = (self.emotion_curve or {}).get("global_tlp") or {}
        truth = float(tlp.get("truth") or 0.0)
        love = float(tlp.get("love") or 0.0)
        pain = float(tlp.get("pain") or 0.0)
        profiles = []
        threshold = 0.6
        if pain >= threshold:
            profiles.append("distorted male low + aggressive fry")
        if love >= threshold:
            profiles.append("soft female airy + close mic")
        if truth >= threshold:
            profiles.append("spoken male baritone + clean harmonics")

        if not profiles:
            # choose the strongest axis as a fallback
            dominant_axis = max(("truth", truth), ("love", love), ("pain", pain), key=lambda item: item[1])
            axis_map = {
                "pain": "distorted male low + aggressive fry",
                "love": "soft female airy + close mic",
                "truth": "spoken male baritone + clean harmonics",
            }
            profiles.append(axis_map.get(dominant_axis[0], "adaptive vocal blend"))

        return " / ".join(profiles)

    def _resolve_instrumentation(self) -> str:
        cluster = (self.emotion_curve or {}).get("dominant_cluster") or ""
        mapping = {
            "rage": "distorted guitars, hard drums, sub-bass pulses",
            "despair": "distorted guitars, hard drums, sub-bass pulses",
            "tender": "piano, cello, warm pads",
            "hope": "high strings, bells, shimmer layers",
            "narrative": "acoustic guitar, soft percussion",
        }
        return mapping.get(cluster, "hybrid adaptive instrumentation")

    def _build_section_annotations(self) -> Dict[str, str]:
        annotations: Dict[str, str] = {}
        for entry in self.sections:
            section_name = entry.get("section") or entry.get("name") or "section"
            intensity = self._safe_float(entry.get("intensity"))
            intensity_label = self._intensity_label(intensity)
            hot_phrases = [
                f'hot phrase: "{phrase}" → emphasize with vocal stress / pause'
                for phrase in (entry.get("hot_phrases") or [])
                if phrase
            ]
            annotation = intensity_label
            if hot_phrases:
                annotation = f"{annotation}; " + " | ".join(hot_phrases)
            annotations[str(section_name)] = annotation
        return annotations

    def _intensity_label(self, intensity: float) -> str:
        if intensity > 0.8:
            return "MAX intensity: full instruments, wide reverb"
        if 0.5 <= intensity <= 0.8:
            return "MID intensity: moderate build"
        return "LOW intensity: minimal instruments"

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


def _dominant_emotion(vectors):
    """
    Определяет доминирующую эмоцию по сглаженным векторам.
    Возвращает: "dark", "love", "rage", "melancholic", "epic", "hope"
    """
    if not vectors:
        return "neutral"

    total_valence = sum(v.valence for v in vectors) / len(vectors)
    total_arousal = sum(v.arousal for v in vectors) / len(vectors)
    total_pain = sum(v.pain for v in vectors) / len(vectors)

    # НАБОР ПРАВИЛ ДЛЯ ЭМОЦИЙ — НЕ МЕНЯТЬ
    if total_pain > 0.6 and total_valence < -0.3:
        return "dark"
    if total_pain > 0.5 and total_arousal > 0.5:
        return "rage"
    if total_valence > 0.6 and total_arousal > 0.4:
        return "hope"
    if total_valence > 0.5 and total_pain < 0.2:
        return "love"
    if total_valence < -0.2 and total_arousal < 0.3:
        return "melancholic"
    if total_arousal > 0.7:
        return "epic"

    return "neutral"


def emotion_to_instruments(emotion: str) -> List[str]:
    """
    Подбор инструментов по эмоции.
    Это ПРАВИЛА, НЕ ИИ.
    """
    table = {
        "dark": ["cello", "low choir", "synth pads", "metallic hits"],
        "rage": ["distorted guitars", "blast beat", "aggro bass", "choir shouts"],
        "love": ["acoustic guitar", "soft piano", "warm strings", "harp"],
        "hope": ["piano", "string ensemble", "soft drums", "airy synth"],
        "melancholic": ["cello", "ambient pads", "piano", "soft drums"],
        "epic": ["full orchestra", "toms", "horns", "epic choir"],
        "neutral": ["piano", "cello"],
    }
    return table.get(emotion, table["neutral"])


def emotion_to_vocal(emotion: str) -> str:
    """
    Подбор вокала по эмоции.
    """
    table = {
        "dark": "male low whisper + distant choir",
        "rage": "male harsh / female aggressive",
        "love": "soft female alto / gentle male tenor",
        "hope": "female airy soprano",
        "melancholic": "male baritone soft",
        "epic": "layered choir",
        "neutral": "auto",
    }
    return table.get(emotion, "auto")


def emotion_to_style(emotion: str) -> str:
    """
    Отдаём стилистический лейбл для Suno.
    """
    table = {
        "dark": "dark gothic dramatic",
        "rage": "extreme rage industrial",
        "love": "romantic emotional ballad",
        "hope": "uplifting cinematic heroic",
        "melancholic": "melancholic soft indie",
        "epic": "epic orchestral hybrid",
        "neutral": "cinematic narrative",
    }
    return table.get(emotion, "cinematic narrative")


def build_suno_annotations(text: str, sections: Sequence[Dict[str, Any]], emotion_curve: Dict[str, Any]) -> Dict[str, Any]:
    adapter = EmotionDrivenSunoAdapter(text, sections, emotion_curve)
    return adapter.build()


class SunoAnnotationEngine:
    """Wrap annotations with English parenthesised commands."""

    def build_suno_safe_annotations(self, sections: Sequence[str], diagnostics: Dict[str, Any]) -> List[str]:
        headers = self.generate_section_headers(sections, diagnostics)
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

    def _starts_with_ljubimaya(self, section: str) -> bool:
        return section.strip().startswith("Любимая!")

    def _has_direct_address_peak(self, section: str, diagnostics: Dict[str, Any] | None) -> bool:
        lowered = section.lower()
        direct_tokens = ("ты", "тебя", "тебе", "твой", "любимая", "дорогая", "друг мой")
        address_hit = any(token in lowered for token in direct_tokens)
        emotional_peak = section.count("!") >= 1 or section.count("!") + section.count("?") >= 2
        if not address_hit:
            return False
        if emotional_peak:
            return True
        commands = diagnostics.get("commands", {}) if isinstance(diagnostics, dict) else {}
        return bool(commands)

    def generate_section_headers(self, sections: Sequence[str], diagnostics: Dict[str, Any] | None = None) -> List[str]:
        headers = []
        labels = ("Intro", "Verse", "Pre-Chorus", "Chorus", "Bridge", "Outro")
        for idx in range(len(sections)):
            section_text = sections[idx] if idx < len(sections) else ""
            label = labels[idx % len(labels)]
            chorus_override = False
            if self._starts_with_ljubimaya(section_text):
                label = "Chorus"
                chorus_override = True
            elif self._has_direct_address_peak(section_text, diagnostics):
                label = "Chorus"
                chorus_override = True
            header = f"{label} {idx + 1}"
            if chorus_override:
                header = f"{header} ★"
            headers.append(header)
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
