# -*- coding: utf-8 -*-
"""Rhythm analysis engine for StudioCore v6.

The engine extracts tempo information from lyric structure, respecting hints
provided by the author (e.g. ``[BPM: 120]``) while still analysing the natural
flow of the text. The output is a structured ``RhythmAnalysis`` dictionary that
contains global tempo, per-section statistics, and micro-variations that other
modules (emotion, meaning, breathing) can consume.
"""

from __future__ import annotations

import math
import re
import statistics
from typing import Dict, List, Optional, Tuple, TypedDict

from .text_utils import extract_sections

PUNCT_WEIGHTS = {
    "!": 0.6,
    "?": 0.4,
    ".": 0.1,
    ",": 0.05,
    "…": 0.5,
    "—": 0.2,
    ":": 0.15,
    ";": 0.1,
}

HEADER_BPM_RE = re.compile(r"\[\s*BPM\s*:?\s*(?P<bpm>[0-9]{2,3}(?:\.[0-9]+)?)\s*\]", re.I)
SECTION_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "INTRO": ("intro", "интро", "start", "opening"),
    "VERSE": ("verse", "куплет", "kup", "strofa", "куплет"),
    "PRE_CHORUS": ("pre-chorus", "prechorus", "преприпев"),
    "CHORUS": ("chorus", "припев", "hook", "drop"),
    "POST_CHORUS": ("post-chorus", "postchorus", "постприпев"),
    "BRIDGE": ("bridge", "бридж", "middle 8", "middle8"),
    "BREAKDOWN": ("break", "breakdown", "drop", "beat switch"),
    "OUTRO": ("outro", "финал", "ending", "концовка"),
}

MIN_BPM = 60.0
MAX_BPM = 180.0
MICRO_MIN = 40.0
MICRO_MAX = 200.0


class RhythmSection(TypedDict, total=False):
    """Per-section rhythm metrics."""

    mean_bpm: float
    micro_curve: List[float]
    tension: float
    phrase_pattern: List[int]
    line_count: int


class RhythmConflict(TypedDict, total=False):
    """Diagnostic data about BPM conflicts."""

    has_conflict: bool
    conflict_level: float
    notes: str


class RhythmAnalysis(TypedDict, total=False):
    """Structured output of the rhythm engine."""

    global_bpm: float
    header_bpm: Optional[float]
    estimated_bpm: Optional[float]
    density_bpm: Optional[float]
    sections: Dict[str, RhythmSection]
    section_order: List[str]
    conflict: RhythmConflict


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def resolve_global_bpm(header_bpm: Optional[float], estimated_bpm: Optional[float]) -> float:
    """Blend BPM estimates while respecting the explicit header value."""

    if header_bpm is not None:
        if estimated_bpm is None:
            return header_bpm
        diff = abs(header_bpm - estimated_bpm)
        if diff > 30:
            # strong disagreement — keep the author's intent fully
            return header_bpm
        return header_bpm * 0.7 + estimated_bpm * 0.3

    if estimated_bpm is not None:
        return estimated_bpm

    return 120.0


def calc_tension(curve: List[float]) -> float:
    """Normalised rhythmic tension based on micro-curve variance."""

    if len(curve) <= 1:
        return 0.0
    spread = statistics.pstdev(curve)
    return clamp(spread / 30.0, 0.0, 1.0)


class LyricMeter:
    """Adaptive rhythm analyser with per-section awareness."""

    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")

    def _syllables(self, s: str) -> int:
        return max(1, sum(1 for ch in s if ch in self.vowels))

    def _punct_energy(self, text: str) -> float:
        return sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)

    def _extract_header_bpm(self, text: str) -> Optional[float]:
        match = HEADER_BPM_RE.search(text)
        if not match:
            return None
        try:
            return float(match.group("bpm"))
        except (TypeError, ValueError):
            return None

    def _strip_header_lines(self, text: str) -> str:
        lines = []
        for ln in text.split("\n"):
            if HEADER_BPM_RE.search(ln):
                continue
            lines.append(ln)
        return "\n".join(lines).strip()

    def _normalize_section_name(self, tag: str, counters: Dict[str, int], index: int) -> str:
        raw = tag.strip()
        tag_low = raw.lower()
        for canonical, keywords in SECTION_KEYWORDS.items():
            if any(k in tag_low for k in keywords):
                counters[canonical] = counters.get(canonical, 0) + 1
                if canonical in {"INTRO", "OUTRO", "BRIDGE"}:
                    count = counters[canonical]
                    return canonical if count == 1 else f"{canonical}_{count}"
                return f"{canonical}_{counters[canonical]}"

        # Try to preserve explicit numbering: "Verse 2" -> VERSE_2
        number_match = re.search(r"(intro|verse|chorus|bridge|outro|куплет|припев)[^0-9]*([0-9]+)", tag_low)
        if number_match:
            base = number_match.group(1)
            num = number_match.group(2)
            for canonical, keywords in SECTION_KEYWORDS.items():
                if any(base.startswith(k) for k in keywords):
                    counters[canonical] = counters.get(canonical, 0) + 1
                    return f"{canonical}_{num}"

        base = re.sub(r"[^A-Za-z0-9]+", "_", raw.upper()).strip("_") or f"SECTION_{index + 1}"
        counters[base] = counters.get(base, 0) + 1
        if counters[base] > 1:
            return f"{base}_{counters[base]}"
        return base

    def _build_sections(self, text: str) -> Dict[str, str]:
        sections = extract_sections(text)
        if not sections:
            clean_lines = [ln for ln in text.split("\n") if ln.strip()]
            return {"BODY": "\n".join(clean_lines)} if clean_lines else {}

        counters: Dict[str, int] = {}
        structured: Dict[str, str] = {}
        for idx, section in enumerate(sections):
            tag = section.get("tag", f"Section {idx + 1}")
            key = self._normalize_section_name(tag, counters, idx)
            body_lines = [ln for ln in section.get("lines", []) if ln.strip()]
            if body_lines:
                structured[key] = "\n".join(body_lines)
        return structured

    def _density_bpm(
        self,
        text: str,
        emotions: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        tlp: Optional[Dict[str, float]] = None,
        emotion_weight: float = 0.3,
    ) -> float:
        emotions = emotions or {}
        tlp = tlp or {}
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return 0.0

        syllables = [self._syllables(l) for l in lines]
        avg_syll = sum(syllables) / len(lines)

        base = 60 + 120 / (1 + math.exp((avg_syll - 8) / 2.5 * 0.8))

        p_energy = self._punct_energy(text)
        base += min(18.0, p_energy * 3.5)

        anger = emotions.get("anger", 0.0)
        epic = emotions.get("epic", 0.0)
        joy = emotions.get("joy", 0.0)
        sadness = emotions.get("sadness", 0.0)
        fear = emotions.get("fear", 0.0)
        peace = emotions.get("peace", 0.0)

        energy_factor = clamp(1 + (anger + epic + joy - sadness - fear) * 0.6, 0.8, 1.4)
        accel = 10.0 * (0.7 * anger + 0.6 * epic + 0.3 * joy)
        brake = 10.0 * (0.6 * sadness + 0.5 * fear + 0.2 * peace)
        bpm = (base + accel - brake) * energy_factor

        if cf is not None:
            bpm += (cf - 0.8) * 100 * emotion_weight

        if tlp:
            pain_boost = tlp.get("Pain", 0.0) * 50 * emotion_weight
            love_smooth = tlp.get("Love", 0.0) * 25 * emotion_weight
            truth_drive = tlp.get("Truth", 0.0) * 20 * emotion_weight
            bpm += pain_boost + truth_drive - love_smooth

        n_lines = len(lines)
        if n_lines <= 4:
            bpm += 4
        elif n_lines > 16:
            bpm -= 3

        return clamp(bpm, MIN_BPM, MAX_BPM)

    def _heuristic_section_bpm(self, section_text: str) -> float:
        lines = [l.strip() for l in section_text.split("\n") if l.strip()]
        if not lines:
            return 0.0

        phrase_lengths = [max(1, len(line.split())) for line in lines]
        total_words = sum(phrase_lengths)
        avg_words = total_words / len(phrase_lengths)
        char_count = sum(len(line) for line in lines)
        avg_word_len = char_count / max(total_words, 1)

        punctuation_hits = sum(line.count(",") + line.count(";") + line.count(":") for line in lines)
        accent_hits = sum(line.count("!") + line.count("?") for line in lines)
        dash_hits = sum(line.count("—") + line.count("-") for line in lines)
        ellipsis_hits = sum(line.count("…") for line in lines)
        breath_pauses = sum(line.count("/") for line in lines)

        variation = statistics.pstdev(phrase_lengths) if len(phrase_lengths) > 1 else 0.0

        base = 58.0 + avg_words * 3.2
        base += variation * 1.5
        base += punctuation_hits * 1.2
        base += accent_hits * 4.0
        base += dash_hits * 0.8
        base += breath_pauses * 2.0
        base -= ellipsis_hits * 3.5
        base -= max(0.0, (avg_word_len - 5.5) * 1.7)

        short_lines = sum(1 for w in phrase_lengths if w <= 4)
        long_lines = sum(1 for w in phrase_lengths if w >= 11)
        base += short_lines * 2.0
        base -= long_lines * 1.6

        return clamp(base, MIN_BPM - 15.0, MAX_BPM + 25.0)

    def _blend_section_bpm(
        self,
        density_bpm: float,
        heuristic_bpm: float,
        global_density: float,
    ) -> float:
        values: List[Tuple[float, float]] = []
        if density_bpm > 0:
            values.append((density_bpm, 0.45))
        if heuristic_bpm > 0:
            values.append((heuristic_bpm, 0.45 if density_bpm > 0 else 0.65))
        if global_density > 0:
            values.append((global_density, 0.10 if values else 1.0))

        if not values:
            return global_density or 0.0

        total_weight = sum(weight for _, weight in values)
        blended = sum(val * weight for val, weight in values) / total_weight
        return clamp(blended, MIN_BPM - 10.0, MAX_BPM + 15.0)

    def _build_micro_curve(self, section_text: str, section_bpm: float) -> List[float]:
        lines = [l.strip() for l in section_text.split("\n") if l.strip()]
        if not lines:
            return []

        phrase_lengths = [max(1, len(line.split())) for line in lines]
        avg_phrase = sum(phrase_lengths) / len(phrase_lengths)
        curve: List[float] = []

        for idx, line in enumerate(lines):
            length = phrase_lengths[idx]
            energy = self._punct_energy(line)
            accent = line.count("!") + line.count("?")
            ellipsis = line.count("…")
            dash = line.count("—") + line.count("-")
            comma_breaks = line.count(",")

            shift = 0.0
            shift += (avg_phrase - length) * 2.0
            if length <= 3:
                shift += 6.0
            if length >= 12:
                shift -= 5.0

            shift += energy * 10.0
            shift += accent * 4.5
            shift -= ellipsis * 4.0
            shift += dash * 1.2
            shift += comma_breaks * 0.8

            if idx > 0:
                prev_len = phrase_lengths[idx - 1]
                shift -= (length - prev_len) * 0.9

            local_bpm = clamp(section_bpm + shift, MICRO_MIN, MICRO_MAX)
            curve.append(local_bpm)

        return curve

    def _phrase_pattern(self, section_text: str) -> List[int]:
        return [max(1, len(line.split())) for line in section_text.split("\n") if line.strip()]

    def analyze(
        self,
        text: str,
        *,
        structured_sections: Optional[Dict[str, str]] = None,
        header_bpm: Optional[float] = None,
        emotions: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        tlp: Optional[Dict[str, float]] = None,
        emotion_weight: float = 0.3,
    ) -> RhythmAnalysis:
        emotions = emotions or {}
        tlp = tlp or {}

        header = header_bpm if header_bpm is not None else self._extract_header_bpm(text)
        text_without_header = self._strip_header_lines(text)

        sections = structured_sections or self._build_sections(text_without_header)
        if not sections:
            sections = {"BODY": text_without_header}

        density_global = self._density_bpm(
            text_without_header,
            emotions=emotions,
            cf=cf,
            tlp=tlp,
            emotion_weight=emotion_weight,
        )

        section_results: Dict[str, RhythmSection] = {}
        section_bpms: List[float] = []
        for name, body in sections.items():
            density_section = self._density_bpm(body, emotion_weight=0.0)
            heuristic_section = self._heuristic_section_bpm(body)
            section_bpm = self._blend_section_bpm(density_section, heuristic_section, density_global)
            micro_curve = self._build_micro_curve(body, section_bpm)
            section_results[name] = {
                "mean_bpm": section_bpm,
                "micro_curve": micro_curve,
                "tension": calc_tension(micro_curve),
                "phrase_pattern": self._phrase_pattern(body),
                "line_count": len([ln for ln in body.split("\n") if ln.strip()]),
            }
            if section_bpm > 0:
                section_bpms.append(section_bpm)

        estimated_from_sections = (
            sum(section_bpms) / len(section_bpms) if section_bpms else None
        )

        if estimated_from_sections is not None and density_global > 0:
            estimated_global = 0.65 * estimated_from_sections + 0.35 * density_global
        else:
            estimated_global = estimated_from_sections or (density_global if density_global > 0 else None)

        global_bpm = resolve_global_bpm(header, estimated_global)
        global_bpm = clamp(global_bpm, MIN_BPM, MAX_BPM)

        conflict_level = 0.0
        if header is not None and estimated_global is not None:
            conflict_level = clamp(abs(header - estimated_global) / 60.0, 0.0, 1.0)

        conflict: RhythmConflict = {
            "has_conflict": conflict_level > 0.2,
            "conflict_level": conflict_level,
            "notes": f"header={header}, estimated={estimated_global}, density={density_global}, resolved={global_bpm}",
        }

        return RhythmAnalysis(
            global_bpm=global_bpm,
            header_bpm=header,
            estimated_bpm=estimated_global,
            density_bpm=density_global if density_global > 0 else None,
            sections=section_results,
            section_order=list(section_results.keys()),
            conflict=conflict,
        )

    def bpm_from_density(
        self,
        text: str,
        emotions: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        tlp: Optional[Dict[str, float]] = None,
        emotion_weight: float = 0.3,
    ) -> int:
        analysis = self.analyze(
            text,
            emotions=emotions,
            cf=cf,
            tlp=tlp,
            emotion_weight=emotion_weight,
        )
        return int(round(analysis["global_bpm"]))


__all__ = [
    "LyricMeter",
    "RhythmAnalysis",
    "RhythmSection",
    "RhythmConflict",
    "resolve_global_bpm",
    "calc_tension",
]
