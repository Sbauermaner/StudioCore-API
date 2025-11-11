# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — VocalProfileRegistry (Adaptive + Overlay Integration)
Интеграция с AdaptiveVocalAllocator и внешним overlay-вводом (из app.py).
Поддержка автораспознавания вокального описания из текста:
tone (тембр), texture (характер), emotion (эмоциональный стиль).
"""

from typing import List, Dict, Any, Tuple
from .emotion import AutoEmotionalAnalyzer

VALID_VOICES = [
    "male","female","duet","trio","quartet","quintet","choir",
    "tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic",
    "deep","whispered","warm","clear"
]

VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello",
    "trumpet","saxophone","organ","harp","choir","vocals","pad","flute",
    "horns","percussion","tagelharpa"
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
    def auto_vocal_form(self, emo: Dict[str,float], tlp: Dict[str,float], text: str) -> str:
        wc = len(text.split())
        cf = tlp.get("conscious_frequency", 0.0)
        love, pain, truth = tlp.get("love", 0.0), tlp.get("pain", 0.0), tlp.get("truth", 0.0)

        base_energy = (truth * 0.4 + pain * 0.6 + cf * 0.8) - (love * 0.3)
        emo_energy = max(emo.values()) if emo else 0.25
        ensemble_intensity = round(min(1.0, max(0.0, (base_energy + emo_energy) / 1.5)), 3)

        if wc < 40 and ensemble_intensity < 0.3:
            form = "solo"
        elif 40 <= wc < 80 or 0.3 <= ensemble_intensity < 0.45:
            form = "duet"
        elif 80 <= wc < 150 or 0.45 <= ensemble_intensity < 0.6:
            form = "trio"
        elif 150 <= wc < 250 or 0.6 <= ensemble_intensity < 0.75:
            form = "quartet"
        elif wc >= 250 or ensemble_intensity >= 0.75:
            form = "choir"
        else:
            form = "solo"

        if cf > 0.9 and form != "choir":
            form = "choir"
        elif cf > 0.85 and pain > 0.05 and form in ["solo", "duet"]:
            form = "trio"
        elif cf < 0.6 and love > 0.25 and pain < 0.04:
            form = "solo"

        return form

    # --------------------------------------------------------
    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]],
            override: Dict[str, Any] | None = None) -> Tuple[List[str], List[str], str]:
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)
        emo = AutoEmotionalAnalyzer().analyze(text)

        tlp_stub = {
            "conscious_frequency": emo.get("intensity", 0.5),
            "love": emo.get("joy", 0.3),
            "pain": emo.get("sadness", 0.2),
            "truth": emo.get("peace", 0.4)
        }

        form = self.auto_vocal_form(emo, tlp_stub, text)

        # 🔸 override integration
        vox = []
        if override:
            form = override.get("vocal_form", form)
            preferred_gender = override.get("gender", preferred_gender)

            voice_override = override.get("voice_profile") or override.get("vocals")
            if isinstance(voice_override, dict):
                tone = voice_override.get("tone", "")
                texture = voice_override.get("texture", "")
                emotion = voice_override.get("emotion", "")
                vox.extend([tone, texture, emotion])
            elif isinstance(voice_override, list) and len(voice_override) > 0:
                v = voice_override[0]
                vox.extend([
                    v.get("tone", ""), v.get("texture", ""), v.get("emotion", "")
                ])
        else:
            voice_hint = detect_voice_profile_from_text(text)
            vox.extend([voice_hint["tone"], voice_hint["texture"], voice_hint["emotion"]])

        # 🔸 Gender selection
        if preferred_gender == "female":
            vox += self.map[g]["female"]
        elif preferred_gender == "male":
            vox += self.map[g]["male"]
        elif preferred_gender == "auto":
            vox += self.map[g]["female"] if emo.get("joy",0) > emo.get("anger",0) else self.map[g]["male"]
        else:
            vox += self.map[g]["female"]

        inst = self.map[g]["inst"]

        # 🔸 Ensemble hints
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

        vox = [form] + [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]

        # 🎙 Define vocal form
        if "choir" in vox:
            if "male" in vox and "female" in vox:
                vocal_form = "choir_mixed"
            elif "female" in vox:
                vocal_form = "choir_female"
            elif "male" in vox:
                vocal_form = "choir_male"
            else:
                vocal_form = "choir_auto"
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

        return vox, inst, vocal_form


# --------------------------------------------------------
def detect_voice_profile_from_text(text: str) -> Dict[str, str]:
    """Распознаёт вокальный характер из текста (tone, texture, emotion)."""
    t = text.lower()
    voice = {"tone": "neutral", "texture": "clean", "emotion": "balanced"}

    # --- Tone (тембр)
    if any(k in t for k in ["баритон", "низкий", "глубокий", "bass", "baritone"]):
        voice["tone"] = "baritone"
    elif any(k in t for k in ["высокий", "тонкий", "soprano", "alto", "женский"]):
        voice["tone"] = "soprano"
    elif any(k in t for k in ["тенор", "мужской", "male", "deep voice"]):
        voice["tone"] = "tenor"

    # --- Texture (характер)
    if any(k in t for k in ["хрип", "хриплый", "rasp", "rough", "gritty"]):
        voice["texture"] = "raspy"
    elif any(k in t for k in ["мягкий", "soft", "теплый", "warm"]):
        voice["texture"] = "soft"
    elif any(k in t for k in ["чистый", "clear", "bright"]):
        voice["texture"] = "clean"

    # --- Emotion (эмоциональность)
    if any(k in t for k in ["эмоцион", "душев", "сердеч", "heart", "soul", "tear"]):
        voice["emotion"] = "emotional"
    elif any(k in t for k in ["спокой", "тихий", "calm", "gentle"]):
        voice["emotion"] = "calm"
    elif any(k in t for k in ["груб", "агрессив", "anger", "strong"]):
        voice["emotion"] = "aggressive"

    return voice


# --------------------------------------------------------
def map_emotion_to_english(mood: str, tone: str = "mid") -> str:
    """Converts emotion/tone info into English phrasing hints for Suno inline annotation."""
    mood = (mood or "neutral").lower()
    tone = (tone or "mid").lower()
    emotion_map = {
        "calm": "soft whisper, warm tone",
        "peaceful": "gentle flow, smooth phrasing",
        "hopeful": "light rise, airy resonance",
        "joyful": "open tone, bright timbre, smiling delivery",
        "sad": "slow breath, trembling vibrato",
        "melancholy": "emotional depth, low register warmth",
        "dramatic": "belted rasp, strong dynamic contrast",
        "angry": "harsh tone, powerful projection",
        "prayerful": "vibrato with tender breath",
        "romantic": "soft dynamics, emotional phrasing",
        "intense": "raspy tone, controlled tension",
        "neutral": "balanced tone, natural phrasing"
    }
    tone_map = {
        "low": "deep resonance",
        "mid": "mid-range timbre",
        "high": "bright tone",
        "whisper": "breathy delivery",
        "belt": "strong projection",
    }
    phrase = emotion_map.get(mood, "neutral phrasing, natural tone")
    tone_descr = tone_map.get(tone, "")
    return f"{phrase}, {tone_descr}".strip(", ")
