# -*- coding: utf-8 -*-
"""
StudioCore v5 — VocalProfileRegistry
Адаптивный подбор вокальных и инструментальных профилей по жанру, эмоциям и структуре.
"""

from typing import List, Dict, Any, Tuple
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
    "rock":       {"female":["female","emotional","alto"], "male":["male","raspy","tenor"], "inst":["guitar","drums","bass","piano"]},
    "pop":        {"female":["female","clear","soprano"],  "male":["male","soft","tenor"],   "inst":["piano","synth","bass","drums"]},
    "folk":       {"female":["female","warm","alto"],      "male":["male","emotional","baritone"], "inst":["guitar","strings","flute"]},
    "cinematic":  {"female":["female","angelic"],          "male":["male","deep"],          "inst":["strings","piano","choir","drums"]},
    "electronic": {"female":["female","breathy"],          "male":["male","soft"],          "inst":["synth","pad","bass","drums"]},
    "ambient":    {"female":["female","whispered"],        "male":["male","soft"],          "inst":["pad","piano","strings"]},
    "orchestral": {"female":["female","angelic"],          "male":["male","deep"],          "inst":["strings","choir","horns","percussion"]},
}


class VocalProfileRegistry:
    """Adaptive engine: suggests suitable vocal & instrumental settings."""

    def __init__(self):
        self.map = DEFAULT_VOCAL_MAP

    # --------------------------------------------------------
    # 🔍 Анализ текста и разделов для определения состава
    # --------------------------------------------------------
    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str, Any]]) -> Dict[str, bool]:
        s = (text + " " + " ".join(s.get("tag", "") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir","хор","chorus","anthem","mass"]),
            "wants_duet":  any(k in s for k in ["duet","дуэт","duo","вместе","pair"]),
            "wants_trio":  any(k in s for k in ["trio","трио"]),
            "wants_quartet": any(k in s for k in ["quartet","квартет"]),
            "wants_quintet": any(k in s for k in ["quintet","квинтет"]),
            "dialogue": any(k in s for k in ["(male)","(female)","he said","she said","он","она"]),
            "call_response": any(k in s for k in ["в ответ","отклик","ответил","respond","reply"]),
        }

    # --------------------------------------------------------
    # 🎙 Автоматическое определение вокальной формы
    # --------------------------------------------------------
    def auto_vocal_form(self, emo: Dict[str,float], tlp: Dict[str,float], text: str) -> str:
        wc = len(text.split())
        cf = tlp.get("conscious_frequency", 0)
        love, pain, truth = tlp.get("love",0), tlp.get("pain",0), tlp.get("truth",0)
        energy = (love + pain + truth) / 3
        emo_energy = max(emo.values()) if emo else 0.3

        ensemble_intensity = round(min(1.0, (energy + emo_energy + cf) / 3), 3)

        if wc < 40 and ensemble_intensity < 0.3:
            return "solo"
        elif 40 <= wc < 80 or ensemble_intensity > 0.4:
            return "duet"
        elif 80 <= wc < 150 or ensemble_intensity > 0.5:
            return "trio"
        elif 150 <= wc < 250 or ensemble_intensity > 0.6:
            return "quartet"
        elif wc >= 250 or ensemble_intensity > 0.75:
            return "choir"
        return "solo"

    # --------------------------------------------------------
    # 🧩 Подбор вокала и инструментов
    # --------------------------------------------------------
    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]]) -> Tuple[List[str], List[str], str]:
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)

        emo = AutoEmotionalAnalyzer().analyze(text)
        tlp_stub = {"conscious_frequency": 0.5, "love": emo.get("joy", 0.3), "pain": emo.get("sadness", 0.2), "truth": emo.get("peace", 0.4)}
        form = self.auto_vocal_form(emo, tlp_stub, text)

        # Пол/вокал
        if preferred_gender == "female":
            vox = self.map[g]["female"]
        elif preferred_gender == "male":
            vox = self.map[g]["male"]
        elif preferred_gender == "auto":
            vox = self.map[g]["female"] if emo.get("joy",0) > emo.get("anger",0) else self.map[g]["male"]
        else:
            vox = self.map[g]["female"]

        # Подсказки текста
        if hints["wants_choir"]:
            form = "choir"
        elif hints["wants_quintet"]:
            form = "quintet"
        elif hints["wants_quartet"]:
            form = "quartet"
        elif hints["wants_trio"]:
            form = "trio"
        elif hints["wants_duet"] or hints["dialogue"] or hints["call_response"]:
            form = "duet"

        # Формирование состава
        vox = [form] + vox
        inst = self.map[g]["inst"]

        # --- Определение формы ансамбля ---
        if "choir" in vox:
            if "male" in vox and "female" in vox:
                vocal_form = "choir_mixed"
            elif "female" in vox:
                vocal_form = "choir_female"
            elif "male" in vox:
                vocal_form = "choir_male"
            else:
                vocal_form = "choir_auto"
        elif "quintet" in vox:
            vocal_form = "quintet_mixed"
        elif "quartet" in vox:
            vocal_form = "quartet_mixed"
        elif "trio" in vox:
            vocal_form = "trio_mixed"
        elif "duet" in vox:
            if "male" in vox and "female" in vox:
                vocal_form = "duet_mf"
            elif "male" in vox:
                vocal_form = "duet_mm"
            elif "female" in vox:
                vocal_form = "duet_ff"
            else:
                vocal_form = "duet_auto"
        elif "female" in vox and "male" not in vox:
            vocal_form = "solo_female"
        elif "male" in vox and "female" not in vox:
            vocal_form = "solo_male"
        else:
            vocal_form = "solo_auto"

        vox = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]

        return vox, inst, vocal_form
