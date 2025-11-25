# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
"""Hybrid Instrumentation Layer - wrapper module for compatibility."""

from __future__ import annotations

# Re-export from hybrid_instrumentation for compatibility
from .hybrid_instrumentation import HybridInstrumentationLayer

__all__ = ["HybridInstrumentationLayer"]

