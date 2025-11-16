import re
from typing import List, Dict, Any

ANNOTATION_PATTERN = re.compile(
    r"\[(?P<section>[A-Za-zА-Яа-я0-9\s\-]+)\s*[-–]\s*(?P<tags>[^\]]+)\]",
    flags=re.I
)

EMO_MAP = {
    "whisper": {"energy": -0.2, "intimacy": +0.3},
    "reverb": {"space": +0.2},
    "belt": {"energy": +0.3, "confidence": +0.2},
    "cry": {"pain": +0.3, "truth": +0.1},
    "scream": {"pain": +0.4, "love": -0.1},
    "vibrato": {"beauty": +0.2},
    "distorted": {"chaos": +0.3},
}

class SectionTagAnalyzer:
    """Dynamic section parser that applies emotional hints to analyzed text."""

    def parse(self, text: str) -> List[Dict[str, Any]]:
        matches = ANNOTATION_PATTERN.finditer(text)
        result = []
        for m in matches:
            section = m.group("section").strip()
            tags = [t.strip().lower() for t in re.split(r"[,+/]", m.group("tags"))]
            emo_effects = {}
            for tag in tags:
                if tag in EMO_MAP:
                    for k, v in EMO_MAP[tag].items():
                        emo_effects[k] = emo_effects.get(k, 0) + v
            result.append({
                "section": section,
                "tags": tags,
                "emo_mod": emo_effects
            })
        return result

    def integrate_with_core(self, core_result: Dict[str, Any], annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Applies annotation-based emotional corrections to the core result."""
        emo = core_result["emotions"]
        bpm = core_result["bpm"]
        for a in annotations:
            for key, val in a["emo_mod"].items():
                emo[key] = emo.get(key, 0) + val
            # reactivity: strong belt/cry may slightly raise BPM
            if any(t in a["tags"] for t in ["belt", "scream", "cry"]):
                bpm += 3
        core_result["emotions"] = emo
        core_result["bpm"] = bpm
        core_result["annotations"] = annotations
        return core_result
