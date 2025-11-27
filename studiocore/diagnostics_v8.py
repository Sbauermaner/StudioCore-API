# -*- coding: utf - 8 -*-
"""
DiagnosticsBuilderV8 — structured diagnostics wrapper for StudioCore.

This module introduces a stable, schema - based view over the raw diagnostics
produced by the engines while preserving all legacy keys at the top level.

Schema version: v8.0
"""

import time
from typing import Any, Dict, Optional

from studiocore.config import DEFAULT_CONFIG


class DiagnosticsBuilderV8:
    """Build a structured diagnostics view on top of the legacy flat dict."""

    # Task 6.2: Import version from config instead of hardcoding
    SCHEMA_VERSION = DEFAULT_CONFIG.DIAGNOSTICS_VERSION

    def __init__(
        self, base: Dict[str, Any], payload: Optional[Dict[str, Any]] = None
    ) -> None:
        # base is the raw diagnostics dict built by core_v6 / monolith
        self._base = base or {}
        self._payload = payload or {}
        # Task 10.1: Timer for runtime calculation
        self._start_time: Optional[float] = None

    # --- small helpers -------------------------------------------------

    def _extract_engines_block(self) -> Dict[str, Any]:
        """Group engine - related fields into a nested 'engines' block."""
        base = self._base

        engines: Dict[str, Any] = {}

        # These keys are heuristic – they are safe even if missing.
        if "bpm" in base:
            engines["bpm"] = base.get("bpm")
        if "rde" in base:
            engines["rde"] = base.get("rde")
        if "tlp" in base or "tlp_vector" in base:
            engines["tlp"] = base.get("tlp") or base.get("tlp_vector")
        if "genre_universe_tags" in base or "genre" in base:
            engines["genre"] = base.get("genre_universe_tags") or base.get("genre")
        if "tone_profile" in base:
            engines["tone"] = base.get("tone_profile")
        if "frequency_profile" in base or "frequency" in base:
            engines["frequency"] = base.get("frequency_profile") or base.get(
                "frequency"
            )

        return engines

    def _extract_summary_blocks(self) -> Dict[str, Any]:
        """Group known textual blocks into a nested 'summary_blocks' section."""
        base = self._base
        summary_blocks: Dict[str, Any] = {}

        for key in (
            "tlp_block",
            "rde_block",
            "genre_block",
            "zeropulse_block",
            "color_wave_block",
            "integrity_block",
            "summary_block",
        ):
            value = base.get(key)
            if isinstance(value, str) and value.strip():
                summary_blocks[key] = value

        return summary_blocks

    def start_timer(self) -> None:
        """Task 10.1: Start timer for runtime calculation."""
        self._start_time = time.time()

    def stop_timer(self) -> float:
        """Task 10.1: Stop timer and return runtime in milliseconds."""
        if self._start_time is None:
            return 0.0
        runtime_ms = (time.time() - self._start_time) * 1000
        self._start_time = None
        return runtime_ms

    def _extract_meta(self) -> Dict[str, Any]:
        """Basic meta - information about diagnostics."""
        meta: Dict[str, Any] = {
            "schema": self.SCHEMA_VERSION,
        }

        # Engine version — try to infer from payload if available.
        engine_name = self._payload.get("engine")
        if isinstance(engine_name, str) and engine_name:
            meta["engine"] = engine_name

        # Task 10.1: Calculate runtime_ms if timer was used, otherwise use value from base
        if self._start_time is not None:
            # Timer still running, calculate current runtime
            meta["runtime_ms"] = int((time.time() - self._start_time) * 1000)
        elif "runtime_ms" in self._base:
            # Use runtime from base (e.g., from monolith)
            meta["runtime_ms"] = self._base.get("runtime_ms")
        else:
            # No runtime available
            meta["runtime_ms"] = None

        return meta

    # --- public API ----------------------------------------------------

    def build(self) -> Dict[str, Any]:
        """
        Build a structured diagnostics dict.

        Strategy:
          1) Start from a shallow copy of the legacy base diagnostics, so any
             existing keys remain available for backward compatibility.
          2) Add nested sections:
               - 'engines'
               - 'summary_blocks'
               - 'consistency' (if present in base)
               - 'meta'
          3) Do NOT delete or rename existing keys to avoid breaking tests / clients.
        """
        result: Dict[str, Any] = dict(self._base)  # preserve legacy keys

        # New structured views
        result["engines"] = self._extract_engines_block()
        result["summary_blocks"] = self._extract_summary_blocks()

        # Consistency is already a structured block if present
        if "consistency" in self._base:
            result["consistency"] = self._base.get("consistency")

        # Meta section
        result["meta"] = self._extract_meta()

        # Mark diagnostics schema version explicitly (top - level key)
        result["diagnostic_schema"] = self.SCHEMA_VERSION

        return result
