# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
"""Global emotion curve construction utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


SECTION_ORDER = ["intro", "verse", "prechorus", "chorus", "bridge", "outro"]


@dataclass
class GlobalEmotionCurve:
    sections: List[Dict]
    global_tlp: Dict[str, float]
    dominant_cluster: str | None
    peaks: List[int]
    valleys: List[int]
    dynamic_bias: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return {
            "sections": self.sections,
            "global_tlp": self.global_tlp,
            "dominant_cluster": self.dominant_cluster,
            "peaks": self.peaks,
            "valleys": self.valleys,
            "dynamic_bias": self.dynamic_bias,
        }


def _ordered_sections(section_emotions: Sequence[Dict]) -> List[Dict]:
    order_index = {name: idx for idx, name in enumerate(SECTION_ORDER)}
    augmented: List[Dict] = []
    for idx, section in enumerate(section_emotions):
        section_name = str(section.get("section", "")).lower()
        augmented.append((order_index.get(section_name, len(order_index) + idx), idx, dict(section)))

    augmented.sort(key=lambda item: (item[0], item[1]))
    ordered = []
    for new_idx, (_, _, section) in enumerate(augmented):
        section["index"] = new_idx
        ordered.append(section)
    return ordered


def _mean(values: Iterable[float]) -> float:
    total = 0.0
    count = 0
    for value in values:
        try:
            total += float(value)
            count += 1
        except (TypeError, ValueError):
            continue
    return total / count if count else 0.0


def _compute_global_tlp(sections: Sequence[Dict]) -> Dict[str, float]:
    truth_vals = [section.get("tlp_mean", {}).get("truth", 0.0) for section in sections]
    love_vals = [section.get("tlp_mean", {}).get("love", 0.0) for section in sections]
    pain_vals = [section.get("tlp_mean", {}).get("pain", 0.0) for section in sections]
    return {
        "truth": _mean(truth_vals),
        "love": _mean(love_vals),
        "pain": _mean(pain_vals),
    }


def _dominant_cluster(sections: Sequence[Dict]) -> str | None:
    frequency: Dict[str, int] = {}
    intensity_sum: Dict[str, float] = {}

    for section in sections:
        cluster = section.get("cluster_peak")
        if not cluster:
            continue
        frequency[cluster] = frequency.get(cluster, 0) + 1
        try:
            intensity = float(section.get("intensity", 0.0) or 0.0)
        except (TypeError, ValueError):
            intensity = 0.0
        intensity_sum[cluster] = intensity_sum.get(cluster, 0.0) + intensity

    if not frequency:
        return None

    max_freq = max(frequency.values())
    candidates = [cluster for cluster, freq in frequency.items() if freq == max_freq]
    if len(candidates) == 1:
        return candidates[0]

    best_cluster = None
    best_intensity = -1.0
    for cluster in candidates:
        avg_intensity = intensity_sum.get(cluster, 0.0) / max(frequency.get(cluster, 1), 1)
        if avg_intensity > best_intensity:
            best_cluster = cluster
            best_intensity = avg_intensity
    return best_cluster


def _peaks_and_valleys(intensities: Sequence[float]) -> tuple[List[int], List[int]]:
    if not intensities:
        return [], []
    safe_values = [float(value or 0.0) for value in intensities]
    max_intensity = max(safe_values)
    min_intensity = min(safe_values)
    peak_threshold = max_intensity - 0.05
    valley_threshold = min_intensity + 0.05
    peaks = [idx for idx, value in enumerate(safe_values) if value >= peak_threshold]
    valleys = [idx for idx, value in enumerate(safe_values) if value <= valley_threshold]
    return peaks, valleys


def _compute_dynamic_bias(global_tlp: Dict[str, float], cluster: str | None) -> Dict[str, object]:
    bias = {"bpm_delta": 0.0, "key_hint": None, "genre_hint": None}
    cluster_key = (cluster or "").lower()
    truth = float(global_tlp.get("truth", 0.0) or 0.0)
    love = float(global_tlp.get("love", 0.0) or 0.0)
    pain = float(global_tlp.get("pain", 0.0) or 0.0)

    cluster_to_genre = {
        "rage": "metal_adaptive",
        "despair": "dark_rock",
        "fear": "dark_rock",
        "tender": "lyrical_ballad",
        "hope": "lyrical_ballad",
        "contemplative": "poetic_narrative",
        "narrative": "poetic_narrative",
    }

    if pain > love and pain > truth and cluster_key in {"rage", "despair", "fear"}:
        bias["bpm_delta"] = 7.5
        bias["key_hint"] = "minor"
    elif love > pain and love > truth and cluster_key in {"tender", "hope"}:
        bias["bpm_delta"] = -6.0
        bias["key_hint"] = "major"
    elif truth > pain and truth > love and cluster_key in {"contemplative", "narrative"}:
        bias["bpm_delta"] = -3.0
        bias["key_hint"] = None

    bias["genre_hint"] = cluster_to_genre.get(cluster_key)
    return bias


def build_global_emotion_curve(section_emotions: Sequence[Dict]) -> GlobalEmotionCurve:
    ordered_sections = _ordered_sections(section_emotions)
    global_tlp = _compute_global_tlp(ordered_sections)
    dominant_cluster = _dominant_cluster(ordered_sections)
    intensities = [section.get("intensity", 0.0) for section in ordered_sections]
    peaks, valleys = _peaks_and_valleys(intensities)
    dynamic_bias = _compute_dynamic_bias(global_tlp, dominant_cluster)
    return GlobalEmotionCurve(
        sections=ordered_sections,
        global_tlp=global_tlp,
        dominant_cluster=dominant_cluster,
        peaks=peaks,
        valleys=valleys,
        dynamic_bias=dynamic_bias,
    )


__all__ = ["GlobalEmotionCurve", "build_global_emotion_curve"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
