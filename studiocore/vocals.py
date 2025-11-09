from typing import List, Dict, Any, Tuple
from .emotion import AutoEmotionalAnalyzer

VALID_VOICES = [
    "male","female","duet","choir","tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","warm","clear"
]

VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello","trumpet",
    "saxophone","organ","harp","choir","vocals","pad","flute","horns","percussion","tagelharpa"
]

DEFAULT_VOCAL_MAP = {
    "metal":      {"female":["female","powerful","alto"],  "male":["male","powerful","baritone"], "inst":["guitar","drums","strings","choir"]},
    "rock":       {"female":["female","emotional","alto"], "male":["male","raspy","tenor"],       "inst":["guitar","drums","bass","piano"]},
    "pop":        {"female":["female","clear","soprano"],  "male":["male","soft","tenor"],       "inst":["piano","synth","bass","drums"]},
    "folk":       {"female":["female","warm","alto"],      "male":["male","emotional","baritone"],"inst":["guitar","strings","flute"]},
    "classical":  {"female":["soprano","angelic"],         "male":["tenor","baritone"],          "inst":["strings","piano","choir"]},
    "electronic": {"female":["female","breathy"],          "male":["male","soft"],               "inst":["synth","pad","bass","drums"]},
    "ambient":    {"female":["female","whispered"],        "male":["male","soft"],               "inst":["pad","piano","strings"]},
    "orchestral": {"female":["female","angelic"],          "male":["male","deep"],               "inst":["strings","choir","horns","percussion"]},
    "hip hop":    {"female":["female","clear"],            "male":["male","deep"],               "inst":["drums","bass","synth","piano"]},
    "rap":        {"female":["female","clear"],            "male":["male","deep"],               "inst":["drums","bass","synth","piano"]},
    "jazz":       {"female":["female","warm"],             "male":["male","soft"],               "inst":["piano","saxophone","bass","drums"]},
    "blues":      {"female":["female","emotional"],        "male":["male","raspy"],              "inst":["guitar","piano","bass","drums"]},
}

class VocalProfileRegistry:
    """Suggests appropriate vocal and instrumental settings based on genre, emotion, and text."""

    def __init__(self):
        self.map = DEFAULT_VOCAL_MAP

    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str,Any]]) -> Dict[str, bool]:
        s = (text + " " + " ".join(s.get("tag", "") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir","chant","хор","сканд","group"]),
            "wants_duet":  any(k in s for k in ["duet","дуэт","duo","вместе"]),
        }

    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]]) -> Tuple[List[str], List[str]]:
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)

        if preferred_gender == "female":
            vox = self.map[g]["female"]
        elif preferred_gender == "male":
            vox = self.map[g]["male"]
        elif preferred_gender == "duet":
            vox = ["duet"] + self.map[g]["female"][:1] + self.map[g]["male"][:1]
        elif preferred_gender == "choir":
            vox = ["choir"] + ["male", "female"]
        else:
            emo = AutoEmotionalAnalyzer().analyze(text)
            if (emo.get("love",0)+emo.get("peace",0)) > (emo.get("anger",0)+emo.get("epic",0)):
                vox = self.map[g]["female"]
            else:
                vox = self.map[g]["male"]

        if hints["wants_choir"] and "choir" not in vox:
            vox = ["choir"] + vox
        if hints["wants_duet"] and "duet" not in vox:
            vox = ["duet"] + vox

        inst = list(self.map[g]["inst"])
        tag_text = " ".join([s["tag"] for s in sections]).lower()
        if "tagelharpa" in tag_text and "tagelharpa" not in inst:
            inst.append("tagelharpa")

        vox = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]
        return vox, inst
