# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""User override helpers required by the StudioCore Codex specification."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


def _ensure_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value]
    if isinstance(value, tuple):
        return list(value)
    return [value]


@dataclass
class UserOverrides:
    """Container describing user supplied override information."""

    bpm: Optional[float] = None
    key: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    vocal_profile: Dict[str, Any] | None = None
    instrumentation: List[str] | None = None
    structure_hints: List[Dict[str, Any]] | None = None
    color_state: Optional[str] = None
    semantic_hints: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        bpm: Optional[float] = None,
        key: Optional[str] = None,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        vocal_profile: Dict[str, Any] | None = None,
        instrumentation: Iterable[str] | None = None,
        structure_hints: Iterable[Dict[str, Any]] | None = None,
        color_state: Optional[str] = None,
        semantic_hints: Dict[str, Any] | None = None,
    ) -> None:
        # Валидация BPM: ограничиваем разумными значениями (40-200)
        if isinstance(bpm, (int, float)):
            self.bpm = float(max(40.0, min(200.0, bpm)))
        else:
            self.bpm = None
        
        # Валидация Key: проверяем базовую структуру (нота + опционально mode)
        if key and isinstance(key, str) and key.strip():
            key_clean = key.strip()
            # Простая валидация: должна начинаться с валидной ноты или быть "auto"
            valid_notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            key_parts = key_clean.split(maxsplit=1)
            root_note = key_parts[0].replace("#", "").upper()
            # Если начинается с валидной ноты или это "auto" - принимаем
            if key_clean.lower() == "auto" or root_note in valid_notes:
                self.key = key_clean
            else:
                # Некорректный key - используем None (будет fallback)
                self.key = None
        else:
            self.key = None
        
        self.genre = genre
        self.mood = mood
        
        # Валидация vocal_profile: ограничиваем допустимые значения gender
        vocal_profile_clean = dict(vocal_profile or {})
        if "gender" in vocal_profile_clean:
            valid_genders = ["male", "female", "auto", "neutral", "mixed"]
            if vocal_profile_clean["gender"] not in valid_genders:
                # Некорректный gender - удаляем или используем fallback
                vocal_profile_clean.pop("gender", None)
        self.vocal_profile = vocal_profile_clean
        
        self.instrumentation = _ensure_list(instrumentation)
        self.structure_hints = [dict(item) for item in (structure_hints or [])]
        self.color_state = color_state
        self.semantic_hints = dict(semantic_hints or {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "UserOverrides":
        if not isinstance(data, dict):
            data = {}
        return cls(
            bpm=data.get("bpm"),
            key=data.get("key"),
            genre=data.get("genre"),
            mood=data.get("mood"),
            vocal_profile=data.get("vocal_profile"),
            instrumentation=data.get("instrumentation"),
            structure_hints=data.get("structure_hints"),
            color_state=data.get("color_state"),
            semantic_hints=data.get("semantic_hints"),
        )


class UserOverrideManager:
    """Applies UserOverrides to logical engine payloads."""

    def __init__(self, overrides: UserOverrides | None = None) -> None:
        self.overrides = overrides or UserOverrides()

    def resolve_bpm(self, auto_bpm: float | None) -> float | None:
        manual = self.overrides.bpm
        if manual is not None:
            return float(manual)
        meta = self._get_meta_bpm(auto_bpm)
        return meta if meta is not None else auto_bpm

    def _get_meta_bpm(self, auto_bpm: float | None) -> float | None:
        hints = self.overrides.semantic_hints
        target = None
        if isinstance(hints.get("bpm"), dict):
            target = hints["bpm"].get("target")
        target = target or hints.get("target_bpm")
        if target is None:
            return None
        try:
            return float(target)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            return auto_bpm

    def apply_to_rhythm(self, rhythm_payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(rhythm_payload)
        manual_bpm = self.resolve_bpm(payload.get("estimate"))
        if manual_bpm is not None:
            payload["estimate"] = manual_bpm
            payload.setdefault("manual_override", {})["bpm"] = manual_bpm
        if self.overrides.structure_hints:
            payload.setdefault("structure_hints", self.overrides.structure_hints)
        return payload

    def apply_to_style(self, style_payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(style_payload)
        if self.overrides.genre:
            payload["genre"] = self.overrides.genre
        if self.overrides.mood:
            payload["mood"] = self.overrides.mood
        if self.overrides.color_state:
            payload.setdefault("visual", {})
            payload["visual"] = {
                "primary": self.overrides.color_state,
                "source": "user",
            }
        if self.overrides.instrumentation:
            payload.setdefault("instrumentation", {})
            payload["instrumentation"] = {
                "explicit": list(self.overrides.instrumentation),
                "source": "user",
            }
        return payload

    def apply_to_vocals(self, vocal_payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(vocal_payload)
        if self.overrides.vocal_profile:
            payload.update({k: v for k, v in self.overrides.vocal_profile.items() if v is not None})
            payload.setdefault("source", "user")
        return payload

    def debug_summary(self) -> Dict[str, Any]:
        return {
            "has_overrides": any(
                getattr(self.overrides, field)
                for field in ("bpm", "key", "genre", "mood", "vocal_profile", "instrumentation", "structure_hints")
            ),
            "fields": {
                "bpm": self.overrides.bpm,
                "key": self.overrides.key,
                "genre": self.overrides.genre,
                "mood": self.overrides.mood,
                "vocal_profile": self.overrides.vocal_profile,
                "instrumentation": self.overrides.instrumentation,
                "structure_hints": self.overrides.structure_hints,
            },
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
