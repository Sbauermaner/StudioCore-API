"""Fallback implementation for StudioCore when the main engine is unavailable."""
from __future__ import annotations


class StudioCoreFallback:
    """Simple safe-mode placeholder that prevents crashes when core loading fails."""

    def __init__(self, *args, **kwargs) -> None:
        print("🧩 [StudioCoreFallback] Активен временный режим.")
        self.is_fallback = True
        self.status = "safe-mode"
        self.subsystems = []

    def analyze(self, *_args, **_kwargs):
        raise RuntimeError(
            "⚠️ StudioCoreFallback: анализ недоступен — основное ядро не загружено."
        )
