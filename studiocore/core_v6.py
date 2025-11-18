"""StudioCore v6 compatibility wrapper.

The implementation does not aim to be feature-complete.  Instead it provides a
stable, testable façade that wires the existing monolith (v5) into the new
logical engines required by the Codex specification.  Each helper returns
structured data so downstream tooling can evolve without breaking imports.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Sequence

from .bpm_engine import BPMEngine
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
from .section_intelligence import SectionIntelligenceEngine
from .suno_annotations import SunoAnnotationEngine
from .text_utils import detect_language, translate_text_for_analysis
from .user_override_manager import UserOverrideManager, UserOverrides


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
        self.rem_engine = REM_Synchronizer()
        self.zero_pulse_engine = ZeroPulseEngine()
        self.command_interpreter = CommandInterpreter()
        self.style_engine = StyleEngine()
        self.annotation_engine = LyricsAnnotationEngine()
        self.compiler = FinalCompiler()
        self.suno_engine = SunoAnnotationEngine()
        self.override_engine = UserOverrideEngine()
        self.symbiosis_engine = UserAdaptiveSymbiosisEngine()
        self.tlp_engine = TruthLovePainEngine()
        self.rde_engine = RhythmDynamicsEmotionEngine()

        # Late import to avoid circular dependencies during module import time.
        from .monolith_v4_3_1 import StudioCore as LegacyCore  # pylint: disable=import-outside-toplevel

        self._legacy_core_cls = LegacyCore

    def analyze(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        params = self._merge_user_params(dict(kwargs))
        overrides: UserOverrides = params.get("user_overrides")
        override_manager = UserOverrideManager(overrides)
        language_info = detect_language(text)
        language_info["original_text_preview"] = text[:500]
        translated_text = translate_text_for_analysis(text, language_info["language"])
        language_info["was_translated"] = translated_text != text
        auto_context = self._auto_generate_missing_params(
            translated_text,
            params.get("semantic_hints"),
            overrides,
            language_info=language_info,
        )

        semantic_hints = auto_context.get("semantic_hints", {})

        backend_payload = self._backend_analyze(
            translated_text,
            preferred_gender=params.get("preferred_gender", "auto"),
            version=params.get("version"),
            semantic_hints=semantic_hints,
            auto_context=auto_context,
            override_manager=override_manager,
            language_info=language_info,
            original_text=text,
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

    def _auto_generate_missing_params(
        self,
        text: str,
        existing_hints: Dict[str, Any] | None = None,
        overrides: UserOverrides | None = None,
        *,
        language_info: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        existing_hints = dict(existing_hints or {})
        if overrides and overrides.structure_hints:
            existing_hints.setdefault("sections", overrides.structure_hints)
        if overrides and overrides.semantic_hints:
            existing_hints = self._merge_semantic_hints(existing_hints, overrides.semantic_hints)

        auto_sections = self.text_engine.auto_section_split(text)
        hinted_sections = existing_hints.get("sections")
        sections = self._resolve_sections_from_hints(text, hinted_sections, fallback_sections=auto_sections)
        section_result = self.section_parser.parse(text, sections=sections)
        section_meta = section_result.metadata
        commands = self.command_interpreter.detect_commands_in_text(text)
        hinted_commands = existing_hints.get("commands") if isinstance(existing_hints, dict) else None
        if hinted_commands:
            commands = _merge_command_lists(commands, hinted_commands)

        emotion_profile = self.emotion_engine.emotion_detection(text)
        intensity_curve = self.emotion_engine.emotion_intensity_curve(text)

        section_intel = self.section_intelligence.analyze(text, sections, intensity_curve)

        generated_hints = {
            "section_count": len(sections),
            "section_lengths": [len(_ensure_tokens(section)) for section in sections],
            "dominant_emotion": max(emotion_profile, key=emotion_profile.get) if emotion_profile else None,
            "command_count": len(commands),
            "section_intelligence": section_intel,
            "section_headers": section_meta,
            "annotations": section_result.annotations,
        }

        if intensity_curve:
            generated_hints["emotion_curve_max"] = max(intensity_curve)
        if hinted_sections:
            generated_hints["sections"] = hinted_sections
        if language_info:
            generated_hints["language"] = dict(language_info)

        merged_hints = self._merge_semantic_hints(generated_hints, existing_hints)

        return {
            "semantic_hints": merged_hints,
            "sections": sections,
            "commands": commands,
            "emotion_profile": self._merge_semantic_hints(dict(emotion_profile), existing_hints.get("emotion_profile", {})),
            "emotion_curve": intensity_curve,
            "section_intelligence": section_intel,
            "section_metadata": section_meta,
            "language": language_info,
            "annotations": section_result.annotations,
        }

    def _backend_analyze(
        self,
        text: str,
        *,
        preferred_gender: str,
        version: str | None,
        semantic_hints: Dict[str, Any],
        auto_context: Dict[str, Any],
        override_manager: UserOverrideManager,
        language_info: Dict[str, Any] | None = None,
        original_text: str | None = None,
    ) -> Dict[str, Any]:
        sections = auto_context.get("sections", [])
        hinted_sections = semantic_hints.get("sections")
        if hinted_sections:
            sections = self._resolve_sections_from_hints(text, hinted_sections) or sections
        section_intel_payload = auto_context.get("section_intelligence") or self.section_intelligence.analyze(
            text, sections, auto_context.get("emotion_curve")
        )

        emotion_profile = self._merge_semantic_hints(
            auto_context.get("emotion_profile", {}),
            semantic_hints.get("emotion_profile", {}),
        )
        emotion_curve = auto_context.get("emotion_curve", [])
        commands = auto_context.get("commands", [])

        # 1. Call the legacy core for full analysis.
        try:
            legacy_core = self._legacy_core_cls()
            legacy_result = legacy_core.analyze(
                original_text or text,
                preferred_gender=preferred_gender,
                version=version,
                semantic_hints=semantic_hints or None,
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
        if auto_context.get("section_metadata"):
            structure["headers"] = auto_context["section_metadata"]
        if language_info:
            structure["language"] = dict(language_info)

        zero_hint = self.text_engine.detect_zero_pulse(text, sections=sections)

        # 3. Emotional layers
        emotion_payload = {
            "profile": emotion_profile,
            "curve": emotion_curve,
            "pivots": self.emotion_engine.emotion_pivot_points(text, intensity_curve=emotion_curve),
            "secondary": self.emotion_engine.secondary_emotion_detection(emotion_profile),
            "conflict": self.emotion_engine.emotion_conflict_map(emotion_profile),
        }
        tlp_profile = self.tlp_engine.analyze(text)
        emotion_payload = self._merge_semantic_hints(emotion_payload, semantic_hints.get("emotion", {}))

        # 4. Tonal colours and style hints
        color_profile = self.color_engine.assign_color_by_emotion(emotion_profile)
        color_profile = self._merge_semantic_hints(color_profile, semantic_hints.get("color", {}))
        color_wave = self.color_engine.generate_color_wave(emotion_profile)
        color_transitions = self.color_engine.color_transition_map(emotion_profile)

        # 5. Vocal character
        voice_gender = self.vocal_engine.detect_voice_gender(text)
        voice_type = self.vocal_engine.detect_voice_type(text)
        voice_tone = self.vocal_engine.detect_voice_tone(text)
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
        vocal_payload = self.override_engine.apply_to_vocals(vocal_payload, override_manager)

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
        bpm_estimate = self.bpm_engine.text_bpm_estimation(text)
        if isinstance(semantic_hints.get("target_bpm"), (int, float)):
            bpm_estimate = float(semantic_hints["target_bpm"])
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
        bpm_payload = self.override_engine.apply_to_rhythm(bpm_payload, override_manager)

        annotations_from_text = auto_context.get("annotations", [])
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
            vocal_payload.get("style"),
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

        # 14. Style synthesis
        style_commands = command_payload.get("style") or {}
        style_genre = (
            style_commands.get("genre")
            or semantic_hints.get("style", {}).get("genre")
            or self.style_engine.genre_selection(emotion_profile, tlp_profile)
        )
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
        if style_commands.get("intensity"):
            style_payload["intensity"] = style_commands["intensity"]
        if style_commands:
            style_payload["commands"] = style_commands
        style_payload = self._merge_semantic_hints(style_payload, semantic_hints.get("style", {}))
        style_payload = self.override_engine.apply_to_style(style_payload, override_manager)

        rde_summary = self.rde_engine.compose(
            bpm_payload=bpm_payload,
            breathing_profile={**breathing_profile, "sync_score": breath_sync},
            emotion_profile=emotion_profile,
            instrumentation_payload=instrumentation_payload,
        )

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

        suno_annotations = self.suno_engine.build_suno_safe_annotations(
            sections,
            {
                "bpm": bpm_payload,
                "instrumentation": {
                    "palette": instrumentation_payload.get("palette"),
                    "fractures": instrument_dynamics_payload.get("fractures"),
                },
                "vocal": vocal_payload,
                "commands": command_payload,
            },
        )

        result = {
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
            "style": style_payload,
            "commands": command_payload,
            "annotations": annotations,
            "semantic_hints": semantic_hints,
            "auto_context": auto_context,
            "instrument_dynamics": instrument_dynamics_payload,
            "suno_annotations": suno_annotations,
            "override_debug": override_manager.debug_summary(),
            "rde_summary": rde_summary,
        }
        result["symbiosis"] = self.symbiosis_engine.build_final_symbiosis_state(override_manager, result)
        if language_info:
            result["language"] = dict(language_info)
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
        merged["suno_annotations"] = payload.get("suno_annotations", [])
        merged["symbiosis"] = payload.get("symbiosis", {})
        merged["override_debug"] = payload.get("override_debug", {})
        merged["language"] = payload.get("language", payload.get("auto_context", {}).get("language"))
        merged["rde_summary"] = payload.get("rde_summary", {})
        return merged

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
