"""Advanced section detection helpers mandated by the Codex specification."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Sequence


class SectionIntelligenceEngine:
    """Detect chorus/mantra/transition cues beyond naive splitting."""

    def __init__(self) -> None:
        self._last_sections: List[str] = []

    def _ensure_sections(self, sections: Sequence[str] | None, text: str) -> List[str]:
        if sections:
            cleaned = [section.strip() for section in sections if section]
        else:
            cleaned = [block.strip() for block in text.split("\n\n") if block.strip()]
        self._last_sections = cleaned
        return cleaned

    def detect_repeated_motif(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        motif_counter: Counter[str] = Counter()
        for section in sections:
            for line in section.splitlines():
                motif = line.strip().lower()
                if motif:
                    motif_counter[motif] += 1
        repeated = [line for line, count in motif_counter.items() if count > 1]
        return {"motifs": repeated[:8], "count": len(repeated)}

    def detect_chorus_by_pattern(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        candidate = None
        highest_repeat = -1
        for idx, section in enumerate(sections):
            words = section.split()
            unique = len(set(words)) or 1
            repetition_score = len(words) / unique
            if repetition_score > highest_repeat:
                highest_repeat = repetition_score
                candidate = idx
        return {"index": candidate, "score": round(highest_repeat, 3)}

    def detect_emotional_peak_chorus(self, emotion_curve: Sequence[float] | None) -> Dict[str, Any]:
        if not emotion_curve:
            return {"index": None, "intensity": 0.0}
        max_idx = max(range(len(emotion_curve)), key=emotion_curve.__getitem__)
        return {"index": max_idx, "intensity": round(float(emotion_curve[max_idx]), 3)}

    def detect_prechorus(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        if not sections:
            return {"index": None, "confidence": 0.0}
        if len(sections) < 3:
            return {"index": 0, "confidence": 0.3}
        return {"index": max(0, self.detect_chorus_by_pattern(sections, text)["index"] - 1), "confidence": 0.6}

    def detect_semantic_block_shift(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        deltas: List[int] = []
        prev_len = None
        for section in sections:
            length = len(section.split())
            if prev_len is not None:
                deltas.append(abs(length - prev_len))
            prev_len = length
        shift_index = deltas.index(max(deltas)) + 1 if deltas else None
        return {"index": shift_index, "delta": max(deltas) if deltas else 0}

    def detect_mantra_section(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        mantra_idx = None
        for idx, section in enumerate(sections):
            lines = section.splitlines()
            if lines and len(set(lines)) <= max(1, len(lines) // 2):
                mantra_idx = idx
                break
        return {"index": mantra_idx, "confidence": 0.8 if mantra_idx is not None else 0.0}

    def detect_transition_drop(self, emotion_curve: Sequence[float] | None) -> Dict[str, Any]:
        if not emotion_curve:
            return {"index": None, "delta": 0.0}
        drops = [emotion_curve[i] - emotion_curve[i + 1] for i in range(len(emotion_curve) - 1)]
        if not drops:
            return {"index": None, "delta": 0.0}
        idx = drops.index(max(drops))
        return {"index": idx + 1, "delta": round(drops[idx], 3)}

    def detect_intro_ending(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        if not sections:
            return {"index": None, "confidence": 0.0}
        intro_length = len(sections[0].split())
        confidence = 1.0 if intro_length < 30 else 0.4
        return {"index": 0, "confidence": confidence}

    def detect_outro_fade(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        if not sections:
            return {"index": None, "confidence": 0.0}
        outro_length = len(sections[-1].split())
        confidence = 1.0 if outro_length < 20 else 0.5
        return {"index": len(sections) - 1, "confidence": confidence}

    def detect_chorus(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        motif = self.detect_chorus_by_pattern(sections, text)
        return {"index": motif.get("index"), "confidence": min(1.0, (motif.get("score") or 0) / 3)}

    def detect_intro(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        intro = self.detect_intro_ending(sections, text)
        intro["label"] = "intro"
        return intro

    def detect_outro(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        outro = self.detect_outro_fade(sections, text)
        outro["label"] = "outro"
        return outro

    def analyze(self, text: str, sections: Sequence[str] | None, emotion_curve: Sequence[float] | None = None) -> Dict[str, Any]:
        sections = self._ensure_sections(sections, text)
        return {
            "motifs": self.detect_repeated_motif(sections, text),
            "chorus_pattern": self.detect_chorus_by_pattern(sections, text),
            "chorus_emotion": self.detect_emotional_peak_chorus(emotion_curve),
            "prechorus": self.detect_prechorus(sections, text),
            "semantic_shift": self.detect_semantic_block_shift(sections, text),
            "mantra": self.detect_mantra_section(sections, text),
            "transition_drop": self.detect_transition_drop(emotion_curve),
            "intro": self.detect_intro(sections, text),
            "outro": self.detect_outro(sections, text),
        }
