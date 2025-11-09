from typing import List, Dict, Any, Tuple
import re
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
    """Adaptive vocal+instrument selector with gender and ensemble detection."""

    def __init__(self):
        self.map = DEFAULT_VOCAL_MAP

    # ----------------------------------------------------------
    # 1️⃣ Определение пола по тексту
    # ----------------------------------------------------------
    def _detect_gender_from_text(self, text: str) -> str:
        """
        Определяет предполагаемый пол исполнителя по местоимениям, окончаниям и эмоциональной окраске.
        """
        text_low = text.lower()

        # Женские маркеры
        female_tokens = [
            "она", "ей", "её", "девушка", "женщина", "мама", "дочь",
            "любила", "ушла", "смотрела", "грустила", "плакала"
        ]

        # Мужские маркеры
        male_tokens = [
            "он", "ему", "его", "мужчина", "отец", "сын",
            "любил", "ушёл", "смотрел", "грустил", "плакал"
        ]

        female_score = sum(t in text_low for t in female_tokens)
        male_score = sum(t in text_low for t in male_tokens)

        if female_score > male_score:
            return "female"
        elif male_score > female_score:
            return "male"
        else:
            return "auto"

    # ----------------------------------------------------------
    # 2️⃣ Определение ансамбля по контексту
    # ----------------------------------------------------------
    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str,Any]]) -> Dict[str, bool]:
        s = (text + " " + " ".join(s.get("tag", "") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir","chorus","хор","сканд","толпа","group","voices"]),
            "wants_duet":  any(k in s for k in ["duet","дуэт","duo","вместе","вдвоём"]),
        }

    # ----------------------------------------------------------
    # 3️⃣ Основной метод получения вокала и инструментов
    # ----------------------------------------------------------
    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]]) -> Tuple[List[str], List[str]]:
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)
        detected_gender = self._detect_gender_from_text(text)

        # Определяем форму вокала
        if hints["wants_choir"]:
            vocal_form = "choir"
        elif hints["wants_duet"]:
            vocal_form = "duet_mf"
        elif preferred_gender in ("male", "female"):
            vocal_form = f"solo_{preferred_gender}"
        elif detected_gender in ("male", "female"):
            vocal_form = f"solo_{detected_gender}"
        else:
            vocal_form = "solo_auto"

        # Определяем профиль вокала
        if "duet" in vocal_form:
            vox = ["duet"] + self.map[g]["female"][:1] + self.map[g]["male"][:1]
        elif "choir" in vocal_form:
            vox = ["choir", "male", "female"]
        elif "female" in vocal_form:
            vox = self.map[g]["female"]
        elif "male" in vocal_form:
            vox = self.map[g]["male"]
        else:
            # fallback — по эмоциям
            emo = AutoEmotionalAnalyzer().analyze(text)
            if (emo.get("love",0)+emo.get("peace",0)) > (emo.get("anger",0)+emo.get("epic",0)):
                vox = self.map[g]["female"]
            else:
                vox = self.map[g]["male"]

        # Инструменты
        inst = list(self.map[g]["inst"])
        tag_text = " ".join([s["tag"] for s in sections]).lower()
        if "tagelharpa" in tag_text and "tagelharpa" not in inst:
            inst.append("tagelharpa")

        vox = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]

        return vox, inst, vocal_form
