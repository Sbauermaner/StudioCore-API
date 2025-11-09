from typing import List, Dict, Any, Tuple
import re
from .emotion import AutoEmotionalAnalyzer

VALID_VOICES = [
    "male","female","duet","trio","quartet","quintet","choir",
    "tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","warm","clear"
]

VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello","trumpet",
    "saxophone","organ","harp","choir","vocals","pad","flute","horns","percussion","tagelharpa"
]

DEFAULT_VOCAL_MAP = {
    "rock": {"female":["female","emotional","alto"], "male":["male","raspy","tenor"], "inst":["guitar","drums","bass","piano"]},
    "pop": {"female":["female","clear","soprano"], "male":["male","soft","tenor"], "inst":["piano","synth","bass","drums"]},
    "folk": {"female":["female","warm","alto"], "male":["male","emotional","baritone"], "inst":["guitar","strings","flute"]},
    "orchestral": {"female":["female","angelic"], "male":["male","deep","baritone"], "inst":["strings","choir","horns","percussion"]},
    "jazz": {"female":["female","warm"], "male":["male","soft"], "inst":["piano","saxophone","bass","drums"]},
}


class VocalProfileRegistry:
    """Adaptive multi-gender ensemble and instrument selector."""

    def __init__(self):
        self.map = DEFAULT_VOCAL_MAP

    # ----------------------------------------------------------
    # 1️⃣ Определение пола по контексту
    # ----------------------------------------------------------
    def _detect_gender_from_text(self, text: str) -> str:
        text_low = text.lower()
        female_tokens = ["она","ей","её","девушка","женщина","мама","дочь","сестра","любила","ушла"]
        male_tokens = ["он","его","ему","мужчина","отец","сын","брат","любил","ушёл"]
        female_score = sum(t in text_low for t in female_tokens)
        male_score = sum(t in text_low for t in male_tokens)

        if female_score > male_score:
            return "female"
        elif male_score > female_score:
            return "male"
        else:
            return "mixed"

    # ----------------------------------------------------------
    # 2️⃣ Определение формы ансамбля и состава
    # ----------------------------------------------------------
    def _detect_ensemble_form(self, text: str) -> Tuple[str, int, int]:
        s = text.lower()
        M = F = 0

        if "два" in s or "две" in s:
            n = 2
        elif "три" in s or "втроем" in s:
            n = 3
        elif "четыре" in s or "вчетвером" in s:
            n = 4
        elif "пять" in s or "впятером" in s:
            n = 5
        elif any(k in s for k in ["хор","толпа","все вместе","голоса","choir"]):
            n = 10
        else:
            n = 1

        if "муж" in s or "парн" in s or "юноши" in s:
            M = max(1, n // 2)
        if "жен" in s or "девуш" in s or "голос жен" in s:
            F = max(1, n // 2)
        if M == 0 and F == 0:
            if n == 1: F = 1
            elif n == 2: M, F = 1, 1
            elif n == 3: M, F = 1, 2
            elif n == 4: M, F = 2, 2
            elif n >= 5: M, F = 3, 2

        if n == 1:
            form = "solo"
        elif n == 2:
            form = "duet"
        elif n == 3:
            form = "trio"
        elif n == 4:
            form = "quartet"
        elif n == 5:
            form = "quintet"
        else:
            form = "choir"

        return form, M, F

    # ----------------------------------------------------------
    # 3️⃣ Генерация ансамблевого тега
    # ----------------------------------------------------------
    def _ensemble_label(self, base: str, M: int, F: int) -> str:
        if base == "choir":
            if M > 0 and F > 0:
                return "choir_mixed"
            elif M > 0:
                return "choir_male"
            else:
                return "choir_female"
        else:
            tag = base + "_" + ("m" * M) + ("f" * F)
            return tag

    # ----------------------------------------------------------
    # 4️⃣ Основной метод
    # ----------------------------------------------------------
    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]]) -> Tuple[List[str], List[str], str]:
        g = genre if genre in self.map else "rock"

        detected_gender = self._detect_gender_from_text(text)
        base_form, M, F = self._detect_ensemble_form(text)
        vocal_form = self._ensemble_label(base_form, M, F)

        if M and F:
            vox = ["male","female"]
        elif F and not M:
            vox = self.map[g]["female"]
        elif M and not F:
            vox = self.map[g]["male"]
        else:
            vox = ["male","female"]

        if "choir" in vocal_form and "choir" not in vox:
            vox = ["choir"] + vox

        inst = list(self.map[g]["inst"])
        vox = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]

        return vox, inst, vocal_form
