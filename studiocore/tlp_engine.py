"""Public wrapper for the Truth × Love × Pain engine."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .emotion import TruthLovePainEngine as _TruthLovePainEngine


class TruthLovePainEngine(_TruthLovePainEngine):
    """Adds convenience helpers on top of the base TLP engine."""

    def describe(self, text: str) -> Dict[str, Any]:
        profile = self.analyze(text)
        ordered: List[Tuple[str, float]] = sorted(profile.items(), key=lambda item: item[1], reverse=True)
        dominant = ordered[0][0] if ordered else "truth"
        profile["dominant_axis"] = dominant
        profile["balance"] = round((profile.get("truth", 0.0) + profile.get("love", 0.0)) - profile.get("pain", 0.0), 3)
        return profile


__all__ = ["TruthLovePainEngine"]
