# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""Logical engine helpers used by the StudioCore v6 compatibility layer.

The Codex specification expects a wide collection of logical engines.  The
implementations below provide light - weight, deterministic heuristics that can
run in restricted environments while still producing structured data.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from statistics import mean
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple  # noqa: F401

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .color_engine_adapter import EMOTION_COLOR_MAP, get_emotion_colors
from .emotion import AutoEmotionalAnalyzer

# Import required engine for EmotionVector
from .emotion import TruthLovePainEngine
from .emotion_profile import EmotionVector
from .instrument import (
    InstrumentLibrary,
    instrument_based_on_emotion as _instrument_based_on_emotion,
    instrument_based_on_voice as _instrument_based_on_voice,
    instrument_color_sync as _instrument_color_sync,
    instrument_rhythm_sync as _instrument_rhythm_sync,
    instrument_selection as _instrument_selection,
)
from .rhythm import LyricMeter
from .text_utils import extract_sections, normalize_text_preserve_symbols
from .tone_sync import ToneSyncEngine
from .user_override_manager import UserOverrideManager

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
_COMMAND_RE = re.compile(r"\[(?P < name > [A - Z_]+)\s*:?\s * (?P < value > [^\]]+)\]")
_VOWEL_RE = re.compile(r"[aeiouyаеёиоуыэюя]", re.I)


def _split_sentences(text: str) -> List[str]:
    if not text.strip():
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _words(text: str) -> List[str]:
    return re.findall(r"[a - zA - Zа - яА - ЯёЁ]+", text)


def _section_texts(text: str) -> List[str]:
    structured = extract_sections(text)
    if structured:
        sections = []
        for section in structured:
            lines = [ln.strip() for ln in section.get("lines", []) if ln.strip()]
            if lines:
                sections.append("\n".join(lines))
        if sections:
            return sections
    chunks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    return chunks or ([text.strip()] if text.strip() else [])


class TextStructureEngine:
    """Detect song sections and structural anchors."""

    KEYWORDS = {
        "intro": ("intro", "интро", "вступ", "opening"),
        "verse": ("verse", "куплет", "strofa"),
        "prechorus": ("pre - chorus", "prechorus", "преприпев"),
        "chorus": ("chorus", "припев", "hook", "refrain"),
        "bridge": ("bridge", "бридж", "middle"),
        "outro": ("outro", "финал", "ending"),
    }

    def __init__(self) -> None:
        self._section_metadata: List[Dict[str, Any]] = []

    def reset(self) -> None:
        """Clear cached structural metadata to avoid cross - request bleed."""
        self._section_metadata = []

    def auto_section_split(self, text: str) -> List[str]:
        self.reset()
        structured = extract_sections(text)
        sections: List[str] = []
        metadata: List[Dict[str, Any]] = []

        # Проверяем, есть ли пользовательские маркеры (до вызова
        # _assign_section_names)
        has_user_markers = any(
            item.get("tag", "").lower() not in ("body", "")
            and (
                item.get("tag", "")
                in [
                    "Verse 1",
                    "Verse 2",
                    "Verse 3",
                    "Final Chorus",
                    "Pre - Chorus",
                    "Chorus",
                    "Bridge",
                    "Outro",
                    "Intro",
                ]
                or "куплет" in item.get("tag", "").lower()
                or "припев" in item.get("tag", "").lower()
                or "мост" in item.get("tag", "").lower()
                or "аутро" in item.get("tag", "").lower()
                or "интро" in item.get("tag", "").lower()
                or "преприпев" in item.get("tag", "").lower()
            )
            for item in structured
        )

        # Если есть пользовательские маркеры - НЕ вызываем _assign_section_names
        # Она вызывается только для текстов без явных маркеров
        # НО: проверяем повторяющиеся секции и аннотируем их, даже если есть
        # пользовательские маркеры
        if not has_user_markers and structured:
            # Вызываем _assign_section_names только если нет пользовательских
            # маркеров
            from .text_utils import _assign_section_names

            _assign_section_names(structured)
        elif has_user_markers and structured:
            # Если есть пользовательские маркеры, все равно проверяем
            # повторяющиеся секции
            from .text_utils import _detect_duplicate_sections

            duplicates = _detect_duplicate_sections(structured)
            if duplicates:
                # Группируем повторяющиеся секции
                section_groups: Dict[str, List[int]] = {}

                for i, sec in enumerate(structured):
                    lines = sec.get("lines", [])
                    text_content = "\n".join(lines).strip()
                    normalized = text_content.lower().replace(" ", "").replace("\n", "")

                    if normalized not in section_groups:
                        section_groups[normalized] = []
                    section_groups[normalized].append(i)

                # Аннотируем повторяющиеся секции
                for normalized, indices in section_groups.items():
                    if len(indices) > 1:
                        indices.sort()
                        first_tag = structured[indices[0]].get("tag", "Section")
                        base_name = (
                            "Chorus"
                            if "chorus" in first_tag.lower()
                            or "припев" in first_tag.lower()
                            else first_tag.split()[0]
                            if first_tag.split()
                            else "Section"
                        )

                        for idx, sec_idx in enumerate(indices, 1):
                            structured[sec_idx]["tag"] = f"{base_name} {idx}"

        for item in structured:
            lines = item.get("lines", [])
            section_text = "\n".join(lines).strip()
            if section_text:
                sections.append(section_text)
            # Используем тег из structured (который сохранен из маркеров или
            # установлен _assign_section_names)
            tag = item.get("tag", "Body")
            metadata.append(
                {
                    "tag": tag,
                    "label": tag,  # Добавляем label для совместимости
                    "name": tag,  # Добавляем name для совместимости
                    "lines": list(lines),
                    "line_count": len(lines),
                }
            )
        if not sections and text.strip():
            sections = [text.strip()]
            metadata = [
                {
                    "tag": "Verse",
                    "label": "Verse",
                    "name": "Verse",
                    "lines": text.strip().split("\n"),
                    "line_count": len(text.strip().split("\n")),
                }
            ]
        self._section_metadata = []
        for item in metadata:
            tag = item.get("tag", "Body")
            self._section_metadata.append(
                {
                    "tag": tag,
                    "label": tag,  # Используем tag как label
                    "name": tag,  # Используем tag как name
                    "lines": list(item.get("lines", [])),
                    "line_count": item.get("line_count", len(item.get("lines", []))),
                }
            )
        return sections

    def _resolve_sections(self, text: str, sections: Sequence[str] | None) -> List[str]:
        if sections is not None:
            return [section for section in sections if isinstance(section, str)]
        return self.auto_section_split(text)

    def _resolve_section(
        self, label: str, text: str, sections: Sequence[str] | None, fallback_index: int
    ) -> Dict[str, Any]:
        sections = self._resolve_sections(text, sections)
        if not sections:
            return {"label": label, "index": None, "text": "", "confidence": 0.0}

        keywords = self.KEYWORDS.get(label, ())
        match_index = None
        for idx, section in enumerate(sections):
            low = section.lower()
            if any(token in low for token in keywords):
                match_index = idx
                break
        if match_index is None:
            match_index = min(fallback_index, len(sections) - 1)
            confidence = 0.4
        else:
            confidence = 0.75

        return {
            "label": label,
            "index": match_index,
            "text": sections[match_index],
            "confidence": round(confidence, 3),
        }

    def section_metadata(self) -> List[Dict[str, Any]]:
        return [
            {
                "tag": item.get("tag"),
                "lines": list(item.get("lines", [])),
                "line_count": item.get("line_count", len(item.get("lines", []))),
                "strict_boundary": item.get("strict_boundary"),
                "lyrical_density": item.get("lyrical_density"),
                "rde_emotion_hint": item.get("rde_emotion_hint"),
            }
            for item in self._section_metadata
        ]

    def detect_intro(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        return self._resolve_section("intro", text, sections, 0)

    def detect_verse(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        resolved = self._resolve_sections(text, sections)
        return self._resolve_section(
            "verse", text, resolved, 0 if len(resolved) == 1 else 1
        )

    def detect_prechorus(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        return self._resolve_section("prechorus", text, sections, 1)

    def detect_chorus(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        return self._resolve_section("chorus", text, sections, 1)

    def detect_bridge(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        resolved = self._resolve_sections(text, sections)
        return self._resolve_section(
            "bridge", text, resolved, max(len(resolved) - 2, 0)
        )

    def detect_outro(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        resolved = self._resolve_sections(text, sections)
        return self._resolve_section("outro", text, resolved, max(len(resolved) - 1, 0))

    def detect_meta_pause(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        sections = self._resolve_sections(text, sections)
        pause_locations: List[int] = []
        for idx, section in enumerate(sections):
            if (
                "..." in section
                or "(pause" in section.lower()
                or "[pause" in section.lower()
            ):
                pause_locations.append(idx)
        confidence = 0.8 if pause_locations else 0.2
        return {
            "count": len(pause_locations),
            "locations": pause_locations,
            "confidence": confidence,
        }

    def detect_zero_pulse(
        self, text: str, *, sections: Sequence[str] | None = None
    ) -> Dict[str, Any]:
        sections = self._resolve_sections(text, sections)
        zero_sections: List[int] = []
        for idx, section in enumerate(sections):
            if not section.strip() or "[silence]" in section.lower():
                zero_sections.append(idx)
        return {
            "has_zero_pulse": bool(zero_sections),
            "locations": zero_sections,
            "confidence": 0.9 if zero_sections else 0.3,
        }


class EmotionEngine:
    """High - level wrapper above the heuristic emotional analyzers."""

    def __init__(self) -> None:
        self._analyzer = AutoEmotionalAnalyzer()
        # Initialize TLP for vector calculation
        self._tlp_engine = TruthLovePainEngine()
        # Task 2.1: Cache using text hash to prevent re-analyzing the same text multiple times
        self._cache: Dict[str, Dict[str, float]] = {}

    def emotion_detection(self, text: str) -> Dict[str, float]:
        """
        MASTER - PATCH v2: Добавляем пост - фильтр для дорожной исповеди.
        MASTER - PATCH v4.0: Добавляем Rage - mode конфликт резолвер.
        """
        # Task 2.1: Use cache with text hash to prevent re-analyzing the same text
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in self._cache:
            emo = self._cache[text_hash].copy()
        else:
            emo = self._analyzer.analyze(text)
            # Cache the result using hash
            self._cache[text_hash] = emo.copy()

        # Мягкий фильтр для дорожной исповеди: sensual не доминирует над sorrow
        # / determination.
        sorrow = emo.get("sorrow", 0.0)
        determination = emo.get("determination", 0.0)
        sensual = emo.get("sensual", 0.0)

        if sensual > 0.15 and (sorrow + determination) > 0.5:
            # чутка режем sensual, перераспределяя в sorrow / determination
            delta = sensual - 0.15
            emo["sensual"] = 0.15
            emo["sorrow"] = sorrow + 0.6 * delta
            emo["determination"] = determination + 0.4 * delta

        # MASTER - PATCH v6.0 — Rage - mode conflict resolver (только anger /
        # tension)
        anger = emo.get("anger", 0.0)
        tension = emo.get("tension", 0.0)

        # Rage mode: anger > 0.22 ИЛИ tension > 0.25 (НЕ epic)
        is_rage = anger > 0.22 or tension > 0.25

        if is_rage:
            # Remove peace / calm / serenity if rage mode detected
            if "peace" in emo:
                emo["peace"] = 0.0
            if "calm" in emo:
                emo["calm"] = 0.0
            if "serenity" in emo:
                emo["serenity"] = 0.0

            # Boost tension if anger > 0.20
            if anger > 0.20:
                tension = emo.get("tension", 0.0)
                emo["tension"] = max(tension, 0.25)

        return emo

    def resolve_emotion_genre_conflict(
        self, emotions: Dict[str, float], genre: str
    ) -> Tuple[Optional[str], bool]:
        """
        Task 19.2: Resolve emotion-genre conflicts.
        
        Rules from KONFLIKTE_UND_PROZESSE.md:
        - love + metal → conflict (suggest: lyrical, soft_pop)
        - rage + lyrical → conflict (suggest: metal, hardcore_rap)
        - joy + gothic → conflict (suggest: pop, electronic, dark_pop)
        - sadness + pop → conflict (suggest: gothic, darkwave)
        - peace + metal → conflict (suggest: soft, ambient)
        
        Args:
            emotions: Dictionary of emotion scores
            genre: Current genre string
        
        Returns:
            Tuple of (suggested_genre, was_resolved)
        """
        if not emotions or not genre:
            return None, False
        
        genre_lower = str(genre).lower()
        was_resolved = False
        suggested_genre = None
        
        # Get dominant emotion
        dominant_emotion = max(emotions, key=emotions.get) if emotions else None
        if not dominant_emotion:
            return None, False
        
        dominant_value = emotions.get(dominant_emotion, 0.0)
        
        # Conflict 1: love + metal
        if dominant_emotion == "love" and dominant_value > 0.3:
            if "metal" in genre_lower or "thrash" in genre_lower or "death" in genre_lower:
                suggested_genre = "lyrical_song"  # or "soft_pop"
                was_resolved = True
        
        # Conflict 2: rage + lyrical
        elif (dominant_emotion == "anger" or dominant_emotion == "tension") and dominant_value > 0.25:
            if "lyrical" in genre_lower or "ballad" in genre_lower or "soft" in genre_lower:
                suggested_genre = "metal"  # or "hardcore_rap"
                was_resolved = True
        
        # Conflict 3: joy + gothic
        elif dominant_emotion == "joy" and dominant_value > 0.3:
            if "gothic" in genre_lower or "darkwave" in genre_lower or "dark" in genre_lower:
                suggested_genre = "pop"  # or "electronic", "dark_pop"
                was_resolved = True
        
        # Conflict 4: sadness + pop
        elif dominant_emotion == "sadness" and dominant_value > 0.3:
            if "pop" in genre_lower and "dark" not in genre_lower:
                suggested_genre = "gothic_rock"  # or "darkwave"
                was_resolved = True
        
        # Conflict 5: peace + metal
        elif dominant_emotion == "peace" and dominant_value > 0.3:
            if "metal" in genre_lower or "thrash" in genre_lower or "death" in genre_lower:
                suggested_genre = "soft"  # or "ambient"
                was_resolved = True
        
        return suggested_genre, was_resolved

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Delegates to the unified TLP engine implementation.
        This ensures consistency across all engines.
        """
        return self._tlp_engine.export_emotion_vector(text)

    def emotion_intensity_curve(self, text: str) -> List[float]:
        sentences = _split_sentences(text)
        if not sentences:
            return []
        curve: List[float] = []
        # Task 2.1: Cache full text analysis if available using hash
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        full_text_emo = self._cache.get(text_hash)
        
        for sentence in sentences:
            # For sentence-level analysis, we still analyze each sentence separately
            # but can use cached full text if sentence matches full text
            if sentence == text and full_text_emo:
                scores = full_text_emo
            else:
                # Cache sentence-level analysis too
                sentence_hash = hashlib.md5(sentence.encode("utf-8")).hexdigest()
                if sentence_hash in self._cache:
                    scores = self._cache[sentence_hash].copy()
                else:
                    scores = self._analyzer.analyze(sentence)
                    self._cache[sentence_hash] = scores.copy()
            intensity = sum(scores.values())
            curve.append(round(intensity, 3))
        return curve

    def emotion_pivot_points(
        self, text: str, *, intensity_curve: Sequence[float] | None = None
    ) -> List[int]:
        curve = list(intensity_curve or self.emotion_intensity_curve(text))
        if not curve:
            return []
        indexed = sorted(enumerate(curve), key=lambda item: item[1], reverse=True)
        return [idx for idx, _ in indexed[:3]]

    def secondary_emotion_detection(
        self, text: str | Dict[str, float]
    ) -> Dict[str, float]:
        if isinstance(text, dict):
            scores = dict(text)
        else:
            # Task 2.1: Use cache with text hash
            text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
            if text_hash in self._cache:
                scores = self._cache[text_hash].copy()
            else:
                scores = self._analyzer.analyze(text)
                # Cache the result using hash
                self._cache[text_hash] = scores.copy()
        if not scores:
            return {}
        dominant = max(scores, key=scores.get)
        return {k: round(v, 3) for k, v in scores.items() if k != dominant}

    def emotion_conflict_map(self, text: str | Dict[str, float]) -> Dict[str, Any]:
        if isinstance(text, dict):
            scores = dict(text)
        else:
            # Task 2.1: Use cache with text hash
            text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
            if text_hash in self._cache:
                scores = self._cache[text_hash].copy()
            else:
                scores = self._analyzer.analyze(text)
                # Cache the result using hash
                self._cache[text_hash] = scores.copy()
        if not scores:
            return {"conflict": 0.0, "primary": None, "secondary": None}
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        primary, primary_value = ordered[0]
        secondary, secondary_value = ordered[1] if len(ordered) > 1 else (None, 0.0)
        conflict = round(abs(primary_value - secondary_value), 3)
        return {"primary": primary, "secondary": secondary, "conflict": conflict}


class ColorEmotionEngine:
    """Translate emotions into colour palettes using a canonical map."""

    def assign_color_by_emotion(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        if not emotions:
            palette = EMOTION_COLOR_MAP["neutral"]
            return {
                "primary_color": palette[0],
                "accent_color": palette[-1],
                "confidence": 0.2,
            }
        dominant = max(emotions, key=emotions.get)
        palette = get_emotion_colors(dominant, default=EMOTION_COLOR_MAP["neutral"])
        return {
            "primary_color": palette[0],
            "accent_color": palette[-1],
            "confidence": round(emotions.get(dominant, 0.0), 3),
        }

    def generate_color_wave(
        self, emotions: Dict[str, float], *, steps: int = 5
    ) -> List[str]:
        if not emotions:
            return [EMOTION_COLOR_MAP["neutral"][0] for _ in range(steps)]
        ordered = sorted(emotions.items(), key=lambda item: item[1], reverse=True)
        palette = []
        for name, _ in ordered:
            palette.extend(
                get_emotion_colors(name, default=EMOTION_COLOR_MAP["neutral"])
            )
            if len(palette) >= steps:
                break
        if len(palette) >= steps:
            return palette[:steps]
        while len(palette) < steps:
            palette.append(palette[-1])
        return palette

    def color_transition_map(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        wave = self.generate_color_wave(emotions)
        transitions = []
        for idx in range(len(wave) - 1):
            transitions.append({"from": wave[idx], "to": wave[idx + 1], "blend": 0.5})
        return {"transitions": transitions, "palette": wave}


class VocalEngine:
    """Extracts rough vocal characteristics from the lyrics."""

    def detect_voice_gender(self, text: str) -> str:
        """Определяет пол вокала по местоимениям и грамматике глаголов."""
        import re

        tokens = [t.lower() for t in _words(text)]
        # 1. Анализ местоимений третьего лица
        feminine = sum(
            tokens.count(pronoun) for pronoun in ("she", "her", "она", "её", "ей")
        )
        masculine = sum(
            tokens.count(pronoun) for pronoun in ("he", "him", "он", "его", "ему")
        )

        # 2. Анализ грамматики глаголов прошедшего времени (для русского языка)
        # Мужские формы: "я стоял", "я был", "я шел", "я знал", "я искал"
        # Ищем "я" + глагол с окончанием на "л" (но не "ла", "ли", "ло")
        male_verbs = len(re.findall(r"\bя\s+\w * л(?![аеиоуыэюяё])\b", text, re.I))
        # Женские формы: "я стояла", "я была", "я шла", "я знала", "я искала"
        female_verbs = len(re.findall(r"\bя\s+\w * ла\b", text, re.I))

        # 3. Анализ притяжательных местоимений и прилагательных
        # Мужские: "мой", "моя" (в контексте мужского рода), "мой дом", "моя
        # работа" (но это сложнее)
        male_possessive = len(re.findall(r"\b(мой|свой)\s+\w + [^ая]\b", text, re.I))
        # Женские: "моя" (в контексте женского рода), но это сложнее определить

        # 4. Анализ глаголов настоящего времени с окончаниями
        # Мужские: "я иду", "я делаю" (но это не всегда работает)
        # Женские: "я иду", "я делаю" (одинаково)

        # 5. Анализ причастий и деепричастий
        # Мужские: "сделавший", "увидевший"
        male_participles = len(re.findall(r"\b\w + вший\b", text, re.I))
        # Женские: "сделавшая", "увидевшая"
        female_participles = len(re.findall(r"\b\w + вшая\b", text, re.I))

        # Подсчет общего количества индикаторов
        total_feminine = feminine + female_verbs + female_participles
        total_masculine = masculine + male_verbs + male_possessive + male_participles

        if total_feminine > total_masculine:
            return "female"
        if total_masculine > total_feminine:
            return "male"
        return "neutral"

    def detect_voice_type(self, text: str) -> str:
        sentences = _split_sentences(text)
        if not sentences:
            return "narration"
        avg_length = mean(len(sentence.split()) for sentence in sentences)
        if avg_length <= 6:
            return "spoken"
        if avg_length <= 12:
            return "lyrical"
        return "melismatic"

    def detect_voice_tone(self, text: str, emotion: EmotionVector | None = None) -> str:
        energy = sum(ch in "!?" for ch in text)
        softness = sum(ch in "…" for ch in text)
        if energy > softness * 2:
            timbre = "intense"
        elif softness > energy:
            timbre = "soft"
        else:
            timbre = "balanced"

        if emotion:
            if emotion.arousal > 0.7:
                timbre = "intense"
            elif emotion.valence < -0.5:
                timbre = "cold"

        return timbre

    def detect_vocal_style(
        self, text: str, *, voice_type: str | None = None, voice_tone: str | None = None
    ) -> str:
        voice_type = voice_type or self.detect_voice_type(text)
        voice_tone = voice_tone or self.detect_voice_tone(text)
        if voice_type == "spoken":
            return "spoken - word"
        if voice_tone == "intense":
            return "belting"
        if voice_tone == "soft":
            return "breathy"
        return "lyrical"

    def vocal_dynamics_map(self, sections: Sequence[str]) -> Dict[str, float]:
        dynamics: Dict[str, float] = {}
        if not sections:
            return dynamics
        for idx, section in enumerate(sections):
            emphasis = sum(1 for ch in section if ch.isupper())
            exclaims = section.count("!")
            ellipsis = section.count("…")
            score = 0.4 + 0.1 * exclaims + 0.05 * emphasis - 0.05 * ellipsis
            dynamics[f"section_{idx + 1}"] = round(max(0.0, score), 3)
        return dynamics

    def vocal_intensity_curve(self, dynamics: Dict[str, float]) -> List[float]:
        return [dynamics[key] for key in sorted(dynamics.keys())]


class BreathingEngine:
    """Estimate breathing points using simple heuristics."""

    def _lines(self, text: str) -> List[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def detect_inhale_points(self, text: str) -> List[int]:
        lines = self._lines(text)
        inhale_points: List[int] = []
        for idx, line in enumerate(lines):
            if len(line.split()) >= 12 or line.endswith((";", ":")):
                inhale_points.append(idx)
        return inhale_points

    def detect_short_breath(self, text: str) -> List[int]:
        lines = self._lines(text)
        return [idx for idx, line in enumerate(lines) if len(line.split()) <= 4]

    def detect_broken_breath(self, text: str) -> List[int]:
        lines = self._lines(text)
        broken = []
        for idx, line in enumerate(lines):
            if "--" in line or "—" in line:
                broken.append(idx)
        return broken

    def detect_spasms(self, text: str) -> List[int]:
        lines = self._lines(text)
        return [idx for idx, line in enumerate(lines) if "?!" in line or "!!" in line]

    def detect_emotional_breathing(
        self, text: str, emotions: Dict[str, float] | None = None
    ) -> Dict[str, Any]:
        emotions = emotions or {}
        inhale = self.detect_inhale_points(text)
        spasms = self.detect_spasms(text)
        return {
            "inhale_points": inhale,
            "spasm_points": spasms,
            "emotional_weight": emotions,
            "intensity": round(
                min(1.0, len(spasms) * 0.1 + emotions.get("anger", 0) * 0.5), 3
            ),
        }

    def breath_to_emotion_sync(
        self, text: str, emotions: Dict[str, float]
    ) -> Dict[str, Any]:
        inhale = self.detect_inhale_points(text)
        short = self.detect_short_breath(text)
        density = len(inhale) / max(1, len(short))
        dominant = max(emotions, key=emotions.get) if emotions else "neutral"
        return {
            "breath_density": round(density, 3),
            "dominant_emotion": dominant,
            "sync_score": round(min(1.0, emotions.get(dominant, 0) + density * 0.1), 3),
        }


class BPMEngine:
    """Expose BPM - related helpers from the lyric meter."""

    def __init__(self) -> None:
        self._meter = LyricMeter()

    def text_bpm_estimation(self, text: str) -> int:
        analysis = self._meter.analyze(normalize_text_preserve_symbols(text))
        return int(round(analysis.get("global_bpm", 120.0)))

    def emotion_bpm_mapping(
        self, emotions: Dict[str, float], *, base_bpm: int | None = None
    ) -> Dict[str, Any]:
        if not emotions:
            return {"map": {}, "target_bpm": base_bpm or 120, "target_energy": 0.5}
        base = float(base_bpm or 120)
        mapping: Dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0
        for emotion, weight in emotions.items():
            shift = (weight - 0.3) * 40
            mapping[emotion] = round(base + shift, 1)
            weighted_sum += mapping[emotion] * weight
            total_weight += weight
        target_bpm = round(weighted_sum / max(total_weight, 1e-6), 1)
        target_energy = round(min(1.0, max(0.0, (target_bpm - 90) / 80)), 3)
        return {
            "map": mapping,
            "target_bpm": target_bpm,
            "target_energy": target_energy,
        }

    def meaning_bpm_curve(
        self, sections: Sequence[str], *, base_bpm: int | None = None
    ) -> List[float]:
        if not sections:
            return []
        base = float(base_bpm or 120)
        curve: List[float] = []
        for section in sections:
            words = _words(section)
            syllables = sum(len(_VOWEL_RE.findall(word)) for word in words)
            density = syllables / max(1, len(words))
            curve.append(round(base + (density - 3) * 8, 2))
        return curve

    def breathing_bpm_integration(
        self, breathing: Dict[str, Any], base_bpm: int
    ) -> Dict[str, Any]:
        inhale = breathing.get("inhale_points", [])
        spasm = breathing.get("spasm_points", [])
        modifier = len(spasm) * 2 - len(inhale)
        adjusted = max(60.0, base_bpm + modifier)
        return {
            "base_bpm": base_bpm,
            "adjusted_bpm": round(adjusted, 1),
            "breathing_modifier": modifier,
        }

    def poly_rhythm_detection(self, bpm_curve: Sequence[float]) -> Dict[str, Any]:
        if not bpm_curve:
            return {"has_poly_rhythm": False, "variance": 0.0}
        variance = max(bpm_curve) - min(bpm_curve)
        return {"has_poly_rhythm": variance > 15.0, "variance": round(variance, 2)}


class MeaningVelocityEngine:
    """Estimate semantic speed and fractures between sections."""

    def semantic_shift_detection(self, sections: Sequence[str]) -> Dict[str, Any]:
        shifts: List[Dict[str, Any]] = []
        for idx in range(1, len(sections)):
            prev_words = Counter(_words(sections[idx - 1]))
            current_words = Counter(_words(sections[idx]))
            if not prev_words or not current_words:
                overlap = 0.0
            else:
                common = sum((prev_words & current_words).values())
                total = sum((prev_words | current_words).values())
                overlap = common / max(total, 1)
            shifts.append({"index": idx, "overlap": round(overlap, 3)})
        return {"shifts": shifts}

    def meaning_acceleration(self, curve: Sequence[float]) -> List[float]:
        acceleration: List[float] = []
        for idx in range(1, len(curve)):
            acceleration.append(round(curve[idx] - curve[idx - 1], 3))
        return acceleration

    def meaning_fracture_detection(
        self, shifts: Sequence[Dict[str, Any]]
    ) -> Dict[str, Any]:
        fractures = [shift for shift in shifts if shift.get("overlap", 0.0) < 0.15]
        return {"fractures": fractures, "count": len(fractures)}

    def meaning_curve_generation(self, sections: Sequence[str]) -> List[float]:
        if not sections:
            return []
        curve: List[float] = []
        for section in sections:
            unique_words = len(set(_words(section)))
            total_words = len(_words(section)) or 1
            curve.append(round(unique_words / total_words, 3))
        return curve


class TonalityEngine:
    """Provide basic tonal reasoning for the v6 pipeline."""

    def __init__(self) -> None:
        self._tone = ToneSyncEngine()

    def mode_detection(
        self, emotions: Dict[str, float], tlp: Dict[str, float]
    ) -> Dict[str, Any]:
        love = emotions.get("joy", 0) + emotions.get("peace", 0)
        sadness = emotions.get("sadness", 0)
        anger = emotions.get("anger", 0)
        if sadness > max(love, anger):
            mode = "minor"
        elif anger > love:
            mode = "modal"
        else:
            mode = "major"
        confidence = round(max(love, sadness, anger), 3)
        return {
            "mode": mode,
            "confidence": confidence,
            "tlp_cf": tlp.get("conscious_frequency"),
        }

    def major_minor_classifier(self, sections: Sequence[str], mode: str) -> str:
        if not sections:
            return mode
        melancholy_lines = sum(
            """sad""" in section.lower() or """тоск""" in section.lower()
            for section in sections
        )
        if melancholy_lines > len(sections) // 2:
            return "minor"
        if any(
            "rise" in section.lower() or "свет" in section.lower()
            for section in sections
        ):
            return "major"
        return mode

    def section_key_selection(self, sections: Sequence[str], mode: str) -> List[str]:
        keys = []
        palette = ["C", "G", "D", "A", "E", "B", "F#", "C#"]
        for idx, section in enumerate(sections):
            seed = sum(ord(ch) for ch in section) + idx
            key = palette[seed % len(palette)]
            keys.append(f"{key} {mode}")
        return keys

    def modal_shift_detection(self, section_keys: Sequence[str]) -> Dict[str, Any]:
        if not section_keys:
            return {"shifts": [], "count": 0}
        shifts = []
        for idx in range(1, len(section_keys)):
            prev = section_keys[idx - 1]
            current = section_keys[idx]
            if prev != current:
                shifts.append({"index": idx, "from": prev, "to": current})
        return {"shifts": shifts, "count": len(shifts)}

    def key_transition_curve(self, section_keys: Sequence[str]) -> List[str]:
        return list(section_keys)


class InstrumentationEngine:
    """Bridge the convenience helpers from :mod:`studiocore.instrument`."""

    def __init__(self) -> None:
        self._library = InstrumentLibrary()

    def instrument_selection(self, **kwargs: Any) -> Dict[str, Any]:
        return _instrument_selection(**kwargs)

    def instrument_based_on_emotion(
        self, emotions: Dict[str, float], **kwargs: Any
    ) -> Dict[str, Any]:
        return _instrument_based_on_emotion(emotions, **kwargs)

    def instrument_based_on_voice(
        self, voice_profile: str | None, **kwargs: Any
    ) -> Dict[str, Any]:
        return _instrument_based_on_voice(voice_profile, **kwargs)

    def instrument_color_sync(
        self, color_profile: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        return _instrument_color_sync(color_profile, **kwargs)

    def instrument_rhythm_sync(self, bpm: float, **kwargs: Any) -> Dict[str, Any]:
        return _instrument_rhythm_sync(bpm, **kwargs)


class REM_Synchronizer:
    """Coordinate cross - layer alignment for REM (Rhythmic Emotional Matrix)."""

    def detect_layer_conflicts(
        self,
        structure: Dict[str, Any],
        bpm_curve: Sequence[float],
        instrumentation: Dict[str, Any],
    ) -> Dict[str, Any]:
        sections = structure.get("sections", [])
        conflict_notes: List[str] = []
        level = 0.0
        if sections and bpm_curve and len(sections) != len(bpm_curve):
            level += 0.3
            conflict_notes.append("BPM curve length differs from section count.")
        energy = instrumentation.get("energy", 0.5)
        if energy > 0.8 and bpm_curve and min(bpm_curve) < 90:
            level += 0.4
            conflict_notes.append("High instrumental energy with slow tempo segments.")
        return {
            "has_conflict": level > 0.0,
            "conflict_level": round(level, 2),
            "notes": conflict_notes,
        }

    def resolve_layer_conflicts(self, conflicts: Dict[str, Any]) -> Dict[str, Any]:
        if not conflicts.get("has_conflict"):
            return {"actions": ["No adjustments required."], "status": "stable"}
        actions = [
            "Re - balance percussion energy",
            "Adjust arrangement dynamics",
        ]
        return {"actions": actions, "status": "mitigated"}

    def assign_dominant_layer(
        self, *, structure: Dict[str, Any], emotion: Dict[str, Any]
    ) -> Dict[str, Any]:
        sections = structure.get("sections", [])
        dominant_emotion = max(
            emotion.get("profile", {"peace": 1.0}),
            key=emotion.get("profile", {"peace": 1.0}).get,
        )
        if len(sections) >= 4 and dominant_emotion in {"joy", "epic"}:
            layer = "rhythm"
        elif dominant_emotion in {"sadness", "fear"}:
            layer = "melody"
        else:
            layer = "harmonic"
        return {"layer": layer, "rationale": f"Dominant emotion '{dominant_emotion}'"}

    def align_layers_for_final_output(
        self,
        structure: Dict[str, Any],
        instrumentation: Dict[str, Any],
        tonality: Dict[str, Any],
    ) -> Dict[str, Any]:
        section_keys = tonality.get("section_keys", [])
        return {
            "sections": structure.get("sections", []),
            "instrument_palette": instrumentation.get("palette", []),
            "section_keys": section_keys,
        }


class ZeroPulseEngine:
    """Handle silent segments that should be preserved in the arrangement."""

    def detect_zero_pulse(self, text: str) -> Dict[str, Any]:
        sections = _section_texts(text)
        zero_sections = [
            idx
            for idx, section in enumerate(sections)
            if not section.strip() or "[silence]" in section.lower()
        ]
        return {"has_zero_pulse": bool(zero_sections), "sections": zero_sections}

    def vacuum_beat_state(self, text: str) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        state = "active" if zero["has_zero_pulse"] else "inactive"
        return {"state": state, "count": len(zero["sections"])}

    def silence_as_emotion(
        self, text: str, emotions: Dict[str, float]
    ) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        peace = emotions.get("peace", 0.0)
        return {
            "aligned_emotion": "peace" if peace >= 0.3 else "neutral",
            "zero_pulse_sections": zero["sections"],
        }

    def silence_as_transition(self, text: str) -> Dict[str, Any]:
        zero = self.detect_zero_pulse(text)
        transitions = [
            {"from": idx, "to": idx + 1, "type": "silence - gap"}
            for idx in zero["sections"]
        ]
        return {"transitions": transitions}


class CommandInterpreter:
    """Parse inline commands that control arrangement parameters."""

    def detect_commands_in_text(self, text: str) -> List[Dict[str, Any]]:
        commands: List[Dict[str, Any]] = []
        for match in _COMMAND_RE.finditer(text):
            commands.append(
                {
                    "type": match.group("name").lower(),
                    "value": match.group("value").strip(),
                    "raw": match.group(0),
                    "position": match.start(),
                }
            )
        return commands

    def _extract_command(
        self, commands: Iterable[Dict[str, Any]], names: Sequence[str]
    ) -> Dict[str, Any] | None:
        for command in commands:
            if command.get("type") in names:
                return command
        return None

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_number_list(value: str, allow_arrow: bool = False) -> List[float]:
        if not value:
            return []
        separators = ["/", ",", "→", "-", " "]
        if allow_arrow:
            normalized = value.replace("->", "→").replace("=>", "→")
        else:
            normalized = value
        for sep in separators:
            normalized = normalized.replace(sep, " ")
        values: List[float] = []
        for token in normalized.split():
            num = CommandInterpreter._to_float(token)
            if num is not None:
                values.append(num)
        return values

    def execute_bpm_commands(
        self, commands: Iterable[Dict[str, Any]], base_bpm: int | None = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"bpm": base_bpm}
        fallback = base_bpm if base_bpm is not None else 120
        offset = 0.0
        parallels: List[float] = []
        fractures: List[float] = []
        for command in commands:
            ctype = (command.get("type") or "").lower()
            value = command.get("value", "")
            if ctype in {"bpm", "tempo", "set bpm"}:
                parsed = self._to_float(value)
                if parsed is not None:
                    payload["bpm"] = parsed
                    payload["source"] = command.get("raw")
            elif ctype == "raise bpm":
                delta = self._to_float(value)
                if delta is not None:
                    offset += delta
                    payload["source"] = command.get("raw")
            elif ctype == "lower bpm":
                delta = self._to_float(value)
                if delta is not None:
                    offset -= delta
                    payload["source"] = command.get("raw")
            elif ctype in {"parallel bpm", "parallel"}:
                parallels = self._parse_number_list(str(value))
            elif ctype in {"fracture rhythm", "fracture"}:
                fractures = self._parse_number_list(str(value), allow_arrow=True)
        base = payload.get("bpm", fallback)
        if base is not None and offset:
            payload["bpm"] = max(1.0, float(base) + offset)
        if parallels:
            payload["parallel"] = parallels
        if fractures:
            payload["fracture"] = fractures
        return payload

    def execute_key_commands(
        self, commands: Iterable[Dict[str, Any]], default_key: str | None = None
    ) -> Dict[str, Any]:
        command = self._extract_command(commands, ["key", "scale", "set key"])
        if not command:
            return {"key": default_key}
        return {"key": command["value"], "source": command["raw"]}

    def execute_rhythm_commands(
        self, commands: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        command = self._extract_command(commands, ["rhythm", "groove", "set intensity"])
        if not command:
            return {"rhythm": None}
        return {"rhythm": command["value"], "source": command["raw"]}

    def execute_emotion_commands(
        self, commands: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        emotion_cmd = self._extract_command(commands, ["emotion", "set emotion"])
        mood_cmd = self._extract_command(commands, ["mood", "set mood"])
        intensity_cmd = self._extract_command(commands, ["intensity", "set intensity"])
        result: Dict[str, Any] = {}
        if emotion_cmd:
            result["emotion"] = emotion_cmd["value"]
            result.setdefault("source", emotion_cmd.get("raw"))
        if mood_cmd:
            result["mood"] = mood_cmd["value"]
            result.setdefault("source", mood_cmd.get("raw"))
        if intensity_cmd:
            result["intensity"] = intensity_cmd["value"]
            result.setdefault("source", intensity_cmd.get("raw"))
        if not result:
            result["emotion"] = None
        return result

    def execute_style_commands(
        self, commands: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for command in commands:
            ctype = command.get("type")
            if ctype in {"set genre", "genre"}:
                result["genre"] = command.get("value")
                result.setdefault("source", []).append(command.get("raw"))
            elif ctype in {"set vocal", "vocal"}:
                result["vocal"] = command.get("value")
                result.setdefault("source", []).append(command.get("raw"))
            elif ctype in {"set mood", "mood"}:
                result["mood"] = command.get("value")
                result.setdefault("source", []).append(command.get("raw"))
            elif ctype in {"set intensity", "intensity"}:
                result["intensity"] = command.get("value")
                result.setdefault("source", []).append(command.get("raw"))
        if "source" in result and isinstance(result["source"], list):
            result["source"] = ", ".join(filter(None, result["source"]))
        return result


class StyleEngine:
    """Assemble stylistic guidance for the arrangement and prompts."""

    GENRE_MAP = {
        "joy": "indie pop",
        "sadness": "ambient ballad",
        "anger": "industrial rock",
        "fear": "cinematic darkwave",
        "peace": "neo - classical",
        "epic": "epic orchestral",
    }

    def genre_selection(self, emotions: Dict[str, float], tlp: Dict[str, float]) -> str:
        if not emotions:
            return "ambient"
        dominant = max(emotions, key=emotions.get)
        return self.GENRE_MAP.get(dominant, "experimental")

    def mood_selection(self, emotions: Dict[str, float], tlp: Dict[str, float]) -> str:
        cf = tlp.get("conscious_frequency", 0.5)
        if cf > 0.7:
            return "uplifting"
        if cf < 0.4:
            return "melancholic"
        return "reflective"

    def instrumentation_style(self, instrumentation: Dict[str, Any]) -> str:
        palette = (
            instrumentation.get("selected") or instrumentation.get("toolkit") or []
        )
        return ", ".join(palette) if palette else "minimal instrumentation"

    def vocal_style(self, vocal: Dict[str, Any]) -> str:
        profile = vocal.get("style", "lyrical")
        tone = vocal.get("tone", "balanced")
        return f"{tone} {profile}"

    def visual_style(self, color_profile: Dict[str, Any]) -> str:
        primary = color_profile.get("primary_color") or EMOTION_COLOR_MAP["neutral"][0]
        accent = color_profile.get("accent_color") or EMOTION_COLOR_MAP["neutral"][-1]
        return f"{primary} with {accent}"

    def tone_style(self, tonality: Dict[str, Any]) -> str:
        return f"{tonality.get('mode', 'major')} mood, keys {', '.join(tonality.get('section_keys', []))}"

    def final_style_prompt_build(
        self,
        *,
        genre: str,
        mood: str,
        instrumentation: str,
        vocal: str,
        visual: str,
        tone: str,
    ) -> str:
        entries = [
            ("GENRE", genre),
            ("MOOD", mood),
            ("VOCALS", vocal),
            ("INSTRUMENTS", instrumentation),
            ("VISUALS", visual),
            ("TONALITY", tone),
        ]
        prompt_parts = [f"({label}: {value})" for label, value in entries if value]
        prompt_parts.append(f"(INSTRUMENTAL_BREAK: {instrumentation or 'dynamic'})")
        prompt_parts.append("[END]")
        return " ".join(prompt_parts)


class UserOverrideEngine:
    """Bridge between overrides and the logical engine payloads."""

    def resolve_bpm(
        self, manager: UserOverrideManager, auto_bpm: float | None
    ) -> float | None:
        return manager.resolve_bpm(auto_bpm)

    def apply_to_rhythm(
        self, rhythm_payload: Dict[str, Any], manager: UserOverrideManager
    ) -> Dict[str, Any]:
        return manager.apply_to_rhythm(rhythm_payload)

    def apply_to_style(
        self, style_payload: Dict[str, Any], manager: UserOverrideManager
    ) -> Dict[str, Any]:
        return manager.apply_to_style(style_payload)

    def apply_to_vocals(
        self, vocal_payload: Dict[str, Any], manager: UserOverrideManager
    ) -> Dict[str, Any]:
        return manager.apply_to_vocals(vocal_payload)


class UserAdaptiveSymbiosisEngine:
    """Merge user intent with automatically generated layers."""

    def collect_user_params(self, manager: UserOverrideManager) -> Dict[str, Any]:
        return manager.debug_summary()

    def merge_user_with_auto_core(
        self, manager: UserOverrideManager, auto_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged = dict(auto_payload)
        merged["user"] = self.collect_user_params(manager)
        return merged

    def recalculate_rhythm_under_user_settings(
        self, manager: UserOverrideManager, rhythm_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return manager.apply_to_rhythm(rhythm_payload)

    def recalculate_tone_under_user_settings(
        self, manager: UserOverrideManager, tonality_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = dict(tonality_payload)
        if manager.overrides.key:
            payload["manual_key"] = manager.overrides.key
            payload["mode"] = payload.get("mode") or "user"
        return payload

    def recalculate_vocals_under_user_settings(
        self, manager: UserOverrideManager, vocal_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return manager.apply_to_vocals(vocal_payload)

    def recalculate_instrumental_under_user_settings(
        self, manager: UserOverrideManager, instrumentation_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = dict(instrumentation_payload)
        if manager.overrides.instrumentation:
            payload["palette"] = list(manager.overrides.instrumentation)
            payload["source"] = "user"
        return payload

    def build_final_symbiosis_state(
        self,
        manager: UserOverrideManager,
        payload: Dict[str, Any],
        *,
        applied_overrides: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if applied_overrides is not None:
            snapshot = self.merge_user_with_auto_core(manager, payload)
            snapshot["applied_overrides"] = applied_overrides
            snapshot["rhythm"] = payload.get("bpm", {})
            snapshot["tonality"] = payload.get("tonality", {})
            snapshot["vocal"] = payload.get("vocal", {})
            snapshot["instrumentation"] = payload.get("instrumentation", {})
            return snapshot

        rhythm = self.recalculate_rhythm_under_user_settings(
            manager, payload.get("bpm", {})
        )
        tone = self.recalculate_tone_under_user_settings(
            manager, payload.get("tonality", {})
        )
        vocal = self.recalculate_vocals_under_user_settings(
            manager, payload.get("vocal", {})
        )
        instrumentation = self.recalculate_instrumental_under_user_settings(
            manager, payload.get("instrumentation", {})
        )
        merged = self.merge_user_with_auto_core(manager, payload)
        merged.update(
            {
                "rhythm": rhythm,
                "tonality": tone,
                "vocal": vocal,
                "instrumentation": instrumentation,
            }
        )
        return merged


class LyricsAnnotationEngine:
    """Produce lightweight annotations for UI or downstream exporters."""

    def add_vocal_annotations(
        self, sections: Sequence[str], vocal: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        intensity_curve = vocal.get("intensity_curve", [])
        annotations: List[Dict[str, Any]] = []
        for idx, section in enumerate(sections):
            intensity = (
                intensity_curve[idx]
                if idx < len(intensity_curve)
                else vocal.get("average_intensity", 0.5)
            )
            annotations.append(
                {
                    "section": idx,
                    "type": "vocal",
                    "intensity": round(float(intensity), 3),
                }
            )
        return annotations

    def add_breath_annotations(
        self, sections: Sequence[str], breathing: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        inhale = set(breathing.get("inhale_points", []))
        return [
            {
                "section": idx,
                "type": "breath",
                "marker": "inhale" if idx in inhale else "flow",
            }
            for idx in range(len(sections))
        ]

    def add_tonal_annotations(
        self, sections: Sequence[str], tonality: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        keys = tonality.get("section_keys", [])
        return [
            {
                "section": idx,
                "type": "tonality",
                "key": keys[idx] if idx < len(keys) else tonality.get("mode"),
            }
            for idx in range(len(sections))
        ]

    def add_emotional_annotations(
        self, sections: Sequence[str], emotions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        profile = emotions.get("profile", {})
        dominant = max(profile, key=profile.get) if profile else "neutral"
        return [
            {"section": idx, "type": "emotion", "dominant": dominant}
            for idx in range(len(sections))
        ]

    def add_rhythm_annotations(
        self, sections: Sequence[str], bpm_curve: Sequence[float]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "section": idx,
                "type": "rhythm",
                "bpm": bpm_curve[idx] if idx < len(bpm_curve) else None,
            }
            for idx in range(len(sections))
        ]


class FinalCompiler:
    """Merge logical engine outputs into a convenient response payload."""

    def merge_all_layers(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = {
            "engine": "StudioCoreV6",
            "legacy": payload.get("legacy"),
            "structure": payload.get("structure"),
            "emotion": payload.get("emotion"),
            "color": payload.get("color"),
            "vocal": payload.get("vocal"),
            "breathing": payload.get("breathing"),
            "bpm": payload.get("bpm"),
            "meaning": payload.get("meaning"),
            "tonality": payload.get("tonality"),
            "instrumentation": payload.get("instrumentation"),
            "rem": payload.get("rem"),
            "zero_pulse": payload.get("zero_pulse"),
            "style": payload.get("style"),
            "commands": payload.get("commands"),
        }
        return merged

    def generate_final_structure(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        structure_block = payload.get("structure", {})
        sections = structure_block.get("sections", [])
        result = {
            "section_count": len(sections),
            "sections": sections,
            "intro": structure_block.get("intro"),
            "chorus": structure_block.get("chorus"),
            "outro": structure_block.get("outro"),
        }
        # Сохраняем headers если они есть
        if structure_block.get("headers"):
            result["headers"] = structure_block["headers"]
        return result

    def generate_final_prompt(self, payload: Dict[str, Any]) -> str:
        style = payload.get("style", {})
        return style.get("prompt", "")

    def generate_final_annotations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return payload.get("annotations", {})

    def consistency_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = []
        if not payload.get("structure", {}).get("sections"):
            issues.append("Structure lacks sections")
        if not payload.get("emotion", {}).get("profile"):
            issues.append("Emotion profile missing")
        if not payload.get("style", {}).get("prompt"):
            issues.append("Style prompt missing")
        return {"issues": issues, "is_consistent": not issues}


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
