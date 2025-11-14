"""Compatibility shim for legacy imports of monolith_v4_3_1."""
from __future__ import annotations

from .monolith_v6_0_0 import *  # noqa: F401,F403

# Provide backwards-compatible version marker for tooling that inspects the module.
STUDIOCORE_VERSION = "v6.0.0-maxi"  # type: ignore[assignment]
