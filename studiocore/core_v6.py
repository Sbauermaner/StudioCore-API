"""StudioCore v6 compatibility wrapper.

The implementation does not aim to be feature-complete.  Instead it provides a
stable, testable façade that wires the existing monolith (v5) into the new
logical engines required by the Codex specification.  Each helper returns
structured data so downstream tooling can evolve without breaking imports.
"""
from __future__ import annotations

import copy
import os
import re
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Sequence

from .bpm_engine import BPMEngine
from .emotion_field import EmotionFieldEngine
from .emotion_profile import EmotionVector
from .rde_engine import RhythmDynamicsEmotionEngine
from .section_parser import SectionParser
from .tlp_engine import TruthLovePainEngine
from .logical_engines import (
    BreathingEngine,
    ColorEmotionEngine,
    CommandInterpreter,
    EmotionEngine,
    FinalCompiler,
    InstrumentationEngine,
    LyricsAnnotationEngine,
    MeaningVelocityEngine,
    REM_Synchronizer,
    StyleEngine,
    TextStructureEngine,
    TonalityEngine,
    UserAdaptiveSymbiosisEngine,
    UserOverrideEngine,
    VocalEngine,
    ZeroPulseEngine,
)
from .instrument_dynamics import InstrumentalDynamicsEngine
from .genre_matrix_extended import GenreMatrixExtended
from .section_intelligence import SectionIntelligenceEngine
from .suno_annotations import SunoAnnotationEngine
from .fanf_annotation import FANFAnnotationEngine
from .text_utils import (
    detect_language,
    extract_commands_and_tags,
    translate_text_for_analysis,
)
from .user_override_manager import UserOverrideManager, UserOverrides

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.

STUDIOCORE_LICENSE_ENV = os.getenv("STUDIOCORE_LICENSE", "").strip()

# Anti-piracy soft hook (does not block execution, only marks environment intent)
if STUDIOCORE_LICENSE_ENV == "":
    # Это "юридический крючок": факт запуска без указания лицензии можно трактовать как несанкционированное использование.
    pass


class StudioCoreV6:
    """Light-weight compatibility surface for the upcoming v6 engine."""

    def __init__(self) -> None:
        self.text_engine = TextStructureEngine()
        self.section_parser = SectionParser(self.text_engine)
        self.emotion_engine = EmotionEngine()
        self.color_engine = ColorEmotionEngine()
        self.vocal_engine = VocalEngine()
        self.breathing_engine = BreathingEngine()
        self.bpm_engine = BPMEngine()
        self.meaning_engine = MeaningVelocityEngine()
        self.tonality_engine = TonalityEngine()
        self.instrumentation_engine = InstrumentationEngine()
        self.section_intelligence = SectionIntelligenceEngine()
        self.instrument_dynamics = InstrumentalDynamicsEngine()
        self.genre_matrix = GenreMatrixExtended()
        self.rem_engine = REM_Synchronizer()
        self.zero_pulse_engine = ZeroPulseEngine()
        self.command_interpreter = CommandInterpreter()
        self.style_engine = StyleEngine()
        self.annotation_engine = LyricsAnnotationEngine()
        self.compiler = FinalCompiler()
        self.suno_engine = SunoAnnotationEngine()
        self.fanf_engine = FANFAnnotationEngine()
        self.override_engine = UserOverrideEngine()
        self.symbiosis_engine = UserAdaptiveSymbiosisEngine()
        self.tlp_engine = TruthLovePainEngine()
        self.rde_engine = RhythmDynamicsEmotionEngine()

        # Late import to avoid circular dependencies during module import time.
        from .monolith_v4_3_1 import StudioCore as LegacyCore  # pylint: disable=import-outside-toplevel

        self._legacy_core_cls = LegacyCore
        self._last_backend_payload: Dict[str, Any] = {}
        self._last_fanf_output: Dict[str, Any] = {}
        self._last_sections: Sequence[str] | None = None
        self._last_text: str | None = None
        self._last_fanf_context: Dict[str, Any] | None = None

    def analyze(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        incoming_text = text or ""
        params = self._merge_user_params(dict(kwargs))
        overrides: UserOverrides = params.get("user_overrides")
        override_manager = UserOverrideManager(overrides)
        cleaned_text, command_bundle, preserved_tags = extract_commands_and_tags(incoming_text)
        commands = list(command_bundle.get("detected", []))
        language_info = detect_language(cleaned_text)
        language_info["original_text_preview"] = cleaned_text[:500]
        translated_text, was_translated = translate_text_for_analysis(
            cleaned_text, language_info["language"]
        )
        language_info["was_translated"] = bool(was_translated)
        structure_context = self._build_structure_context(
            translated_text,
            params.get("semantic_hints"),
            commands=commands,
            preserved_tags=preserved_tags,
            language_info=language_info,
        )
        structure_context = self._apply_overrides_to_context(
            structure_context,
            override_manager,
            text=translated_text,
        )

        backend_payload = self._backend_analyze(
            translated_text,
            preferred_gender=params.get("preferred_gender", "auto"),
            version=params.get("version"),
            semantic_hints=structure_context.get("semantic_hints", {}),
            structure_context=structure_context,
            override_manager=override_manager,
            language_info=language_info,
            original_text=cleaned_text,
            command_bundle=command_bundle,
        )
        return self._finalize_result(backend_payload)

    def _merge_user_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(params)
        merged = {
            "preferred_gender": params.pop("preferred_gender", "auto"),
            "version": params.pop("version", None),
            "semantic_hints": {},
        }
        hints = params.pop("semantic_hints", None)
        if isinstance(hints, dict):
            merged["semantic_hints"] = self._merge_semantic_hints({}, hints)
        override_seed = {}
        for field in ("bpm", "key", "genre", "mood", "vocal_profile", "instrumentation", "structure_hints", "color_state"):
            if field in params:
                override_seed[field] = params.pop(field)
        user_override_dict = params.pop("user_overrides", None)
        if isinstance(user_override_dict, dict):
            override_seed = {**user_override_dict, **override_seed}
        overrides = UserOverrides.from_dict(override_seed)
        merged["user_overrides"] = overrides
        if overrides.semantic_hints:
            merged["semantic_hints"] = self._merge_semantic_hints(merged["semantic_hints"], overrides.semantic_hints)
        if overrides.structure_hints:
            merged["semantic_hints"] = self._merge_semantic_hints(
                merged["semantic_hints"], {"sections": overrides.structure_hints}
            )
        merged.update(params)
        return merged

    def _build_structure_context(
        self,
        text: str,
        existing_hints: Dict[str, Any] | None = None,
        *,
        commands: Sequence[Dict[str, Any]] | None = None,
        preserved_tags: Sequence[str] | None = None,
        language_info: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        existing_hints = dict(existing_hints or {})
        auto_sections = self.text_engine.auto_section_split(text)
        hinted_sections = existing_hints.get("sections")
        sections = self._resolve_sections_from_hints(text, hinted_sections, fallback_sections=auto_sections)
        section_result = self.section_parser.parse(text, sections=sections)
        metadata = [dict(item) for item in section_result.metadata]
        generated_hints = {
            "section_count": len(sections),
            "section_lengths": [len(_ensure_tokens(section)) for section in sections],
            "command_count": len(commands or []),
            "section_headers": metadata,
            "annotations": section_result.annotations,
        }
        if hinted_sections:
            generated_hints["sections"] = hinted_sections
        if language_info:
            generated_hints["language"] = dict(language_info)

        semantic_hints = self._merge_semantic_hints(generated_hints, existing_hints)
        detected_commands = list(commands or [])
        hinted_commands = existing_hints.get("commands") if isinstance(existing_hints, dict) else None
        if hinted_commands:
            detected_commands = _merge_command_lists(detected_commands, hinted_commands)

        return {
            "semantic_hints": semantic_hints,
            "sections": sections,
            "commands": detected_commands,
            "section_metadata": metadata,
            "section_headers": metadata,
            "annotations": section_result.annotations,
            "preserved_tags": list(preserved_tags or []),
        }

    def _apply_overrides_to_context(
        self,
        context: Dict[str, Any],
        manager: UserOverrideManager,
        *,
        text: str,
    ) -> Dict[str, Any]:
        updated = copy.deepcopy(context)
        overrides = manager.overrides
        semantic_hints = updated.get("semantic_hints", {})
        if overrides.structure_hints:
            sections = self._resolve_sections_from_hints(
                text,
                overrides.structure_hints,
                fallback_sections=updated.get("sections"),
            )
            updated["sections"] = sections
            semantic_hints = self._merge_semantic_hints(semantic_hints, {"sections": overrides.structure_hints})
        if overrides.semantic_hints:
            semantic_hints = self._merge_semantic_hints(semantic_hints, overrides.semantic_hints)
        manual: Dict[str, Any] = {}
        if overrides.bpm is not None:
            manual["bpm"] = overrides.bpm
            semantic_hints = self._merge_semantic_hints(
                semantic_hints,
                {"bpm": {"target": overrides.bpm}, "target_bpm": overrides.bpm},
            )
        if overrides.key:
            manual["key"] = overrides.key
            semantic_hints = self._merge_semantic_hints(semantic_hints, {"tonality": {"manual_key": overrides.key}})
        if overrides.genre:
            manual["genre"] = overrides.genre
            semantic_hints = self._merge_semantic_hints(semantic_hints, {"style": {"genre": overrides.genre}})
        if overrides.mood:
            manual["mood"] = overrides.mood
            semantic_hints = self._merge_semantic_hints(semantic_hints, {"style": {"mood": overrides.mood}})
        if overrides.vocal_profile:
            manual["vocal_profile"] = dict(overrides.vocal_profile)
        if overrides.instrumentation:
            manual["instrumentation"] = list(overrides.instrumentation)
        if overrides.color_state:
            manual["color_state"] = overrides.color_state
        if overrides.structure_hints:
            manual["structure_hints"] = [dict(item) for item in overrides.structure_hints]
        if manual:
            updated["manual_overrides"] = manual
        updated["semantic_hints"] = semantic_hints
        return updated

    def _backend_analyze(
        self,
        text: str,
        *,
        preferred_gender: str,
        version: str | None,
        semantic_hints: Dict[str, Any],
        structure_context: Dict[str, Any],
        override_manager: UserOverrideManager,
        language_info: Dict[str, Any] | None = None,
        original_text: str | None = None,
        command_bundle: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        sections = list(structure_context.get("sections", []))
        hinted_sections = semantic_hints.get("sections")
        if hinted_sections:
            sections = self._resolve_sections_from_hints(text, hinted_sections) or sections
        if not sections:
            sections = self.text_engine.auto_section_split(text)
        self._last_sections = sections
        self._last_text = text
        emotion_profile = self.emotion_engine.emotion_detection(text)
        emotion_curve = self.emotion_engine.emotion_intensity_curve(text)
        section_intel_payload = self.section_intelligence.analyze(text, sections, emotion_curve)
        structure_context["section_intelligence"] = section_intel_payload
        structure_context["emotion_profile"] = dict(emotion_profile)
        structure_context["emotion_curve"] = list(emotion_curve)
        if language_info:
            structure_context["language"] = dict(language_info)

        semantic_hints = self._merge_semantic_hints(
            semantic_hints,
            {
                "dominant_emotion": max(emotion_profile, key=emotion_profile.get) if emotion_profile else None,
                "emotion_curve_max": max(emotion_curve) if emotion_curve else None,
                "section_intelligence": section_intel_payload,
            },
        )
        structure_context["semantic_hints"] = semantic_hints

        emotion_profile = self._merge_semantic_hints(
            dict(emotion_profile),
            semantic_hints.get("emotion_profile", {}),
        )
        commands = list(structure_context.get("commands", []))

        # 1. Call the legacy core for full analysis.
        try:
            legacy_core = self._legacy_core_cls()
            legacy_result = legacy_core.analyze(
                original_text or text,
                preferred_gender=preferred_gender,
                version=version,
                semantic_hints=copy.deepcopy(semantic_hints) if semantic_hints else None,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            legacy_result = {"error": str(exc)}

        # 2. Structural analysis
        structure = {
            "sections": sections,
            "intro": self.text_engine.detect_intro(text, sections=sections),
            "verse": self.text_engine.detect_verse(text, sections=sections),
            "prechorus": self.text_engine.detect_prechorus(text, sections=sections),
            "chorus": self.text_engine.detect_chorus(text, sections=sections),
            "bridge": self.text_engine.detect_bridge(text, sections=sections),
            "outro": self.text_engine.detect_outro(text, sections=sections),
            "meta_pause": self.text_engine.detect_meta_pause(text, sections=sections),
            "intelligence": section_intel_payload,
        }
        if isinstance(semantic_hints.get("section_labels"), list):
            structure["labels"] = list(semantic_hints["section_labels"])
        if structure_context.get("section_metadata"):
            structure["headers"] = structure_context["section_metadata"]
        if structure_context.get("preserved_tags"):
            structure["preserved_tags"] = list(structure_context.get("preserved_tags", []))
        if language_info:
            structure["language"] = dict(language_info)

        result: Dict[str, Any] = {}

        zero_hint = self.text_engine.detect_zero_pulse(text, sections=sections)

        # 3. Emotional layers
        dominant_emotion = self._resolve_dominant_emotion(text, emotion_profile)
        tlp_profile = self.tlp_engine.analyze(text)
        if dominant_emotion:
            tlp_profile["dominant_name"] = dominant_emotion
            tlp_profile["emotion"] = dominant_emotion
        emotion_payload = {
            "profile": emotion_profile,
            "curve": emotion_curve,
            "pivots": self.emotion_engine.emotion_pivot_points(text, intensity_curve=emotion_curve),
            "secondary": self.emotion_engine.secondary_emotion_detection(emotion_profile),
            "conflict": self.emotion_engine.emotion_conflict_map(emotion_profile),
        }
        emotion_payload = self._merge_semantic_hints(emotion_payload, semantic_hints.get("emotion", {}))

        try:
            from studiocore.emotion_profile import EmotionAggregator

            result["_emotion_stub"] = EmotionAggregator
        except Exception:
            result["_emotion_stub"] = None

        # 4. Tonal colours and style hints
        color_profile = self.color_engine.assign_color_by_emotion(emotion_profile)
        color_profile = self._merge_semantic_hints(color_profile, semantic_hints.get("color", {}))
        color_wave = self.color_engine.generate_color_wave(emotion_profile)
        color_transitions = self.color_engine.color_transition_map(emotion_profile)

        # 5. Vocal character
        voice_gender = self.vocal_engine.detect_voice_gender(text)
        voice_type = self.vocal_engine.detect_voice_type(text)
        voice_emotion_vector = self.emotion_engine.export_emotion_vector(text)
        voice_tone = self.vocal_engine.detect_voice_tone(text, emotion=voice_emotion_vector)
        voice_style = self.vocal_engine.detect_vocal_style(text, voice_type=voice_type, voice_tone=voice_tone)
        vocal_dynamics = self.vocal_engine.vocal_dynamics_map(sections)
        vocal_curve = self.vocal_engine.vocal_intensity_curve(vocal_dynamics)
        vocal_payload = {
            "gender": voice_gender,
            "type": voice_type,
            "tone": voice_tone,
            "style": voice_style,
            "dynamics": vocal_dynamics,
            "intensity_curve": vocal_curve,
            "average_intensity": round(sum(vocal_curve) / max(len(vocal_curve), 1), 3) if vocal_curve else 0.5,
        }
        vocal_payload = self._merge_semantic_hints(vocal_payload, semantic_hints.get("vocal", {}))
        vocal_payload = self._apply_vocal_fusion(vocal_payload, override_manager.overrides)
        vocal_for_instrumentation = self.override_engine.apply_to_vocals(
            vocal_payload, override_manager
        )

        # 6. Breathing cues
        breathing_profile = {
            "inhale_points": self.breathing_engine.detect_inhale_points(text),
            "short_breath": self.breathing_engine.detect_short_breath(text),
            "broken_breath": self.breathing_engine.detect_broken_breath(text),
            "spasms": self.breathing_engine.detect_spasms(text),
        }
        breathing_profile.update(self.breathing_engine.detect_emotional_breathing(text, emotion_profile))
        breath_sync = self.breathing_engine.breath_to_emotion_sync(text, emotion_profile)
        breathing_profile = self._merge_semantic_hints(breathing_profile, semantic_hints.get("breathing", {}))

        # 7. Rhythm & BPM
        legacy_bpm = None
        if isinstance(legacy_result, dict):
            legacy_bpm = legacy_result.get("bpm") or legacy_result.get("style", {}).get("bpm")
            semantic_layers = legacy_result.get("semantic_layers", {}) if isinstance(legacy_result.get("semantic_layers"), dict) else {}
        else:
            semantic_layers = {}

        bpm_estimate = self.bpm_engine.text_bpm_estimation(text)
        user_bpm_hint = semantic_hints.get("target_bpm") if isinstance(semantic_hints, dict) else None
        if isinstance(user_bpm_hint, (int, float)):
            bpm_estimate = float(user_bpm_hint)
        elif legacy_bpm is not None:
            bpm_estimate = float(legacy_bpm)

        semantic_suggested_bpm = semantic_layers.get("bpm_suggested")
        if semantic_suggested_bpm is not None and user_bpm_hint is None:
            bpm_estimate = float(semantic_suggested_bpm)

        bpm_estimate = self.override_engine.resolve_bpm(override_manager, bpm_estimate)
        bpm_curve = self.bpm_engine.meaning_bpm_curve(sections, base_bpm=bpm_estimate)
        bpm_estimate, bpm_curve, bpm_locks = self._enforce_bpm_limits(
            bpm_estimate, bpm_curve, override_manager.overrides, len(sections)
        )
        bpm_mapping = self.bpm_engine.emotion_bpm_mapping(emotion_profile, base_bpm=bpm_estimate)
        bpm_breath = self.bpm_engine.breathing_bpm_integration(breathing_profile, bpm_estimate)
        bpm_poly = self.bpm_engine.poly_rhythm_detection(bpm_curve)
        bpm_payload = {
            "estimate": bpm_estimate,
            "emotion_map": bpm_mapping,
            "curve": bpm_curve,
            "breathing": bpm_breath,
            "poly_rhythm": bpm_poly,
            "locks": bpm_locks,
        }
        bpm_payload = self._merge_semantic_hints(bpm_payload, semantic_hints.get("bpm", {}))

        annotations_from_text = structure_context.get("annotations", [])
        if annotations_from_text:
            annotation_effects = self.section_parser.apply_annotation_effects(
                emotions=emotion_profile,
                bpm=bpm_payload.get("estimate", bpm_estimate),
                annotations=annotations_from_text,
            )
            emotion_profile = annotation_effects.get("emotions", emotion_profile)
            bpm_estimate = annotation_effects.get("bpm", bpm_payload.get("estimate"))
            bpm_payload["estimate"] = bpm_estimate
            bpm_payload["section_annotations"] = annotation_effects.get("annotations", [])

        # 8. Meaning velocity
        meaning_curve = self.meaning_engine.meaning_curve_generation(sections)
        meaning_shifts = self.meaning_engine.semantic_shift_detection(sections)
        meaning_accel = self.meaning_engine.meaning_acceleration(meaning_curve)
        meaning_fractures = self.meaning_engine.meaning_fracture_detection(meaning_shifts.get("shifts", []))
        meaning_payload = {
            "curve": meaning_curve,
            "shifts": meaning_shifts,
            "acceleration": meaning_accel,
            "fractures": meaning_fractures,
        }

        # 9. Tonality
        mode_result = self.tonality_engine.mode_detection(emotion_profile, tlp_profile)
        mode = self.tonality_engine.major_minor_classifier(sections, mode_result.get("mode", "major"))
        section_keys = self.tonality_engine.section_key_selection(sections, mode)
        modal_shifts = self.tonality_engine.modal_shift_detection(section_keys)
        section_keys, mode, anchor_key = self._align_section_keys(section_keys, override_manager.overrides, sections, mode)
        tonality_payload = {
            "mode": mode,
            "confidence": mode_result.get("confidence"),
            "section_keys": section_keys,
            "modal_shifts": modal_shifts,
            "key_curve": self.tonality_engine.key_transition_curve(section_keys),
            "fallback_key": anchor_key,
        }
        tonality_payload = self._merge_semantic_hints(tonality_payload, semantic_hints.get("tonality", {}))

        legacy_key = None
        if isinstance(legacy_result, dict):
            legacy_key = legacy_result.get("style", {}).get("key") or legacy_result.get("key")
        if legacy_key and not getattr(override_manager.overrides, "key", None):
            if "minor" in str(legacy_key).lower():
                tonality_payload["mode"] = "minor"
                tonality_payload["section_keys"] = [
                    key if "minor" in key.lower() or key.split()[0].startswith(str(legacy_key).split()[0]) else f"{legacy_key}" for key in tonality_payload.get("section_keys", [])
                ] or [str(legacy_key)]

        # 10. Instrumentation suggestions
        instrument_selection = self.instrumentation_engine.instrument_selection(
            genre=legacy_result.get("style", {}).get("genre") if isinstance(legacy_result, dict) else None,
            energy=semantic_hints.get("target_energy", bpm_mapping.get("target_energy")),
            mood=semantic_hints.get("target_mood"),
            reference_palette=_ensure_iterable(semantic_hints.get("instrument_palette")),
        )
        instrument_emotion = self.instrumentation_engine.instrument_based_on_emotion(
            emotion_profile,
            base_palette=instrument_selection.get("palette"),
        )
        instrument_voice = self.instrumentation_engine.instrument_based_on_voice(
            vocal_for_instrumentation.get("style"),
            target_energy=bpm_mapping.get("target_energy"),
        )
        instrument_color = self.instrumentation_engine.instrument_color_sync(
            color_profile,
            base_palette=instrument_emotion.get("palette"),
        )
        instrument_rhythm = self.instrumentation_engine.instrument_rhythm_sync(
            bpm_estimate,
            rhythm_profile=bpm_curve,
        )
        instrumentation_payload = {
            "selection": instrument_selection,
            "emotion": instrument_emotion,
            "voice": instrument_voice,
            "color": instrument_color,
            "rhythm": instrument_rhythm,
            "palette": instrument_color.get("palette")
            or instrument_emotion.get("palette")
            or instrument_selection.get("palette"),
            "energy": semantic_hints.get("target_energy", bpm_mapping.get("target_energy")),
        }
        instrumentation_payload = self._merge_semantic_hints(
            instrumentation_payload, semantic_hints.get("instrumentation", {})
        )

        # 11. Command interpretation
        command_payload = {
            "detected": commands,
            "bpm": self.command_interpreter.execute_bpm_commands(commands, base_bpm=bpm_estimate),
            "key": self.command_interpreter.execute_key_commands(commands, default_key=section_keys[0] if section_keys else None),
            "rhythm": self.command_interpreter.execute_rhythm_commands(commands),
            "emotion": self.command_interpreter.execute_emotion_commands(commands),
            "style": self.command_interpreter.execute_style_commands(commands),
        }
        if isinstance(semantic_hints.get("commands"), list):
            command_payload["manual_overrides"] = list(semantic_hints["commands"])
        if command_bundle and command_bundle.get("map"):
            command_payload["map"] = dict(command_bundle["map"])
        if structure_context.get("preserved_tags"):
            command_payload["preserved_tags"] = list(structure_context.get("preserved_tags", []))

        # 12. REM synchronization
        rem_conflicts = self.rem_engine.detect_layer_conflicts(structure, bpm_curve, instrument_selection)
        rem_resolution = self.rem_engine.resolve_layer_conflicts(rem_conflicts)
        rem_dominant = self.rem_engine.assign_dominant_layer(structure=structure, emotion=emotion_payload)
        rem_alignment = self.rem_engine.align_layers_for_final_output(
            structure, instrument_selection, tonality_payload
        )
        rem_payload = {
            "conflicts": rem_conflicts,
            "resolution": rem_resolution,
            "dominant_layer": rem_dominant,
            "alignment": rem_alignment,
        }

        # 13. Zero pulse & silence
        zero_pulse_payload = {
            "structure_hint": zero_hint,
            "analysis": self.zero_pulse_engine.detect_zero_pulse(text),
            "vacuum": self.zero_pulse_engine.vacuum_beat_state(text),
            "emotion": self.zero_pulse_engine.silence_as_emotion(text, emotion_profile),
            "transition": self.zero_pulse_engine.silence_as_transition(text),
        }

        instrument_dynamics_payload = self.instrument_dynamics.map_instruments_to_structure(
            sections,
            instrumentation_payload.get("palette"),
            bpm_payload,
            emotion_payload,
            zero_pulse_payload,
        )

        # 13b. Domain feature map for the genre engine
        def _clamp(value: float) -> float:
            try:
                return round(max(0.0, min(1.0, float(value))), 3)
            except (TypeError, ValueError):
                return 0.0

        bpm_value = bpm_payload.get("estimate") or bpm_estimate or 0.0
        avg_intensity = vocal_payload.get("average_intensity", 0.0) or 0.0
        conflict_value = emotion_payload.get("conflict", {}).get("conflict", 0.0) or 0.0
        semantic_aggression = _clamp(conflict_value + emotion_profile.get("anger", 0.0) * 0.4)
        power_vector = _clamp((bpm_value / 180.0) + avg_intensity * 0.3)
        bpm_curve_values = bpm_payload.get("curve") or bpm_curve or []
        bpm_deltas = [abs(bpm_curve_values[idx] - bpm_curve_values[idx - 1]) for idx in range(1, len(bpm_curve_values))]
        if bpm_deltas:
            density = sum(bpm_deltas) / max(len(bpm_deltas), 1)
            rhythm_density = _clamp(density / max(bpm_value or 120.0, 1.0))
        else:
            rhythm_density = _clamp(bpm_value / 200.0)
        edge_factor = emotion_profile.get("anger", 0.0) * 0.6
        tone = vocal_payload.get("tone")
        if tone == "intense":
            edge_factor += 0.3
        elif tone == "balanced":
            edge_factor += 0.15
        edge_factor = _clamp(edge_factor)
        acceleration = meaning_payload.get("acceleration", [])
        accel_value = (
            sum(abs(value) for value in acceleration) / max(len(acceleration), 1)
            if acceleration
            else 0.0
        )
        fractures = meaning_payload.get("fractures", {}).get("count", 0)
        narrative_pressure = _clamp(accel_value + fractures * 0.1)
        gradient_curve = emotion_payload.get("curve") or emotion_curve or []
        if gradient_curve:
            amplitude = max(gradient_curve) - min(gradient_curve)
            gradient_max = max(max(gradient_curve), 1.0)
            emotional_gradient = _clamp(amplitude / gradient_max)
        else:
            emotional_gradient = _clamp(conflict_value)
        mode = (tonality_payload.get("mode") or "").lower()
        harmonic_lumen_minor = _clamp(0.8 if "minor" in mode else 0.2 if "modal" in mode else 0.1)
        harmonic_lumen_major = _clamp(0.8 if "major" in mode else 0.2 if "modal" in mode else 0.1)
        transition_delta = section_intel_payload.get("transition_drop", {}).get("delta", 0.0) or 0.0
        chorus_intensity = section_intel_payload.get("chorus_emotion", {}).get("intensity", 0.0) or 0.0
        motif_count = section_intel_payload.get("motifs", {}).get("count", 0) or 0
        cinematic_spread = _clamp(0.2 + transition_delta * 0.3 + chorus_intensity * 0.2 + motif_count * 0.05)
        vocal_intention = _clamp(avg_intensity)
        structure_tension = _clamp(section_intel_payload.get("structure_tension", 0.0))
        text_lower = text.lower()
        tokens = [token for token in re.split(r"[^a-z0-9а-яё]+", text_lower) if token]
        token_count = max(len(tokens), 1)
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        emotion_engine = self.emotion_engine
        local_vectors: List[EmotionVector] = []
        for line in lines:
            vec = emotion_engine.export_emotion_vector(line)
            local_vectors.append(vec)

        field = EmotionFieldEngine(window=4)
        smoothed_vectors = field.smooth(local_vectors)
        result["_emotion_dynamic"] = [v.to_dict() for v in smoothed_vectors]

        line_count = max(len(lines), 1)
        palette_items = [
            str(item).lower()
            for item in (instrumentation_payload.get("palette") or [])
            if isinstance(item, str)
        ]
        command_blob = " ".join(
            str(command.get("raw") or command.get("value") or "").lower()
            for command in commands
            if isinstance(command, dict)
        )
        hint_blob = str(semantic_hints).lower() if semantic_hints else ""

        def _token_hits(keywords: Sequence[str]) -> int:
            hits = 0
            for token in tokens:
                for keyword in keywords:
                    if keyword and keyword in token:
                        hits += 1
                        break
            return hits

        poetic_keywords = (
            "lyric",
            "poem",
            "ode",
            "sonnet",
            "haiku",
            "ballad",
            "serenade",
            "lullaby",
            "lyrical",
            "серд",
            "люб",
            "луна",
            "звезд",
            "тиши",
            "ветер",
            "лепест",
            "шеп",
            "сон",
            "dream",
            "soul",
            "moon",
            "star",
            "ocean",
            "tear",
            "rose",
        )
        imagery_hits = _token_hits(poetic_keywords)
        imagery_score = imagery_hits / token_count
        punctuation_score = sum(line.count(",") + line.count(";") + line.count(":") for line in lines)
        punctuation_score = punctuation_score / max(line_count * 4, 1)
        long_lines = sum(1 for line in lines if len(line) > 70)
        long_line_score = long_lines / line_count
        motif_score = (section_intel_payload.get("motifs", {}).get("count", 0) or 0) / max(len(sections) or 1, 1)
        poetic_density = _clamp(imagery_score * 2.2 + punctuation_score * 0.4 + long_line_score * 0.3 + motif_score * 0.1)

        swing_keywords = ("swing", "shuffle", "bebop", "boogie", "ragtime", "stride", "jive")
        swing_keyword_hits = _token_hits(swing_keywords)
        swing_keyword_score = swing_keyword_hits / line_count
        if any(keyword in command_blob for keyword in swing_keywords):
            swing_keyword_score += 0.25
        if any(keyword in hint_blob for keyword in swing_keywords):
            swing_keyword_score += 0.25
        swing_keyword_score = _clamp(swing_keyword_score)
        poly_variance = float((bpm_payload.get("poly_rhythm") or {}).get("variance", 0.0) or 0.0)
        swing_ratio = _clamp(0.6 * swing_keyword_score + 0.4 * _clamp(poly_variance / 40.0))

        jazz_keywords = swing_keywords + ("jazz", "bossa", "samba", "fusion", "manouche", "bebop")
        jazz_text_score = _clamp(_token_hits(jazz_keywords) / line_count)
        jazz_palette_keywords = ("sax", "trumpet", "trombone", "clarinet", "upright", "brush", "double bass", "rhodes", "jazz")
        palette_jazz_hits = 0
        for name in palette_items:
            if any(keyword in name for keyword in jazz_palette_keywords):
                palette_jazz_hits += 1
        palette_jazz_score = _clamp(palette_jazz_hits / max(len(palette_items), 1))
        modal_shift_score = _clamp(len(tonality_payload.get("modal_shifts", [])) / max(len(sections) or 1, 4))
        jazz_complexity = _clamp(0.35 * palette_jazz_score + 0.35 * modal_shift_score + 0.3 * max(jazz_text_score, swing_ratio))

        electronic_keywords = (
            "synth",
            "pad",
            "edm",
            "electro",
            "techno",
            "trance",
            "house",
            "club",
            "808",
            "fm",
            "digital",
            "chip",
            "glitch",
            "modular",
            "drum machine",
        )
        palette_electronic_hits = 0
        for name in palette_items:
            if any(keyword in name for keyword in electronic_keywords):
                palette_electronic_hits += 1
        palette_electronic_score = _clamp(palette_electronic_hits / max(len(palette_items), 1))
        text_electronic_hits = sum(1 for keyword in electronic_keywords if keyword in text_lower or keyword in command_blob or keyword in hint_blob)
        text_electronic_score = _clamp(text_electronic_hits / 5.0)
        bpm_pressure = _clamp((bpm_value - 100.0) / 120.0)
        electronic_pressure = _clamp(0.5 * palette_electronic_score + 0.3 * text_electronic_score + 0.2 * bpm_pressure)

        comedy_keywords = (
            "comedy",
            "comic",
            "funny",
            "humor",
            "humour",
            "parody",
            "satire",
            "joke",
            "lol",
            "lmao",
            "haha",
            "rofl",
            "юмор",
            "юморист",
            "шутк",
            "смешн",
            "ирони",
            "сарказ",
            "парод",
            "анекдот",
            "комед",
            "угар",
        )
        comedy_hits = _token_hits(comedy_keywords)
        comedy_blob_hits = sum(1 for keyword in comedy_keywords if keyword in command_blob or keyword in hint_blob)
        laughter_keywords = ("haha", "ahah", "ahaha", "хаха", "ахаха")
        laughter_hits = sum(1 for keyword in laughter_keywords if keyword in text_lower)
        comedy_factor = _clamp((comedy_hits / line_count) * 0.6 + comedy_blob_hits * 0.15 + laughter_hits * 0.1)

        gothic_keywords = ("gothic", "готик", "dark", "тень", "мрак", "ноч", "grave", "cathedral")
        gothic_hits = _token_hits(gothic_keywords)
        gothic_factor = _clamp((gothic_hits / max(line_count, 1)) + (harmonic_lumen_minor * 0.3))

        dramatic_weight = _clamp((structure_tension * 0.5) + (emotional_gradient * 0.3) + (narrative_pressure * 0.2))
        darkness_level = _clamp((harmonic_lumen_minor * 0.4) + (tlp_profile.get("pain", 0.0) * 0.3) + (gothic_hits * 0.1))
        lyric_form_weight = _clamp(poetic_density * 0.6 + (gothic_hits * 0.05))
        narrative_arch = _clamp((narrative_pressure + emotional_gradient) / 2)

        rde_axes = {
            "epic": float(emotion_profile.get("epic", 0.0)),
            "hope": float(max(emotion_profile.get("joy", 0.0), tlp_profile.get("love", 0.0))),
            "pain": float(
                max(
                    emotion_profile.get("anger", 0.0),
                    emotion_profile.get("fear", 0.0),
                    tlp_profile.get("pain", 0.0),
                )
            ),
            "sadness": float(emotion_profile.get("sadness", 0.0)),
        }

        genre_feature_inputs = {
            "semantic_aggression": semantic_aggression,
            "power_vector": power_vector,
            "rhythm_density": rhythm_density,
            "edge_factor": edge_factor,
            "narrative_pressure": narrative_pressure,
            "emotional_gradient": emotional_gradient,
            "hl_minor": harmonic_lumen_minor,
            "hl_major": harmonic_lumen_major,
            "cinematic_spread": cinematic_spread,
            "vocal_intention": vocal_intention,
            "structure_tension": structure_tension,
            "swing_ratio": swing_ratio,
            "jazz_complexity": jazz_complexity,
            "electronic_pressure": electronic_pressure,
            "comedy_factor": comedy_factor,
            "poetic_density": poetic_density,
            "gothic_factor": gothic_factor,
            "dramatic_weight": dramatic_weight,
            "darkness_level": darkness_level,
            "lyric_form_weight": lyric_form_weight,
            "narrative_arch": narrative_arch,
            "rde": rde_axes,
            "tlp": dict(tlp_profile),
        }
        feature_map = self.build_feature_map(genre_feature_inputs)
        domain_genre = self.genre_matrix.evaluate(feature_map)

        try:
            from .genre_universe_loader import load_genre_universe

            universe = load_genre_universe()
        except Exception:  # pragma: no cover - fallback if loader fails
            universe = None

        legacy_style_genre = legacy_result.get("style", {}).get("genre") if isinstance(legacy_result, dict) else None
        if legacy_style_genre and universe:
            resolved = universe.resolve(legacy_style_genre)
            domain_info = universe.detect_domain(resolved)
            if domain_info.get("domain") != "unknown":
                domain_genre = resolved

        gothic_bias = feature_map.get("gothic_factor", 0.0)
        poetic_bias = feature_map.get("poetic_density", 0.0)
        lyric_bias = feature_map.get("lyric_form_weight", 0.0)
        dramatic_bias = feature_map.get("dramatic_weight", 0.0)

        if domain_genre == "edm" and (gothic_bias > 0.2 or poetic_bias > 0.25 or lyric_bias > 0.25):
            domain_genre = "gothic_poetry" if gothic_bias >= max(poetic_bias, lyric_bias) else "lyrical_song"
        elif domain_genre == "edm" and dramatic_bias > 0.25:
            domain_genre = "cinematic"
        genre_analysis = {"feature_map": feature_map, "domain_genre": domain_genre}

        # 14. Style synthesis
        style_commands = command_payload.get("style") or {}
        style_genre = (
            style_commands.get("genre")
            or semantic_hints.get("style", {}).get("genre")
            or domain_genre
            or self.style_engine.genre_selection(emotion_profile, tlp_profile)
        )
        emotion_label = (tlp_profile.get("dominant_name") or tlp_profile.get("emotion") or "").lower()
        forced_genres = {
            "melancholy_dark": "gothic adaptive darkwave",
            "rage_extreme": "ideological extreme adaptive rage",
            "love_soft": "lyrical love adaptive classic",
            "joy_bright": "pop adaptive light",
            "confidence": "hiphop adaptive",
        }
        if not style_commands.get("genre") and emotion_label in forced_genres:
            style_genre = forced_genres[emotion_label]
        style_mood = (
            style_commands.get("mood")
            or semantic_hints.get("style", {}).get("mood")
            or self.style_engine.mood_selection(emotion_profile, tlp_profile)
        )
        style_instrumentation = self.style_engine.instrumentation_style(instrumentation_payload.get("selection", {}))
        style_vocal = style_commands.get("vocal") or self.style_engine.vocal_style(vocal_payload)
        style_visual = self.style_engine.visual_style(color_profile)
        style_tone = self.style_engine.tone_style(tonality_payload)
        style_prompt = self.style_engine.final_style_prompt_build(
            genre=style_genre,
            mood=style_mood,
            instrumentation=style_instrumentation,
            vocal=style_vocal,
            visual=style_visual,
            tone=style_tone,
        )
        style_payload = {
            "genre": style_genre,
            "mood": style_mood,
            "instrumentation": style_instrumentation,
            "vocal": style_vocal,
            "visual": style_visual,
            "tone": style_tone,
            "prompt": style_prompt,
        }
        if domain_genre:
            style_payload["domain_genre"] = domain_genre
        if style_commands.get("intensity"):
            style_payload["intensity"] = style_commands["intensity"]
        if style_commands:
            style_payload["commands"] = style_commands
        style_payload = self._merge_semantic_hints(style_payload, semantic_hints.get("style", {}))

        rde_snapshot = self.rde_engine.compose(
            bpm_payload=bpm_payload,
            breathing_profile={**breathing_profile, "sync_score": breath_sync},
            emotion_profile=emotion_profile,
            instrumentation_payload=instrumentation_payload,
        )
        rde_summary = asdict(rde_snapshot)

        # 15. Lyrics annotations
        annotations = {
            "vocal": self.annotation_engine.add_vocal_annotations(sections, vocal_payload),
            "breath": self.annotation_engine.add_breath_annotations(sections, breathing_profile),
            "tonality": self.annotation_engine.add_tonal_annotations(sections, tonality_payload),
            "emotion": self.annotation_engine.add_emotional_annotations(sections, emotion_payload),
            "rhythm": self.annotation_engine.add_rhythm_annotations(sections, bpm_curve),
        }
        if semantic_hints.get("annotations"):
            annotations = self._merge_semantic_hints(annotations, semantic_hints["annotations"])

        result.update(
            {
                "legacy": legacy_result,
                "structure": structure,
                "emotion": emotion_payload,
                "color": {
                    "profile": color_profile,
                    "wave": color_wave,
                    "transitions": color_transitions,
                },
                "vocal": vocal_payload,
                "breathing": {**breathing_profile, "sync": breath_sync},
                "bpm": bpm_payload,
                "meaning": meaning_payload,
                "tonality": tonality_payload,
                "instrumentation": instrumentation_payload,
                "rem": rem_payload,
                "zero_pulse": zero_pulse_payload,
                "tlp": dict(tlp_profile),
                "style": style_payload,
                "commands": command_payload,
                "annotations": annotations,
                "semantic_hints": semantic_hints,
                "auto_context": structure_context,
                "instrument_dynamics": instrument_dynamics_payload,
                "override_debug": override_manager.debug_summary(),
                "rde_summary": rde_summary,
                "genre_analysis": genre_analysis,
            }
        )
        fanf_analysis_payload = {
            "emotion": {"profile": emotion_profile, "curve": emotion_curve},
            "bpm": bpm_payload,
            "tonality": tonality_payload,
            "style": style_payload,
            "tlp": tlp_profile,
            "zero_pulse": zero_pulse_payload,
            "color": {"wave": color_wave, "profile": color_profile},
            "instrumentation": instrumentation_payload,
            "rde": rde_summary,
        }
        self._last_fanf_context = {"text": text, "sections": sections, "analysis": fanf_analysis_payload}
        try:
            fanf_annotation = self.fanf_engine.build_annotations(
                text,
                sections,
                fanf_analysis_payload,
            )
            result["fanf"] = {
                "annotated_text_fanf": fanf_annotation.annotated_text_fanf,
                "annotated_text_ui": fanf_annotation.annotated_text_ui,
                "annotated_text_suno": fanf_annotation.annotated_text_suno,
                "choir_active": fanf_annotation.choir_active,
                "cinematic_header": fanf_annotation.cinematic_header,
                "resonance_header": fanf_annotation.resonance_header,
            }
        except Exception as exc:  # pragma: no cover - defensive guard
            result["fanf"] = {
                "annotated_text_fanf": "FANF generation unavailable.",
                "annotated_text_ui": "FANF generation unavailable.",
                "annotated_text_suno": "FANF generation unavailable.",
                "choir_active": False,
                "error": str(exc),
            }
        self._last_fanf_output = result.get("fanf", {})
        applied_overrides = self._apply_user_overrides_once(result, override_manager)
        result["symbiosis"] = self.symbiosis_engine.build_final_symbiosis_state(
            override_manager,
            result,
            applied_overrides=applied_overrides,
        )
        suno_annotations = self.suno_engine.build_suno_safe_annotations(
            sections,
            {
                "bpm": result.get("bpm", {}),
                "instrumentation": {
                    "palette": result.get("instrumentation", {}).get("palette"),
                    "fractures": instrument_dynamics_payload.get("fractures"),
                },
                "vocal": result.get("vocal", {}),
                "commands": command_payload,
            },
        )
        result["suno_annotations"] = suno_annotations
        if language_info:
            result["language"] = dict(language_info)
        self._last_backend_payload = dict(result)
        return result

    def _finalize_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = self.compiler.merge_all_layers(payload)
        merged["structure"] = self.compiler.generate_final_structure(payload)
        merged["prompt"] = self.compiler.generate_final_prompt(payload)
        merged["annotations"] = self.compiler.generate_final_annotations(payload)
        merged["consistency"] = self.compiler.consistency_check(payload)
        merged["commands"] = payload.get("commands", {})
        merged["style"] = payload.get("style", {})
        merged["zero_pulse"] = payload.get("zero_pulse", {})
        merged["bpm"] = payload.get("bpm", {})
        merged["semantic_hints"] = payload.get("semantic_hints", {})
        merged["auto_context"] = payload.get("auto_context", {})
        merged["instrument_dynamics"] = payload.get("instrument_dynamics", {})
        merged["tlp"] = payload.get("tlp", {})
        merged["suno_annotations"] = payload.get("suno_annotations", [])
        merged["symbiosis"] = payload.get("symbiosis", {})
        merged["override_debug"] = payload.get("override_debug", {})
        merged["language"] = payload.get("language", payload.get("auto_context", {}).get("language"))
        merged["rde_summary"] = payload.get("rde_summary", {})
        merged["genre_analysis"] = payload.get("genre_analysis", {})
        merged["fanf"] = payload.get("fanf", {})
        merged["summary"] = payload.get("style", {}).get("prompt") or payload.get("summary") or ""
        merged.pop("_overrides_applied", None)
        return merged

    def build_fanf_output(self) -> Dict[str, Any]:
        context = self._last_fanf_context or {}
        text = context.get("text") or self._last_text or ""
        sections = context.get("sections") or self._last_sections or []
        analysis = context.get("analysis") or {}
        try:
            annotation = self.fanf_engine.build_annotations(text, sections, analysis)
        except TypeError:
            safe_sections = (
                list(sections.values()) if isinstance(sections, dict) else list(sections or [])
            )
            annotation = self.fanf_engine.build_annotations(text, safe_sections, analysis)
        self._last_fanf_output = {
            "annotated_text_fanf": annotation.annotated_text_fanf,
            "annotated_text_ui": annotation.annotated_text_ui,
            "annotated_text_suno": annotation.annotated_text_suno,
            "choir_active": annotation.choir_active,
            "cinematic_header": annotation.cinematic_header,
            "resonance_header": annotation.resonance_header,
        }
        return self._last_fanf_output

    def annotate_ui(self) -> str | None:
        return (self._last_fanf_output or {}).get("annotated_text_ui")

    def annotate_suno(self) -> str | None:
        return (self._last_fanf_output or {}).get("annotated_text_suno")

    def _apply_vocal_fusion(self, vocal_payload: Dict[str, Any], overrides: UserOverrides | None) -> Dict[str, Any]:
        payload = dict(vocal_payload)
        user_profile = dict(getattr(overrides, "vocal_profile", {}) or {})
        fusion_meta = {
            "strategy": "user_first" if user_profile else "analysis_only",
            "weights": {"analysis": 0.65, "user": 0.35},
            "allowed_outputs": [
                "solo_male",
                "solo_female",
                "duet_mf",
                "duet_mm",
                "duet_ff",
                "choir_male",
                "choir_female",
                "choir_mixed",
            ],
            "max_bias_limit": 0.25,
            "user_mix": ["male", "female", "choir", "growl", "scream", "soft", "whisper", "raspy"],
        }
        if user_profile:
            for field in ("gender", "type", "tone", "style", "dynamics"):
                if user_profile.get(field):
                    payload[field] = user_profile[field]
            if user_profile.get("mix"):
                fusion_meta["user_mix"] = list(user_profile["mix"])
            fusion_meta["bias_applied"] = True
        payload["fusion"] = fusion_meta
        return payload

    def _enforce_bpm_limits(
        self,
        base_bpm: float | None,
        bpm_curve: Sequence[float] | None,
        overrides: UserOverrides | None,
        section_count: int,
    ) -> tuple[float, list[float], Dict[str, Any]]:
        limit = 5
        fallback = 120.0
        if overrides and overrides.bpm is not None:
            fallback = float(overrides.bpm)
        elif base_bpm is not None:
            fallback = float(base_bpm)
        stabilized: list[float] = []
        curve = list(bpm_curve or [])
        if not curve:
            curve = [fallback] * max(section_count, 1)
        for value in curve:
            candidate = fallback if value is None else float(value)
            delta = candidate - fallback
            if abs(delta) > limit:
                candidate = fallback + limit if delta > 0 else fallback - limit
            stabilized.append(round(candidate, 3))
        lock_info = {
            "user_lock": bool(overrides and overrides.bpm is not None),
            "global_lock": True,
            "max_section_variation": limit,
            "fallback_bpm": 120,
        }
        return fallback, stabilized, lock_info

    def _align_section_keys(
        self,
        detected_keys: Sequence[str] | None,
        overrides: UserOverrides | None,
        sections: Sequence[str],
        detected_mode: str,
    ) -> tuple[list[str], str, str]:
        manual_key = getattr(overrides, "key", None)
        keys = [key for key in (detected_keys or []) if key]
        base_key = manual_key or (keys[0] if keys else None) or "C minor"
        section_count = len(sections)
        normalized: list[str] = []
        if section_count:
            for idx in range(section_count):
                if idx < len(keys):
                    normalized.append(keys[idx])
                else:
                    normalized.append(base_key)
        else:
            normalized = keys or [base_key]
        mode = detected_mode
        key_reference = (manual_key or base_key or "").lower()
        if "minor" in key_reference:
            mode = "minor"
        elif "major" in key_reference:
            mode = "major"
        return normalized, mode, base_key

    def build_feature_map(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        Унифицированная карта признаков для жанрового движка.
        analysis — сводный словарь, который собирают RDE/TLP/Rhythm/Tone/Section.
        """
        from .lyrical_emotion import LyricalEmotionEngine

        if not isinstance(analysis, dict):
            analysis = {}

        source: Dict[str, Any] = dict(analysis.get("features") or analysis)

        # вычисляем лирическую эмоцию (даже если это не лирика — будет ~0)
        lee = LyricalEmotionEngine().from_analysis(source)

        def _value(key: str) -> float:
            try:
                return float(source.get(key, 0.0))
            except (TypeError, ValueError):
                return 0.0

        return {
            # жёсткие признаки
            "sai": _value("semantic_aggression"),
            "power": _value("power_vector"),
            "rhythm_density": _value("rhythm_density"),
            "edge": _value("edge_factor"),

            # нарратив/эмоция
            "narrative_pressure": _value("narrative_pressure"),
            "emotional_gradient": _value("emotional_gradient"),

            # тональность
            "hl_minor": _value("hl_minor"),
            "hl_major": _value("hl_major"),

            # кино/масштаб
            "cinematic_spread": _value("cinematic_spread"),

            # вокал
            "vocal_intention": _value("vocal_intention"),

            # структура
            "structure_tension": _value("structure_tension"),

            # джаз/свинг/электронная плотность
            "swing_ratio": _value("swing_ratio"),
            "jazz_complexity": _value("jazz_complexity"),
            "electronic_pressure": _value("electronic_pressure"),

            # Лирика/комедия
            "lyrical_emotion_score": float(lee.get("lyrical_emotion_score", 0.0)),
            "comedy_factor": _value("comedy_factor"),
            "poetic_density": _value("poetic_density"),

            # Новые жанровые маркеры
            "gothic_factor": _value("gothic_factor"),
            "dramatic_weight": _value("dramatic_weight"),
            "narrative_arch": _value("narrative_arch"),
            "darkness_level": _value("darkness_level"),
            "lyric_form_weight": _value("lyric_form_weight"),
        }

    def _resolve_dominant_emotion(self, text: str, emotion_profile: Dict[str, float]) -> str:
        corpus = text.lower()
        keyword_map = [
            ("melancholy_dark", ["готик", "darkwave", "мрак", "тьма", "темн"]),
            ("rage_extreme", ["убей", "уничтож", "ненавиж", "смерт", "rage"]),
            ("love_soft", ["люб", "поцел", "неж", "ласк", "тепл"]),
            ("joy_bright", ["солн", "чудо", "радост", "улыб", "свет"]),
            ("confidence", ["бит", "улиц", "флоу", "правда", "силой", "hiphop", "рэп"]),
        ]
        for label, keywords in keyword_map:
            if any(token in corpus for token in keywords):
                return label
        if emotion_profile:
            dominant = max(emotion_profile.items(), key=lambda item: item[1])[0]
            fallback_map = {
                "joy": "joy_bright",
                "peace": "confidence",
                "anger": "rage_extreme",
                "sadness": "melancholy_dark",
                "awe": "love_soft",
            }
            return fallback_map.get(dominant, dominant)
        return ""

    @staticmethod
    def _merge_semantic_hints(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for source in (base, override):
            if not isinstance(source, dict):
                continue
            for key, value in source.items():
                if isinstance(value, dict) and isinstance(result.get(key), dict):
                    result[key] = StudioCoreV6._merge_semantic_hints(result[key], value)
                elif isinstance(value, list) and isinstance(result.get(key), list):
                    existing = result[key]
                    result[key] = existing + [item for item in value if item not in existing]
                elif isinstance(value, list):
                    result[key] = list(value)
                else:
                    result[key] = value
        return result

    def _apply_user_overrides_once(
        self, payload: Dict[str, Any], manager: UserOverrideManager
    ) -> Dict[str, Any]:
        if payload.get("_overrides_applied"):
            debug_info = payload.get("override_debug", {})
            applied = (
                debug_info.get("applied_overrides", {}) if isinstance(debug_info, dict) else {}
            )
            return copy.deepcopy(applied)

        adjustments: Dict[str, Any] = {}

        # VOCAL
        vocal = payload.get("vocal")
        if isinstance(vocal, dict):
            applied_vocal = self.override_engine.apply_to_vocals(vocal, manager)
            payload["vocal"] = applied_vocal
            adjustments["vocal"] = copy.deepcopy(applied_vocal)

        # BPM
        bpm = payload.get("bpm")
        if isinstance(bpm, dict):
            applied_bpm = self.override_engine.apply_to_rhythm(bpm, manager)

            sections = payload.get("structure", {}).get("sections", [])
            estimate_changed = (
                applied_bpm.get("estimate") is not None
                and applied_bpm.get("estimate") != bpm.get("estimate")
            )

            if sections and estimate_changed:
                applied_bpm["curve"] = self.bpm_engine.meaning_bpm_curve(
                    sections,
                    base_bpm=applied_bpm.get("estimate") or bpm.get("estimate"),
                )
                applied_bpm["estimate"], applied_bpm["curve"], applied_bpm["locks"] = self._enforce_bpm_limits(
                    applied_bpm.get("estimate"),
                    applied_bpm.get("curve"),
                    manager.overrides,
                    len(sections),
                )

            payload["bpm"] = applied_bpm
            adjustments["bpm"] = copy.deepcopy(applied_bpm)

        # STYLE
        style = payload.get("style")
        if isinstance(style, dict):
            applied_style = self.override_engine.apply_to_style(style, manager)
            payload["style"] = applied_style
            adjustments["style"] = copy.deepcopy(applied_style)

        # DEBUG
        payload["_overrides_applied"] = True
        override_debug = manager.debug_summary()
        override_debug["applied_overrides"] = copy.deepcopy(adjustments)
        payload["override_debug"] = override_debug

        return copy.deepcopy(adjustments)

    def _resolve_sections_from_hints(
        self,
        text: str,
        hinted_sections: Iterable[Any] | None,
        fallback_sections: Iterable[str] | None = None,
    ) -> list[str]:
        if not hinted_sections:
            if fallback_sections is not None:
                return list(fallback_sections)
            return self.text_engine.auto_section_split(text)
        resolved: list[str] = []
        for item in hinted_sections:
            if isinstance(item, dict):
                if "text" in item:
                    resolved.append(str(item["text"]))
                elif "content" in item:
                    resolved.append(str(item["content"]))
            elif isinstance(item, str):
                resolved.append(item)
        if not resolved:
            return self.text_engine.auto_section_split(text)
        return resolved


def _ensure_tokens(section: str) -> list[str]:
    return [token for token in section.split() if token]


def _ensure_iterable(value: Any) -> Iterable[Any] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _merge_command_lists(
    detected: list[Dict[str, Any]],
    hinted: Iterable[Any],
) -> list[Dict[str, Any]]:
    merged = list(detected)
    seen_raw = {cmd.get("raw") for cmd in merged if isinstance(cmd, dict)}
    for item in hinted:
        if not isinstance(item, dict):
            continue
        raw = item.get("raw") or item.get("type")
        if raw in seen_raw:
            continue
        merged.append({k: v for k, v in item.items()})
        seen_raw.add(raw)
    return merged
