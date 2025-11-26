# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
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
import logging
from typing import Any, Dict, Iterable, List, Sequence

from .bpm_engine import BPMEngine
from .multimodal_emotion_matrix import MultimodalEmotionMatrixV1
from .color_engine_adapter import ColorEngineAdapter
from .emotion_field import EmotionFieldEngine
from .emotion_profile import EmotionAggregator, EmotionVector
# HIGH PRIORITY FIX: Move imports to top for "Fail Fast" behavior
from .tone import ToneSyncEngine as LegacyToneSyncEngine
from .tone_sync import ToneSyncEngine
from .genre_router import DynamicGenreRouter
from .genre_universe_adapter import GenreUniverseAdapter
from .dynamic_emotion_engine import DynamicEmotionEngine
from .tlp_engine import TruthLovePainEngine
from .rde_engine import RhythmDynamicsEmotionEngine, ResonanceDynamicsEngine
from .genre_matrix_extended import GenreMatrixExtended, GenreMatrixEngine
from .section_parser import SectionParser
from .emotion_genre_matrix import compute_genre_bias
from .logical_engines import (
    BreathingEngine,
    ColorEmotionEngine,
    CommandInterpreter,
    EmotionEngine as LegacyEmotionEngine,
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
from .emotion import EmotionEngine, EmotionEngineV2
from .instrument_dynamics import InstrumentalDynamicsEngine
from .integrity import IntegrityScanEngine
from .section_intelligence import SectionIntelligenceEngine
from .suno_annotations import (
    SunoAnnotationEngine,
    _dominant_emotion,
    build_suno_annotations,
    emotion_to_instruments,
    emotion_to_style,
    emotion_to_vocal,
)
from .fanf_annotation import FANFAnnotationEngine
from .text_utils import (
    detect_language,
    extract_commands_and_tags,
    translate_text_for_analysis,
)
from .user_override_manager import UserOverrideManager, UserOverrides
from .adapter import build_suno_prompt
from .fusion_engine_v64 import FusionEngineV64
from studiocore.emotion_map import EmotionMapEngine
from studiocore.emotion_curve import build_global_emotion_curve
from studiocore.frequency import RNSSafety, UniversalFrequencyEngine
from studiocore.config import (
    DEFAULT_CONFIG, 
    FORCED_GENRES,
    ALGORITHM_WEIGHTS,
    ROAD_NARRATIVE_KEYWORDS,
    FOLK_BALLAD_KEYWORDS,
    FOLK_BALLAD_KEYWORDS_LEGACY,
)
from studiocore.diagnostics_v8 import DiagnosticsBuilderV8
from studiocore.consistency_v8 import ConsistencyLayerV8
from studiocore.logger_runtime import write_runtime_log

# === MASTER_PATCH V6.1 HOOK ===
try:
    from .master_patch_v6_1 import *
except (ImportError, Exception) as e:
    # MEDIUM PRIORITY FIX: Use specific exception and log
    logger.warning(f"Master Patch V6.1 import failed: {e}")

logger = logging.getLogger(__name__)

import threading

_GENRE_UNIVERSE = None
_genre_universe_lock = threading.Lock()


def get_genre_universe():
    """
    Thread-safe cached GenreUniverse loader.
    
    Uses double-checked locking pattern to ensure thread-safety
    while avoiding unnecessary locking after initialization.
    """
    global _GENRE_UNIVERSE
    if _GENRE_UNIVERSE is None:
        with _genre_universe_lock:
            # Double-checked locking: check again after acquiring lock
            if _GENRE_UNIVERSE is None:
                from .genre_universe_loader import load_genre_universe
                _GENRE_UNIVERSE = load_genre_universe()
    return _GENRE_UNIVERSE


_BRACKET_LINE_RE = re.compile(r"^\s*\[.*\]\s*$")


def _extract_ui_text(from_block: str) -> str:
    lines = from_block.splitlines()
    clean_lines: list[str] = []
    for ln in lines:
        if _BRACKET_LINE_RE.match(ln.strip()):
            continue
        if not ln.strip():
            clean_lines.append(ln)
            continue
        clean_lines.append(ln)
    text = "\n".join(clean_lines).strip()
    return text


def _build_summary_block(diagnostics: dict) -> str:
    """
    Build a single human-readable summary block from diagnostics fields.

    Expected keys (if present):
      - tlp_block
      - rde_block
      - genre_block
      - zeropulse_block
      - color_wave_block
      - integrity_block
    """
    parts: list[str] = []

    for key in (
        "tlp_block",
        "rde_block",
        "genre_block",
        "zeropulse_block",
        "color_wave_block",
        "integrity_block",
    ):
        value = diagnostics.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())

    summary_block = "\n".join(parts).strip()
    if not summary_block:
        summary_block = "[TLP: 0/0/0 | CF 0.0]\n[RDE: no rhythm detected]\n[Integrity: undefined]"

    diagnostics["summary_block"] = summary_block
    return summary_block


def _safe_float(value: object, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:  # noqa: BLE001
        return default


def _build_consistency_report(
    diagnostics: dict,
    payload: dict,
) -> dict:
    """
    Build a semantic consistency report for the current analysis.

    It compares:
      - bpm in diagnostics vs bpm/style/fanf
      - tlp vs conscious_frequency (if present)
      - genre tags vs primary genre/style
      - tone_profile vs key (if present)

    Returns a dict with boolean flags and notes and also attaches it into diagnostics.
    """
    report: dict[str, object] = {
        "ok": True,
        "warnings": [],
        "checks": {},
    }

    checks: dict[str, bool] = {}
    warnings: list[str] = []

    # -----------------------
    # BPM consistency
    # -----------------------
    diag_bpm = _safe_float(diagnostics.get("bpm"))
    fanf = payload.get("fanf") or {}
    style_block = payload.get("style") or {}
    # FanF may not carry bpm explicitly, so we try a few places.
    fanf_bpm = _safe_float(fanf.get("bpm"))
    style_bpm = _safe_float(style_block.get("bpm"))

    bpm_values = [v for v in (diag_bpm, fanf_bpm, style_bpm) if v is not None]

    bpm_consistent = True
    if len(bpm_values) > 1:
        # consider consistent if all are within ±3 BPM of each other
        min_bpm = min(bpm_values)
        max_bpm = max(bpm_values)
        bpm_consistent = (max_bpm - min_bpm) <= 3.0

    checks["bpm_consistent"] = bpm_consistent
    if not bpm_consistent:
        warnings.append("BPM mismatch between diagnostics/style/FANF.")

    # -----------------------
    # TLP / Conscious Frequency
    # -----------------------
    tlp_data = diagnostics.get("tlp") or diagnostics.get("tlp_vector")
    cf_diag = _safe_float(
        diagnostics.get("conscious_frequency")
        or diagnostics.get("cf")
    )

    cf_recomputed: float | None = None
    if isinstance(tlp_data, dict):
        t = _safe_float(tlp_data.get("truth"), 0.0) or 0.0
        l = _safe_float(tlp_data.get("love"), 0.0) or 0.0
        p = _safe_float(tlp_data.get("pain"), 0.0) or 0.0
        total = t + l + p
        if total > 0:
            # The precise formula can be adjusted, but we keep it simple and
            # consistent with previous documentation.
            # Use externalized weights from config
            cf_recomputed = (
                t * ALGORITHM_WEIGHTS["tlp_truth_weight"] + 
                l * ALGORITHM_WEIGHTS["tlp_love_weight"] + 
                p * ALGORITHM_WEIGHTS["tlp_pain_weight"]
            ) / total

    tlp_consistent = True
    if cf_diag is not None and cf_recomputed is not None:
        # small numeric tolerance
        tlp_consistent = abs(cf_diag - cf_recomputed) <= 0.05

    checks["tlp_consistent"] = tlp_consistent
    if not tlp_consistent:
        warnings.append("Conscious Frequency differs from TLP-derived value.")

    # -----------------------
    # Genre vs primary style
    # -----------------------
    primary_genre = None
    if isinstance(style_block, dict):
        primary_genre = style_block.get("genre") or style_block.get("primary_genre")

    genre_tags = diagnostics.get("genre_universe_tags")
    genre_consistent = True
    if primary_genre and isinstance(genre_tags, (list, tuple)) and genre_tags:
        # require at least one tag sharing a substring with primary genre
        genre_consistent = any(
            isinstance(tag, str)
            and isinstance(primary_genre, str)
            and (
                primary_genre.lower() in tag.lower()
                or tag.lower() in primary_genre.lower()
            )
            for tag in genre_tags
        )

    checks["genre_consistent"] = genre_consistent
    if not genre_consistent:
        warnings.append("Primary style/genre does not match GenreUniverse tags.")

    # -----------------------
    # Tone / key consistency
    # -----------------------
    tone_profile = diagnostics.get("tone_profile")
    style_key = None
    if isinstance(style_block, dict):
        style_key = style_block.get("key")

    tone_consistent = True
    if tone_profile and isinstance(tone_profile, dict) and style_key:
        # If tone_profile includes a key, check they match at least on note name
        tone_key = tone_profile.get("key") or tone_profile.get("primary_key")
        if isinstance(tone_key, str) and isinstance(style_key, str):
            tone_consistent = tone_key.split()[0].upper() == style_key.split()[0].upper()

    checks["tone_consistent"] = tone_consistent
    if not tone_consistent:
        warnings.append("ToneSync key/profile does not match style key.")

    # -----------------------
    # Final flags
    # -----------------------
    report["checks"] = checks
    report["warnings"] = warnings
    report["ok"] = all(checks.values())

    diagnostics["consistency"] = report

    # Do not raise, only log in debug mode so CI is not blocked.
    if not report["ok"]:
        logger.debug("StudioCore consistency report: %s", report)

    return report

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
    # === MASTER_PATCH_V5_SKELETON: BEGIN ===
    # Hooks for:
    #  - HybridGenreEngine (HGE)
    #  - RageFilterV2
    #  - EpicOverride
    #  - SectionMergeMode (SM2)
    #  - HybridInstrumentationLayer (HIL)
    #  - GenreConflictResolver (GCR)
    #  - NeutralModePreFinalizer (NMPF)
    #  - ColorEngineV3 (CEv3)
    # These are NO-OP in v5.0 skeleton and only provide structure.
    # === MASTER_PATCH_V5_SKELETON: END ===
    
    # === MASTER_PATCH V6.1 HOOK ===

    # === Normalized snapshot helper ===
    def _inject_normalized_snapshot(self, text_for_analysis: str, result: dict) -> dict:
        """
        Ensure normalized_text / normalized_sections / auto_context.normalized
        are always present, even when translation is not configured.
        This is a non-destructive helper: it only fills missing fields.
        """
        if result is None or not isinstance(result, dict):
            return result

        auto_ctx = result.get("auto_context") or {}
        if not isinstance(auto_ctx, dict):
            auto_ctx = {}

        normalized = auto_ctx.get("normalized") or {}
        if not isinstance(normalized, dict):
            normalized = {}

        # Base text
        normalized_text = normalized.get("text") or text_for_analysis
        normalized["text"] = normalized_text

        # Sections: prefer normalized sections, then generic 'sections'
        sections = normalized.get("sections") or result.get("sections")
        if sections is not None:
            normalized["sections"] = sections

        auto_ctx["normalized"] = normalized
        result["auto_context"] = auto_ctx

        # Expose top-level normalized fields for external consumers
        result.setdefault("normalized_text", normalized_text)
        if sections is not None:
            result.setdefault("normalized_sections", sections)

        return result

    # === Fusion + Suno integration helper ===
    def _apply_fusion_and_suno(self, result: dict) -> dict:
        """
        Best-effort integration of FusionEngineV64 and Suno prompt builder.
        Never raises: all errors are captured into diagnostics.fusion / diagnostics.suno.
        """
        if result is None or not isinstance(result, dict):
            return result

        diagnostics = result.get("diagnostics") or {}
        if not isinstance(diagnostics, dict):
            diagnostics = {}
        result["diagnostics"] = diagnostics

        def _errors_list() -> list:
            errors = diagnostics.get("errors")
            if not isinstance(errors, list):
                errors = [] if errors is None else [errors]
                diagnostics["errors"] = errors
            return errors

        try:
            from .fusion_engine_v64 import FusionEngineV64
        except Exception as e:
            logger.exception("FusionEngineV64 import failed: %s", e)
            diagnostics.setdefault("fusion_warning", str(e))
            _errors_list().append("fusion_import_failed")
            FusionEngineV64 = None  # type: ignore

        try:
            from .adapter import build_suno_prompt
        except Exception as e:
            logger.exception("Suno prompt adapter import failed: %s", e)
            diagnostics.setdefault("suno_prompt_warning", str(e))
            _errors_list().append("suno_prompt_import_failed")
            build_suno_prompt = None  # type: ignore

        fusion_summary = None

        # --- Fusion summary (optional) ---
        if FusionEngineV64 is not None:
            try:
                # Получаем genre_route из result
                genre_route = result.get("style", {}).get("genre_route") or result.get("genre_route") or {}
                if genre_route:
                    fusion = FusionEngineV64()
                    fusion_summary = fusion.fuse(result, genre_route=genre_route)
                if fusion_summary is not None:
                    result["fusion_summary"] = fusion_summary
            except Exception as e:
                logger.exception("Fusion generate failed: %s", e)
                _errors_list().append("fusion_generate_failed")
                diagnostics["fusion_warning"] = f"FusionEngineV64 failed: {e}"

        # --- Suno prompt (optional) ---
        if build_suno_prompt is not None:
            try:
                # Получаем необходимые параметры из result
                style_data = result.get("style", {}) or {}
                vocals = result.get("vocal", {}).get("techniques", []) if isinstance(result.get("vocal"), dict) else []
                instruments = result.get("instrumentation", {}).get("selection", []) if isinstance(result.get("instrumentation"), dict) else []
                bpm_val = result.get("bpm", {})
                if isinstance(bpm_val, dict):
                    bpm_val = bpm_val.get("estimate") or bpm_val.get("target_bpm") or 120
                elif not isinstance(bpm_val, (int, float)):
                    bpm_val = 120
                bpm_val = int(bpm_val)
                
                philosophy = result.get("philosophy", "adaptive emotional")
                version = result.get("version", "v5")
                
                suno_prompt = build_suno_prompt(
                    style_data=style_data,
                    vocals=vocals or [],
                    instruments=instruments or [],
                    bpm=bpm_val,
                    philosophy=philosophy,
                    version=version,
                    prompt_variant="suno_style"
                )
                if suno_prompt:
                    result["suno_prompt"] = suno_prompt
            except Exception as e:
                logger.exception("Suno prompt build failed: %s", e)
                _errors_list().append("suno_prompt_build_failed")
                diagnostics["suno_prompt_warning"] = f"suno prompt build failed: {e}"

        result["diagnostics"] = diagnostics
        return result

    def __init__(self) -> None:
        """
        Stateless constructor: initialize static config and stateless engines.
        
        HIGH PRIORITY FIX: Stateless engines are initialized once here to avoid
        re-instantiation overhead on every analyze() call.
        """

        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self._engine_bundle: dict[str, object] = {}
        
        # Initialize stateless engines once (HIGH PRIORITY FIX: Performance optimization)
        # These engines have no state and can be reused across requests
        self._text_engine = TextStructureEngine()
        self._section_parser = SectionParser(self._text_engine)
        self._emotion_engine = EmotionEngine()
        self._bpm_engine = BPMEngine()
        self._frequency_engine = UniversalFrequencyEngine()
        self._tlp_engine = TruthLovePainEngine()
        self._rde_engine = RhythmDynamicsEmotionEngine()
        self._genre_router_ext = GenreMatrixExtended()
        # Use LegacyToneSyncEngine (from tone.py) for detect_key() method
        self._tone_engine = LegacyToneSyncEngine()
        self._integrity_engine = IntegrityScanEngine()
        self._dynamic_emotion_engine = DynamicEmotionEngine()
        self._section_intelligence = SectionIntelligenceEngine()
        self._meaning_engine = MeaningVelocityEngine()
        self._instrument_dynamics = InstrumentalDynamicsEngine()
        self._color_adapter = ColorEngineAdapter()
        self._color_emotion_engine = ColorEmotionEngine()
        self._color_wave_engine = self._color_emotion_engine  # Alias
        self._instrumentation_engine = InstrumentationEngine()
        self._command_interpreter = CommandInterpreter()
        self._rem_engine = REM_Synchronizer()
        self._zero_pulse_engine = ZeroPulseEngine()
        self._annotation_engine = LyricsAnnotationEngine()
        self._genre_matrix = GenreMatrixEngine()
        self._style_engine = StyleEngine()
        self._genre_router = DynamicGenreRouter()
        self._genre_universe_adapter = GenreUniverseAdapter()
        self._emotion_aggregator = EmotionAggregator()
        self._vocal_engine = VocalEngine()
        self._rns_safety = RNSSafety(self.config)
        self._legacy_emotion_engine = EmotionEngine()  # Legacy alias
        self._legacy_tone_engine = LegacyToneSyncEngine()  # Legacy alias (same as _tone_engine)
        self._multimodal_matrix = MultimodalEmotionMatrixV1()
        self._breathing_engine = BreathingEngine()
        self._suno_engine = SunoAnnotationEngine()
        self._fanf_engine = FANFAnnotationEngine()
        self._compiler = FinalCompiler()
        self._resonance_engine = ResonanceDynamicsEngine()
        self._emotion_engine_v2 = EmotionEngineV2()
        
        # Classes and functions (not instances)
        self._fusion_builder_cls = FusionEngineV64
        self._suno_prompt_builder_fn = build_suno_prompt
        self._user_override_manager_cls = UserOverrideManager
        
        # MASTER_PATCH_V5_SKELETON: helper modules (NO-OP)
        # Note: HybridGenreEngine is already defined as inner class in v6.0, so we use that
        try:
            from .rage_filter_v2 import RageFilterV2
            from .epic_override import EpicOverride
            from .section_merge_mode import SectionMergeMode
            from .hybrid_instrumentation import HybridInstrumentationLayer
            from .genre_conflict_resolver import GenreConflictResolver
            from .neutral_mode import NeutralModePreFinalizer
            from .color_engine_v3 import ColorEngineV3
        except (ImportError, Exception) as e:
            # MEDIUM PRIORITY FIX: Use specific exception and log
            logger.warning(f"Master Patch modules import failed: {e}")
            RageFilterV2 = EpicOverride = SectionMergeMode = \
                HybridInstrumentationLayer = GenreConflictResolver = \
                NeutralModePreFinalizer = ColorEngineV3 = None

        # Use external HybridGenreEngine class (from hybrid_genre_engine.py)
        try:
            from .hybrid_genre_engine import HybridGenreEngine as ExternalHGE
            self._hge = ExternalHGE()
        except ImportError as e:
            # MEDIUM PRIORITY FIX: Log the import error
            logger.warning(f"External HybridGenreEngine import failed: {e}, using fallback")
            # Fallback to inner class if external not available
            self._hge = self.HybridGenreEngine() if hasattr(self, 'HybridGenreEngine') else None
        self._rage_filter = RageFilterV2() if RageFilterV2 else None
        self._epic_override = EpicOverride() if EpicOverride else None
        self._section_merge_mode = SectionMergeMode() if SectionMergeMode else None
        self._hil = HybridInstrumentationLayer() if HybridInstrumentationLayer else None
        self._gcr = GenreConflictResolver() if GenreConflictResolver else None
        self._neutral_prefinal = NeutralModePreFinalizer() if NeutralModePreFinalizer else None
        self._color_v3 = ColorEngineV3() if ColorEngineV3 else None

    def __getattr__(self, name: str):
        # HIGH PRIORITY FIX: Support both _engine_bundle (legacy) and direct attributes
        # First check _engine_bundle (for backward compatibility)
        bundle = self.__dict__.get("_engine_bundle", {})
        if name in bundle:
            return bundle[name]
        # Then check if it's a direct engine attribute (with _ prefix)
        if name.startswith("_"):
            # Try without underscore
            direct_name = name
        else:
            # Try with underscore (engines are stored as _engine_name)
            direct_name = f"_{name}"
        if hasattr(self, direct_name):
            return getattr(self, direct_name)
        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

    def _validate_and_sanitize_input(self, text: str, diagnostics: dict) -> str:
        """
        Validate and sanitize input text to prevent prompt injection and other attacks.
        
        Args:
            text: Input text to validate
            diagnostics: Diagnostics dict to update with validation info
            
        Returns:
            Sanitized text
            
        Raises:
            ValueError: If text is invalid or dangerous
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        if not text.strip():
            raise ValueError("Empty input text")
        
        original_length = len(text)
        
        # Проверка длины
        max_len = int(
            getattr(self.config, "MAX_INPUT_LENGTH", 0)
            or (self.config.get("MAX_INPUT_LENGTH") if isinstance(self.config, dict) else 0)
            or 16000
        )
        if len(text) > max_len:
            logger.warning(f"Input text too long: {len(text)} > {max_len}, truncating")
            text = text[:max_len]
            diagnostics.update({
                "input_truncated": True,
                "max_input_length": max_len,
                "original_length": original_length,
            })
        else:
            diagnostics.update({"input_truncated": False})
        
        # Защита от prompt injection
        dangerous_patterns = [
            (r'\[SYSTEM\]', 'SYSTEM tag'),
            (r'\[INST\]', 'INST tag'),
            (r'<\|.*?\|>', 'Special tokens'),
            (r'\{.*?prompt.*?\}', 'Prompt injection pattern'),
            (r'\{.*?injection.*?\}', 'Injection pattern'),
            (r'\{.*?system.*?\}', 'System pattern'),
            (r'\{.*?assistant.*?\}', 'Assistant pattern'),
            (r'\{.*?user.*?\}', 'User pattern'),
            (r'<script.*?>', 'Script tag'),
            (r'javascript:', 'JavaScript protocol'),
            (r'onerror=', 'Event handler'),
            (r'onload=', 'Event handler'),
        ]
        
        sanitized_text = text
        detected_patterns = []
        for pattern, description in dangerous_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected_patterns.append(description)
                # Удаляем опасные паттерны
                sanitized_text = re.sub(pattern, '', sanitized_text, flags=re.IGNORECASE)
                logger.warning(f"Potential prompt injection detected: {description}, removed")
        
        if detected_patterns:
            diagnostics.update({
                "prompt_injection_detected": True,
                "detected_patterns": detected_patterns,
                "sanitized_length": len(sanitized_text),
            })
            logger.warning(f"Input sanitized due to detected patterns: {detected_patterns}")
        
        # Удаляем лишние пробелы после санитизации
        sanitized_text = sanitized_text.strip()
        
        if not sanitized_text:
            raise ValueError("Text became empty after sanitization")
        
        return sanitized_text

    def _build_engine_bundle(self) -> dict[str, object]:
        """Create engine bundle using pre-initialized stateless engines.
        
        HIGH PRIORITY FIX: Uses engines initialized in __init__ to avoid
        re-instantiation overhead. Only request-specific data is created here.
        """
        # Use pre-initialized stateless engines from __init__
        # Request-specific layers (empty dicts for now, populated per request)
        consistency_layer = ConsistencyLayerV8({})
        diagnostics_builder = DiagnosticsBuilderV8({})
        
        # Import legacy core dynamically (only used for fallback)
        from . import StudioCore as LegacyStudioCore

        # Return bundle using pre-initialized engines
        return {
            "text_engine": self._text_engine,
            "section_parser": self._section_parser,
            "emotion_engine": self._emotion_engine,
            "bpm_engine": self._bpm_engine,
            "frequency_engine": self._frequency_engine,
            "tlp_engine": self._tlp_engine,
            "rde_engine": self._rde_engine,
            "genre_router_ext": self._genre_router_ext,
            "tone_engine": self._tone_engine,
            "integrity_engine": self._integrity_engine,
            "dynamic_emotion_engine": self._dynamic_emotion_engine,
            "section_intelligence": self._section_intelligence,
            "meaning_engine": self._meaning_engine,
            "instrument_dynamics": self._instrument_dynamics,
            "color_adapter": self._color_adapter,
            "color_wave_engine": self._color_wave_engine,
            "instrumentation_engine": self._instrumentation_engine,
            "command_interpreter": self._command_interpreter,
            "rem_engine": self._rem_engine,
            "zero_pulse_engine": self._zero_pulse_engine,
            "annotation_engine": self._annotation_engine,
            "genre_matrix": self._genre_matrix,
            "style_engine": self._style_engine,
            "genre_router": self._genre_router,
            "genre_universe_adapter": self._genre_universe_adapter,
            "_emotion_engine": self._emotion_aggregator,
            "vocal_engine": self._vocal_engine,
            "instrumentation_selector": self._instrumentation_engine,  # Alias
            "rns_safety": self._rns_safety,
            "legacy_emotion_engine": self._legacy_emotion_engine,
            "legacy_tone_engine": self._legacy_tone_engine,
            "multimodal_matrix": self._multimodal_matrix,
            "color_emotion_engine": self._color_emotion_engine,
            "breathing_engine": self._breathing_engine,
            "consistency_layer": consistency_layer,  # Request-specific
            "diagnostics_builder": diagnostics_builder,  # Request-specific
            "suno_engine": self._suno_engine,
            "fanf_engine": self._fanf_engine,
            "resonance_engine": self._resonance_engine,
            "fusion_builder": self._fusion_builder_cls,
            "suno_prompt_builder": self._suno_prompt_builder_fn,
            "integrity_scan_engine": self._integrity_engine,  # Reuse
            "emotion_engine_v2": self._emotion_engine_v2,
            "user_override_manager_cls": self._user_override_manager_cls,
            "compiler": self._compiler,
            "_legacy_core_cls": LegacyStudioCore,
        }

    def _reset_state(self) -> None:
        """Remove only transient state after analyze(), preserve system components.
        
        CRITICAL FIX: Only clear transient data (_engine_bundle), not system components
        like _hge, _rage_filter, _epic_override, etc. that were initialized in __init__.
        """
        # Only clear transient request-scoped data
        if hasattr(self, '_engine_bundle'):
            self._engine_bundle = {}
        
        # Preserve all system components initialized in __init__:
        # - self._hge
        # - self._rage_filter
        # - self._epic_override
        # - self._section_merge_mode
        # - self._hil
        # - self._gcr
        # - self._neutral_prefinal
        # - self._color_v3
        # - self.config

    def analyze(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Main analysis entry point. Coordinates all engines and returns structured results.
        
        Refactored to reduce complexity by extracting logical blocks into separate methods.
        """
        engines = self._build_engine_bundle()   # STATELESS FIX: Always build fresh bundle
        # Removed: self._engine_bundle = engines  # STATELESS: Don't cache between requests
        diagnostics: dict[str, object] = {}
        payload: dict[str, object] = {
            "engine": "StudioCoreV6",
            "ok": True,
            "diagnostics": diagnostics,
        }

        def _errors_list() -> list:
            errors = diagnostics.get("errors")
            if not isinstance(errors, list):
                errors = [] if errors is None else [errors]
                diagnostics["errors"] = errors
            return errors

        # Input validation
        validation_result = self._validate_input(text, payload)
        if validation_result is not None:
            return validation_result

        try:
            # Extract engines (already done in _extract_engines, but we need them here too)
            text_engine = engines["text_engine"]
            
            # Prepare text and structure context
            preparation_result = self._prepare_text_and_structure(
                text, engines, diagnostics, kwargs
            )
            if preparation_result is None:
                payload.update({"ok": False, "error": "text_preparation_failed"})
                _errors_list().append("text_preparation_failed")
                return payload
            
            incoming_text = preparation_result["incoming_text"]
            normalized_text = preparation_result["normalized_text"]
            structure_context = preparation_result["structure_context"]
            params = preparation_result["params"]
            override_manager = preparation_result["override_manager"]
            command_bundle = preparation_result["command_bundle"]
            language_info = preparation_result["language_info"]
            # MASTER-PATCH: Используем sections_text если есть (реальный текст), иначе sections (имена)
            sections = list(structure_context.get("sections_text", structure_context.get("sections", [])))
            section_metadata = {
                "section_metadata": structure_context.get("section_metadata", []),
                "annotations": structure_context.get("annotations", []),
            }

            # Main analysis
            backend_payload = self._backend_analyze(
                normalized_text,
                preferred_gender=params.get("preferred_gender", "auto"),
                version=params.get("version"),
                semantic_hints=structure_context.get("semantic_hints", {}),
                structure_context=structure_context,
                override_manager=override_manager,
                language_info=language_info,
                original_text=preparation_result["cleaned_text"],
                command_bundle=command_bundle,
                engines=engines,
            )

            # Post-analysis processing
            backend_payload = self._inject_normalized_snapshot(normalized_text, backend_payload)
            backend_payload = self._apply_fusion_and_suno(backend_payload)
            
            # Additional diagnostics and tone profile
            post_analysis_result = self._process_post_analysis(
                incoming_text, backend_payload, engines, diagnostics
            )
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем mood и color_wave из backend_payload ДО update
            # backend_updates["style"] может содержать только bpm, key, genre, subgenre
            backend_style = backend_payload.get("style", {})
            saved_mood = backend_style.get("mood") if isinstance(backend_style, dict) else None
            saved_color_wave = backend_style.get("color_wave") if isinstance(backend_style, dict) else None
            
            backend_payload.update(post_analysis_result["backend_updates"])
            diagnostics.update(post_analysis_result["diagnostics_updates"])
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Восстанавливаем mood и color_wave после update
            # backend_updates["style"] перезаписывает backend_payload["style"] без этих полей
            if saved_mood or saved_color_wave:
                backend_style_after = backend_payload.get("style", {})
                if not isinstance(backend_style_after, dict):
                    backend_style_after = {}
                if saved_mood:
                    backend_style_after["mood"] = saved_mood
                if saved_color_wave:
                    backend_style_after["color_wave"] = saved_color_wave
                backend_payload["style"] = backend_style_after
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем mood и color_wave из backend_payload ДО update
            # Это гарантирует, что они не будут потеряны при payload.update(backend_payload)
            backend_style = backend_payload.get("style", {})
            saved_mood = backend_style.get("mood") if isinstance(backend_style, dict) else None
            saved_color_wave = backend_style.get("color_wave") if isinstance(backend_style, dict) else None
            
            # Update payload with backend results
            payload.update(backend_payload)
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Восстанавливаем mood и color_wave после update
            # Убеждаемся, что style из backend_payload сохраняется в payload с mood и color_wave
            if isinstance(backend_style, dict):
                payload_style = payload.get("style", {})
                if not isinstance(payload_style, dict):
                    payload_style = {}
                
                # ЯВНО сохраняем mood и color_wave (приоритет из backend_payload)
                if saved_mood:
                    payload_style["mood"] = saved_mood
                if saved_color_wave:
                    payload_style["color_wave"] = saved_color_wave
                
                # Обновляем остальные поля из backend_style, но НЕ перезаписываем mood и color_wave
                for key, value in backend_style.items():
                    if key not in ("mood", "color_wave"):
                        payload_style[key] = value
                
                payload["style"] = payload_style
            
            # Build diagnostics and finalize result
            diagnostics_result = self._build_diagnostics_blocks(
                backend_payload, payload, diagnostics, structure_context, sections
            )
            diagnostics.update(diagnostics_result["diagnostics"])
            payload.update(diagnostics_result["payload_updates"])
            
            # Build lyrics sections with vocals
            lyrics_sections = self._build_lyrics_sections_with_vocals(
                sections, structure_context, payload
            )
            
            # Build FANF output and finalize
            final_result = self._build_final_result(
                normalized_text, incoming_text, payload, lyrics_sections, diagnostics
            )
            
            # === RUNTIME LOGGING ===================================================
            try:
                write_runtime_log({
                    "text_preview": text[:200],
                    "diagnostics": final_result.get("diagnostics"),
                    "fanf": final_result.get("fanf"),
                })
            except Exception as e:
                # Logging must never break execution
                pass
            return final_result
        finally:
            self._reset_state()

    def _validate_input(self, text: str, payload: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Validate input text and return error payload if validation fails.
        
        Returns:
            Error payload dict if validation fails, None otherwise
        """
        if not isinstance(text, str):
            payload.update({"error": DEFAULT_CONFIG.ERROR_INVALID_INPUT_TYPE, "ok": False})
            return payload
        if not text.strip():
            payload.update({"error": DEFAULT_CONFIG.ERROR_EMPTY_INPUT, "ok": False})
            return payload
        return None

    def _prepare_text_and_structure(
        self,
        text: str,
        engines: Dict[str, Any],
        diagnostics: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        """
        Prepare text for analysis: validate, sanitize, translate, and build structure context.
        
        Returns:
            Dict with prepared data or None if preparation fails
        """
        try:
            text_engine = engines["text_engine"]
            
            # Валидация и санитизация input
            incoming_text = self._validate_and_sanitize_input(text, diagnostics)
            text_engine.reset()

            params = self._merge_user_params(dict(kwargs))
            overrides: UserOverrides = params.get("user_overrides")
            override_manager = engines["user_override_manager_cls"](overrides)
            cleaned_text, command_bundle, preserved_tags = extract_commands_and_tags(incoming_text)
            commands = list(command_bundle.get("detected", []))
            language_info = detect_language(cleaned_text)
            language_info["original_text_preview"] = cleaned_text[:500]
            translated_text, was_translated = translate_text_for_analysis(
                cleaned_text, language_info["language"]
            )
            language_info["was_translated"] = bool(was_translated)
            normalized_text = translated_text
            structure_context = self._build_structure_context(
                translated_text,
                params.get("semantic_hints"),
                commands=commands,
                preserved_tags=preserved_tags,
                language_info=language_info,
                text_engine=text_engine,
            )
            structure_context = self._apply_overrides_to_context(
                structure_context,
                override_manager,
                text=translated_text,
            )

            return {
                "incoming_text": incoming_text,
                "normalized_text": normalized_text,
                "cleaned_text": cleaned_text,
                "structure_context": structure_context,
                "params": params,
                "override_manager": override_manager,
                "command_bundle": command_bundle,
                "language_info": language_info,
            }
        except Exception as e:
            logger.exception("Text preparation failed: %s", e)
            errors = diagnostics.get("errors")
            if not isinstance(errors, list):
                errors = [] if errors is None else [errors]
                diagnostics["errors"] = errors
            errors.append("text_preparation_failed")
            return None

    def _process_post_analysis(
        self,
        incoming_text: str,
        backend_payload: Dict[str, Any],
        engines: Dict[str, Any],
        diagnostics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process post-analysis data: emotion matrix, TLP, RDE, tone profile, and fusion summary.
        
        Returns:
            Dict with backend_updates and diagnostics_updates
        """
        emotion_engine_v2 = engines["emotion_engine_v2"]
        emotion_matrix = emotion_engine_v2.analyze(incoming_text)

        tlp_engine = engines["tlp_engine"]
        # Используем analyze() вместо tlp_vector() для правильного распознавания исповедального стиля
        tlp = tlp_engine.analyze(incoming_text)

        bpm_engine = engines["bpm_engine"]
        bpm_v2 = bpm_engine.compute_bpm_v2(incoming_text.splitlines())

        resonance_engine = engines["resonance_engine"]
        rde = {
            "resonance": resonance_engine.calc_resonance(incoming_text),
            "fracture": resonance_engine.calc_fracture(incoming_text),
            "entropy": resonance_engine.calc_entropy(incoming_text),
        }
        
        # MASTER-PATCH v6.0 — Rage fracturing (только anger/tension)
        # Get emotion profile to check for rage mode
        # Try multiple sources: emotion_matrix (from emotion_engine_v2) and backend_payload emotions
        emotion_profile_for_rage = {}
        if isinstance(emotion_matrix, dict):
            emotion_profile_for_rage = emotion_matrix.get("profile") or emotion_matrix
        # Also check backend_payload for processed emotions
        if not emotion_profile_for_rage or not self._is_rage_mode(emotion_profile_for_rage):
            emotions_from_payload = backend_payload.get("emotions", {})
            if isinstance(emotions_from_payload, dict):
                emotion_profile_for_rage = emotions_from_payload.get("profile") or emotions_from_payload
        
        # Boost fracture and entropy only for rage mode (not epic)
        if isinstance(emotion_profile_for_rage, dict) and self._is_rage_mode(emotion_profile_for_rage):
            rde["fracture"] = min(1.0, rde.get("fracture", 0.0) + 0.15)
            rde["entropy"] = min(1.0, rde.get("entropy", 0.0) + 0.10)

        tone_profile = None
        try:  # Используем tone_sync engine из tone_sync.py для создания profile
            from .tone_sync import ToneSyncEngine as ToneSyncEngineV2
            tse = ToneSyncEngineV2()
            # Получаем key и bpm для pick_profile
            style_key = backend_payload.get("style", {}).get("key") if isinstance(backend_payload.get("style"), dict) else None
            bpm_val = backend_payload.get("bpm", {})
            if isinstance(bpm_val, dict):
                bpm_val = bpm_val.get("estimate") or bpm_val.get("flow_estimate") or 80
            elif not isinstance(bpm_val, (int, float)):
                bpm_val = 80
            bpm_val = int(bpm_val)
            
            tone_profile = tse.pick_profile(
                bpm=bpm_val,
                key=style_key,
                tlp=tlp,
                emotion_matrix=emotion_matrix,
            )
        except Exception as e:
            logger.exception("Tone profile creation failed: %s", e)
            diagnostics.setdefault("errors", []).append("tone_sync_failed")
    
        diagnostics_updates = {
            "emotion_matrix": emotion_matrix,
            "tlp": tlp,
            "rde": rde,
            "bpm_v2": bpm_v2,
        }
        if tone_profile is not None:
            diagnostics_updates["tone_profile"] = tone_profile

        backend_updates = {
            "emotion_matrix": emotion_matrix,
            "tlp": tlp,
            "rde": rde,
        }
        bpm_block = backend_payload.get("bpm") if isinstance(backend_payload.get("bpm"), dict) else {}
        backend_updates["bpm"] = {**(bpm_block or {}), "flow_estimate": bpm_v2, "estimate": bpm_v2}
    
        if tone_profile is not None:
            backend_updates["tone_profile"] = tone_profile
    
        # Process fusion summary
        fusion_summary = backend_payload.get("fusion_summary")
        if fusion_summary:
            bpm_block = backend_updates.setdefault("bpm", {}) if isinstance(backend_updates.get("bpm"), dict) else backend_updates.setdefault("bpm", {})
            manual_override = bpm_block.get("manual_override") if isinstance(bpm_block, dict) else None
            bpm_override = manual_override.get("bpm") if isinstance(manual_override, dict) else None
    
            final_bpm = bpm_override if bpm_override is not None else fusion_summary.get("final_bpm")
            if final_bpm is not None:
                bpm_block["estimate"] = final_bpm
                backend_updates.setdefault("rhythm", {})["global_bpm"] = final_bpm
                backend_updates.setdefault("style", {})["bpm"] = final_bpm
    
            final_key = fusion_summary.get("final_key")
            if final_key is not None:
                # Проверяем, не был ли Key уже установлен из эмоций
                # Проверяем в backend_payload, который уже содержит tonality_payload
                backend_tonality = backend_payload.get("tonality", {}) if isinstance(backend_payload.get("tonality"), dict) else {}
                backend_emotion_key = backend_tonality.get("emotion_color_key")
                
                tonality_block = backend_updates.get("tonality", {})
                existing_key = tonality_block.get("key")
                emotion_key = tonality_block.get("emotion_color_key")
                
                # Приоритет: Key из эмоций > Key из fusion_engine
                emotion_key_to_use = emotion_key or backend_emotion_key
                if emotion_key_to_use and emotion_key_to_use != "auto":
                    # Сохраняем Key из эмоций, не перезаписываем fusion_engine
                    backend_updates.setdefault("tonality", {})["key"] = emotion_key_to_use
                    backend_updates.setdefault("style", {})["key"] = emotion_key_to_use
                    backend_updates.setdefault("tonality", {})["source"] = "emotion_color"
                    backend_updates.setdefault("tonality", {})["emotion_color_key"] = emotion_key_to_use
                elif not existing_key or existing_key == "auto":
                    # Используем Key из fusion_engine только если нет Key из эмоций
                    backend_updates.setdefault("tonality", {})["key"] = final_key
                    backend_updates.setdefault("style", {})["key"] = final_key
                    backend_updates.setdefault("tonality", {})["source"] = "fusion_engine"
    
            final_genre = fusion_summary.get("final_genre") or fusion_summary.get("final_subgenre")
            if final_genre:
                style_block = backend_updates.setdefault("style", {})
                style_block["genre"] = final_genre
                style_block.setdefault("subgenre", final_genre)
    
        # Process style block
        style_block = backend_payload.get("style")
        if isinstance(style_block, dict):
            macro_genre = style_block.get("macro_genre") or style_block.get("subgenre")
            current_genre = style_block.get("genre")
            if macro_genre and (not current_genre or macro_genre not in current_genre):
                backend_updates.setdefault("style", {})["genre"] = macro_genre

        return {
            "backend_updates": backend_updates,
            "diagnostics_updates": diagnostics_updates,
        }

    def _build_diagnostics_blocks(
        self,
        backend_payload: Dict[str, Any],
        payload: Dict[str, Any],
        diagnostics: Dict[str, Any],
        structure_context: Dict[str, Any],
        sections: List[str],
    ) -> Dict[str, Any]:
        """
        Build diagnostic blocks from analysis results.
        
        Returns:
            Dict with diagnostics and payload_updates
        """
        diagnostics_block = backend_payload.get("diagnostics") if isinstance(backend_payload.get("diagnostics"), dict) else {}
        diagnostics = {**diagnostics_block, **diagnostics}
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем mood и color_wave из payload ДО update
        # Это гарантирует, что они не будут потеряны при payload.update(backend_payload)
        payload_style = payload.get("style", {})
        saved_mood = payload_style.get("mood") if isinstance(payload_style, dict) else None
        saved_color_wave = payload_style.get("color_wave") if isinstance(payload_style, dict) else None
        
        payload.update(backend_payload)
        payload["diagnostics"] = diagnostics
    
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Восстанавливаем mood и color_wave после update
        if saved_mood or saved_color_wave:
            payload_style_after = payload.get("style", {})
            if not isinstance(payload_style_after, dict):
                payload_style_after = {}
            if saved_mood:
                payload_style_after["mood"] = saved_mood
            if saved_color_wave:
                payload_style_after["color_wave"] = saved_color_wave
            payload["style"] = payload_style_after

        style_block = backend_payload.get("style")
        genre_universe = get_genre_universe()
        genre_info = None
        if isinstance(style_block, dict) and style_block.get("genre"):
            try:
                genre_info = genre_universe.detect_domain(str(style_block.get("genre")))
            except Exception:
                genre_info = None
        if genre_info:
            diagnostics["genre_universe_tags"] = genre_info
    
        color_diag = None
        if isinstance(payload.get("style"), dict):
            color_wave = payload.get("style", {}).get("color_wave")
            if color_wave:
                color_diag = {"color_wave": color_wave}
        if color_diag:
            diagnostics["color"] = color_diag
    
        tlp_data = diagnostics.get("tlp")
        if isinstance(tlp_data, dict):
            diagnostics["tlp_block"] = (
                f"[TLP: {tlp_data.get('truth', 0):.2f}/{tlp_data.get('love', 0):.2f}/{tlp_data.get('pain', 0):.2f} | CF {tlp_data.get('conscious_frequency', 0):.2f}]"
            )
    
        rde_diag = diagnostics.get("rde")
        if isinstance(rde_diag, dict):
            diagnostics["rde_block"] = (
                f"[RDE: resonance={rde_diag.get('resonance')}, fracture={rde_diag.get('fracture')}, entropy={rde_diag.get('entropy')}]"
            )
    
        macro_genre = None
        if isinstance(payload.get("style"), dict):
            macro_genre = (
                payload.get("style", {}).get("macro_genre")
                or payload.get("style", {}).get("genre")
                or payload.get("style", {}).get("subgenre")
            )
        if macro_genre:
            diagnostics["genre_block"] = f"[Genre: {macro_genre}]"
    
        zero_pulse_info = payload.get("zero_pulse") if isinstance(payload.get("zero_pulse"), dict) else diagnostics.get("zero_pulse")
        if isinstance(zero_pulse_info, dict):
            status = zero_pulse_info.get("status", zero_pulse_info.get("has_zero_pulse"))
            diagnostics["zeropulse_block"] = f"[ZeroPulse: {status}]"
    
        color_wave = None
        if isinstance(payload.get("style"), dict):
            color_wave = payload.get("style", {}).get("color_wave")
        if color_wave:
            color_repr = ", ".join(color_wave) if isinstance(color_wave, list) else str(color_wave)
            diagnostics["color_wave_block"] = f"[ColorWave: {color_repr}]"
    
            integrity_diag = diagnostics.get("integrity")
            if integrity_diag:
                diagnostics["integrity_block"] = f"[Integrity: {integrity_diag}]"
    
            # Build unified summary block from diagnostics
            summary_block = _build_summary_block(diagnostics)
    
            # Run semantic consistency checks and attach report into diagnostics
            _build_consistency_report(diagnostics, payload)
    
            payload["engine"] = "StudioCoreV6"
            payload.setdefault("ok", True)
            payload.setdefault("diagnostics", diagnostics)
    
            # === Consistency Layer v8 ===
            try:
                consistency_block = ConsistencyLayerV8(diagnostics).build()
                diagnostics["consistency"] = consistency_block
            except Exception as e:  # noqa: BLE001
                diagnostics["consistency_error"] = str(e)
    
            structured_diagnostics = DiagnosticsBuilderV8(
                base=diagnostics,
                payload=payload,
            ).build()
    
        return {
            "diagnostics": diagnostics,
            "payload_updates": {"diagnostics": structured_diagnostics},
        }

    def _build_lyrics_sections_with_vocals(
        self,
        sections: List[str],
        structure_context: Dict[str, Any],
        payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Build lyrics sections with vocal techniques based on section emotions.
        КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлена передача цветовых гамм эмоций в вокальные секции.
        
        Returns:
            List of section dicts with vocal techniques and color waves
        """
        from .color_engine_adapter import get_emotion_colors
        
        lyrics_sections: list[dict[str, Any]] = []
        headers = structure_context.get("section_headers") or structure_context.get("section_metadata") or []
        
        # Получаем эмоции секций для определения вокальных техник
        section_emotions_data = []
        section_intel_payload = payload.get("section_intelligence", {}) if isinstance(payload.get("section_intelligence"), dict) else {}
        section_emotions_list = section_intel_payload.get("section_emotions", [])
        if section_emotions_list:
            section_emotions_data = section_emotions_list
        
        # Получаем глобальную эмоцию и жанр для контекста
        emotion_data = payload.get("emotion", {}) if isinstance(payload.get("emotion"), dict) else {}
        if isinstance(emotion_data, dict) and "profile" in emotion_data:
            emotion_profile = emotion_data.get("profile", {})
        else:
            emotion_profile = emotion_data if isinstance(emotion_data, dict) else {}
        
        # Безопасное извлечение доминирующей эмоции
        global_emotion = "neutral"
        if emotion_profile and isinstance(emotion_profile, dict):
            try:
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    global_emotion = max(numeric_profile, key=numeric_profile.get)
            except (ValueError, TypeError):
                global_emotion = "neutral"
        
        style_block = payload.get("style", {}) if isinstance(payload.get("style"), dict) else {}
        genre = style_block.get("genre", "adaptive")
        
        # MASTER-PATCH v5.1: Улучшенная логика для section headers
        def generate_section_name(idx: int, total: int) -> str:
            """Генерирует осмысленное имя секции на основе позиции и длины."""
            if idx == 0:
                return "Intro"
            elif idx == total - 1:
                return "Outro"
            elif total <= 3:
                return f"Verse {idx}"
            elif idx == 1 or (idx > 1 and idx < total - 1 and idx % 2 == 1):
                return f"Chorus {idx // 2 + 1}" if idx > 1 else "Chorus"
            elif idx == 2 or (idx > 2 and idx < total - 2):
                return f"Verse {(idx - 1) // 2 + 1}"
            elif idx == total - 2:
                return "Bridge"
            else:
                return f"Verse {idx}"
        
        for idx, section in enumerate(sections or []):
            header_label = None
            if idx < len(headers) and isinstance(headers[idx], dict):
                header_label = headers[idx].get("tag") or headers[idx].get("label") or headers[idx].get("name")
            # Если header_label пустой или "?" - автогенерируем осмысленное имя
            if not header_label or header_label == "?":
                header_label = generate_section_name(idx, len(sections or []))
            section_header = header_label
            
            # Преобразуем строку секции в список строк для lines
            section_lines = []
            if isinstance(section, str):
                section_lines = [line.strip() for line in section.split("\n") if line.strip()]
            elif isinstance(section, list):
                section_lines = [str(line).strip() for line in section if str(line).strip()]
            
            # Определяем вокальную технику для секции на основе эмоций
            vocal_technique = "tenor"  # Fallback
            sec_emotion = "neutral"
            sec_intensity = 0.5
            if idx < len(section_emotions_data) and isinstance(section_emotions_data[idx], dict):
                sec_emotion = section_emotions_data[idx].get("dominant", "neutral")
                sec_intensity = section_emotions_data[idx].get("intensity", 0.5)
                try:
                    from .vocal_techniques import get_vocal_for_section
                    vocal_technique = get_vocal_for_section(
                        section_emotion=sec_emotion,
                        section_intensity=sec_intensity,
                        global_emotion=global_emotion,
                        genre=genre,
                        section_name=section_header,
                    )
                except (ImportError, Exception):
                    vocal_technique = "tenor"
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавляем цветовую гамму эмоции для секции
            # Цвета берутся из EMOTION_COLOR_MAP на основе эмоции секции
            section_color_wave = get_emotion_colors(sec_emotion) if sec_emotion else get_emotion_colors("neutral")
            
            lyrics_sections.append(
                {
                    "name": section_header,
                    "tag": header_label or section_header,
                    "mood": sec_emotion or "neutral",  # Используем эмоцию секции как mood
                    "energy": "mid",
                    "arrangement": "standard",
                    "vocal_technique": vocal_technique,
                    "emotion": sec_emotion,
                    "color_wave": section_color_wave,  # КРИТИЧНО: Добавлена цветовая гамма
                    "lines": section_lines,
                }
            )
        
        return lyrics_sections

    def _build_final_result(
        self,
        normalized_text: str,
        incoming_text: str,
        payload: Dict[str, Any],
        lyrics_sections: List[Dict[str, Any]],
        diagnostics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build final result with FANF output and UI text.
        
        Returns:
            Final result dict
        """
        style = payload.get("style") if isinstance(payload.get("style"), dict) else {}
        structured_diagnostics = payload.get("diagnostics", diagnostics)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем mood и color_wave из style ДО любых операций
        # Это гарантирует, что они не будут потеряны
        saved_mood = style.get("mood") if isinstance(style, dict) else None
        saved_color_wave = style.get("color_wave") if isinstance(style, dict) else None
        
        # Добавляем lyrics в payload перед build_fanf_output
        payload["lyrics"] = {"sections": lyrics_sections}
        
        # MASTER_PATCH_V5_SKELETON: Neutral pre-finalizer (NO-OP)
        result = payload  # Create result reference for hooks
        if self._neutral_prefinal is not None:
            result = self._neutral_prefinal.apply(result)
        
        # MASTER_PATCH_V5_SKELETON: ColorEngineV3 (NO-OP)
        if self._color_v3 is not None and isinstance(result.get("style"), dict):
            result["style"] = self._color_v3.normalize_style(result["style"])
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Восстанавливаем mood и color_wave в payload["style"]
        # Это гарантирует, что они попадут в _finalize_result()
        if saved_mood or saved_color_wave:
            payload_style = payload.get("style", {})
            if not isinstance(payload_style, dict):
                payload_style = {}
            if saved_mood:
                payload_style["mood"] = saved_mood
            if saved_color_wave:
                payload_style["color_wave"] = saved_color_wave
            payload["style"] = payload_style
        
        fanf_payload = self.build_fanf_output(
                text=normalized_text,
                style=style or {},
                lyrics={"sections": lyrics_sections},
                diagnostics=structured_diagnostics,
            )
    
        ui_text = _extract_ui_text(fanf_payload.get("lyrics_prompt", "")) if fanf_payload.get("lyrics_prompt") else _extract_ui_text(incoming_text)
    
        fanf_block: dict[str, Any] = {}
        if isinstance(payload.get("fanf"), dict):
            fanf_block.update(payload.get("fanf", {}))
        fanf_block.update(fanf_payload)
        fanf_block.setdefault("ui_text", ui_text)
    
        summary_block = _build_summary_block(diagnostics)
        payload["summary"] = fanf_block.get("summary", summary_block)
        payload["fanf"] = fanf_block
    
        # Убеждаемся, что RDE попадает в финальный результат
        # MASTER-PATCH v3: сглаживаем RDE для low-emotion текстов
        rde = diagnostics.get("rde") or payload.get("rde") or {}
        if rde:
            tlp = payload.get("tlp") or payload.get("legacy", {}).get("tlp")
            rde = self._smooth_rde_for_low_emotion(tlp, rde)
            payload["rde"] = rde
            diagnostics["rde"] = rde
        elif "rde" not in payload and "rde" in diagnostics:
            payload["rde"] = diagnostics.get("rde")
        
        # ============================================================
        # NEW: Road Narrative / Dark Country Rap overrides
        # Перенесено сюда — ПЕРЕД финализацией результата,
        # иначе _finalize_result перезапишет genre обратно в lyrical_song.
        # ============================================================
        self._apply_road_narrative_overrides(
            text=payload.get("normalized_text") or payload.get("text") or "",
            tlp=payload.get("tlp") or payload.get("legacy", {}).get("tlp"),
            emotions=payload.get("emotions") or payload.get("emotion", {}).get("profile") or payload.get("legacy", {}).get("emotions") or {},
            bpm_block=payload.get("bpm") or payload.get("legacy", {}).get("bpm") or {},
            sections=payload.get("structure", {}).get("sections")
                     or payload.get("sections")
                     or [],
            result=payload,   # ВАЖНО: результат передаём В payload
        )
        # ============================================================
        
        # MASTER-PATCH v6.0 — Rage-mode mood override (только anger/tension)
        emotion_profile = payload.get("emotions", {}).get("profile") or payload.get("emotion", {}).get("profile") or {}
        if isinstance(emotion_profile, dict) and self._is_rage_mode(emotion_profile):
            style = payload.get("style", {})
            if not isinstance(style, dict):
                style = {}
            style["mood"] = "furious, aggressive, explosive"
            style["_mood_corrected"] = True
            payload["style"] = style
        
        # MASTER-PATCH v6.0 — Epic-mode mood override
        # Mood override logic may overwrite mood
        # FIX: Preserve mood unless override is stronger
        current_mood = payload.get("style", {}).get("mood") if isinstance(payload.get("style"), dict) else None
        if isinstance(emotion_profile, dict) and self._is_epic_mode(emotion_profile):
            style = payload.get("style", {})
            if not isinstance(style, dict):
                style = {}
            # Epic mood override только если mood еще не исправлен
            if not style.get("_mood_corrected"):
                # Preserve mood if override is weak
                if current_mood and not style.get("force_mood"):
                    style["mood"] = current_mood
                else:
                    style["mood"] = "cinematic, rising, powerful"
                style["_mood_corrected"] = True
                payload["style"] = style
        
        final_result = self._finalize_result(payload)
        final_result["engine"] = "StudioCoreV6"
        final_result.setdefault("ok", True)
        final_result["diagnostics"] = structured_diagnostics
        final_result.setdefault("fanf", fanf_block)
    
        # Убеждаемся, что lyrics и rde есть в финальном результате
        if "lyrics" not in final_result:
            final_result["lyrics"] = {"sections": lyrics_sections}
        if "rde" not in final_result and "rde" in payload:
            final_result["rde"] = payload.get("rde")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убеждаемся, что style содержит mood и color_wave
        # _finalize_result может перезаписать style, поэтому восстанавливаем эти поля
        if isinstance(final_result.get("style"), dict):
            style_final = final_result["style"]
            # Пробуем восстановить mood, color_wave и genre из payload
            if isinstance(payload.get("style"), dict):
                style_from_payload = payload.get("style")
                # MASTER-PATCH v3.3 — Skip normalization for locked or neutral
                if not (style_final.get("_color_locked") or style_final.get("_neutral_mode")):
                    if "mood" not in style_final or style_final.get("mood") is None:
                        if style_from_payload.get("mood"):
                            style_final["mood"] = style_from_payload.get("mood")
                    if "color_wave" not in style_final or style_final.get("color_wave") is None:
                        if style_from_payload.get("color_wave"):
                            style_final["color_wave"] = style_from_payload.get("color_wave")
                # ============================================================
                # NEW: protect genre from fallback overwrite
                # Prevent any "lyrical_song" fallback from overwriting overrides.
                # ============================================================
                if "genre" not in style_final and style_from_payload.get("genre"):
                    style_final["genre"] = style_from_payload["genre"]
        
        # Folk ballad detection and override
        # Try multiple sources for normalized_text
        normalized_text_for_detection = final_result.get("normalized_text") or payload.get("normalized_text") or normalized_text or ""
        if self._detect_folk_ballad(normalized_text_for_detection):
            if not isinstance(final_result.get("style"), dict):
                final_result["style"] = {}
            final_result["style"]["genre"] = "folk narrative ballad"
            final_result["style"]["color_wave"] = ['#6B4F2A', '#C89D66']
            final_result["style"]["_color_locked"] = True
            final_result["style"]["_folk_mode"] = True
        
        # Replace instruments with folk ballad instruments if _folk_mode is True
        if final_result.get("style", {}).get("_folk_mode") is True:
            from .instrument import folk_ballad_instruments
            folk_instruments = folk_ballad_instruments()
            # Check both final_result and payload for instrumentation
            instrumentation_block = final_result.get("instrumentation") or payload.get("instrumentation", {})
            if not isinstance(instrumentation_block, dict):
                instrumentation_block = {}
            selection = instrumentation_block.get("selection", {})
            if not isinstance(selection, dict):
                selection = {}
            selection["selected"] = folk_instruments
            instrumentation_block["selection"] = selection
            final_result["instrumentation"] = instrumentation_block
            # Also update in payload if it exists
            if "instrumentation" in payload:
                payload["instrumentation"] = instrumentation_block
        
        return final_result

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
        text_engine = None,
    ) -> Dict[str, Any]:
        """
        FIX: disable fallback for contextual reconstruction.
        DO NOT alter parsed sections.
        """
        existing_hints = dict(existing_hints or {})
        # Получаем text_engine из _engine_bundle если не передан
        if text_engine is None:
            if hasattr(self, '_engine_bundle') and self._engine_bundle:
                text_engine = self._engine_bundle.get("text_engine")
            else:
                from .logical_engines import TextStructureEngine
                text_engine = TextStructureEngine()
        auto_sections = text_engine.auto_section_split(text)
        hinted_sections = existing_hints.get("sections")
        sections = self._resolve_sections_from_hints(text, hinted_sections, fallback_sections=auto_sections)
        section_result = self.section_parser.parse(text, sections=sections)
        metadata = [dict(item) for item in section_result.metadata]
        strict_boundary = bool(getattr(section_result, "prefer_strict_boundary", False))
        
        # MASTER_PATCH_V5_SKELETON: SectionMergeMode hook (NO-OP)
        if self._section_merge_mode is not None and sections:
            sections = self._section_merge_mode.merge(sections, text_engine=text_engine)
        
        # MASTER-PATCH: Строим названия секций на основе объектов секций из SectionParser
        # НЕ используем structure_context как источник пустых секций
        section_names = []
        for i, meta in enumerate(metadata):
            # Извлекаем имя секции из метаданных
            section_name = (
                meta.get("tag") or 
                meta.get("name") or 
                meta.get("label") or 
                (sections[i] if i < len(sections) else None) or
                "UNKNOWN"
            )
            section_names.append(section_name)
        
        # Если section_names пустые, используем metadata напрямую
        if not section_names and metadata:
            section_names = [meta.get("tag", "UNKNOWN") for meta in metadata]
        
        # Если все еще пустые, используем индексы
        if not section_names:
            section_names = [f"Section {i+1}" for i in range(len(sections))]
        
        generated_hints = {
            "section_count": len(sections),
            "section_lengths": [len(_ensure_tokens(section)) for section in sections],
            "command_count": len(commands or []),
            "section_headers": metadata,
            "annotations": section_result.annotations,
            "section_names": section_names,  # Добавляем реальные имена секций
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

        # FIX: возвращаем parsed_sections как есть, без изменений
        # ВАЖНО: sections теперь содержит реальные имена секций
        parsed_sections = {
            "semantic_hints": semantic_hints,
            "sections": section_names,  # Используем реальные имена секций
            "sections_text": sections,  # Сохраняем текст секций отдельно
            "commands": detected_commands,
            "section_metadata": metadata,
            "section_headers": metadata,
            "strict_boundary": strict_boundary,
            "annotations": section_result.annotations,
            "preserved_tags": list(preserved_tags or []),
        }
        return parsed_sections

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
        engines: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        # MASTER-PATCH: Используем sections_text если есть (реальный текст), иначе sections (имена)
        base_sections = list(structure_context.get("sections_text", structure_context.get("sections", [])))
        hinted_sections = semantic_hints.get("sections")
        sections = self._resolve_sections_from_hints(text, hinted_sections, fallback_sections=base_sections)
        diagnostics: Dict[str, Any] = {
            "bpm": {},
            "tonality": {},
            "vocal": {},
            "instrumentation": {},
            "emotion_matrix": {},
        }
        # Извлекаем движки из словаря engines в начале метода
        extracted_engines = self._extract_engines(engines)
        text_engine = extracted_engines["text_engine"]
        emotion_engine = extracted_engines["emotion_engine"]
        bpm_engine = extracted_engines["bpm_engine"]
        tlp_engine = extracted_engines["tlp_engine"]
        dynamic_emotion_engine = extracted_engines["dynamic_emotion_engine"]
        section_intelligence = extracted_engines["section_intelligence"]
        vocal_engine = extracted_engines["vocal_engine"]
        breathing_engine = extracted_engines["breathing_engine"]
        color_emotion_engine = extracted_engines["color_emotion_engine"]
        genre_matrix = extracted_engines["genre_matrix"]
        
        # Используем EmotionEngine из logical_engines для основных методов
        from .logical_engines import EmotionEngine as LogicalEmotionEngine
        logical_emotion = LogicalEmotionEngine()
        emotion_profile = logical_emotion.emotion_detection(text)
        emotion_curve = logical_emotion.emotion_intensity_curve(text)
        dynamic_emotion_profile = dynamic_emotion_engine.emotion_profile(text) if dynamic_emotion_engine else {}
        if hasattr(emotion_engine, 'reset_phrase_packets'):
            emotion_engine.reset_phrase_packets()
        section_intel_payload = section_intelligence.analyze(
            text, sections, emotion_curve, emotion_engine=emotion_engine
        ) if section_intelligence else {}
        section_emotions = list(section_intel_payload.get("section_emotions", []))
        global_emotion_curve = build_global_emotion_curve(section_emotions)
        curve_dict = global_emotion_curve.to_dict()
        dynamic_bias = curve_dict.get("dynamic_bias", {})
        structure_context["section_intelligence"] = section_intel_payload
        structure_context["emotion_profile"] = dict(emotion_profile)
        structure_context["emotion_profile_axes7"] = dict(dynamic_emotion_profile)
        structure_context["emotion_curve"] = list(emotion_curve)
        structure_context["emotion_curve_global"] = curve_dict
        structure_context.setdefault("dynamic_bias", curve_dict.get("dynamic_bias", {}))
        if language_info:
            structure_context["language"] = dict(language_info)

        # MASTER-PATCH: Используем _resolve_dominant_emotion_enhanced для учета TLP контекста
        # Это исправляет проблему с "sensual 0.979" для драматических текстов
        dominant_emotion = None
        if emotion_profile and isinstance(emotion_profile, dict) and emotion_profile:
            try:
                # Получаем TLP профиль для контекста
                tlp_profile = logical_emotion.export_emotion_vector(text).to_dict() if hasattr(logical_emotion, 'export_emotion_vector') else {}
                if not tlp_profile:
                    # Fallback: получаем TLP из tlp_engine если есть
                    tlp_engine = extracted_engines.get("tlp_engine")
                    if tlp_engine:
                        tlp_result = tlp_engine.analyze(text) if hasattr(tlp_engine, 'analyze') else {}
                        tlp_profile = {
                            "truth": tlp_result.get("truth", 0.0),
                            "love": tlp_result.get("love", 0.0),
                            "pain": tlp_result.get("pain", 0.0),
                        }
                
                # Используем улучшенную функцию с учетом TLP
                dominant_emotion = self._resolve_dominant_emotion_enhanced(text, emotion_profile, tlp_profile)
            except (ValueError, TypeError, AttributeError) as e:
                # Fallback на простое определение если что-то пошло не так
                try:
                    dominant_emotion = max(emotion_profile, key=emotion_profile.get)
                except (ValueError, TypeError):
                    dominant_emotion = None
        
        # Безопасное извлечение emotion_curve_max с защитой от пустого списка
        emotion_curve_max = None
        if emotion_curve and isinstance(emotion_curve, (list, tuple)) and emotion_curve:
            try:
                emotion_curve_max = max(emotion_curve)
            except (ValueError, TypeError):
                emotion_curve_max = None

        semantic_hints = self._merge_semantic_hints(
            semantic_hints,
            {
                "dominant_emotion": dominant_emotion,
                "emotion_curve_max": emotion_curve_max,
                "section_intelligence": section_intel_payload,
                "emotion_profile_axes7": dynamic_emotion_profile,
            },
        )
        structure_context["semantic_hints"] = semantic_hints

        # MASTER-PATCH: Корректируем emotion_profile с учетом TLP контекста
        # Снижаем значение "sensual" для драматических текстов
        tlp_profile = logical_emotion.export_emotion_vector(text).to_dict() if hasattr(logical_emotion, 'export_emotion_vector') else {}
        if not tlp_profile:
            tlp_engine = extracted_engines.get("tlp_engine")
            if tlp_engine:
                tlp_result = tlp_engine.analyze(text) if hasattr(tlp_engine, 'analyze') else {}
                tlp_profile = {
                    "truth": tlp_result.get("truth", 0.0),
                    "love": tlp_result.get("love", 0.0),
                    "pain": tlp_result.get("pain", 0.0),
                }
        
        # MASTER-PATCH: Корректируем emotion_profile если контекст драматический
        # Проверяем как TLP, так и содержание текста
        if tlp_profile:
            pain_level = float(tlp_profile.get("pain", 0.0) or 0.0)
            love_level = float(tlp_profile.get("love", 0.0) or 0.0)
            truth_level = float(tlp_profile.get("truth", 0.0) or 0.0)
            
            # Проверяем драматические ключевые слова в тексте
            text_lower = text.lower()
            dramatic_keywords = ["bury", "grave", "die", "death", "pain", "hurt", "lost", "crossed", "fate", "reaper", "chains"]
            has_dramatic_content = any(keyword in text_lower for keyword in dramatic_keywords)
            
            # Если высокий pain и низкий love - снижаем sensual
            # ИЛИ если есть драматический контент и низкий love - тоже снижаем sensual
            should_reduce_sensual = (
                (pain_level > 0.5 and love_level < 0.3) or
                (has_dramatic_content and love_level < 0.3 and "sensual" in emotion_profile and emotion_profile["sensual"] > 0.7)
            )
            
            if should_reduce_sensual:
                if "sensual" in emotion_profile and emotion_profile["sensual"] > 0.5:
                    # Снижаем sensual и повышаем sorrow/sadness/determination
                    sensual_value = emotion_profile["sensual"]
                    emotion_profile["sensual"] = sensual_value * 0.2  # Снижаем на 80%
                    emotion_profile.setdefault("sorrow", 0.0)
                    emotion_profile["sorrow"] = max(emotion_profile["sorrow"], sensual_value * 0.5)
                    emotion_profile.setdefault("sadness", 0.0)
                    emotion_profile["sadness"] = max(emotion_profile["sadness"], sensual_value * 0.3)
                    if truth_level > 0.4:
                        emotion_profile.setdefault("determination", 0.0)
                        emotion_profile["determination"] = max(emotion_profile["determination"], sensual_value * 0.2)

        emotion_profile = self._merge_semantic_hints(
            dict(emotion_profile),
            semantic_hints.get("emotion_profile", {}),
        )
        dynamic_emotion_profile = self._merge_semantic_hints(
            dict(dynamic_emotion_profile), semantic_hints.get("emotion_profile_axes7", {})
        )
        commands = list(structure_context.get("commands", []))

        # 1. Call the legacy core for full analysis.
        try:
            legacy_core_cls = engines.get("_legacy_core_cls") or engines.get("legacy_core_cls")
            if legacy_core_cls:
                legacy_core = legacy_core_cls()
            # Note: Pass only original_text to avoid double-translation/normalization
            legacy_result = legacy_core.analyze(
                original_text or text,
                preferred_gender=preferred_gender,
                version=version,
                semantic_hints=copy.deepcopy(semantic_hints) if semantic_hints else None,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            legacy_result = {"error": str(exc)}

        # Fix #2.1: Check for legacy error and set flag
        legacy_error_detected = isinstance(legacy_result, dict) and legacy_result.get("error")
        if legacy_error_detected:
            diagnostics["legacy_error"] = {"message": legacy_result.get("error")}
            # CRITICAL FIX: If legacy core failed, reset the entire result to prevent V6 from using faulty/stale legacy data.
            legacy_result = {"error": legacy_result["error"]}

        # 2. Structural analysis
        structure = {
            "sections": sections,
            "intro": text_engine.detect_intro(text, sections=sections),
            "verse": text_engine.detect_verse(text, sections=sections),
            "prechorus": text_engine.detect_prechorus(text, sections=sections),
            "chorus": text_engine.detect_chorus(text, sections=sections),
            "bridge": text_engine.detect_bridge(text, sections=sections),
            "outro": text_engine.detect_outro(text, sections=sections),
            "meta_pause": text_engine.detect_meta_pause(text, sections=sections),
            "intelligence": section_intel_payload,
        }
        if isinstance(semantic_hints.get("section_labels"), list):
            structure["labels"] = list(semantic_hints["section_labels"])
        # Получаем метаданные секций из structure_context
        # КРИТИЧНО: Сначала проверяем section_metadata из text_engine (пользовательские маркеры)
        structure["headers"] = self._build_structure_headers(text_engine, sections, structure_context)
        if structure_context.get("strict_boundary") is not None:
            structure["strict_boundary"] = bool(structure_context.get("strict_boundary"))
        if structure_context.get("preserved_tags"):
            structure["preserved_tags"] = list(structure_context.get("preserved_tags", []))
        if language_info:
            structure["language"] = dict(language_info)

        result: Dict[str, Any] = {}

        zero_hint = text_engine.detect_zero_pulse(text, sections=sections)

        # 3. Emotional layers
        tlp_profile = {
            "truth": float(min(1, max(0, tlp_engine.truth_score(text)))),
            "love": float(min(1, max(0, tlp_engine.love_score(text)))),
            "pain": float(min(1, max(0, tlp_engine.pain_score(text)))),
        }
        # Улучшенное определение доминирующей эмоции с учетом контекста
        dominant_emotion = self._resolve_dominant_emotion_enhanced(text, emotion_profile, tlp_profile)
        tlp_profile["conscious_frequency"] = round(
            (tlp_profile["truth"] + tlp_profile["love"] + tlp_profile["pain"]) / 3, 4
        )
        if all(value == 0.0 for value in (tlp_profile.get("truth"), tlp_profile.get("love"), tlp_profile.get("pain"))):
            tlp_profile.update({"truth": 0.33, "love": 0.33, "pain": 0.34})
        tlp_profile.setdefault("base_hz", 432.1)
        tlp_profile.setdefault("base_frequency", tlp_profile.get("base_hz"))
        tlp_profile.setdefault("consciousness_level", tlp_profile.get("conscious_frequency", 0.5))
        if dominant_emotion:
            tlp_profile["dominant_name"] = dominant_emotion
            tlp_profile["emotion"] = dominant_emotion
        else:
            tlp_profile.setdefault("dominant_name", DEFAULT_CONFIG.FALLBACK_EMOTION)
            tlp_profile.setdefault("emotion", DEFAULT_CONFIG.FALLBACK_EMOTION)
        emotion_payload = {
            "profile": emotion_profile,
            "dynamic_profile": dynamic_emotion_profile,
            "curve": emotion_curve,
            "pivots": logical_emotion.emotion_pivot_points(text, intensity_curve=emotion_curve),
            "secondary": logical_emotion.secondary_emotion_detection(emotion_profile),
            "conflict": logical_emotion.emotion_conflict_map(emotion_profile),
        }
        emotion_payload = self._merge_semantic_hints(emotion_payload, semantic_hints.get("emotion", {}))

        smoothed_vectors: list[EmotionVector] = []

        # 4. RDE (Resonance, Dynamics, Entropy) - после TLP, перед Color
        rde_summary = {
            "resonance": self.rde_engine.calc_resonance(text) if hasattr(self, 'rde_engine') and self.rde_engine else 0.0,
            "fracture": self.rde_engine.calc_fracture(text) if hasattr(self, 'rde_engine') and self.rde_engine else 0.0,
            "entropy": self.rde_engine.calc_entropy(text) if hasattr(self, 'rde_engine') and self.rde_engine else 0.0,
        }
        diagnostics["rde"] = dict(rde_summary)

        # 5. Tonal colours and style hints
        color_engine = engines.get("color_emotion_engine")
        color_profile = color_engine.assign_color_by_emotion(emotion_profile) if color_engine else {}
        color_profile = self._merge_semantic_hints(color_profile, semantic_hints.get("color", {}))
        color_wave = color_engine.generate_color_wave(emotion_profile) if color_engine else []
        color_transitions = color_engine.color_transition_map(emotion_profile) if color_engine else {}

        # 5. Vocal character
        # Определяем пол: preferred_gender имеет приоритет над автоматическим определением
        auto_gender = vocal_engine.detect_voice_gender(text) if vocal_engine else "auto"
        # Валидация preferred_gender: только допустимые значения
        valid_genders = ["male", "female", "auto", "neutral", "mixed"]
        if preferred_gender and preferred_gender in valid_genders and preferred_gender != "auto":
            voice_gender = preferred_gender
        else:
            voice_gender = auto_gender if auto_gender != "neutral" else "auto"
        
        voice_type = vocal_engine.detect_voice_type(text) if vocal_engine else "neutral"
        voice_emotion_vector = logical_emotion.export_emotion_vector(text)
        voice_tone = vocal_engine.detect_voice_tone(text, emotion=voice_emotion_vector) if vocal_engine else "neutral"
        voice_style = vocal_engine.detect_vocal_style(text, voice_type=voice_type, voice_tone=voice_tone) if vocal_engine else "neutral"
        vocal_dynamics = vocal_engine.vocal_dynamics_map(sections) if vocal_engine else {}
        vocal_curve = vocal_engine.vocal_intensity_curve(vocal_dynamics) if vocal_engine else []
        # Расширенная система вокалов на основе эмоций секций
        section_vocals = []
        if section_intelligence and hasattr(section_intelligence, 'section_emotions'):
            section_emotions_data = section_intelligence.section_emotions(sections) if hasattr(section_intelligence, 'section_emotions') else []
            try:
                from .vocal_techniques import get_vocal_for_section
                
                headers = structure_context.get("section_headers") or structure_context.get("section_metadata") or []
                
                for idx, sec_emo in enumerate(section_emotions_data):
                    if isinstance(sec_emo, dict):
                        sec_emotion = sec_emo.get("dominant", "neutral")
                        sec_intensity = sec_emo.get("intensity", 0.5)
                        # Получаем название секции для вариативности вокала
                        section_name = None
                        if idx < len(headers) and isinstance(headers[idx], dict):
                            section_name = headers[idx].get("tag") or headers[idx].get("label") or headers[idx].get("name")
                        
                        section_vocal = get_vocal_for_section(
                            section_emotion=sec_emotion,
                            section_intensity=sec_intensity,
                            global_emotion=_dominant_emotion(smoothed_vectors) if smoothed_vectors else None,
                            genre=style_payload.get("genre") if isinstance(style_payload, dict) else None,
                            section_name=section_name,
                        )
                        section_vocals.append(section_vocal)
                    else:
                        # MASTER-PATCH: Умный fallback вместо "tenor"
                        section_text = sections[idx] if idx < len(sections) else text
                        section_vocal = self._guess_vocal_from_text(section_text)
                        section_vocals.append(section_vocal)
            except ImportError:
                logger.warning("vocal_techniques module not available, using smart fallback")
                # MASTER-PATCH: Умный fallback вместо ["tenor"] * len(sections)
                section_vocals = [self._guess_vocal_from_text(sec if isinstance(sec, str) else text) for sec in sections]
        else:
            # MASTER-PATCH: Умный fallback вместо ["tenor"] * len(sections)
            section_vocals = [self._guess_vocal_from_text(sec if isinstance(sec, str) else text) for sec in sections] if sections else []
        
        vocal_payload = {
            "gender": voice_gender,
            "type": voice_type,
            "tone": voice_tone,
            "style": voice_style,
            "dynamics": vocal_dynamics,
            "intensity_curve": vocal_curve,
            "average_intensity": round(sum(vocal_curve) / max(len(vocal_curve), 1), 3) if vocal_curve else 0.5,
            "section_techniques": section_vocals,  # Добавляем техники для каждой секции
        }
        vocal_payload = self._merge_semantic_hints(vocal_payload, semantic_hints.get("vocal", {}))
        # FIX: Removed redundant mid-pipeline vocal fusion/mutation to comply with stateless architecture.
        # vocal_payload = self._apply_vocal_fusion(vocal_payload, override_manager.overrides)
        vocal_for_instrumentation = dict(vocal_payload)
        diagnostics["vocal"] = dict(vocal_payload)

        # 7. Breathing cues
        if breathing_engine:
            breathing_profile = {
                "inhale_points": breathing_engine.detect_inhale_points(text),
                "short_breath": breathing_engine.detect_short_breath(text),
                "broken_breath": breathing_engine.detect_broken_breath(text),
                "spasms": breathing_engine.detect_spasms(text),
            }
            breathing_profile.update(breathing_engine.detect_emotional_breathing(text, emotion_profile))
            breath_sync = breathing_engine.breath_to_emotion_sync(text, emotion_profile)
        else:
            breathing_profile = {}
            breath_sync = 0.0
        breathing_profile = self._merge_semantic_hints(breathing_profile, semantic_hints.get("breathing", {}))

        # 8. Rhythm & BPM
        legacy_bpm = None
        if isinstance(legacy_result, dict):
            legacy_bpm = legacy_result.get("bpm") or legacy_result.get("style", {}).get("bpm") if not legacy_error_detected else None
            semantic_layers = legacy_result.get("semantic_layers", {}) if isinstance(legacy_result.get("semantic_layers"), dict) and not legacy_error_detected else {}
        else:
            semantic_layers = {}

        bpm_estimate = bpm_engine.text_bpm_estimation(text)
        user_bpm_hint = semantic_hints.get("target_bpm") if isinstance(semantic_hints, dict) else None
        if isinstance(user_bpm_hint, (int, float)):
            bpm_estimate = float(user_bpm_hint)
        elif legacy_bpm is not None:
            bpm_estimate = float(legacy_bpm)

        semantic_suggested_bpm = semantic_layers.get("bpm_suggested")
        if semantic_suggested_bpm is not None and user_bpm_hint is None:
            bpm_estimate = float(semantic_suggested_bpm)

        # BPM override обрабатывается через override_manager напрямую
        # bpm_estimate уже обработан через override_manager
        bpm_curve = self.bpm_engine.meaning_bpm_curve(sections, base_bpm=bpm_estimate)
        bpm_estimate, bpm_curve, bpm_locks = self._enforce_bpm_limits(
            bpm_estimate, bpm_curve, override_manager.overrides, len(sections)
        )
        bpm_mapping = bpm_engine.emotion_bpm_mapping(emotion_profile, base_bpm=bpm_estimate)
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
        
        # КРИТИЧЕСКОЕ ДОБАВЛЕНИЕ: Обновляем BPM на основе цвета эмоции (если определен)
        # Это происходит после определения bpm_payload, но до использования в выборе жанра
        if emotion_profile and isinstance(emotion_profile, dict):
            try:
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    dominant_emotion = max(numeric_profile, key=numeric_profile.get)
                    from .color_engine_adapter import get_emotion_colors
                    emotion_colors = get_emotion_colors(dominant_emotion)
                    emotion_color = emotion_colors[0] if emotion_colors else None
                    
                    if emotion_color:
                        from .genre_colors import get_bpm_from_emotion_color
                        bpm_range = get_bpm_from_emotion_color(emotion_color)
                        if bpm_range:
                            emotion_bpm = bpm_range[2]  # default_bpm
                            # Обновляем BPM только если он не был установлен пользователем
                            if not bpm_payload.get("manual_override") and not override_manager.overrides.bpm:
                                bpm_payload["estimate"] = emotion_bpm
                                bpm_payload["emotion_color_bpm"] = emotion_bpm
                                bpm_payload["emotion_color_source"] = emotion_color
            except (ValueError, TypeError, KeyError, ImportError):
                pass

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

        diagnostics["bpm"] = dict(bpm_payload)

        # 9. Meaning velocity
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

        # 10. Tonality
        tonality_engine = engines.get("tonality_engine")
        if tonality_engine and hasattr(tonality_engine, 'mode_detection'):
            mode_result = tonality_engine.mode_detection(emotion_profile, tlp_profile)
        else:
            # Fallback: определяем mode на основе TLP
            mode_result = {
                "mode": "minor" if tlp_profile.get("pain", 0) > tlp_profile.get("love", 0) else "major", 
                "confidence": ALGORITHM_WEIGHTS["default_confidence"]
            }
        
        if tonality_engine:
            mode = tonality_engine.major_minor_classifier(sections, mode_result.get("mode", "major"))
            section_keys = tonality_engine.section_key_selection(sections, mode)
            modal_shifts = tonality_engine.modal_shift_detection(section_keys)
        else:
            mode = mode_result.get("mode", "major")
            section_keys = []
            modal_shifts = []
        section_keys, mode, anchor_key = self._align_section_keys(section_keys, override_manager.overrides, sections, mode)
        tonality_payload = {
            "mode": mode,
            "confidence": mode_result.get("confidence"),
            "section_keys": section_keys,
            "modal_shifts": modal_shifts,
            "key_curve": tonality_engine.key_transition_curve(section_keys) if tonality_engine and hasattr(tonality_engine, 'key_transition_curve') else [],
            "fallback_key": anchor_key,
        }
        tonality_payload = self._merge_semantic_hints(tonality_payload, semantic_hints.get("tonality", {}))
        
        # КРИТИЧЕСКОЕ ДОБАВЛЕНИЕ: Обновляем Key на основе цвета эмоции (если определен)
        # Это происходит после определения tonality_payload, но до использования в выборе жанра
        if emotion_profile and isinstance(emotion_profile, dict):
            try:
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    dominant_emotion = max(numeric_profile, key=numeric_profile.get)
                    from .color_engine_adapter import get_emotion_colors
                    emotion_colors = get_emotion_colors(dominant_emotion)
                    emotion_color = emotion_colors[0] if emotion_colors else None
                    
                    if emotion_color:
                        from .genre_colors import get_key_from_emotion_color
                        emotion_keys = get_key_from_emotion_color(emotion_color)
                        if emotion_keys:
                            emotion_key = emotion_keys[0]  # Первый предпочтительный ключ
                            # Обновляем Key только если он не был установлен пользователем
                            if not tonality_payload.get("manual_override") and not override_manager.overrides.key:
                                tonality_payload["key"] = emotion_key
                                tonality_payload["emotion_color_key"] = emotion_key
                                tonality_payload["emotion_color_source"] = emotion_color
                                # Обновляем anchor_key и fallback_key, если они не были установлены
                                if not tonality_payload.get("anchor_key") or tonality_payload.get("anchor_key") == "auto":
                                    tonality_payload["anchor_key"] = emotion_key
                                if not tonality_payload.get("fallback_key") or tonality_payload.get("fallback_key") == "auto":
                                    tonality_payload["fallback_key"] = emotion_key
            except (ValueError, TypeError, KeyError, ImportError):
                pass

        legacy_key = None
        if isinstance(legacy_result, dict):
            legacy_key = legacy_result.get("style", {}).get("key") or legacy_result.get("key") if not legacy_error_detected else None
        if legacy_key and not getattr(override_manager.overrides, "key", None):
            if "minor" in str(legacy_key).lower():
                tonality_payload["mode"] = "minor"
                tonality_payload["section_keys"] = [
                    key if "minor" in key.lower() or key.split()[0].startswith(str(legacy_key).split()[0]) else f"{legacy_key}" for key in tonality_payload.get("section_keys", [])
                ] or [str(legacy_key)]

        tone_result = self.tone_engine.detect_key(text)

        try:
            local_tone_mod = []
            for ev in smoothed_vectors:   # список EmotionVector из шага 5
                mod = self.tone_engine.apply_emotion_modulation(
                    {"key": tone_result.get("key"), "mode": mode},
                    ev,
                )
                local_tone_mod.append(mod)
            result["_tone_dynamic"] = local_tone_mod
        except Exception:
            result["_tone_dynamic"] = []

        # Fix Key-Emotion Link: Apply the final modulated key/mode
        # This ensures the Style Engine and later stages see the emotionally corrected key.
        if local_tone_mod and (final_mod := local_tone_mod[-1]):
            # Use final_mod key only if it's explicitly detected and the tonality_payload is 'auto' or missing
            if final_mod.get("key") and tonality_payload.get("key") in (None, "auto"):
                tonality_payload["key"] = final_mod["key"]
                tonality_payload["source"] = "emotional_tone_modulation"
            if final_mod.get("mode"):
                # Always prefer the modulated mode, as it's emotionally synced
                tonality_payload["mode"] = final_mod["mode"]
                tonality_payload.setdefault("source", "emotional_tone_modulation")

        freq_profile = self.frequency_engine.resonance_profile(tlp_profile)
        freq_profile["recommended_octaves"] = self.rns_safety.clamp_octaves(
            freq_profile.get("recommended_octaves", [])
        )
        freq_profile["safe_band_hz"] = self.rns_safety.clamp_band(freq_profile.get("safe_band_hz", 0.0) or 0.0)
        diagnostics["freq_profile"] = dict(freq_profile)
        diagnostics["rns_safety"] = {
            "safe_band_hz": freq_profile.get("safe_band_hz"),
            "octaves": list(freq_profile.get("recommended_octaves", [])),
        }

        # MASTER-PATCH v5.1: Валидация legacy genre перед использованием в инструментации
        legacy_genre_for_instruments = None
        if isinstance(legacy_result, dict):
            legacy_ok = legacy_result.get("ok") is True or legacy_result.get("status") == "ok"
            if legacy_ok:
                legacy_genre = legacy_result.get("style", {}).get("genre")
                if legacy_genre and legacy_genre not in ("auto", "unknown", "", None):
                    legacy_genre_for_instruments = legacy_genre
        
        # 11. Instrumentation suggestions
        instrument_selection = self.instrumentation_engine.instrument_selection(
            genre=legacy_genre_for_instruments,
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
        # MASTER-PATCH v4.0 — Use rage-mode instruments if detected
        selected_instruments = instrument_selection.get("selected", [])
        if instrument_emotion.get("suggested") and instrument_emotion.get("explanation", "").startswith("Rage-mode"):
            # Rage-mode detected — use aggressive instruments
            selected_instruments = instrument_emotion.get("suggested", [])
        
        instrumentation_payload = {
            "selection": {**instrument_selection, "selected": selected_instruments},
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
        diagnostics["instrumentation"] = dict(instrumentation_payload)

        # 12. Command interpretation
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

        # 13. REM synchronization
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

        # 14. Zero pulse & silence
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

        # Строим feature map для жанров (выделено в отдельный метод для уменьшения сложности)
        genre_feature_inputs = self._build_genre_feature_map(
            text=text,
            bpm_payload=bpm_payload,
            emotion_profile=emotion_profile,
            emotion_payload=emotion_payload,
            emotion_curve=emotion_curve,
            vocal_payload=vocal_payload,
            meaning_payload=meaning_payload,
            tonality_payload=tonality_payload,
            tlp_profile=tlp_profile,
            section_intel_payload=section_intel_payload,
            color_profile=color_profile,
            instrumentation_payload=instrumentation_payload,
            commands=commands,
            semantic_hints=semantic_hints,
            sections=sections,
        )
        feature_map = self.build_feature_map(genre_feature_inputs)
        # Get style_payload for folk mode check (from result)
        style_payload = result.get("style", {}) if isinstance(result, dict) else {}
        domain_genre = genre_matrix.evaluate(feature_map, style_payload=style_payload) if genre_matrix and hasattr(genre_matrix, 'evaluate') else None

        try:
            from .genre_universe_loader import load_genre_universe

            universe = load_genre_universe()
        except Exception:  # pragma: no cover - fallback if loader fails
            universe = None

        # MASTER-PATCH v5.1: Валидация legacy genre перед использованием
        genre_source = "matrix"
        legacy_style_genre = None
        if isinstance(legacy_result, dict):
            # Проверяем статус legacy_result перед использованием
            legacy_ok = legacy_result.get("ok") is True or legacy_result.get("status") == "ok"
            if legacy_ok:
                legacy_style_genre = legacy_result.get("style", {}).get("genre")
                # Валидируем жанр: не None и не "auto" / "unknown"
                if legacy_style_genre and legacy_style_genre not in ("auto", "unknown", "", None):
                    if universe:
                        resolved = universe.resolve(legacy_style_genre)
                        domain_info = universe.detect_domain(resolved)
                        if domain_info.get("domain") != "unknown":
                            domain_genre = resolved
                            genre_source = "legacy"
                        else:
                            genre_source = "mixed"

        gothic_bias = feature_map.get("gothic_factor", 0.0)
        poetic_bias = feature_map.get("poetic_density", 0.0)
        lyric_bias = feature_map.get("lyric_form_weight", 0.0)
        dramatic_bias = feature_map.get("dramatic_weight", 0.0)
        lyrical_emotion_score = feature_map.get("lyrical_emotion_score", 0.0)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверяем TLP ПЕРЕД проверкой лирических признаков
        # TLP имеет АБСОЛЮТНЫЙ ПРИОРИТЕТ над лирическими признаками
        love_level = float(tlp_profile.get("love", 0.0) or 0.0)
        pain_level = float(tlp_profile.get("pain", 0.0) or 0.0)
        truth_level = float(tlp_profile.get("truth", 0.0) or 0.0)
        
        # КРИТИЧНО: Если Love высокий и Pain низкий - это любовная лирика, НЕ gothic (ПРИОРИТЕТ!)
        # Перезаписываем domain_genre даже если он уже установлен как gothic_poetry
        # GLOBAL PATCH: отключен fallback на lyrical_song
        if False:  # love_level > 0.5 and pain_level < 0.5:
            # domain_genre = "lyrical_song"
            genre_source = "love_lyric_conversion"
            # Принудительно перезаписываем gothic_bias для любовной лирики
            gothic_bias = min(gothic_bias, 0.1)  # Снижаем gothic_bias для любовной лирики
        # Если Truth высокий - это исповедальная лирика
        elif False:  # truth_level > 0.5 and love_level > 0.3:
            # domain_genre = "lyrical_song"
            genre_source = "confessional_lyric"
            gothic_bias = min(gothic_bias, 0.1)  # Снижаем gothic_bias для исповедальной лирики
        # Если domain_genre уже установлен как gothic_poetry, но Love высокий - перезаписываем
        elif False:  # domain_genre == "gothic_poetry" and love_level > 0.4:
            # domain_genre = "lyrical_song"
            genre_source = "love_lyric_override"
            gothic_bias = min(gothic_bias, 0.1)  # Снижаем gothic_bias
        # Улучшенная логика преобразования лирических жанров в музыкальные
        # Если domain_genre не определен, но есть лирические признаки - определяем жанр
        elif not domain_genre or domain_genre == "unknown":
            # Проверяем лирические признаки
            if poetic_bias > 0.15 or lyric_bias > 0.15 or lyrical_emotion_score > 0.2:
                if gothic_bias > 0.2:
                    domain_genre = "gothic_poetry"
                    genre_source = "lyrical_to_music_conversion"
                elif poetic_bias > 0.25 or lyric_bias > 0.25:
                    # GLOBAL PATCH: отключен fallback на lyrical_song
                    # domain_genre = "lyrical_song"
                    genre_source = "lyrical_to_music_conversion"
                elif dramatic_bias > 0.25:
                    domain_genre = "cinematic"
                    genre_source = "lyrical_to_music_conversion"
                else:
                    # Fallback для лирических текстов
                    # GLOBAL PATCH: отключен fallback на lyrical_song
                    # domain_genre = "lyrical_song"
                    genre_source = "lyrical_fallback"
            # Проверяем эмоциональный посыл для определения жанра
            elif emotion_profile and isinstance(emotion_profile, dict) and emotion_profile:
                try:
                    # Безопасное извлечение доминирующей эмоции
                    numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                    dominant_emotion = max(numeric_profile, key=numeric_profile.get) if numeric_profile else None
                except (ValueError, TypeError, KeyError):
                    dominant_emotion = None
                
                pain_level = float(tlp_profile.get("pain", 0.0) or 0.0)
                love_level = float(tlp_profile.get("love", 0.0) or 0.0)
                
                # Эмоциональный посыл влияет на жанр
                if pain_level > 0.6:
                    # Готика только при очень высоком pain И наличии готических признаков
                    if gothic_bias > 0.25 and pain_level > 0.6:  # Повышен порог
                        domain_genre = "gothic_poetry"
                    else:
                        # GLOBAL PATCH: отключен fallback на lyrical_song
                        # domain_genre = "lyrical_song"
                        pass
                    genre_source = "emotion_based"
                elif False:  # love_level > 0.6:
                    # GLOBAL PATCH: отключен fallback на lyrical_song
                    # domain_genre = "lyrical_song"
                    genre_source = "emotion_based"
                elif False:  # dominant_emotion and dominant_emotion in ("sadness", "melancholy", "sorrow"):
                    # GLOBAL PATCH: отключен fallback на lyrical_song
                    # domain_genre = "lyrical_song"
                    genre_source = "emotion_based"
                # Дополнительная проверка: если TLP показывает лирику (любая комбинация truth/love/pain)
                elif False:  # (pain_level > 0.3 or love_level > 0.3) and (poetic_bias > 0.05 or lyric_bias > 0.05):
                    # GLOBAL PATCH: отключен fallback на lyrical_song
                    # domain_genre = "lyrical_song"
                    genre_source = "emotion_tlp_based"
        
        # Преобразование EDM в лирические жанры при наличии лирических признаков
        if domain_genre == "edm" and (gothic_bias > 0.25 or poetic_bias > 0.25 or lyric_bias > 0.25):
            # Готика только если gothic_bias значительно выше других признаков
            if gothic_bias > 0.3 and gothic_bias >= max(poetic_bias, lyric_bias) * 1.2:
                domain_genre = "gothic_poetry"
            else:
                # GLOBAL PATCH: отключен fallback на lyrical_song
                # domain_genre = "lyrical_song"
                pass
            genre_source = "lyrical_conversion"
        elif domain_genre == "edm" and dramatic_bias > 0.25:
            domain_genre = "cinematic"
            genre_source = "dramatic_conversion"
        
        # MASTER-PATCH v5.1: Финальный fallback если жанр все еще не определен
        # Проверяем наличие overrides/commands/semantic_hints/legacy перед применением fallback
        has_genre_override = (
            (semantic_hints.get("style", {}).get("genre") and semantic_hints.get("style", {}).get("genre") not in ("auto", "unknown", ""))
            or (commands and any(cmd.get("type") == "genre" for cmd in commands))
            or (isinstance(legacy_result, dict) and legacy_result.get("ok") and legacy_result.get("style", {}).get("genre") and legacy_result.get("style", {}).get("genre") not in ("auto", "unknown", ""))
        )
        
        if not domain_genre or domain_genre == "unknown" or domain_genre is None:
            # Если есть override - не применяем fallback
            if has_genre_override:
                # Используем жанр из override
                override_genre = (
                    semantic_hints.get("style", {}).get("genre")
                    or (commands and next((cmd.get("value") for cmd in commands if cmd.get("type") == "genre"), None))
                    or (isinstance(legacy_result, dict) and legacy_result.get("style", {}).get("genre"))
                )
                if override_genre and override_genre not in ("auto", "unknown", ""):
                    domain_genre = override_genre
                    genre_source = "override"
            # Проверяем TLP для финального решения только если нет override
            elif not has_genre_override:
                pain_level = float(tlp_profile.get("pain", 0.0) or 0.0)
                love_level = float(tlp_profile.get("love", 0.0) or 0.0)
                truth_level = float(tlp_profile.get("truth", 0.0) or 0.0)
                
                # Проверяем наличие сильных жанровых сигналов
                has_strong_genre_signal = (
                    gothic_bias > 0.25
                    or poetic_bias > 0.25
                    or lyric_bias > 0.25
                    or dramatic_bias > 0.25
                    or feature_map.get("hiphop_factor", 0.0) > 0.2
                    or feature_map.get("edm_factor", 0.0) > 0.2
                    or feature_map.get("cinematic_factor", 0.0) > 0.2
                )
                
                # Если есть любая эмоциональная активность - это лирика
                if pain_level > 0.2 or love_level > 0.2 or truth_level > 0.2:
                    # Готика только при очень высоком pain И явных готических признаках
                    if pain_level > 0.6 and gothic_bias > 0.25:  # Повышен порог
                        domain_genre = "gothic_poetry"
                    elif not has_strong_genre_signal:
                        # SOFT-fallback: lyrical_song только если нет сильных жанровых сигналов
                        domain_genre = "lyrical_song"
                    genre_source = "final_tlp_fallback"
                elif not has_strong_genre_signal:
                    # SOFT-fallback: lyrical_song только если нет сильных жанровых сигналов
                    domain_genre = "lyrical_song"
                    genre_source = "final_fallback"
        
        # MASTER_PATCH_V5_SKELETON: hook points (NO-OP)
        # Genre Conflict Resolver + Hybrid Genre Engine
        backend_payload = result  # Create backend_payload reference for hooks
        if self._gcr is not None:
            domain_genre = self._gcr.resolve(domain_genre, backend_payload)
        if self._hge is not None:
            # HybridGenreEngine.resolve() supports both signatures:
            # - resolve(text_input: str) -> dict
            # - resolve(genre: str, context: dict) -> str
            if hasattr(self._hge, 'resolve'):
                domain_genre = self._hge.resolve(genre=domain_genre, context=backend_payload)
            else:
                # Fallback for inner class
                pass
        
        # Rage / Epic filters (currently NO-OP)
        if self._rage_filter is not None:
            backend_payload = self._rage_filter.apply(backend_payload)
        if self._epic_override is not None:
            backend_payload = self._epic_override.apply(backend_payload)
        
        # NORMALIZED_TEXT FIX:
        # Ensure normalized_text always exists and is valid.
        # Lazy import to avoid circular dependencies.
        try:
            from .text_utils import normalize_text_preserve_symbols
            normalized_text = normalize_text_preserve_symbols(text)
        except Exception:
            normalized_text = text  # Safe fallback
        
        # Use normalized_text in all downstream engines
        text_for_engines = normalized_text
        
        # MASTER-PATCH v6.0: Hybrid Genre Engine (HGE) integration
        # Собираем сигналы для гибридного жанра
        folk_ballad_candidate = None
        if normalized_text:
            folk_ballad_candidate = self._detect_folk_ballad_v2(normalized_text, emotion_profile)
        
        road_narrative_score = 0.0
        if hasattr(self, '_detect_road_narrative_signals'):
            road_signals = self._detect_road_narrative_signals(
                text, tlp_profile, emotion_profile, sections
            )
            road_narrative_score = road_signals.get("score", 0.0) if isinstance(road_signals, dict) else 0.0
        
        hge_signals = self.HybridGenreEngine.collect_signals(
            domain_genre=domain_genre,
            folk_ballad_candidate=folk_ballad_candidate,
            road_narrative_score=road_narrative_score,
            emotion_profile=emotion_profile,
            feature_map=feature_map,
            legacy_genre=legacy_style_genre if legacy_style_genre else None,
            semantic_hints=semantic_hints,
            commands=commands,
        )
        
        # Проверяем user override
        user_override_genre = None
        if semantic_hints.get("style", {}).get("genre") and semantic_hints.get("style", {}).get("genre") not in ("auto", "unknown", ""):
            user_override_genre = semantic_hints.get("style", {}).get("genre")
        elif commands and any(cmd.get("type") == "genre" for cmd in commands):
            for cmd in commands:
                if cmd.get("type") == "genre" and cmd.get("value") not in ("auto", "unknown", ""):
                    user_override_genre = cmd.get("value")
                    break
        
        # Разрешаем гибридный жанр
        hybrid_genre = self.HybridGenreEngine.resolve_hybrid_genre(hge_signals, user_override_genre)
        
        # Используем hybrid_genre если он есть, иначе domain_genre
        final_domain_genre = hybrid_genre or domain_genre
        
        genre_analysis = {
            "feature_map": feature_map,
            "domain_genre": domain_genre,
            "hybrid_genre": hybrid_genre,
            "final_domain_genre": final_domain_genre,
            "genre_source": genre_source,
            "hge_signals": hge_signals
        }
        diagnostics["genre_source"] = genre_source
        diagnostics["genre_analysis"] = genre_analysis

        # 15. Style synthesis
        style_commands = command_payload.get("style") or {}
        emotion_bias = compute_genre_bias(dynamic_emotion_profile)
        style_genre = (
            style_commands.get("genre")
            or semantic_hints.get("style", {}).get("genre")
            or domain_genre
            or self.style_engine.genre_selection(emotion_profile, tlp_profile)
        )
        emotion_label = (tlp_profile.get("dominant_name") or tlp_profile.get("emotion") or "").lower()
        if not style_commands.get("genre") and emotion_label in FORCED_GENRES:
            style_genre = FORCED_GENRES[emotion_label]
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
            # Fix: Ensure tone/key are derived from tonality_payload after alignment/modulation
            tone=self.style_engine.tone_style({
                "mode": tonality_payload.get("mode"),
                "section_keys": tonality_payload.get("section_keys", []),
            }),
            instrumentation=style_instrumentation,
            vocal=style_vocal,
            visual=style_visual,
        )
        emotion = _dominant_emotion(smoothed_vectors)
        instrumentation_palette = emotion_to_instruments(emotion)
        vocal_profile = emotion_to_vocal(emotion)
        style_label = emotion_to_style(emotion)
        color_global = result.get("_emotion_map", {}).get("global", "#888888")

        suno_style_prompt = (
            f"[STYLE: {style_label}]\n"
            f"[EMOTION: {emotion}]\n"
            f"[COLOR: {color_global}]\n"
            f"[INSTRUMENTATION: {', '.join(instrumentation_palette)}]\n"
            f"[VOCAL: {vocal_profile}]\n"
            f"[BPM: {result.get('bpm', {}).get('estimate', 'auto')}]\n"
            f"[KEY: {result.get('style', {}).get('key', 'auto')}]\n"
        )

        result["style_prompt"] = suno_style_prompt
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Агрегируем все цвета из цепочки анализа
        # 1. Цвет TLP
        tlp_color = None
        if isinstance(color_profile, dict):
            tlp_color = color_profile.get("primary_color")
        
        # 2. Цвет эмоции → BPM и Key
        emotion_color = None
        emotion_bpm = None
        emotion_key = None
        if emotion_profile and isinstance(emotion_profile, dict):
            try:
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    dominant_emotion = max(numeric_profile, key=numeric_profile.get)
                    from .color_engine_adapter import get_emotion_colors
                    emotion_colors = get_emotion_colors(dominant_emotion)
                    emotion_color = emotion_colors[0] if emotion_colors else None
                    
                    # КРИТИЧЕСКОЕ ДОБАВЛЕНИЕ: Определяем BPM и Key из цвета эмоции
                    if emotion_color:
                        from .genre_colors import get_bpm_from_emotion_color, get_key_from_emotion_color
                        bpm_range = get_bpm_from_emotion_color(emotion_color)
                        if bpm_range:
                            emotion_bpm = bpm_range[2]  # default_bpm
                        emotion_keys = get_key_from_emotion_color(emotion_color)
                        if emotion_keys:
                            emotion_key = emotion_keys[0]  # Первый предпочтительный ключ
            except (ValueError, TypeError, KeyError, ImportError):
                pass
        
        # 3. Цвет жанра лирики
        lyrical_genre_color = None
        if domain_genre:
            try:
                from .genre_colors import get_lyrical_genre_colors
                # MASTER-PATCH v3.2: передаем style_payload для проверки флагов
                lyrical_colors = get_lyrical_genre_colors(domain_genre, style_payload)
                lyrical_genre_color = lyrical_colors[0] if lyrical_colors else None
            except (ImportError, Exception):
                pass
        
        # 4. Цвета вокала (для секций)
        vocal_colors = []
        try:
            from .vocal_techniques import EMOTION_TO_VOCAL_MAP
            from .color_engine_adapter import get_emotion_colors
            if emotion_profile and isinstance(emotion_profile, dict):
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    dominant_emotion = max(numeric_profile, key=numeric_profile.get)
                    if dominant_emotion in EMOTION_TO_VOCAL_MAP:
                        # Берем цвет эмоции для вокала
                        vocal_emotion_colors = get_emotion_colors(dominant_emotion)
                        vocal_colors = vocal_emotion_colors[:2] if vocal_emotion_colors else []
        except (ImportError, Exception):
            pass
        
        # 5. Цвет жанра музыки (сравнение BPM и Key)
        music_genre_color = None
        if style_genre:
            try:
                from .genre_colors import get_music_genre_colors
                # MASTER-PATCH v3.2: передаем style_payload для проверки флагов
                music_colors = get_music_genre_colors(style_genre, style_payload)
                music_genre_color = music_colors[0] if music_colors else None
            except (ImportError, Exception):
                pass
        
        # КРИТИЧЕСКОЕ ДОБАВЛЕНИЕ: Сравнение BPM и Key из цвета эмоции с жанрами музыки
        if emotion_bpm and emotion_key:
            try:
                from .genre_colors import find_matching_music_genre_by_bpm_key
                # Получаем BPM и Key для всех жанров музыки из GENRE_DATABASE
                # (упрощенная версия - в реальности нужно загрузить из JSON)
                genre_bpm_ranges = {}  # Будет заполнено из GENRE_DATABASE
                genre_keys = {}  # Будет заполнено из GENRE_DATABASE
                
                # Пока используем упрощенную логику: если BPM и Key совпадают с текущим жанром
                # В будущем можно загрузить полную базу из GENRE_DATABASE.json
                matching_genre, match_score = find_matching_music_genre_by_bpm_key(
                    emotion_bpm,
                    emotion_key,
                    genre_bpm_ranges,
                    genre_keys,
                )
                
                # Если найден более подходящий жанр, обновляем style_genre
                if match_score > 0.5 and matching_genre != style_genre:
                    style_genre = matching_genre
                    # Обновляем цвет жанра музыки
                    from .genre_colors import get_music_genre_colors
                    # MASTER-PATCH v3.2: передаем style_payload для проверки флагов
                    music_colors = get_music_genre_colors(matching_genre, style_payload)
                    music_genre_color = music_colors[0] if music_colors else music_genre_color
            except (ImportError, Exception):
                pass
        
        # 6. Агрегируем все цвета в общий color_wave
        try:
            from .genre_colors import aggregate_colors
            style_color_wave = aggregate_colors(
                tlp_color=tlp_color,
                emotion_color=emotion_color,
                lyrical_genre_color=lyrical_genre_color,
                vocal_colors=vocal_colors,
                music_genre_color=music_genre_color,
            )
        except (ImportError, Exception):
            # Fallback: используем старую логику
            # MASTER-PATCH v3.3 — Skip normalization for locked or neutral
            if isinstance(style_payload, dict) and (style_payload.get("_color_locked") or style_payload.get("_neutral_mode")):
                # Пропускаем нормализацию, используем существующий color_wave
                style_color_wave = style_payload.get("color_wave")
            else:
                style_color_wave = None
                if isinstance(color_profile, dict):
                    style_color_wave = color_profile.get("wave")
                if not style_color_wave and isinstance(color_profile, dict):
                    primary = color_profile.get("primary_color")
                    accent = color_profile.get("accent_color")
                    if primary:
                        style_color_wave = [primary]
                        if accent:
                            style_color_wave.append(accent)
        
        style_payload = {
            "genre": style_genre,
            "mood": style_mood,
            "color_wave": style_color_wave,  # КРИТИЧНО: Добавлен color_wave
            "instrumentation": style_instrumentation,
            "vocal": style_vocal,
            "visual": style_visual,
            "tone": style_tone,
            "prompt": style_prompt,
            "genre_bias": emotion_bias,
        }
        if domain_genre:
            style_payload["domain_genre"] = domain_genre
        if style_commands.get("intensity"):
            style_payload["intensity"] = style_commands["intensity"]
        if style_commands:
            style_payload["commands"] = style_commands
        style_payload = self._merge_semantic_hints(style_payload, semantic_hints.get("style", {}))

        integrity_block: Dict[str, Any] = {}
        if isinstance(legacy_result, dict) and isinstance(legacy_result.get("integrity"), dict):
            integrity_block = dict(legacy_result["integrity"])

        router_input = {
            **result,
            "bpm": bpm_payload,
            "tlp": tlp_profile,
            "integrity": integrity_block or result.get("integrity", {}),
            "emotion": {**emotion_payload, "label": emotion_label},
            "style": {**style_payload},
        }
        macro_genre, genre_reason = self.genre_router.route(router_input)

        style_block = router_input.get("style") or {}
        if not isinstance(style_block, dict):
            style_block = {}

        # MASTER-PATCH v5.1: Проверяем наличие user-override genre перед установкой macro_genre
        has_user_genre_override = (
            style_block.get("genre") and str(style_block.get("genre")).lower() not in ("auto", "unknown", "")
            or (semantic_hints.get("style", {}).get("genre") and semantic_hints.get("style", {}).get("genre") not in ("auto", "unknown", ""))
            or (commands and any(cmd.get("type") == "genre" for cmd in commands))
        )
        
        if not has_user_genre_override and ("genre" not in style_block or str(style_block.get("genre")).lower() in ("auto", "unknown", "")):
            style_block["genre"] = macro_genre

        style_block.setdefault("genre_reason", genre_reason)

        if not style_block.get("macro_genre"):
            style_block["macro_genre"] = macro_genre

        if not style_block.get("subgenre") and not style_block.get("universe_id"):
            resolution = self.genre_universe_adapter.resolve(macro_genre, result)
            if not style_block.get("subgenre"):
                style_block["subgenre"] = resolution.subgenre
            style_block.setdefault("universe_tags", resolution.tags)
            style_block.setdefault("universe_source", resolution.source)

        # MASTER-PATCH v5.1: Объединяем style_block с style_payload, защищая mood и color_wave
        if isinstance(style_payload, dict) and isinstance(style_block, dict):
            # Защищаем mood и color_wave от перезаписи, если они скорректированы
            protected_mood = style_block.get("_mood_corrected") or style_block.get("_neutral_mode")
            protected_color = style_block.get("_color_locked") or style_block.get("_neutral_mode")
            
            # Приоритет: overrides → скорректированное из движков → payload / router
            # Обновляем остальные поля из style_payload, исключая защищенные
            safe_payload = {k: v for k, v in style_payload.items() 
                           if not (k == "mood" and protected_mood) 
                           and not (k == "color_wave" and protected_color)}
            style_block.update(safe_payload)
            
            # Если mood/color_wave не защищены, используем из style_payload
            if not protected_mood and style_payload.get("mood"):
                style_block["mood"] = style_payload.get("mood")
            if not protected_color and style_payload.get("color_wave"):
                style_block["color_wave"] = style_payload.get("color_wave")
        style_payload = style_block

        # Используем emotion_engine из engines, а не _emotion_engine (который EmotionAggregator)
        # Используем emotion_engine из emotion.py для build_emotion_profile
        emotion_profile_v1 = emotion_engine.build_emotion_profile(
            text,
            legacy_context={
                "style": style_payload,
                "bpm": bpm_payload,
                "tone": tonality_payload,
                "commands": command_payload,
            },
        )

        commands_block = command_payload if isinstance(command_payload, dict) else {}
        overrides_block = commands_block.get("overrides", {}) if isinstance(commands_block, dict) else {}

        legacy_genre = style_payload.get("genre") if isinstance(style_payload, dict) else None
        # Используем emotion_engine из emotion.py для pick_final_genre
        final_genre = emotion_engine.pick_final_genre(
            emotion_profile_v1.get("genre_scores", {}),
            legacy_genre=legacy_genre,
        )

        legacy_bpm = bpm_payload.get("estimate") if isinstance(bpm_payload, dict) else None
        final_bpm = legacy_bpm or emotion_profile_v1.get("bpm")

        legacy_key = None
        if isinstance(tonality_payload, dict):
            legacy_key = tonality_payload.get("key") or tonality_payload.get("mode")
        final_key = legacy_key or (emotion_profile_v1.get("key") or {}).get("scale")

        if "bpm" not in overrides_block:
            bpm_payload["estimate"] = final_bpm

        # MASTER-PATCH v5.1: Проверяем наличие genre override перед setdefault
        if "genre" not in overrides_block and isinstance(style_payload, dict):
            # Проверяем наличие явного жанра из overrides/commands/semantic_hints/legacy
            has_explicit_genre = (
                style_payload.get("genre") and style_payload.get("genre") not in ("auto", "unknown", "")
                or (semantic_hints.get("style", {}).get("genre") and semantic_hints.get("style", {}).get("genre") not in ("auto", "unknown", ""))
                or (commands and any(cmd.get("type") == "genre" for cmd in commands))
                or (isinstance(legacy_result, dict) and legacy_result.get("ok") and legacy_result.get("style", {}).get("genre") and legacy_result.get("style", {}).get("genre") not in ("auto", "unknown", ""))
            )
            # Применяем final_genre только если нет override и final_genre != "lyrical_song" (или если нет других жанров)
            if not has_explicit_genre:
                if final_genre and final_genre != "lyrical_song":
                    style_payload.setdefault("genre", final_genre)
                elif not style_payload.get("genre") and final_genre == "lyrical_song":
                    # SOFT-fallback: lyrical_song только при полном отсутствии других жанров
                    style_payload.setdefault("genre", final_genre)

        if "key" not in overrides_block and isinstance(tonality_payload, dict):
            # Приоритет: Key из эмоций > Key из legacy/fusion
            emotion_key = tonality_payload.get("emotion_color_key")
            if emotion_key and emotion_key != "auto":
                tonality_payload["key"] = emotion_key
                tonality_payload["source"] = "emotion_color"
            else:
                tonality_payload.setdefault("key", final_key)

        result.setdefault("emotions", {})["profile_v1"] = emotion_profile_v1

        # Сохраняем tonality_payload в result до вызова fusion_engine
        # чтобы emotion_color_key был доступен для проверки приоритета
        if isinstance(tonality_payload, dict):
            result["tonality"] = dict(tonality_payload)

        diagnostics["tonality"] = dict(tonality_payload)

        # RDE уже вычислен выше (этап 4), удаляем дубликат

        integrity_report = self.integrity_engine.analyze(text)
        diagnostics["integrity"] = dict(integrity_report)

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

        # 12. StylePrompt - генерация финального промпта для стиля
        style_prompt = {
            "genre": style_payload.get("genre") if isinstance(style_payload, dict) else None,
            "mood": style_payload.get("mood") if isinstance(style_payload, dict) else None,
            "vocal_style": vocal_payload.get("style") if isinstance(vocal_payload, dict) else None,
            "instrumentation": instrument_selection.get("primary") if isinstance(instrument_selection, dict) else None,
            "bpm": bpm_payload.get("estimate") if isinstance(bpm_payload, dict) else None,
            "key": tonality_payload.get("key") if isinstance(tonality_payload, dict) else None,
            "color_wave": color_wave,
        }
        # Формируем текстовый промпт
        style_prompt_text = []
        if style_prompt["genre"]:
            style_prompt_text.append(f"Genre: {style_prompt['genre']}")
        if style_prompt["mood"]:
            style_prompt_text.append(f"Mood: {style_prompt['mood']}")
        if style_prompt["vocal_style"]:
            style_prompt_text.append(f"Vocal: {style_prompt['vocal_style']}")
        if style_prompt["instrumentation"]:
            style_prompt_text.append(f"Instruments: {style_prompt['instrumentation']}")
        if style_prompt["bpm"]:
            style_prompt_text.append(f"BPM: {style_prompt['bpm']}")
        if style_prompt["key"]:
            style_prompt_text.append(f"Key: {style_prompt['key']}")
        style_prompt["text"] = ", ".join(style_prompt_text) if style_prompt_text else "Default style"
        diagnostics["style_prompt"] = style_prompt

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
                "freq_profile": freq_profile,
                "rns_safety": {
                    "safe_band_hz": freq_profile.get("safe_band_hz"),
                    "octaves": freq_profile.get("recommended_octaves"),
                },
                "integrity": integrity_report,
                "commands": command_payload,
                "annotations": annotations,
                "phrase_packets": section_intel_payload.get("phrase_packets", []),
                "section_emotions": section_intel_payload.get("section_emotions", []),
                "semantic_hints": semantic_hints,
                "auto_context": structure_context,
                "emotion_curve": curve_dict,
                "instrument_dynamics": instrument_dynamics_payload,
                "override_debug": override_manager.debug_summary(),
                "rde_summary": rde_summary,
                "genre_analysis": genre_analysis,
            }
        )
        phrase_emotions = section_intel_payload.get("phrase_packets", [])
        tonality_hint = result.get("tonality") or result.get("tone") or {}
        key_hint = tonality_hint.get("key") if isinstance(tonality_hint, dict) else None
        # Используем multimodal_matrix из engines
        multimodal_matrix = engines.get("multimodal_matrix") if engines else None
        if multimodal_matrix and hasattr(multimodal_matrix, 'build_matrix'):
            matrix = multimodal_matrix.build_matrix(
            phrase_emotions=phrase_emotions,
            section_emotions=section_emotions,
            global_curve=curve_dict,
            tlp_profile=tlp_profile,
            dynamic_bias=dynamic_bias,
            genre_hint=result["style"].get("genre") if "style" in result else None,
            bpm_hint=result.get("bpm", {}).get("estimate"),
            key_hint=key_hint,
            suno_annotation=result.get("suno_annotation", {}),
        )
        emotion_matrix = matrix if isinstance(matrix, dict) else {}
        diagnostics["emotion_matrix"] = emotion_matrix

        bpm = max(
            40,
            min(
                200,
                int(
                    80
                    + (emotion_matrix.get("joy", 0) * 30)
                    - (emotion_matrix.get("sadness", 0) * 20)
                    + (emotion_matrix.get("anger", 0) * 25)
                )
            ),
        )

        # Обновляем BPM только если он еще не был установлен из эмоций или других источников
        bpm_block = result.get("bpm") if isinstance(result.get("bpm"), dict) else {}
        bpm_block = dict(bpm_block)
        # Сохраняем BPM из эмоций, если он был установлен
        if bpm_block.get("emotion_color_bpm") and not bpm_block.get("manual_override"):
            bpm = bpm_block.get("emotion_color_bpm", bpm)
        
        # MASTER-PATCH v3: коррекция BPM для low-emotion текстов
        if self._is_low_emotion_context(tlp_profile, result.get("rde", {})):
            from .config import LOW_EMOTION_BPM_MIN, LOW_EMOTION_BPM_MAX
            if bpm is None:
                bpm = (LOW_EMOTION_BPM_MIN + LOW_EMOTION_BPM_MAX) // 2
            else:
                bpm = max(LOW_EMOTION_BPM_MIN, min(LOW_EMOTION_BPM_MAX, bpm))
        
        bpm_block["estimate"] = bpm
        result["bpm"] = bpm_block
        diagnostics.setdefault("bpm", {})["estimate"] = bpm

        style_block = result.get("style") if isinstance(result.get("style"), dict) else {}
        style_block.setdefault("bpm", bpm)
        # Сохраняем mood и color_wave из style_payload, если они есть
        if isinstance(style_payload, dict):
            if style_payload.get("mood"):
                style_block["mood"] = style_payload.get("mood")
            if style_payload.get("color_wave"):
                style_block["color_wave"] = style_payload.get("color_wave")
        result["style"] = style_block
        # === Inject emotion_matrix_v1 hints (fallback) ===
        em_bpm = emotion_matrix.get("bpm", {}) if isinstance(emotion_matrix, dict) else {}
        em_key = emotion_matrix.get("key", {}) if isinstance(emotion_matrix, dict) else {}
        em_voc = emotion_matrix.get("vocals", {}) if isinstance(emotion_matrix, dict) else {}

        bpm_diag = diagnostics.get("bpm", {}) if isinstance(diagnostics.get("bpm"), dict) else {}
        if bpm_diag.get("estimate") is None and em_bpm.get("recommended") is not None:
            bpm_diag = {**bpm_diag, "estimate": em_bpm.get("recommended")}
            if not result.get("bpm") or result.get("bpm", {}).get("estimate") is None:
                result["bpm"] = {
                    **(result.get("bpm") or {}),
                    "estimate": em_bpm.get("recommended"),
                    "source": em_bpm.get("source", "emotion_matrix_v1"),
                }
        diagnostics["bpm"] = bpm_diag

        musical_key = key_hint or (tonality_payload.get("key") if isinstance(tonality_payload, dict) else None)
        from .tone_sync import ToneSyncEngine

        tone_engine = ToneSyncEngine()
        tone_profile = tone_engine.pick_profile(
            bpm=bpm,
            key=musical_key,
            tlp=tlp_profile,
            emotion_matrix=emotion_matrix,
        )

        result["tone_profile"] = tone_profile
        diagnostics["tone_profile"] = tone_profile

        tonality_diag = diagnostics.get("tonality", {}) if isinstance(diagnostics.get("tonality"), dict) else {}
        key_mode = em_key.get("mode")
        if tonality_diag.get("key") in (None, "auto") and key_mode:
            tonality_diag = {**tonality_diag, "key": key_mode}
            if isinstance(result.get("tonality"), dict):
                result["tonality"] = {**result.get("tonality", {}), **tonality_diag}
            else:
                result["tonality"] = dict(tonality_diag)
            if not result.get("tone"):
                result["tone"] = dict(tonality_diag)
        diagnostics["tonality"] = tonality_diag

        vocal_diag = diagnostics.get("vocal", {}) if isinstance(diagnostics.get("vocal"), dict) else {}
        notes = em_voc.get("notes")
        if not vocal_diag.get("style") and notes:
            vocal_diag = {
                **vocal_diag,
                "style": notes if isinstance(notes, str) else ", ".join(notes),
            }
            if not result.get("vocal"):
                result["vocal"] = {
                    "gender": em_voc.get("gender"),
                    "notes": em_voc.get("notes"),
                    "intensity_curve": em_voc.get("intensity_curve"),
                    "source": "emotion_matrix_v1",
                    "style": vocal_diag.get("style"),
                }
        diagnostics["vocal"] = vocal_diag

        instr_diag = diagnostics.get("instrumentation", {}) if isinstance(diagnostics.get("instrumentation"), dict) else {}
        matrix_instruments = emotion_matrix.get("instruments") or {}
        core = matrix_instruments.get("core") or []
        accent = matrix_instruments.get("accent") or []
        texture = matrix_instruments.get("texture") or []
        palette: list[Any] = []
        if core:
            palette.extend(core)
        if accent:
            palette.extend(accent)
        if texture:
            palette.extend(texture)
        if palette and not instr_diag.get("palette"):
            instr_diag = {**instr_diag, "palette": palette}
        diagnostics["instrumentation"] = instr_diag

        result["emotion_matrix"] = matrix
        try:
            result["suno_annotation"] = build_suno_annotations(
                text=text,
                sections=section_intel_payload.get("section_emotions", []),
                emotion_curve=curve_dict,
            )
        except Exception as exc:  # pragma: no cover - external integration guard
            logger.exception("Suno annotation build failed: %s", exc)
            diagnostics.setdefault("errors", []).append("suno_annotation_failed")
            result["suno_annotation"] = {}
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

        # FINAL STEP: Apply Fusion Engine (Task #1 Fix)
        try:
            from .fusion_engine_v64 import FusionEngineV64

            fusion = FusionEngineV64()
            fusion_summary = fusion.fuse(
                result,
                genre_route={
                    "genre": macro_genre,
                    "subgenre": style_payload.get("subgenre", macro_genre),
                },
            )
            result["fusion_summary"] = fusion_summary
        except Exception as exc:
            logger.exception("FusionEngineV64 failed during final fusion: %s", exc)
            diagnostics.setdefault("errors", []).append("fusion_generate_failed")
            result["fusion_summary"] = {
                "annotated_text_fanf": "FANF generation unavailable.",
                "annotated_text_ui": "FANF generation unavailable.",
                "annotated_text_suno": "FANF generation unavailable.",
                "choir_active": False,
                "error": str(exc),
            }
        applied_overrides = self._apply_user_overrides_once(result, override_manager, engines=engines)
        # Получаем symbiosis_engine из engines
        symbiosis_engine = engines.get("symbiosis_engine") if engines else None
        if symbiosis_engine and hasattr(symbiosis_engine, 'build_final_symbiosis_state'):
            result["symbiosis"] = symbiosis_engine.build_final_symbiosis_state(
            override_manager,
            result,
            applied_overrides=applied_overrides,
        )
        else:
            result["symbiosis"] = {}

        # --- COLOR ENGINE ADAPTER ---
        color_res = self.color_adapter.resolve_color_wave(result)
        
        # MASTER-PATCH v3.4 — Force neutral color assignment
        # If low-emotion mode was detected earlier, enforce neutral palette NOW
        style_payload = result.get("style") or {}
        if style_payload.get("_neutral_mode"):
            from .config import NEUTRAL_COLOR_WAVE
            from .color_engine_adapter import ColorResolution
            style_payload["color_wave"] = NEUTRAL_COLOR_WAVE
            style_payload["_color_locked"] = True
            color_res = ColorResolution(colors=NEUTRAL_COLOR_WAVE, source="neutral_mode_forced")
            result["style"] = style_payload

        style_block = result.get("style") or {}
        if not isinstance(style_block, dict):
            style_block = {}

        # MASTER-PATCH v5.1: Сохраняем mood и color_wave из style_payload, защищая скорректированные значения
        # MASTER-PATCH v3.3 — Skip normalization for locked or neutral
        protected_mood = style_block.get("_mood_corrected") or style_block.get("_neutral_mode")
        protected_color = style_block.get("_color_locked") or style_block.get("_neutral_mode")
        
        if isinstance(style_payload, dict):
            # Обновляем все поля, исключая защищенные mood и color_wave
            safe_payload = {k: v for k, v in style_payload.items() 
                           if not (k == "mood" and protected_mood) 
                           and not (k == "color_wave" and protected_color)}
            style_block.update(safe_payload)
            
            # Если mood/color_wave не защищены, используем из style_payload
            if not protected_mood and style_payload.get("mood"):
                style_block["mood"] = style_payload.get("mood")
            if not protected_color and style_payload.get("color_wave"):
                style_block["color_wave"] = style_payload.get("color_wave")
        
        # Устанавливаем color_wave из color_res, если его еще нет
        # GLOBAL PATCH: проверяем _color_locked перед установкой
        # MASTER-PATCH v3.3 — Skip normalization for locked or neutral
        # Ensure color_wave preserved unless explicit override
        if "color_wave" in style_payload and "_color_locked" in style_block:
            if style_block.get("_color_locked"):
                # lock respected — keep original color_wave
                style_block["color_wave"] = style_payload.get("color_wave")
            else:
                # unlocked — override allowed
                if color_res and color_res.colors:
                    style_block["color_wave"] = color_res.colors
        else:
            # Fallback: use color_res if available
            if not (style_block.get("_color_locked") or style_block.get("_neutral_mode")):
                if "color_wave" not in style_block or not style_block.get("color_wave"):
                    if color_res and color_res.colors:
                        style_block["color_wave"] = color_res.colors
            style_block.setdefault("color_source", color_res.source if color_res else None)

        result["style"] = style_block

        instrumentation_block = result.get("instrumentation")
        if not isinstance(instrumentation_block, dict):
            instrumentation_block = {}
        result["instrumentation"] = instrumentation_block

        dynamics_block = (
            instrument_dynamics_payload
            if isinstance(instrument_dynamics_payload, dict)
            else {}
        )
        result["instrument_dynamics"] = dynamics_block

        instrumentation_diag = diagnostics.get("instrumentation", {}) if isinstance(diagnostics.get("instrumentation"), dict) else {}
        palette = instrumentation_block.get("palette")
        fractures = dynamics_block.get("fractures")
        if palette and not instrumentation_diag.get("palette"):
            instrumentation_diag = {**instrumentation_diag, "palette": palette}
        if fractures is not None:
            instrumentation_diag = {**instrumentation_diag, "fractures": fractures}
        diagnostics["instrumentation"] = instrumentation_diag

        suno_annotations: list[Any] = []
        try:
            suno_annotations = self.suno_engine.build_suno_safe_annotations(
                sections,
                {**diagnostics, "commands": command_payload},
            ) or []
        except Exception as exc:
            logger.exception("Suno safe annotations failed: %s", exc)
            diagnostics.setdefault("errors", []).append("suno_safe_annotations_failed")
        result["suno_annotations"] = suno_annotations
        if language_info:
            result["language"] = dict(language_info)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убеждаемся, что style содержит mood и color_wave из style_payload
        # Это последний шанс сохранить эти поля перед возвратом из _backend_analyze
        if isinstance(style_payload, dict):
            style_result = result.get("style") or {}
            if not isinstance(style_result, dict):
                style_result = {}
            # Сохраняем mood из style_payload (приоритет)
            if style_payload.get("mood"):
                style_result["mood"] = style_payload.get("mood")
            # Сохраняем color_wave из style_payload (если есть)
            if style_payload.get("color_wave"):
                style_result["color_wave"] = style_payload.get("color_wave")
            elif color_wave:
                style_result["color_wave"] = color_wave
            # Обновляем result["style"] с сохранением всех полей из style_payload
            # Важно: используем update, чтобы не потерять существующие поля
            style_result.update(style_payload)
            result["style"] = style_result
        
        result["consistency"] = {
            "instrumentation_consistency": rde_summary.get("instrumentation_consistency", "unknown"),
            "vocal_consistency": bool(vocal_payload),
            "genre_alignment": rde_summary.get("genre_alignment", "unknown"),
            "emotion_alignment": bool(emotion_profile),
            "language_alignment": bool(language_info),
            "structure_alignment": bool(structure.get("sections")),
            "zero_pulse_alignment": not bool(zero_pulse_payload.get("has_zero_pulse")),
        }

        # === SAFE DIAGNOSTICS FALLBACK ===
        emotion_matrix = result.get("emotion_matrix", {})
        diagnostics.setdefault("bpm", result.get("bpm", {}))
        tonality_block = diagnostics.get("tonality", {}) if isinstance(diagnostics.get("tonality"), dict) else {}
        if not tonality_block and isinstance(result.get("tonality"), dict):
            tonality_block = dict(result.get("tonality", {}))
        tone_block = result.get("tone") if isinstance(result.get("tone"), dict) else {}
        if tone_block.get("key_hint") and not tonality_block.get("key"):
            tonality_block = {**tonality_block, "key": tone_block.get("key_hint")}
        diagnostics["tonality"] = tonality_block
        diagnostics.setdefault("vocal", result.get("vocal", {}))
        diagnostics.setdefault("instrumentation", result.get("instrumentation", {}))
        diagnostics.setdefault("emotion_matrix", emotion_matrix or {})
        diagnostics.setdefault("sections", result.get("sections", []))
        diagnostics.setdefault("emotion_matrix_source", emotion_matrix.get("version", None))

        result["diagnostics"] = diagnostics

        # =============================================================
        # FANF OUTPUT LAYER (NEW)
        # Builds 4 fields strictly for Gradio interface:
        # 1) style_prompt
        # 2) lyrics_prompt
        # 3) ui_text
        # 4) summary
        # =============================================================

        def _safe(value: Any, default: str = "") -> str:
            return value if isinstance(value, str) and value.strip() else default

        fanf_block = result.get("fanf") if isinstance(result.get("fanf"), dict) else {}
        style_block = result.get("style") if isinstance(result.get("style"), dict) else {}
        instrumentation_block = result.get("instrumentation") if isinstance(result.get("instrumentation"), dict) else {}

        bpm_value = bpm_payload.get("estimate") or bpm_payload.get("flow_estimate") or bpm_payload.get("bpm")
        key_hint = tonality_payload.get("key") or tonality_payload.get("key_hint")
        cf_value = tlp_profile.get("conscious_frequency")
        macro_genre = style_block.get("macro_genre") or style_block.get("genre") or style_block.get("subgenre")
        tone_label = style_block.get("tone") or style_block.get("vibe")
        palette = instrumentation_block.get("palette") if isinstance(instrumentation_block, dict) else None

        style_line_1 = (
            f"[{_safe(macro_genre, 'adaptive style')} | {bpm_value or '120'} BPM | {key_hint or 'N/A'} | CF {cf_value or '0.00'}]"
        )
        style_line_2 = (
            f"[{_safe(tone_label, 'soft vocal tone')}, {', '.join(palette) if palette else 'minimal instrumentation'}]"
        )

        style_prompt = f"{_safe(style_line_1)}\n{_safe(style_line_2)}".strip()

        if not style_prompt:
            style_prompt = (
                "[adaptive minimalistic style | 120 BPM | A minor | A=440 Hz | CF 0.50]\n"
                "[soft male vocal, piano + strings, warm ambiance]"
            )

        lyric_lines: list[str] = []
        # MASTER-PATCH v5.1: Улучшенная логика для section headers
        headers = structure_context.get("section_headers") or structure_context.get("section_metadata") or []
        # Пробуем получить имена секций из SectionParser / structured_hints / commands
        section_names_from_parser = []
        if structure_context.get("sections"):
            # Если есть sections_text с именами
            section_names_from_parser = structure_context.get("sections", [])
        
        # Автогенерация осмысленных имен если headers пустые
        def generate_section_name(idx: int, total: int) -> str:
            """Генерирует осмысленное имя секции на основе позиции и длины."""
            if idx == 0:
                return "Intro"
            elif idx == total - 1:
                return "Outro"
            elif total <= 3:
                return f"Verse {idx}"
            elif idx == 1 or (idx > 1 and idx < total - 1 and idx % 2 == 1):
                return f"Chorus {idx // 2 + 1}" if idx > 1 else "Chorus"
            elif idx == 2 or (idx > 2 and idx < total - 2):
                return f"Verse {(idx - 1) // 2 + 1}"
            elif idx == total - 2:
                return "Bridge"
            else:
                return f"Verse {idx}"
        
        for idx, section in enumerate(sections or []):
            header_label = None
            if idx < len(headers) and isinstance(headers[idx], dict):
                # Используем tag в первую очередь, так как там хранятся правильные имена (Intro, Verse, Chorus и т.д.)
                header_label = headers[idx].get("tag") or headers[idx].get("label") or headers[idx].get("name")
            # Если header_label пустой, пробуем из parser
            if not header_label and idx < len(section_names_from_parser):
                header_label = section_names_from_parser[idx] if isinstance(section_names_from_parser[idx], str) else None
            # Если все еще пусто - автогенерируем осмысленное имя
            if not header_label or header_label == "?":
                header_label = generate_section_name(idx, len(sections or []))
            section_header = header_label
            lyric_lines.append(f"[{section_header}] {section.strip() if isinstance(section, str) else ''}".strip())

        lyrics_prompt = "\n".join(line for line in lyric_lines if line.strip())
        if not lyrics_prompt:
            lyrics_prompt = "[Intro: soft ambience]\n(no lyrical structure detected)"

        ui_text = "\n".join(section for section in sections if isinstance(section, str) and section.strip()) or text
        ui_text = _safe(ui_text)

        summary_parts: list[str] = []
        if tlp_profile:
            summary_parts.append(
                f"[TLP: {tlp_profile.get('truth', 0):.2f}/{tlp_profile.get('love', 0):.2f}/{tlp_profile.get('pain', 0):.2f} | CF {tlp_profile.get('conscious_frequency', 0):.2f}]"
            )
        if rde_summary:
            summary_parts.append(f"[RDE: resonance={rde_summary.get('resonance')}, fracture={rde_summary.get('fracture')}, entropy={rde_summary.get('entropy')}]")
        if macro_genre:
            summary_parts.append(f"[Genre: {macro_genre}]")
        if zero_pulse_payload:
            summary_parts.append(f"[ZeroPulse: {zero_pulse_payload.get('status', zero_pulse_payload.get('has_zero_pulse'))}]")
        if color_wave:
            summary_parts.append(f"[ColorWave: {', '.join(color_wave) if isinstance(color_wave, list) else color_wave}]")
        if diagnostics.get("integrity"):
            summary_parts.append(str(diagnostics.get("integrity")))

        summary = "\n".join(part for part in summary_parts if part).strip()
        if not summary:
            summary = "[TLP: 0/0/0 | CF 0.0]\n[RDE: no rhythm detected]\n[Integrity: undefined]"

        result["fanf"] = {
            **fanf_block,
            "style_prompt": style_prompt,
            "lyrics_prompt": lyrics_prompt,
            "ui_text": ui_text,
            "summary": summary,
        }

        return result

    def _detect_road_narrative_signals(self, text: str, tlp, emotions: dict, sections: list[str]) -> dict:
        """
        MASTER-PATCH v2: Heuristic detector for 'road narrative / dark country rap' profile.

        Signals:
        - burial, death, grave, no name on the stone
        - roads, back road, highway, flyover state
        - chains, gold, weight, karma, reaper, fate
        - high CF, sorrow + determination
        """
        t = text.lower()

        # Use externalized keywords from config
        keywords_road = ROAD_NARRATIVE_KEYWORDS["road"]
        keywords_death = ROAD_NARRATIVE_KEYWORDS["death"]
        keywords_weight = ROAD_NARRATIVE_KEYWORDS["weight"]

        def has_any(words: list[str]) -> bool:
            return any(w in t for w in words)

        road = 1.0 if has_any(keywords_road) else 0.0
        death = 1.0 if has_any(keywords_death) else 0.0
        weight = 1.0 if has_any(keywords_weight) else 0.0

        # Получаем CF из tlp (может быть объект или dict)
        if hasattr(tlp, "conscious_frequency"):
            cf = float(getattr(tlp, "conscious_frequency", 0.0))
        elif isinstance(tlp, dict):
            cf = float(tlp.get("conscious_frequency", tlp.get("cf", 0.0)))
        else:
            cf = 0.0

        sorrow = float(emotions.get("sorrow", 0.0))
        determination = float(emotions.get("determination", 0.0))

        base = (road + death + weight) / 3.0 if (road + death + weight) > 0 else 0.0
        # усиливаем за счёт CF и эмоций (using externalized weights)
        score = base
        score += ALGORITHM_WEIGHTS["road_narrative_cf_weight"] * cf
        score += ALGORITHM_WEIGHTS["road_narrative_sorrow_weight"] * sorrow
        score += ALGORITHM_WEIGHTS["road_narrative_determination_weight"] * determination

        return {
            "score": min(score, 1.0),
            "road": road,
            "death": death,
            "weight": weight,
            "cf": cf,
            "sorrow": sorrow,
            "determination": determination,
            "sections": sections,
        }

    def _adaptive_flow_engine_v2(self, base_bpm: float, emotion_profile: dict, rde: dict, is_epic: bool, is_rage: bool, is_neutral: bool) -> float:
        """
        MASTER-PATCH v6.0: Adaptive Flow Engine v2 (BPM/Flow).
        
        Корректирует BPM на основе режимов (neutral, epic, rage) и RDE.
        
        Args:
            base_bpm: Базовый BPM
            emotion_profile: Профиль эмоций
            rde: RDE метрики
            is_epic: Флаг epic-режима
            is_rage: Флаг rage-режима
            is_neutral: Флаг neutral-режима
            
        Returns:
            Скорректированный BPM
        """
        bpm = float(base_bpm) if base_bpm else 70.0
        
        # Neutral low-emotion → BPM 58–72
        if is_neutral:
            bpm = max(58.0, min(72.0, bpm))
        
        # Epic cinematic без rage → BPM +5–10 от базовой оценки (но не выше 120, если не EDM/rap)
        elif is_epic and not is_rage:
            bpm = min(120.0, bpm + 7.5)  # Среднее между +5 и +10
        
        # Rage → BPM может повышаться сильнее, но только если согласовано с жанром
        elif is_rage:
            # Для rage повышаем BPM, но ограничиваем разумным максимумом
            bpm = min(140.0, bpm + 10.0)
        
        # Учитываем RDE (особенно fracture/entropy)
        if isinstance(rde, dict):
            fracture = float(rde.get("fracture", 0.0) or 0.0)
            entropy = float(rde.get("entropy", 0.0) or 0.0)
            # Высокая fracture/entropy → немного повышаем BPM
            if fracture > 0.3 or entropy > 0.4:
                bpm = min(140.0, bpm + 5.0)
        
        return round(bpm, 1)

    def _is_low_emotion_context(self, tlp, rde) -> bool:
        """
        MASTER-PATCH v3: проверка на низкоэмоциональный контекст.
        """
        from .config import (
            LOW_EMOTION_TLP_PAIN_MAX,
            LOW_EMOTION_RDE_RESONANCE_MAX,
            LOW_EMOTION_RDE_FRACTURE_MAX,
            LOW_EMOTION_RDE_ENTROPY_MAX,
        )
        
        pain = getattr(tlp, "pain", 0.0) if hasattr(tlp, "pain") else (tlp.get("pain", 0.0) if isinstance(tlp, dict) else 0.0)
        resonance = rde.get("resonance", 0.0) if isinstance(rde, dict) else 0.0
        fracture = rde.get("fracture", 0.0) if isinstance(rde, dict) else 0.0
        entropy = rde.get("entropy", 0.0) if isinstance(rde, dict) else 0.0
        
        return (
            pain <= LOW_EMOTION_TLP_PAIN_MAX
            and resonance <= LOW_EMOTION_RDE_RESONANCE_MAX
            and fracture <= LOW_EMOTION_RDE_FRACTURE_MAX
            and entropy <= LOW_EMOTION_RDE_ENTROPY_MAX
        )

    def _smooth_rde_for_low_emotion(self, tlp, rde: dict) -> dict:
        """
        MASTER-PATCH v3:
        Для холодных / наблюдательных текстов RDE должен быть сглажен,
        чтобы не завышать фрактуру и энтропию.
        """
        from .config import (
            LOW_EMOTION_TLP_PAIN_MAX,
            LOW_EMOTION_RDE_RESONANCE_MAX,
            LOW_EMOTION_RDE_FRACTURE_MAX,
        )
        
        if not isinstance(rde, dict):
            return rde
        
        pain = getattr(tlp, "pain", 0.0) if hasattr(tlp, "pain") else (tlp.get("pain", 0.0) if isinstance(tlp, dict) else 0.0)
        resonance = rde.get("resonance", 0.0)
        fracture = rde.get("fracture", 0.0)
        entropy = rde.get("entropy", 0.0)
        
        if (
            pain <= LOW_EMOTION_TLP_PAIN_MAX
            and resonance <= LOW_EMOTION_RDE_RESONANCE_MAX * 2.0
            and fracture <= LOW_EMOTION_RDE_FRACTURE_MAX * 2.0
        ):
            # Use externalized smoothing factors from config
            rde["resonance"] = resonance * ALGORITHM_WEIGHTS["rde_resonance_smoothing"]
            rde["fracture"] = fracture * ALGORITHM_WEIGHTS["rde_fracture_smoothing"]
            # entropy оставляем ближе к исходной, но слегка снижаем
            rde["entropy"] = entropy * ALGORITHM_WEIGHTS["rde_entropy_smoothing"]
        
        return rde

    def _detect_folk_ballad(self, normalized_text: str) -> bool:
        """
        Folk/Ballad semantic detector (legacy, для обратной совместимости).

        Срабатывает при спокойной повествовательной лирике о природе, дороге, ночи, памяти.
        """
        if not normalized_text:
            return False
        
        tokens = normalized_text.lower()
        # Use externalized keywords from config
        folk_keys = FOLK_BALLAD_KEYWORDS_LEGACY
        score = sum(1 for k in folk_keys if k in tokens)
        return score >= 3

    def _is_rage_mode(self, emotion_profile: dict) -> bool:
        """
        MASTER-PATCH v6.0: Rage Filter v2 (только anger/tension).
        
        Определяет, активен ли rage-режим на основе anger и tension.
        НЕ использует epic как триггер rage.
        
        Args:
            emotion_profile: Профиль эмоций (dict)
            
        Returns:
            True если rage-режим активен, иначе False
        """
        if not isinstance(emotion_profile, dict):
            return False
        
        anger = float(emotion_profile.get("anger", 0.0) or 0.0)
        tension = float(emotion_profile.get("tension", 0.0) or 0.0)
        
        # Основные триггеры (using externalized thresholds from config)
        return anger > ALGORITHM_WEIGHTS["rage_anger_threshold"] or \
               tension > ALGORITHM_WEIGHTS["rage_tension_threshold"]

    def _is_epic_mode(self, emotion_profile: dict) -> bool:
        """
        MASTER-PATCH v6.0: Epic-mode (cinematic override).
        
        Определяет, активен ли epic-режим на основе epic эмоции.
        Epic-режим НЕ должен совпадать с rage-режимом.
        
        Args:
            emotion_profile: Профиль эмоций (dict)
            
        Returns:
            True если epic-режим активен, иначе False
        """
        if not isinstance(emotion_profile, dict):
            return False
        
        epic = float(emotion_profile.get("epic", 0.0) or 0.0)
        
        # Epic threshold (using externalized threshold from config) и при этом НЕ rage
        if epic > ALGORITHM_WEIGHTS["epic_threshold"]:
            return not self._is_rage_mode(emotion_profile)
        
        return False

    def _detect_folk_ballad_v2(self, normalized_text: str, emotion_profile: dict, genre_candidates: dict = None) -> dict | None:
        """
        MASTER-PATCH v6.0: Folk Ballad Mode v2 (ослабленный).

        Расширенный детектор folk-баллад с проверкой эмоций и отсутствия городских/электронных подсказок.
        
        Args:
            normalized_text: Нормализованный текст для анализа
            emotion_profile: Профиль эмоций (dict)
            genre_candidates: Словарь с кандидатами жанров (опционально)
            
        Returns:
            dict с "genre" и "confidence" или None, если условия не соблюдены
        """
        if not normalized_text:
            return None
        
        # Расширенный список folk-признаков
        # Use externalized keywords from config
        folk_keywords = FOLK_BALLAD_KEYWORDS
        
        text_lower = normalized_text.lower()
        # Подсчет совпадений (минимум 3 разных токена)
        matches = [kw for kw in folk_keywords if kw in text_lower]
        unique_matches = len(set(matches))
        
        if unique_matches < 3:
            return None
        
        # Проверка эмоций
        if not isinstance(emotion_profile, dict):
            return None
        
        anger = float(emotion_profile.get("anger", 0.0) or 0.0)
        tension = float(emotion_profile.get("tension", 0.0) or 0.0)
        epic = float(emotion_profile.get("epic", 0.0) or 0.0)
        
        if anger >= 0.15 or tension >= 0.15 or epic >= 0.35:
            return None
        
        # Проверка отсутствия городских/электронных/хип-хоп подсказок
        urban_electronic_keywords = [
            "rap", "drill", "trap", "808", "club", "EDM", "techno", "rave", "bass", "beat", "MC",
            "рэп", "бит", "клуб", "техно", "хаус", "бас", "электро", "диджей"
        ]
        
        has_urban_signals = any(kw in text_lower for kw in urban_electronic_keywords)
        if has_urban_signals:
            return None
        
        # Вычисление confidence на основе количества совпадений
        confidence = min(0.85, 0.5 + (unique_matches - 3) * 0.1)
        
        return {
            "genre": "folk narrative ballad",
            "confidence": confidence
        }

    def _apply_neutral_mood_correction(self, tlp, rde, mood: str, emotion_profile: dict = None, style_payload: dict = None) -> str:
        """
        MASTER-PATCH v3:
        Если текст низкоэмоциональный, переводим mood в нейтральный режим.
        """
        from .config import (
            NEUTRAL_MOOD,
            LOW_EMOTION_TLP_PAIN_MAX,
            LOW_EMOTION_TLP_TRUTH_MIN,
            LOW_EMOTION_RDE_RESONANCE_MAX,
            LOW_EMOTION_RDE_FRACTURE_MAX,
            LOW_EMOTION_RDE_ENTROPY_MAX,
        )
        
        original_mood = mood
        
        pain = getattr(tlp, "pain", 0.0) if hasattr(tlp, "pain") else (tlp.get("pain", 0.0) if isinstance(tlp, dict) else 0.0)
        truth = getattr(tlp, "truth", 0.0) if hasattr(tlp, "truth") else (tlp.get("truth", 0.0) if isinstance(tlp, dict) else 0.0)
        resonance = rde.get("resonance", 0.0) if isinstance(rde, dict) else 0.0
        fracture = rde.get("fracture", 0.0) if isinstance(rde, dict) else 0.0
        entropy = rde.get("entropy", 0.0) if isinstance(rde, dict) else 0.0
        
        # Disable neutral mode for nostalgic texts (check before applying neutral correction)
        if emotion_profile and isinstance(emotion_profile, dict):
            if 'nostalgia' in emotion_profile and emotion_profile['nostalgia'] > 0.20:
                # Disable neutral mode for nostalgic texts
                if style_payload and isinstance(style_payload, dict):
                    style_payload['_neutral_mode'] = False
                return original_mood
        
        # Условие низкоэмоционального / наблюдательного текста
        if (
            pain <= LOW_EMOTION_TLP_PAIN_MAX
            and truth >= LOW_EMOTION_TLP_TRUTH_MIN
            and resonance <= LOW_EMOTION_RDE_RESONANCE_MAX
            and fracture <= LOW_EMOTION_RDE_FRACTURE_MAX
            and entropy <= LOW_EMOTION_RDE_ENTROPY_MAX
        ):
            # Если mood выставлен как melancholic / sad / soft-lyric, корректируем
            lowered = (mood or "").lower()
            if any(x in lowered for x in ("melancholic", "sad", "sorrow", "lyric")):
                # MASTER-PATCH v3.2: помечаем нейтральный режим
                # style_payload будет установлен в месте вызова
                return NEUTRAL_MOOD
        
        return mood

    def _apply_road_narrative_overrides(self, text: str, tlp, emotions: dict,
                                        bpm_block: dict, sections: list[str],
                                        result: dict) -> None:
        """
        MASTER-PATCH v2: Post-processing overrides for 'road narrative / dark country rap ballad'.

        Если score достаточно высок, немного корректируем:
        - genre / style
        - bpm (к flow_estimate)
        - color_wave
        - instrumentation
        - vocal_instructions (мягко, если структура уже есть)
        """
        # Безопасная обработка emotions - может быть dict или содержать "profile"
        if isinstance(emotions, dict) and "profile" in emotions:
            emotion_profile = emotions.get("profile", {})
        elif isinstance(emotions, dict):
            emotion_profile = emotions
        else:
            emotion_profile = {}
        
        signals = self._detect_road_narrative_signals(text, tlp, emotion_profile, sections)
        score = signals.get("score", 0.0)

        if score < 0.45:
            # сигнал слабый — ничего не делаем
            return

        style = result.setdefault("style", {})
        # MASTER-PATCH v5.1: 1) Genre / style - мягкая логика
        old_genre = style.get("genre")
        # Проверяем наличие пользовательского override
        has_user_override = (
            style.get("_genre_locked")  # Специальный флаг заморозки жанра
            or (old_genre and old_genre not in ("lyrical_song", "auto", "unknown", "", None, "experimental"))
        )
        # Применяем road narrative genre только если:
        # - нет пользовательского override
        # - текущий жанр пустой, неизвестный или fallback
        # - текст прошел road/folk/rap фильтр (score >= 0.45 уже проверен выше)
        if not has_user_override and (not old_genre or old_genre in ("lyrical_song", "auto", "unknown", "", None, "experimental")):
            style["genre"] = "dark country rap ballad"
            # Apply hybrid instrumentation overrides for road narrative
            self._apply_hybrid_instrumentation_overrides(result)

        # 2) BPM: смещаемся к flow_estimate если он выше baseline
        est = bpm_block.get("estimate") or bpm_block.get("bpm") or style.get("bpm")
        flow = bpm_block.get("flow_estimate") or bpm_block.get("flow") or est
        if est and flow:
            # сглаживаем в сторону flow
            new_bpm = int(round((est + 2 * flow) / 3.0))
            style["bpm"] = new_bpm
            bpm_block["estimate"] = new_bpm

        # 3) Color wave — ночь, дорога, огонь мостов
        # Не трогаем, если уже установлен явный цветовой профиль пользователем.
        color_wave = style.get("color_wave")
        # GLOBAL PATCH: расширенная проверка для защиты road narrative color wave
        if not color_wave or color_wave in (["#FFFFFF", "#FFC0CB"], ['#3E5C82', '#FFC0CB'], ['#3E5C82', '#8A2BE2']):
            style["color_wave"] = ["#1F2A3A", "#C58B3A"]  # deep night blue + burnt amber
            style["_color_locked"] = True  # Устанавливаем флаг блокировки

        # 4) Mood
        if style.get("mood") in (None, "melancholic"):
            style["mood"] = "sorrowful, determined, road_narrative"

        # 5) Instrumentation
        instr = style.setdefault("instrumentation", [])
        if isinstance(instr, str):
            # превратим в список
            instr = [x.strip() for x in instr.split(",") if x.strip()]
        # базовый road-набор
        road_set = [
            "acoustic guitar",
            "slide guitar",
            "dusty snare",
            "low warm bass",
            "subtle organ pad",
            "ambient road noise"
        ]
        for item in road_set:
            if item not in instr:
                instr.append(item)
        style["instrumentation"] = instr

        # 6) Vocal instructions — мягко дополняем, не ломая существующую структуру
        voc = style.setdefault("vocal_instructions", {})
        def ensure(sec: str, line: str):
            if sec not in voc:
                voc[sec] = line

        ensure("intro", "low, intimate spoken voice, almost whisper, close to the mic")
        ensure("verse", "rap-like storytelling, calm but heavy, low register, clear diction")
        ensure("chorus", "melodic gritty singing with chest voice and slight cracks on key phrases")
        ensure("bridge", "soft, prayer-like delivery with more reverb and emotional tension")
        ensure("outro", "fading melodic mantra with echoes and ad-libs in the background")

    @staticmethod
    def merge_sections_smart(sections: list, emotion_profile: dict = None) -> list:
        """
        MASTER-PATCH v6.0: Section Merge Mode (SM²).
        
        Объединяет соседние секции, если они очень короткие и одного типа.
        
        Args:
            sections: Список секций (строки)
            emotion_profile: Профиль эмоций (опционально)
            
        Returns:
            Объединенный список секций
        """
        if not sections or len(sections) <= 1:
            return sections
        
        # Если секций слишком много (> 20-25) при коротком тексте
        total_length = sum(len(str(s)) for s in sections)
        avg_length = total_length / len(sections) if sections else 0
        
        if len(sections) > 20 and avg_length < 50:  # Много коротких секций
            merged = []
            i = 0
            while i < len(sections):
                current = sections[i]
                # Пытаемся объединить с соседними, если они очень короткие
                if i + 1 < len(sections):
                    next_section = sections[i + 1]
                    # Объединяем если обе секции очень короткие (1-2 строки)
                    if len(str(current).split('\n')) <= 2 and len(str(next_section).split('\n')) <= 2:
                        merged.append(str(current) + "\n" + str(next_section))
                        i += 2
                        continue
                merged.append(current)
                i += 1
            return merged
        
        return sections

    class HybridGenreEngine:
        """
        MASTER-PATCH v6.0: Hybrid Genre Engine (HGE).
        
        Собирает жанровые сигналы из различных источников и формирует гибридные жанры.
        """
        
        @staticmethod
        def collect_signals(
            domain_genre: str | None,
            folk_ballad_candidate: dict | None,
            road_narrative_score: float,
            emotion_profile: dict,
            feature_map: dict,
            legacy_genre: str | None,
            semantic_hints: dict,
            commands: list,
        ) -> dict:
            """
            Собирает все жанровые сигналы с весами.
            
            Returns:
                dict с ключами: сигналы (dict жанр -> вес), общий вес
            """
            signals = {}
            
            # 1. Domain genre (основной сигнал)
            if domain_genre and domain_genre not in ("unknown", "auto", ""):
                signals[domain_genre] = signals.get(domain_genre, 0.0) + 0.4
            
            # 2. Folk ballad candidate
            if folk_ballad_candidate and isinstance(folk_ballad_candidate, dict):
                genre = folk_ballad_candidate.get("genre")
                confidence = folk_ballad_candidate.get("confidence", 0.5)
                if genre:
                    signals[genre] = signals.get(genre, 0.0) + confidence * 0.3
            
            # 3. Road narrative
            if road_narrative_score > 0.45:
                signals["dark country rap ballad"] = signals.get("dark country rap ballad", 0.0) + road_narrative_score * 0.3
            
            # 4. Hiphop/rap паттерны из feature_map
            hiphop_factor = feature_map.get("hiphop_factor", 0.0)
            if hiphop_factor > 0.2:
                signals["hiphop"] = signals.get("hiphop", 0.0) + hiphop_factor * 0.25
            
            # 5. Electronic/EDM паттерны
            edm_factor = feature_map.get("edm_factor", 0.0)
            if edm_factor > 0.2:
                signals["edm"] = signals.get("edm", 0.0) + edm_factor * 0.25
            
            # 6. Cinematic/orchestral паттерны
            cinematic_factor = feature_map.get("cinematic_factor", 0.0)
            epic = float(emotion_profile.get("epic", 0.0) or 0.0) if isinstance(emotion_profile, dict) else 0.0
            if cinematic_factor > 0.2 or epic > 0.35:
                signals["cinematic"] = signals.get("cinematic", 0.0) + max(cinematic_factor, epic) * 0.25
            
            # 7. Legacy genre (валидный)
            if legacy_genre and legacy_genre not in ("auto", "unknown", ""):
                signals[legacy_genre] = signals.get(legacy_genre, 0.0) + 0.2
            
            # 8. Semantic hints / overrides (учитываем, но не форсируем)
            hint_genre = semantic_hints.get("style", {}).get("genre") if isinstance(semantic_hints, dict) else None
            if hint_genre and hint_genre not in ("auto", "unknown", ""):
                signals[hint_genre] = signals.get(hint_genre, 0.0) + 0.15
            
            # 9. Commands
            for cmd in commands or []:
                if cmd.get("type") == "genre" and cmd.get("value"):
                    cmd_genre = cmd.get("value")
                    if cmd_genre not in ("auto", "unknown", ""):
                        signals[cmd_genre] = signals.get(cmd_genre, 0.0) + 0.1
            
            total_weight = sum(signals.values())
            return {"signals": signals, "total_weight": total_weight}
        
        @staticmethod
        def resolve_hybrid_genre(signals_data: dict, user_override: str | None = None) -> str | None:
            """
            Разрешает гибридный жанр на основе собранных сигналов.
            
            Args:
                signals_data: Результат collect_signals
                user_override: Явный жанр пользователя (если есть)
            
            Returns:
                final_genre (str) или None
            """
            if user_override and user_override not in ("auto", "unknown", ""):
                # Уважаем user override
                return user_override
            
            signals = signals_data.get("signals", {})
            if not signals:
                return None
            
            # Сортируем по весу
            sorted_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)
            
            # Если один сигнал явно доминирует (вес > 0.5 и в 2+ раза больше следующего)
            if len(sorted_signals) == 1:
                return sorted_signals[0][0]
            
            if len(sorted_signals) >= 2:
                top_weight = sorted_signals[0][1]
                second_weight = sorted_signals[1][1]
                
                if top_weight > 0.5 and top_weight >= second_weight * 2.0:
                    # Моно-жанр
                    return sorted_signals[0][0]
                
                # Гибрид: берем топ-2 или топ-3 с близкими весами
                top_genres = []
                for genre, weight in sorted_signals[:3]:
                    if weight > 0.15:  # Минимальный порог
                        top_genres.append((genre, weight))
                
                if len(top_genres) >= 2:
                    # Формируем гибридный тег
                    genre_names = [g[0] for g in top_genres]
                    # Убираем дубликаты и сортируем по весу
                    unique_genres = []
                    seen = set()
                    for g in genre_names:
                        if g not in seen:
                            unique_genres.append(g)
                            seen.add(g)
                    
                    if len(unique_genres) >= 2:
                        return " ".join(unique_genres[:2]) + " hybrid"
                    elif len(unique_genres) == 1:
                        return unique_genres[0]
                elif len(top_genres) == 1:
                    return top_genres[0][0]
            
            # If no hybrid genre resolved, return None cleanly
            return None
    
    # --- MOVED: CLEANED AND RESTORED HYBRID-INSTRUMENTATION LOGIC ---
    def _apply_hybrid_instrumentation_overrides(self, result: dict) -> None:
        """
        Former unreachable block from resolve_hybrid_genre().
        Restored as a separate safe function.
        Applies road-narrative instrumentation adjustments.
        """
        instrumentation = result.setdefault("instrumentation", {})
        selection = instrumentation.setdefault("selection", {})
        palette = selection.get("palette", [])
        selected = selection.get("selected", [])
        
        # Преобразуем в списки если нужно
        if isinstance(palette, str):
            palette = [x.strip() for x in palette.split(",") if x.strip()]
        if isinstance(selected, str):
            selected = [x.strip() for x in selected.split(",") if x.strip()]
        
        # Palette corrections - добавляем road-инструменты
        road_instruments = [
            "acoustic guitar",
            "slide guitar",
            "dusty snare",
            "low warm bass",
            "subtle organ pad",
            "ambient road noise"
        ]
        palette_set = set(palette)
        for item in road_instruments:
            palette_set.add(item)
        palette = list(palette_set)
        
        # Если selected слишком "киношный", подтолкнуть к гитарному
        if "grand piano" in selected and "acoustic guitar" not in selected:
            selected.append("acoustic guitar")
        if "acoustic guitar" not in selected and len(selected) < 5:
            selected.append("acoustic guitar")
        
        selection["palette"] = palette
        selection["selected"] = selected
        instrumentation["selection"] = selection
        result["instrumentation"] = instrumentation
        # End hybrid instrumentation override

    def _extract_engines(self, engines: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Извлекает движки из словаря engines с fallback.
        
        Args:
            engines: Словарь движков или None
            
        Returns:
            Словарь с извлеченными движками
        """
        if engines:
            return {
                "text_engine": engines.get("text_engine"),
                "emotion_engine": engines.get("emotion_engine"),
                "bpm_engine": engines.get("bpm_engine"),
                "tlp_engine": engines.get("tlp_engine"),
                "dynamic_emotion_engine": engines.get("dynamic_emotion_engine"),
                "section_intelligence": engines.get("section_intelligence"),
                "vocal_engine": engines.get("vocal_engine"),
                "breathing_engine": engines.get("breathing_engine"),
                "color_emotion_engine": engines.get("color_emotion_engine"),
                "genre_matrix": engines.get("genre_matrix"),
            }
        else:
            # Fallback если engines не передан
            from .logical_engines import TextStructureEngine
            return {
                "text_engine": TextStructureEngine(),
                "emotion_engine": None,
                "bpm_engine": None,
                "tlp_engine": None,
                "dynamic_emotion_engine": None,
                "section_intelligence": None,
                "vocal_engine": None,
                "breathing_engine": None,
                "color_emotion_engine": None,
                "genre_matrix": None,
            }

    def _build_structure_headers(
        self,
        text_engine: Any,
        sections: list[str],
        structure_context: Dict[str, Any],
    ) -> list[Dict[str, Any]]:
        """
        FIX: completely disable fallback structure reconstruction.
        Always trust SectionParser.
        """
        # Сначала пытаемся получить из structure_context (приоритет)
        structure = structure_context.get("section_headers") or structure_context.get("section_metadata") or []
        
        # Если структура есть и это список словарей с тегами - возвращаем как есть
        if structure and isinstance(structure, list) and len(structure) > 0:
            # Проверяем, что это не пустые словари
            if any(meta.get("tag") for meta in structure if isinstance(meta, dict)):
                return structure
        
        # Если структуры нет в context, пытаемся получить из text_engine (SectionParser)
        # Это основной источник метаданных после отключения fallback
        if text_engine and hasattr(text_engine, 'section_metadata'):
            try:
                engine_metadata = text_engine.section_metadata()
                if engine_metadata and isinstance(engine_metadata, list) and len(engine_metadata) > 0:
                    # Проверяем, что это не пустые словари и есть теги
                    valid_metadata = [meta for meta in engine_metadata if isinstance(meta, dict) and meta.get("tag")]
                    if valid_metadata:
                        return valid_metadata
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(f"Ошибка при получении section_metadata из text_engine: {e}")
                pass
        
        # Если ничего не найдено - возвращаем пустой список (не создаем fallback)
        return []

    def _guess_vocal_from_text(self, text: str) -> str:
        """
        MASTER-PATCH: Умный fallback для определения вокальной техники по тексту.
        Вместо постоянного "tenor" пытается определить тип вокала по ключевым словам.
        """
        if not text or not isinstance(text, str):
            return "mixed"
        
        t = text.lower()
        
        # Whisper / spoken
        if any(w in t for w in ["whisper", "(whisper", "(spoken", "шепот", "шёпот", "whispered"]):
            return "whisper"
        
        # Scream / shout
        if any(w in t for w in ["scream", "крик", "shout", "yell", "screaming"]):
            return "scream"
        
        # Rap / flow
        if any(w in t for w in ["rap", "flow", "рэп", "rapping", "bars"]):
            return "rap"
        
        # Soft / breathy
        if any(w in t for w in ["soft", "breathy", "gentle", "тихий", "нежный"]):
            return "breathy"
        
        # Intense / belting
        if any(w in t for w in ["intense", "powerful", "strong", "belting", "мощный"]):
            return "belting"
        
        # По умолчанию - mixed (не tenor)
        return "mixed"

    def _build_genre_feature_map(
        self,
        text: str,
        bpm_payload: Dict[str, Any],
        emotion_profile: Dict[str, float],
        emotion_payload: Dict[str, Any],
        emotion_curve: list[float],
        vocal_payload: Dict[str, Any],
        meaning_payload: Dict[str, Any],
        tonality_payload: Dict[str, Any],
        tlp_profile: Dict[str, float],
        section_intel_payload: Dict[str, Any],
        color_profile: Dict[str, Any],
        instrumentation_payload: Dict[str, Any],
        commands: list[Dict[str, Any]],
        semantic_hints: Dict[str, Any],
        sections: list[str],
    ) -> Dict[str, Any]:
        """
        Строит feature map для определения жанров.
        
        Это один из самых больших блоков в _backend_analyze, выделен для уменьшения сложности.
        
        Args:
            text: Исходный текст
            bpm_payload: Данные BPM
            emotion_profile: Профиль эмоций
            emotion_payload: Полные данные эмоций
            emotion_curve: Кривая эмоций
            vocal_payload: Данные вокала
            meaning_payload: Данные meaning velocity
            tonality_payload: Данные тональности
            tlp_profile: Профиль TLP
            section_intel_payload: Данные section intelligence
            color_profile: Профиль цветов
            instrumentation_payload: Данные инструментов
            commands: Список команд
            semantic_hints: Семантические подсказки
            sections: Список секций
            
        Returns:
            Словарь с feature map для genre_weights
        """
        def _clamp(value: float) -> float:
            try:
                return round(max(0.0, min(1.0, float(value))), 3)
            except (TypeError, ValueError):
                return 0.0

        bpm_value = bpm_payload.get("estimate") or 0.0
        avg_intensity = vocal_payload.get("average_intensity", 0.0) or 0.0
        conflict_value = emotion_payload.get("conflict", {}).get("conflict", 0.0) or 0.0
        semantic_aggression = _clamp(conflict_value + emotion_profile.get("anger", 0.0) * 0.4)
        power_vector = _clamp((bpm_value / 180.0) + avg_intensity * 0.3)
        bpm_curve_values = bpm_payload.get("curve") or []
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
            "lyric", "poem", "ode", "sonnet", "haiku", "ballad", "serenade", "lullaby", "lyrical",
            "серд", "люб", "луна", "звезд", "тиши", "ветер", "лепест", "шеп", "сон",
            "dream", "soul", "moon", "star", "ocean", "tear", "rose",
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
            "synth", "pad", "edm", "electro", "techno", "trance", "house", "club", "808",
            "fm", "digital", "chip", "glitch", "modular", "drum machine",
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
            "comedy", "comic", "funny", "humor", "humour", "parody", "satire", "joke",
            "lol", "lmao", "haha", "rofl",
            "юмор", "юморист", "шутк", "смешн", "ирони", "сарказ", "парод", "анекдот", "комед", "угар",
        )
        comedy_hits = _token_hits(comedy_keywords)
        comedy_blob_hits = sum(1 for keyword in comedy_keywords if keyword in command_blob or keyword in hint_blob)
        laughter_keywords = ("haha", "ahah", "ahaha", "хаха", "ахаха")
        laughter_hits = sum(1 for keyword in laughter_keywords if keyword in text_lower)
        comedy_factor = _clamp((comedy_hits / line_count) * 0.6 + comedy_blob_hits * 0.15 + laughter_hits * 0.1)

        gothic_keywords = ("gothic", "готик", "dark", "тень", "мрак", "ноч", "grave", "cathedral")
        gothic_hits = _token_hits(gothic_keywords)
        # Исправление: минорная тональность не должна автоматически означать готику
        # Готика определяется только при наличии готических слов ИЛИ очень высоком pain + миноре
        gothic_from_keywords = gothic_hits / max(line_count, 1)
        gothic_from_minor = harmonic_lumen_minor * 0.1  # Снижено с 0.3 до 0.1
        gothic_factor = _clamp(gothic_from_keywords + gothic_from_minor)

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

        # Добавляем цветовую информацию для genre_weights
        color_profile_for_features = {}
        dominant_emotion_name = None
        if color_profile:
            color_profile_for_features = {
                "primary_color": color_profile.get("primary_color", ""),
                "accent_color": color_profile.get("accent_color", ""),
            }
            # Определяем доминирующую эмоцию по цвету
            if color_profile.get("primary_color"):
                from .color_engine_adapter import EMOTION_COLOR_MAP
                primary_color = color_profile.get("primary_color", "")
                for emotion, colors in EMOTION_COLOR_MAP.items():
                    if primary_color in colors:
                        dominant_emotion_name = emotion
                        break
        
        # Если не нашли по цвету, используем доминирующую эмоцию из профиля
        if not dominant_emotion_name and emotion_profile:
            try:
                numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
                if numeric_profile:
                    dominant_emotion_name = max(numeric_profile, key=numeric_profile.get)
            except (ValueError, TypeError, KeyError):
                pass
        
        return {
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
            "color_profile": color_profile_for_features,
            "dominant_emotion": dominant_emotion_name or "",
        }

    def _finalize_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Получаем compiler из engine_bundle
        compiler = None
        if hasattr(self, '_engine_bundle') and self._engine_bundle:
            compiler = self._engine_bundle.get("compiler")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сохраняем mood и color_wave ДО вызова compiler
        # Это гарантирует, что они не будут потеряны при merge_all_layers
        style_from_payload = payload.get("style", {})
        saved_mood = style_from_payload.get("mood") if isinstance(style_from_payload, dict) else None
        saved_color_wave = style_from_payload.get("color_wave") if isinstance(style_from_payload, dict) else None
        
        if compiler:
            merged = compiler.merge_all_layers(payload)
            merged["structure"] = compiler.generate_final_structure(payload)
            merged["prompt"] = compiler.generate_final_prompt(payload)
            merged["annotations"] = compiler.generate_final_annotations(payload)
            merged["consistency"] = compiler.consistency_check(payload)
        else:
            # Fallback if compiler is not available
            merged = payload.copy()
        merged["commands"] = payload.get("commands", {})
        
        # MASTER-PATCH v5.1: Восстанавливаем mood, color_wave И genre после compiler
        # Создаем style блок, явно включая mood, color_wave и genre
        # Защита от типовых ошибок: проверяем что style_from_merged - dict
        style_from_merged = merged.get("style", {})
        if not isinstance(style_from_merged, dict):
            # Если пришла строка или другой тип - аккуратно оборачиваем в dict
            if isinstance(style_from_merged, str):
                # Пропускаем merge, чтобы не завалить пайплайн
                style_from_merged = {}
            else:
                style_from_merged = {}
        
        # ЯВНО сохраняем mood, color_wave И genre (приоритет из payload/merged)
        # Это критично, так как compiler.merge_all_layers() может их потерять
        if saved_mood:
            # MASTER-PATCH v4.0: защищаем исправленный mood от нормализации
            # Если mood уже был исправлен (например, Rage-mode), не применяем нейтральную коррекцию
            if style_from_merged.get("_mood_corrected"):
                # Mood уже исправлен (Rage-mode или другой override) - не перезаписываем
                style_from_merged["mood"] = saved_mood
            else:
                # MASTER-PATCH v3: применяем коррекцию нейтрального mood
                tlp = payload.get("tlp") or payload.get("legacy", {}).get("tlp")
                rde = payload.get("rde") or payload.get("legacy", {}).get("rde") or {}
                emotion_profile = payload.get("emotions", {}).get("profile") or payload.get("emotion", {}).get("profile") or {}
                corrected_mood = self._apply_neutral_mood_correction(tlp, rde, saved_mood, emotion_profile=emotion_profile, style_payload=style_from_merged)
                style_from_merged["mood"] = corrected_mood
                # MASTER-PATCH v3.1: помечаем mood как исправленный
                style_from_merged["_mood_corrected"] = True
                # MASTER-PATCH v3.2: помечаем нейтральный режим, если mood был исправлен
                if corrected_mood != saved_mood:
                    style_from_merged["_neutral_mode"] = True
        if saved_color_wave:
            style_from_merged["color_wave"] = saved_color_wave
        
        # MASTER-PATCH v2: Защищаем genre от перезаписи, если он был установлен в _apply_road_narrative_overrides
        # Проверяем, не был ли genre установлен в merged (например, "dark country rap ballad")
        saved_genre = style_from_merged.get("genre")
        if saved_genre and saved_genre not in ("lyrical_song", "auto", "unknown", "", None):
            # Genre уже установлен (например, "dark country rap ballad") - не перезаписываем
            pass
        
        # MASTER-PATCH v5.1: Обновляем остальные поля из payload["style"], защищая mood, color_wave и genre
        # Защита от типовых ошибок: проверяем что style_from_payload - dict
        if isinstance(style_from_payload, dict):
            for key, value in style_from_payload.items():
                # Пропускаем mood, color_wave и genre, если они уже установлены выше
                if key == "genre" and saved_genre and saved_genre not in ("lyrical_song", "auto", "unknown", "", None):
                    # Не перезаписываем genre, если он уже установлен в merged (например, "dark country rap ballad")
                    continue
                elif key not in ("mood", "color_wave", "genre"):
                    style_from_merged[key] = value
                elif key == "genre" and not saved_genre:
                    # Если genre не был установлен в merged, используем из payload
                    style_from_merged[key] = value
        elif style_from_payload:
            # Если style_from_payload не dict, но не None - пропускаем merge, чтобы не завалить пайплайн
            pass
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если mood и color_wave все еще отсутствуют,
        # пытаемся взять их из других источников
        if not style_from_merged.get("mood") and not style_from_merged.get("color_wave"):
            # Пробуем взять из merged напрямую (на случай, если они там есть)
            if isinstance(merged.get("style"), dict):
                merged_style = merged.get("style")
                if merged_style.get("mood"):
                    style_from_merged["mood"] = merged_style.get("mood")
                if merged_style.get("color_wave"):
                    style_from_merged["color_wave"] = merged_style.get("color_wave")
        
        merged["style"] = style_from_merged
        
        # ============================================================
        # MASTER-PATCH v5.1 — Color & Mood Protection Layer (с защитой от типовых ошибок)
        # ============================================================
        out_style = merged.get("style", {})
        if not isinstance(out_style, dict):
            # Защита от типовых ошибок: если style не dict, создаем пустой dict
            if isinstance(out_style, str):
                # Пропускаем merge, чтобы не завалить пайплайн
                out_style = {}
            else:
                out_style = {}
            merged["style"] = out_style
        
        # 1) Protect mood if corrected
        if out_style.get("_mood_corrected"):
            pass  # do nothing — do not overwrite mood
        else:
            # no-op, existing logic continues
            pass
        
        # 2) Protect color_wave from overwrites further in the pipeline
        if "color_wave" in out_style and "_color_locked" not in out_style:
            # Automatically lock color to prevent any fallback or emotion overrides
            out_style["_color_locked"] = True
        
        # 3) If locked — forbid rewriting color_wave
        if out_style.get("_color_locked"):
            # color is frozen
            pass
        else:
            # allow color_engine to assign color later
            pass
        
        # Legacy protection for road narrative color wave
        if isinstance(out_style, dict) and "color_wave" in out_style:
            # защищаем override: ['#1F2A3A', '#C58B3A']
            cw = out_style["color_wave"]
            if isinstance(cw, list) and cw == ["#1F2A3A", "#C58B3A"]:
                out_style["_color_locked"] = True
        
        merged["zero_pulse"] = payload.get("zero_pulse", {})
        merged["bpm"] = payload.get("bpm", {})
        merged["semantic_hints"] = payload.get("semantic_hints", {})
        merged["phrase_packets"] = payload.get("phrase_packets", [])
        merged["auto_context"] = payload.get("auto_context", {})
        merged["instrument_dynamics"] = payload.get("instrument_dynamics", {})
        merged["tlp"] = payload.get("tlp", {})
        merged["suno_annotations"] = payload.get("suno_annotations", [])
        merged["suno_annotation"] = payload.get("suno_annotation")
        merged["symbiosis"] = payload.get("symbiosis", {})
        merged["override_debug"] = payload.get("override_debug", {})
        merged["language"] = payload.get("language", payload.get("auto_context", {}).get("language"))
        merged["rde_summary"] = payload.get("rde_summary", {})
        merged["rde"] = payload.get("rde", {})
        merged["lyrics"] = payload.get("lyrics", {})
        merged["genre_analysis"] = payload.get("genre_analysis", {})
        merged["fanf"] = payload.get("fanf", {})
        merged["emotion_matrix"] = payload.get("emotion_matrix", {})
        merged["style_prompt"] = payload.get("style_prompt")
        merged["summary"] = payload.get("style", {}).get("prompt") or payload.get("summary") or ""
        merged["section_emotions"] = payload.get("section_emotions", [])
        merged["emotion"] = payload.get("emotion", {})
        merged["tonality"] = payload.get("tonality", {})
        merged["vocal"] = payload.get("vocal", {})
        merged["emotion_curve"] = payload.get("emotion_curve", {})
        merged["tone_profile"] = payload.get("tone_profile", {})
        # Добавляем блок tone для консистентности (объединяем tone_profile и tonality)
        tone_profile = payload.get("tone_profile", {})
        tonality = payload.get("tonality", {})
        if tone_profile:
            merged["tone"] = dict(tone_profile)
            # Дополняем данными из tonality если их нет в tone_profile
            if tonality.get("key") and not merged["tone"].get("key"):
                merged["tone"]["key"] = tonality.get("key")
            if tonality.get("mode") and not merged["tone"].get("mode"):
                merged["tone"]["mode"] = tonality.get("mode")
        elif tonality:
            merged["tone"] = dict(tonality)
        else:
            merged["tone"] = {}
        merged["diagnostics"] = payload.get("diagnostics", {})
        merged.pop("_overrides_applied", None)
        return merged

    # === FANF v8.1 Output Builder ===
    def build_fanf_output(
        self,
        text: str,
        style: Dict[str, Any],
        lyrics: Dict[str, Any],
        diagnostics: Dict[str, Any],
    ) -> Dict[str, Any]:

        # Extract structured blocks
        engines = diagnostics.get("engines", {})
        summary_blocks = diagnostics.get("summary_blocks", {})
        consistency = diagnostics.get("consistency", {})
        meta = diagnostics.get("meta", {})

        bpm = engines.get("bpm")
        tone = engines.get("tone")
        tlp = engines.get("tlp")
        genre = engines.get("genre")
        freq = engines.get("frequency")

        # --- STYLE PROMPT ---------------------------------------------------
        style_prompt = [
            f"[GENRE: {style.get('genre', 'adaptive')}]",
            f"[MOOD: {style.get('mood', 'neutral')}]",
            f"[BPM: {bpm}]",
        ]

        if tone:
            key_str = tone.get("key_label") or tone.get("key") or "Unknown"
            style_prompt.append(f"[KEY: {key_str}]")

        if tlp:
            cf = tlp.get("conscious_frequency") or 0
            style_prompt.append(f"[CF: {cf:.3f}]")

        if genre:
            style_prompt.append(f"[GENRE_UNIVERSE: {genre}]")

        if freq:
            style_prompt.append(f"[FREQ: {freq}]")

        style_prompt_str = " ".join(style_prompt)

        # --- LYRICS PROMPT --------------------------------------------------
        lyrics_prompt_lines = []
        sections_list = lyrics.get("sections", [])
        # Fallback: если sections пустые, создаем базовую структуру
        if not sections_list:
            # Используем текст как одну секцию Verse
            text_lines = [line.strip() for line in text.split("\n") if line.strip()]
            if text_lines:
                sections_list = [{
                    "name": "Verse",
                    "tag": "Verse",
                    "mood": "neutral",
                    "energy": "mid",
                    "arrangement": "standard",
                    "lines": text_lines,
                }]
        
        for idx, section in enumerate(sections_list):
            # Получаем имя секции - приоритет: tag > name > label
            sec_name = section.get("tag") or section.get("name") or section.get("label")
            # Если имя все еще "Section" или начинается с "Section N", используем fallback
            if not sec_name or sec_name == "Section" or (isinstance(sec_name, str) and sec_name.startswith("Section") and len(sec_name.split()) == 2):
                # Используем стандартные имена секций согласно структуре песни
                num_sections = len(sections_list)
                if num_sections == 1:
                    default_names = ["Verse"]
                elif num_sections == 2:
                    default_names = ["Intro", "Verse"]
                elif num_sections == 3:
                    default_names = ["Intro", "Verse", "Outro"]
                elif num_sections == 4:
                    default_names = ["Intro", "Verse", "Chorus", "Outro"]
                elif num_sections == 5:
                    default_names = ["Intro", "Verse", "Pre-Chorus", "Chorus", "Outro"]
                elif num_sections == 6:
                    default_names = ["Intro", "Verse 1", "Pre-Chorus", "Chorus", "Verse 2", "Outro"]
                elif num_sections == 7:
                    default_names = ["Intro", "Verse 1", "Pre-Chorus", "Chorus", "Verse 2", "Bridge", "Outro"]
                else:
                    # Для 8+ секций используем расширенную структуру
                    default_names = ["Intro", "Verse 1", "Pre-Chorus", "Chorus", "Verse 2", "Bridge"]
                    verse_num = 3
                    for i in range(6, num_sections):
                        if i == num_sections - 1:
                            default_names.append("Outro")
                        elif (i - 5) % 2 == 0:
                            default_names.append(f"Verse {verse_num}")
                            verse_num += 1
                        else:
                            default_names.append("Chorus")
                
                if idx < len(default_names):
                    sec_name = default_names[idx]
                elif idx == len(sections_list) - 1:
                    sec_name = "Outro"
                else:
                    sec_name = f"Section {idx + 1}"
            
            mood = section.get("mood", "neutral")
            energy = section.get("energy", "mid")
            arrangement = section.get("arrangement", "standard")

            # Получаем вокальную технику для секции
            section_vocal = section.get("vocal_technique") or lyrics.get("section_vocals", [])
            if isinstance(section_vocal, list) and idx < len(section_vocal):
                vocal_tech = section_vocal[idx]
            elif isinstance(section_vocal, str):
                vocal_tech = section_vocal
            else:
                # Fallback: определяем по эмоции секции
                try:
                    from .vocal_techniques import get_vocal_for_emotion
                    sec_emotion = section.get("emotion") or mood
                    sec_intensity = float(energy) if isinstance(energy, (int, float)) else 0.5
                    vocal_techs = get_vocal_for_emotion(sec_emotion, sec_intensity)
                    vocal_tech = vocal_techs[0] if vocal_techs else "tenor"
                except (ImportError, Exception):
                    vocal_tech = "tenor"  # Fallback

            header = f"[{sec_name.upper()}: mood={mood}, energy={energy}, arr={arrangement}, vocal={vocal_tech}]"
            lyrics_prompt_lines.append(header)

            for line in section.get("lines", []):
                lyrics_prompt_lines.append(line)

        lyrics_prompt_str = "\n".join(lyrics_prompt_lines)


        # --- UI TEXT CLEAN ---------------------------------------------------
        ui_lines = []
        for line in text.split("\n"):
            s = line.strip()
            if not s:
                continue
            if s.startswith("[") and s.endswith("]"):
                continue
            ui_lines.append(s)

        ui_text_str = "\n".join(ui_lines)


        # --- SUMMARY ---------------------------------------------------------
        summary_lines = []

        # Add summary blocks collected in diagnostics
        for name, block in summary_blocks.items():
            summary_lines.append(block)

        # Add consistency layer
        if consistency:
            summary_lines.append(f"[Consistency: {consistency}]")

        # Add meta
        if meta:
            summary_lines.append(f"[Meta: {meta}]")

        summary_str = "\n".join(summary_lines)


        # Final FANF payload
        return {
            "style_prompt": style_prompt_str,
            "lyrics_prompt": lyrics_prompt_str,
            "ui_text": ui_text_str,
            "summary": summary_str,
        }

    def annotate_ui(self, payload: Dict[str, Any] | None = None) -> str | None:
        """Functional, stateless FANF → UI."""
        if not isinstance(payload, dict):
            return None
        fanf_block = payload.get("fanf") or {}
        if not isinstance(fanf_block, dict):
            return None
        return fanf_block.get("annotated_text_ui")

    def annotate_suno(self, payload: Dict[str, Any] | None = None) -> str | None:
        """Functional, stateless FANF → Suno."""
        if not isinstance(payload, dict):
            return None
        fanf_block = payload.get("fanf") or {}
        if not isinstance(fanf_block, dict):
            return None
        return fanf_block.get("annotated_text_suno")

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
        # Безопасные границы BPM (40-200)
        MIN_SAFE_BPM = 40.0
        MAX_SAFE_BPM = 200.0
        fallback = 120.0
        if overrides and overrides.bpm is not None:
            # Ограничиваем пользовательский BPM безопасными границами
            fallback = max(MIN_SAFE_BPM, min(MAX_SAFE_BPM, float(overrides.bpm)))
        elif base_bpm is not None:
            fallback = max(MIN_SAFE_BPM, min(MAX_SAFE_BPM, float(base_bpm)))
        else:
            fallback = 120.0
        
        stabilized: list[float] = []
        curve = list(bpm_curve or [])
        if not curve:
            curve = [fallback] * max(section_count, 1)
        for value in curve:
            candidate = fallback if value is None else float(value)
            # Ограничиваем каждое значение безопасными границами
            candidate = max(MIN_SAFE_BPM, min(MAX_SAFE_BPM, candidate))
            delta = candidate - fallback
            if abs(delta) > limit:
                candidate = fallback + limit if delta > 0 else fallback - limit
            # Финальная проверка границ
            candidate = max(MIN_SAFE_BPM, min(MAX_SAFE_BPM, candidate))
            stabilized.append(round(candidate, 3))
        lock_info = {
            "user_lock": bool(overrides and overrides.bpm is not None),
            "global_lock": True,
            "max_section_variation": limit,
            "fallback_bpm": 120,
            "min_bpm": MIN_SAFE_BPM,
            "max_bpm": MAX_SAFE_BPM,
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
        base_key = manual_key or (keys[0] if keys else None) or DEFAULT_CONFIG.FALLBACK_KEY
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

        # Извлекаем цветовую информацию (если есть)
        color_profile_data = source.get("color_profile", {}) or {}
        dominant_emotion_data = source.get("dominant_emotion", "") or ""
        
        feature_map_result = {
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
            
            # Цветовая информация для genre_weights (на основе GENRE_DATABASE.json)
            "color_profile": color_profile_data,
            "dominant_emotion": dominant_emotion_data,
        }
        
        return feature_map_result

    def _resolve_dominant_emotion(self, text: str, emotion_profile: Dict[str, float]) -> str:
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
    
    def _resolve_dominant_emotion_enhanced(self, text: str, emotion_profile: Dict[str, float], tlp_profile: Dict[str, float]) -> str:
        """
        Улучшенное определение доминирующей эмоции с учетом контекста.
        Учитывает комбинации эмоций (например, sensual + nostalgia = sensual_nostalgia).
        """
        if not emotion_profile or not isinstance(emotion_profile, dict):
            return "neutral"
        
        try:
            # Безопасное извлечение числовых значений
            numeric_profile = {k: float(v) for k, v in emotion_profile.items() if isinstance(v, (int, float))}
            if not numeric_profile:
                return "neutral"
            
            # Получаем TLP значения
            love_level = float(tlp_profile.get("love", 0.0) or 0.0)
            pain_level = float(tlp_profile.get("pain", 0.0) or 0.0)
            truth_level = float(tlp_profile.get("truth", 0.0) or 0.0)
            
            # MASTER-PATCH: Исправляем проблему с "sensual 0.979" для драматических текстов
            # Проверяем комбинации эмоций с учетом контекста TLP
            sensual_score = numeric_profile.get("sensual", 0.0)
            nostalgia_score = numeric_profile.get("nostalgia", 0.0)
            sadness_score = numeric_profile.get("sadness", 0.0)
            sorrow_score = numeric_profile.get("sorrow", 0.0)
            determination_score = numeric_profile.get("determination", 0.0)
            
            # Если высокий pain и низкий love - это не sensual, а sorrow/determination
            if pain_level > 0.5 and love_level < 0.3:
                if sorrow_score > 0.2 or sadness_score > 0.3:
                    return "sorrow"
                if determination_score > 0.2 or truth_level > 0.4:
                    return "determination"
                if nostalgia_score > 0.2:
                    return "nostalgic_melancholy"
                # Не возвращаем sensual для драматических текстов
                if sensual_score > 0.5:
                    # Если sensual слишком высокий, но контекст драматический - снижаем его влияние
                    return "melancholy"
            
            # Если есть sensual и nostalgia - это sensual_nostalgia (только при низком pain)
            if sensual_score > 0.3 and nostalgia_score > 0.3 and pain_level < 0.4:
                return "sensual_nostalgia"
            
            # Если есть sensual и love - это sensual_love (только при низком pain)
            if sensual_score > 0.3 and love_level > 0.5 and pain_level < 0.4:
                return "sensual_love"
            
            # Если есть nostalgia и sadness - это nostalgic_melancholy
            if nostalgia_score > 0.3 and sadness_score > 0.3:
                return "nostalgic_melancholy"
            
            # Если есть высокий love и низкий pain - это love_tender
            if love_level > 0.6 and pain_level < 0.4:
                if sensual_score > 0.2:
                    return "sensual_love"
                return "love_tender"
            
            # Если есть высокий truth - это confessional
            if truth_level > 0.5:
                if nostalgia_score > 0.2:
                    return "confessional_nostalgia"
                return "confessional"
            
            # Стандартное определение доминирующей эмоции (исключаем sensual для драматических текстов)
            # Если sensual доминирует, но контекст драматический - выбираем следующую по значению
            sorted_emotions = sorted(numeric_profile.items(), key=lambda item: item[1], reverse=True)
            dominant_emotion, dominant_value = sorted_emotions[0] if sorted_emotions else ("neutral", 0.0)
            
            # Если доминирует sensual, но контекст драматический - берем следующую эмоцию
            if dominant_emotion == "sensual" and pain_level > 0.4 and love_level < 0.3:
                if len(sorted_emotions) > 1:
                    dominant_emotion, dominant_value = sorted_emotions[1]
                else:
                    dominant_emotion = "melancholy"
            
            dominant = dominant_emotion
            
            # Маппинг для совместимости
            fallback_map = {
                "joy": "joy_bright",
                "peace": "confidence",
                "anger": "rage_extreme",
                "sadness": "melancholy_dark",
                "awe": "love_soft",
                "sensual": "sensual",
                "nostalgia": "nostalgia",
            }
            return fallback_map.get(dominant, dominant)
            
        except (ValueError, TypeError, KeyError):
            return "neutral"

    @staticmethod
    def _merge_semantic_hints(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Безопасное слияние semantic hints с защитой от мутации исходных данных."""
        # Создаем глубокую копию base для безопасности
        result: Dict[str, Any] = copy.deepcopy(base) if isinstance(base, dict) else {}
        
        if not isinstance(override, dict):
            return result
        
        for key, value in override.items():
            # Создаем копию значения для безопасности
            safe_value = copy.deepcopy(value) if isinstance(value, (dict, list)) else value
            
            if isinstance(safe_value, dict) and isinstance(result.get(key), dict):
                result[key] = StudioCoreV6._merge_semantic_hints(result[key], safe_value)
            elif isinstance(safe_value, list) and isinstance(result.get(key), list):
                existing = result[key]
                result[key] = existing + [item for item in safe_value if item not in existing]
            elif isinstance(safe_value, list):
                result[key] = list(safe_value)
            else:
                result[key] = safe_value
        return result

    def _apply_user_overrides_once(
        self, payload: Dict[str, Any], manager: UserOverrideManager, engines: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        # Получаем override_engine из engines или создаем новый
        if engines:
            override_engine = engines.get("user_override_engine")
            if not override_engine:
                from .logical_engines import UserOverrideEngine
                override_engine = UserOverrideEngine()
        else:
            from .logical_engines import UserOverrideEngine
            override_engine = UserOverrideEngine()
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
            applied_vocal = override_engine.apply_to_vocals(vocal, manager)
            payload["vocal"] = applied_vocal
            adjustments["vocal"] = copy.deepcopy(applied_vocal)

        # BPM
        bpm = payload.get("bpm")
        if isinstance(bpm, dict):
            applied_bpm = override_engine.apply_to_rhythm(bpm, manager)

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
            applied_style = override_engine.apply_to_style(style, manager)
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


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
