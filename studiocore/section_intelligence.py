# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Advanced section detection helpers mandated by the Codex specification."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Sequence, Tuple
import re

from .emotion import EmotionEngine
from .structures import PhraseEmotionPacket, SectionEmotionWave
from .text_utils import extract_phrases_from_section, extract_sections


class SectionIntelligenceEngine:
    """Detect chorus/mantra/transition cues beyond naive splitting."""

    LONGFORM_SECTION_RULES = (
        "semantic_markers_strict",
        "hard_boundary_on_pronouns",
        "no_block_merging",
    )

    def _prepare_sections(self, sections: Sequence[str] | None, text: str | None) -> List[str]:
        if sections:
            return [section.strip() for section in sections if section and section.strip()]
        if text:
            return [block.strip() for block in text.split("\n\n") if block.strip()]
        return []

    def detect_repeated_motif(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._prepare_sections(sections, text)
        motif_counter: Counter[str] = Counter()
        for section in sections:
            for line in section.splitlines():
                motif = line.strip().lower()
                if motif:
                    motif_counter[motif] += 1
        repeated = [line for line, count in motif_counter.items() if count > 1]
        return {"motifs": repeated[:8], "count": len(repeated)}

    def detect_chorus_by_pattern(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._prepare_sections(sections, text)
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
        sections = self._prepare_sections(sections, text)
        if not sections:
            return {"index": None, "confidence": 0.0}
        if len(sections) < 3:
            return {"index": 0, "confidence": 0.3}
        return {"index": max(0, self.detect_chorus_by_pattern(sections, text)["index"] - 1), "confidence": 0.6}

    def detect_semantic_block_shift(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._prepare_sections(sections, text)
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
        sections = self._prepare_sections(sections, text)
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
        sections = self._prepare_sections(sections, text)
        if not sections:
            return {"index": None, "confidence": 0.0}
        intro_length = len(sections[0].split())
        confidence = 1.0 if intro_length < 30 else 0.4
        return {"index": 0, "confidence": confidence}

    def detect_outro_fade(self, sections: Sequence[str] | None, text: str) -> Dict[str, Any]:
        sections = self._prepare_sections(sections, text)
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

    def detect_longform(self, text: str, sections: Sequence[str] | None) -> Dict[str, Any]:
        resolved = self._prepare_sections(sections, text)
        line_count = sum(len(section.splitlines()) for section in resolved) or len(text.splitlines())
        mode = "default"
        rules: List[str] = []
        if line_count > 120:
            mode = "longform"
            rules = list(self.LONGFORM_SECTION_RULES)
        return {
            "mode": mode,
            "line_count": line_count,
            "rules": rules,
            "prefer_strict_markers": mode == "longform",
        }

    def compute_structure_tension(self, sections: Sequence[str] | None) -> float:
        segments = [section.strip() for section in (sections or []) if section and section.strip()]
        if not segments:
            return 0.0

        def _section_energy(payload: str) -> float:
            words = payload.split()
            unique = len(set(words)) or 1
            punctuation = sum(payload.count(symbol) for symbol in "!?" )
            density = len(words) / max(unique, 1)
            return density + punctuation * 0.1

        tension = 0.0
        previous = None
        for section in segments:
            energy = _section_energy(section)
            if previous is not None:
                tension += abs(energy - previous) * 0.25
            previous = energy
        return round(min(1.0, tension), 3)

    def analyze(
        self,
        text: str,
        sections: Sequence[str] | None,
        emotion_curve: Sequence[float] | None = None,
        emotion_engine: EmotionEngine | None = None,
    ) -> Dict[str, Any]:
        sections = self._prepare_sections(sections, text)
        structure_tension = self.compute_structure_tension(sections)
        phrase_packets: List[Dict[str, Any]] = []
        section_waves: List[SectionEmotionWave] = []

        structured_sections = extract_sections(text)
        resolved_sections: List[Tuple[str, str]] = []

        if structured_sections:
            for idx, item in enumerate(structured_sections):
                tag = item.get("tag") or f"Section {idx + 1}"
                section_text = "\n".join(item.get("lines", [])).strip()
                if section_text:
                    resolved_sections.append((tag, section_text))

        if not resolved_sections:
            for idx, section in enumerate(sections):
                if section:
                    resolved_sections.append((f"Section {idx + 1}", section))

        for label, section in resolved_sections:
            raw_lines = [ln for ln in section.splitlines() if ln and ln.strip()]
            cleaned_lines: List[str] = []
            for ln in raw_lines:
                stripped = ln.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    continue
                if stripped.startswith("#"):
                    continue
                cleaned_lines.append(stripped)

            if not cleaned_lines:
                continue

            merged = " \n ".join(cleaned_lines)
            split_phrases = []
            for chunk in re.split(r"[.!?…]+", merged):
                chunk = chunk.strip()
                if chunk:
                    split_phrases.extend(extract_phrases_from_section(chunk))

            unique_phrases = []
            seen = set()
            for phrase in split_phrases:
                if phrase not in seen:
                    unique_phrases.append(phrase)
                    seen.add(phrase)

            section_packets: List[PhraseEmotionPacket] = []
            if emotion_engine:
                for phrase in unique_phrases:
                    packet: PhraseEmotionPacket = emotion_engine.analyze_phrase(phrase)
                    phrase_packets.append(packet.to_dict())
                    section_packets.append(packet)

            if section_packets:
                section_wave = self._build_section_wave(label, section_packets)
                section_waves.append(section_wave)
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
            "longform": self.detect_longform(text, sections),
            "structure_tension": structure_tension,
            "phrase_packets": phrase_packets,
            "section_emotions": [wave.to_dict() for wave in section_waves],
        }

    def _build_section_wave(self, section_label: str, packets: Sequence[PhraseEmotionPacket]) -> SectionEmotionWave:
        count = len(packets) or 1
        truth_sum = sum((p.emotions.get("tlp", {}).get("truth", 0.0) for p in packets))
        love_sum = sum((p.emotions.get("tlp", {}).get("love", 0.0) for p in packets))
        pain_sum = sum((p.emotions.get("tlp", {}).get("pain", 0.0) for p in packets))
        tlp_mean = {
            "truth": round(truth_sum / count, 3),
            "love": round(love_sum / count, 3),
            "pain": round(pain_sum / count, 3),
        }

        cluster_totals: Counter[str] = Counter()
        max_clusters: List[float] = []
        pain_love_series: List[float] = []
        for packet in packets:
            clusters = packet.emotions.get("clusters", {}) or {}
            cluster_totals.update(clusters)
            max_clusters.append(max(clusters.values()) if clusters else 0.0)
            tlp = packet.emotions.get("tlp", {}) or {}
            pain_love_series.append((tlp.get("pain", 0.0) + tlp.get("love", 0.0)))

        cluster_peak = None
        if cluster_totals:
            cluster_peak = max(cluster_totals, key=cluster_totals.get)

        intensity = round(sum(max_clusters) / count, 3)

        emotional_shape = "flat"
        if any(packet.weight > 0.8 for packet in packets):
            emotional_shape = "spike"
        elif len(pain_love_series) >= 2:
            deltas = [pain_love_series[i + 1] - pain_love_series[i] for i in range(len(pain_love_series) - 1)]
            if deltas and all(delta > 0.15 for delta in deltas):
                emotional_shape = "rising"
            elif deltas and all(delta < -0.15 for delta in deltas):
                emotional_shape = "falling"

        hot_phrases = [
            packet.phrase
            for packet in sorted(packets, key=lambda p: p.weight, reverse=True)[:3]
        ]

        return SectionEmotionWave(
            section=section_label,
            tlp_mean=tlp_mean,
            cluster_peak=cluster_peak,
            intensity=intensity,
            emotional_shape=emotional_shape,
            hot_phrases=hot_phrases,
        )


class SectionIntelligence:
    def __init__(self, engine: EmotionEngine | None = None) -> None:
        self.engine = engine or EmotionEngine()
        self._engine = SectionIntelligenceEngine()

    def parse(self, text: str, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        self.engine.reset_phrase_packets()
        result = self._engine.analyze(text, sections, emotion_curve=None, emotion_engine=self.engine)
        return result
