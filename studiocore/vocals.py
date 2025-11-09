# studiocore/vocals.py
from typing import List, Dict, Any, Tuple
import re
from .emotion import AutoEmotionalAnalyzer

VALID_VOICES = [
    "male", "female", "duet", "choir", "tenor", "soprano", "alto", "baritone", "bass",
    "raspy", "breathy", "powerful", "soft", "emotional", "angelic", "deep", "whispered", "warm", "clear"
]

VALID_INSTRUMENTS = [
    "guitar", "piano", "synth", "bass", "drums", "strings", "violin", "cello", "trumpet",
    "saxophone", "organ", "harp", "choir", "vocals", "pad", "flute", "horns", "percussion", "tagelharpa"
]

DEFAULT_VOCAL_MAP = {
    "metal":      {"female": ["female", "powerful", "alto"], "male": ["male", "powerful", "baritone"], "inst": ["guitar", "drums", "strings", "choir"]},
    "rock":       {"female": ["female", "emotional", "alto"], "male": ["male", "raspy", "tenor"], "inst": ["guitar", "drums", "bass", "piano"]},
    "pop":        {"female": ["female", "clear", "soprano"], "male": ["male", "soft", "tenor"], "inst": ["piano", "synth", "bass", "drums"]},
    "folk":       {"female": ["female", "warm", "alto"], "male": ["male", "emotional", "baritone"], "inst": ["guitar", "strings", "flute"]},
    "classical":  {"female": ["soprano", "angelic"], "male": ["tenor", "baritone"], "inst": ["strings", "piano", "choir"]},
    "electronic": {"female": ["female", "breathy"], "male": ["male", "soft"], "inst": ["synth", "pad", "bass", "drums"]},
    "ambient":    {"female": ["female", "whispered"], "male": ["male", "soft"], "inst": ["pad", "piano", "strings"]},
    "orchestral": {"female": ["female", "angelic"], "male": ["male", "deep"], "inst": ["strings", "choir", "horns", "percussion"]},
    "hip hop":    {"female": ["female", "clear"], "male": ["male", "deep"], "inst": ["drums", "bass", "synth", "piano"]},
    "rap":        {"female": ["female", "clear"], "male": ["male", "deep"], "inst": ["drums", "bass", "synth", "piano"]},
    "jazz":       {"female": ["female", "warm"], "male": ["male", "soft"], "inst": ["piano", "saxophone", "bass", "drums"]},
    "blues":      {"female": ["female", "emotional"], "male": ["male", "raspy"], "inst": ["guitar", "piano", "bass", "drums"]},
}


class VocalProfileRegistry:
    """Adaptive vocal/instrument engine — auto-detects gender, duet, choir, and ensemble form."""

    def __init__(self):
        self.map = DEFAULT_VOCAL_MAP

    # -------------------------------------------------------
    # 1. Определение формы вокала (solo, duet, choir)
    # -------------------------------------------------------
    def detect_vocal_form(self, text: str) -> Tuple[str, List[str]]:
        """
        Анализирует лирику и определяет форму вокала и роли.
        Возвращает (vocal_form, [gender_roles]).
        """
        txt = text.lower()

        female_markers = len(re.findall(r"\b(я шла|любила|моя|дев|жен|милая|сестра|дочь)\b", txt))
        male_markers = len(re.findall(r"\b(я шёл|любил|мой|парень|муж|брат|сын)\b", txt))
        plural_markers = len(re.findall(r"\b(мы|вместе|все|нас|люди|голоса)\b", txt))

        if plural_markers > 2:
            return "choir", ["mixed"]
        elif female_markers > 1 and male_markers > 1:
            return "duet_mf", ["female", "male"]
        elif female_markers > 3:
            return "solo_female", ["female"]
        elif male_markers > 3:
            return "solo_male", ["male"]
        elif female_markers > 2 and plural_markers > 1:
            return "duet_ff", ["female", "female"]
        elif male_markers > 2 and plural_markers > 1:
            return "duet_mm", ["male", "male"]
        else:
            return "solo_auto", ["auto"]

    # -------------------------------------------------------
    # 2. Определение ансамблевых подсказок (дуэт/хор по контексту)
    # -------------------------------------------------------
    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str, Any]]) -> Dict[str, bool]:
        s = (text + " " + " ".join(s.get("tag", "") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir", "chant", "хор", "сканд", "group"]),
            "wants_duet":  any(k in s for k in ["duet", "дуэт", "duo", "вместе"]),
        }

    # -------------------------------------------------------
    # 3. Главный метод получения профиля вокала и инструментов
    # -------------------------------------------------------
    def get(self, genre: str, roles: List[str], text: str, sections: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Подбирает вокальные и инструментальные профили с учётом формы и пола."""
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)

        # Определение базового пола (auto fallback)
        primary_gender = roles[0] if roles else "auto"

        if "duet" in roles or len(roles) > 1:
            vox = ["duet"] + sum((self.map[g][r] for r in roles if r in self.map[g]), [])
        elif "choir" in roles or "mixed" in roles:
            vox = ["choir"] + ["male", "female"]
        elif primary_gender in ["female", "male"]:
            vox = self.map[g][primary_gender]
        else:
            emo = AutoEmotionalAnalyzer().analyze(text)
            if (emo.get("love", 0) + emo.get("peace", 0)) > (emo.get("anger", 0) + emo.get("epic", 0)):
                vox = self.map[g]["female"]
            else:
                vox = self.map[g]["male"]

        # Добавляем ансамблевые маркеры при необходимости
        if hints["wants_choir"] and "choir" not in vox:
            vox = ["choir"] + vox
        if hints["wants_duet"] and "duet" not in vox:
            vox = ["duet"] + vox

        # Инструменты
        inst = list(self.map[g]["inst"])
        tag_text = " ".join([s.get("tag", "") for s in sections]).lower()
        if "tagelharpa" in tag_text and "tagelharpa" not in inst:
            inst.append("tagelharpa")

        # Очистка и усечение
        vox = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]
        return vox, inst
