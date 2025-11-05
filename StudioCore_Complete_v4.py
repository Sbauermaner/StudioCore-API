# -*- coding: utf-8 -*-
"""
StudioCore Complete v4 — Conscious Resonant Engine
Author: Bauer Synesthetic Studio (Serhiy Bauer project)
Date: 2025-11-05

Включает:
- Truth × Love × Pain философское ядро
- AutoEmotional Analyzer (RU/EN/ES/FR ключ-слова)
- UniversalFrequencyEngine + Consciousness mapping
- RNS (Resonance–Nervous–Safety) безопасные частоты/ограничения
- IntegrityScan (форма/сущность/рефлексия)
- ToneSync (согласование аудио/визуала)
- LyricMeter & Metronome (силлабика/стресс/темп)
- StyleMatrix (жанр/BPM/тональность из эмо-матрицы)
- SunoAdapter (v3–v5+) с авто-лимитами и soft-trim
- VocalProfileRegistry (жанр→вокал/инструменты; муж/жен/дуэт)
- Профили пользователей: импорт/экспорт/merge
- build_pipeline(): анализ текста → стиль → готовый Suno prompt

Файлы:
- auto: studio_config.json (версия Suno, флаги безопасности)
- опционально: profiles/*.json (пользовательские профили)

Запуск:
python StudioCore_Complete_v4.py
"""

from __future__ import annotations
import re, json, math, os, uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

# ===============================
# ---------- CONFIG -------------
# ===============================

VERSION_LIMITS = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
DEFAULT_CONFIG = {
    "suno_version": "v5",
    "safety": {
        "max_peak_db": -1.0,        # ограничение пикового уровня
        "max_rms_db": -14.0,        # целевой RMS
        "avoid_freq_bands_hz": [18.0, 30.0], # избегать ИНФРА полос
        "safe_octaves": [2,3,4,5],  # рекомендованные октавы
        "max_session_minutes": 20,  # длительность сессии
        "fade_in_ms": 1000,
        "fade_out_ms": 1500
    }
}

def _ensure_dir(p): 
    os.makedirs(p, exist_ok=True)

def load_config(path: str="studio_config.json")->dict:
    if not os.path.exists(path):
        with open(path,"w",encoding="utf-8") as f: json.dump(DEFAULT_CONFIG,f,indent=2,ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path,"r",encoding="utf-8") as f: return json.load(f)

def save_config(cfg:dict, path: str="studio_config.json"):
    with open(path,"w",encoding="utf-8") as f: json.dump(cfg,f,indent=2,ensure_ascii=False)

# ===============================
# ----- PHILOSOPHY CORE ---------
# ===============================

class TruthLovePainEngine:
    """Truth recognizes, Love connects, Pain transforms → Conscious Frequency"""
    _truth = ['truth','true','real','authentic','honest','глуправда','истина','честно','реально','правда']
    _love  = ['love','care','heart','soul','compassion','unity','любовь','сердце','душа','забота','единство']
    _pain  = ['pain','hurt','loss','tears','cry','grief','страдание','боль','печаль','слёзы','горе']

    def analyze(self, text: str)->Dict[str,float]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ']+", text.lower())
        n = max(1,len(words))
        def score(bag): return sum(1 for w in words if w in bag)/n
        t,l,p = score(self._truth), score(self._love), score(self._pain)
        cf = (t*l*max(p,0.05))*10.0
        return {"truth": min(t*5,1.0), "love": min(l*5,1.0), "pain": min(p*5,1.0), "conscious_frequency": min(cf,1.0)}

# ===============================
# ----- EMOTION ANALYZER --------
# ===============================

class AutoEmotionalAnalyzer:
    dicts = {
        "joy": ['joy','happy','счаст','радость','улыб','smile','laugh'],
        "sadness": ['sad','грусть','печаль','слёзы','cry','tear'],
        "anger": ['anger','rage','ярость','злость','hate','furious'],
        "fear": ['страх','fear','паника','panic'],
        "peace": ['мир','спокой','тихо','calm','peace','still'],
        "epic": ['epic','геро','велич','монумент','анфим','anthem'],
        "truth": TruthLovePainEngine._truth,
        "love": TruthLovePainEngine._love,
        "pain": TruthLovePainEngine._pain
    }
    def analyze(self,text:str)->Dict[str,float]:
        s=text.lower(); raw={k: sum(1 for t in v if t in s)/max(1,len(v)) for k,v in self.dicts.items()}
        total=sum(raw.values()) or 1.0
        return {k: v/total for k,v in raw.items()}
    def entropy(self, em:Dict[str,float])->float:
        e=0.0
        for p in em.values():
            if p>0: e-=p*math.log(p)
        return e

# ===============================
# ----- FREQUENCY ENGINE --------
# ===============================

class UniversalFrequencyEngine:
    base=24.5
    mapping={
        0:("16-32Hz","Subconscious","Deep meditation","#000080"),
        1:("33-65Hz","Body awareness","Physical presence","#4169E1"),
        2:("66-130Hz","Emotional base","Feeling foundation","#00BFFF"),
        3:("131-261Hz","Heart center","Emotional expression","#FF69B4"),
        4:("262-523Hz","Voice of truth","Authentic communication","#FFD700"),
        5:("524-1046Hz","Higher mind","Mental clarity","#90EE90"),
        6:("1047-2093Hz","Intuitive wisdom","Inner knowing","#9370DB"),
        7:("2094-4186Hz","Spiritual connection","Universal awareness","#FF4500"),
        8:("4187-7902Hz","Cosmic unity","Transcendence","#FFFFFF")
    }
    def consciousness_info(self,f:float)->Dict[str,Any]:
        for octv,(rng,cons,state,color) in self.mapping.items():
            mn,mx=map(float,rng.replace("Hz","").split("-"))
            if mn<=f<=mx: return {"octave":octv,"range":rng,"consciousness":cons,"state":state,"color":color}
        return {"octave":-1,"range":"Unknown","consciousness":"Unknown","state":"Unknown","color":"#000000"}

    def resonance_profile(self, tlp:Dict[str,float])->Dict[str,Any]:
        base = self.base*(1.0+tlp["truth"])
        spread = tlp["love"]*2000.0
        mod = 1.0 + tlp["pain"]*0.5
        info=self.consciousness_info(base)
        if tlp["conscious_frequency"]>0.7: rec=[4,5,6,7]
        elif tlp["conscious_frequency"]>0.3: rec=[2,3,4,5]
        else: rec=[1,2,3,4]
        return {"base_frequency":base,"harmonic_range":spread,"modulation_depth":mod,"info":info,"recommended_octaves":rec}

# ===============================
# ---------- RNS SAFETY ---------
# ===============================

class RNSSafety:
    """Resonance–Nervous–Safety guard: ограничение частот/длительности/уровней."""
    def __init__(self, config:dict): self.cfg=config["safety"]
    def check_band(self, freq: float)->bool:
        lo,hi=self.cfg["avoid_freq_bands_hz"][0], self.cfg["avoid_freq_bands_hz"][1]
        return not (lo<=freq<=hi)
    def suggested_gain_db(self)->Tuple[float,float]:
        return (self.cfg["max_peak_db"], self.cfg["max_rms_db"])
    def session_limit(self)->int: return self.cfg["max_session_minutes"]
    def fade_edges_ms(self)->Tuple[int,int]: return self.cfg["fade_in_ms"],self.cfg["fade_out_ms"]
    def clamp_octaves(self, rec:List[int])->List[int]:
        safe=set(self.cfg["safe_octaves"])
        filt=[o for o in rec if o in safe]
        return filt or [2,3,4]

# ===============================
# ------- INTEGRITY SCAN --------
# ===============================

class IntegrityScanEngine:
    def analyze(self, text:str)->Dict[str,Any]:
        words=re.findall(r"[^\s]+", text); sents=re.split(r"[.!?]+", text)
        form={"word_count":len(words),
              "sentence_count":len([s for s in sents if s.strip()]),
              "avg_sentence_len": (len(words)/max(1,len(sents)))}
        emo=AutoEmotionalAnalyzer().analyze(text)
        tlp=TruthLovePainEngine().analyze(text)
        ref_words=set("i me my myself я мне мнея ясам сам себя думаю чувствую знаю понимаю".split())
        tokens=set(re.findall(r"[a-zA-Zа-яА-ЯёЁ']+", text.lower()))
        reflection=len(tokens & ref_words)/max(1,len(tokens))
        return {"form":form,"essence":{"emotions":emo,"tlp":tlp},"reflection":{"self_awareness":reflection}}

# ===============================
# --------- TONESYNC ------------
# ===============================

class ToneSyncEngine:
    def colors_for_primary(self, emo:Dict[str,float])->List[str]:
        m=max(emo, key=emo.get)
        cmap={"joy":["#FFD700","#FF6B6B"],"sadness":["#4169E1","#87CEEB"],"anger":["#DC143C","#8B0000"],
              "love":["#FF69B4","#FF1493"],"peace":["#98FB98","#F0FFF0"],"truth":["#FFFFFF","#000000"]}
        return cmap.get(m,["#808080","#A9A9A9"])
    def sync(self, text:str, emo:Dict[str,float])->Dict[str,Any]:
        colors=self.colors_for_primary(emo); intensity=sum(emo.values())/len(emo)
        balance=1.0 - (sum(abs(v-intensity) for v in emo.values())/len(emo))
        # упрощённый аудио-профиль:
        prof={"brightness":emo.get("joy",0)+emo.get("truth",0),
              "warmth":emo.get("love",0)+emo.get("peace",0),
              "depth":emo.get("sadness",0)+emo.get("fear",0),
              "intensity":emo.get("anger",0)+emo.get("epic",0)}
        sync = 1.0 - abs(balance - 0.66)
        return {"visual":{"palette":colors,"balance":balance},"audio":prof,"sync_score":max(0.0,min(sync,1.0))}

# ===============================
# ------ LYRIC METER / BPM ------
# ===============================

class LyricMeter:
    vowels=set("aeiouyауоыиэяюёе")
    def syllables(self,line:str)->int:
        w=line.lower()
        return max(1, sum(1 for ch in w if ch in self.vowels))
    def line_meter(self,line:str)->Dict[str,Any]:
        syl=self.syllables(line)
        stress = "end" if re.search(r"[.!?…—-]?$", line.strip()) else "mixed"
        return {"syllables":syl,"stress":stress}
    def bpm_from_density(self, text:str)->int:
        lines=[l for l in text.splitlines() if l.strip()]
        if not lines: return 100
        avg = sum(self.syllables(l) for l in lines)/len(lines)
        # чем плотнее слогов — тем ниже удобный BPM для ясности
        bpm = int(140 - min(60, (avg-8)*6))
        return max(60, min(160, bpm))

# ===============================
# -------- STYLE MATRIX ---------
# ===============================

class StyleMatrix:
    def genre(self, emo:Dict[str,float], tlp:Dict[str,float])->str:
        if emo.get("anger",0)>0.3 and emo.get("epic",0)>0.2: return "metal"
        if emo.get("joy",0)>0.3 and emo.get("love",0)>0.2: return "pop"
        if emo.get("peace",0)>0.3 and emo.get("truth",0)>0.2: return "folk"
        if emo.get("sadness",0)>0.3 and emo.get("truth",0)>0.2: return "classical"
        return "rock"
    def tonality(self, emo:Dict[str,float])->str:
        pos=emo.get("joy",0)+emo.get("love",0)+emo.get("peace",0)
        neg=emo.get("sadness",0)+emo.get("anger",0)+emo.get("fear",0)
        if pos>neg*1.3: return "major"
        if neg>pos*1.3: return "minor"
        return "modal"
    def recommend(self, emo:Dict[str,float], tlp:Dict[str,float])->str:
        if tlp["truth"]>0.7 and tlp["love"]>0.7: return "uplifting cinematic with warm harmonies"
        if tlp["pain"]>0.7 and tlp["truth"]>0.6: return "raw emotional rock with open space"
        if emo.get("epic",0)>0.4: return "anthemic arrangement with wide dynamics"
        return "balanced production with vocal clarity"

# ===============================
# ---- VOCAL PROFILE REGISTRY ---
# ===============================

VALID_GENRES = [
    "pop","rock","hip hop","rap","r&b","electronic","edm","house","techno","trance",
    "dubstep","lofi","jazz","blues","classical","folk","country","reggae","punk",
    "metal","indie","alternative","k-pop","j-pop","synthwave","ambient","orchestral","cinematic"
]
VALID_VOICES = [
    "male","female","duet","tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered"
]
VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello","trumpet",
    "saxophone","organ","harp","choir","vocals","pad","flute","horns","percussion"
]

DEFAULT_VOCAL_MAP = {
    "metal":       {"female":["female","powerful","alto"], "male":["male","powerful","baritone"], "inst":["guitar","drums","strings","choir"]},
    "rock":        {"female":["female","emotional","alto"], "male":["male","raspy","tenor"], "inst":["guitar","drums","bass","piano"]},
    "pop":         {"female":["female","clear","soprano"], "male":["male","soft","tenor"], "inst":["piano","synth","bass","drums"]},
    "folk":        {"female":["female","warm","alto"],     "male":["male","emotional","baritone"], "inst":["guitar","strings","flute"]},
    "classical":   {"female":["soprano","angelic"],        "male":["tenor","baritone"], "inst":["strings","piano","choir"]},
    "electronic":  {"female":["female","breathy"],         "male":["male","soft"], "inst":["synth","pad","bass","drums"]},
    "orchestral":  {"female":["female","angelic"],         "male":["male","deep"], "inst":["strings","choir","horns","percussion"]},
    "ambient":     {"female":["female","whispered"],       "male":["male","soft"], "inst":["pad","piano","strings"]}
}

class VocalProfileRegistry:
    def __init__(self):
        self.map=DEFAULT_VOCAL_MAP
    def get(self, genre:str, preferred_gender:str="auto")->Tuple[List[str],List[str]]:
        g=genre if genre in self.map else "rock"
        if preferred_gender=="female": vox=self.map[g]["female"]
        elif preferred_gender=="male": vox=self.map[g]["male"]
        else: 
            # auto: жен если love/peace выше, иначе муж
            vox=self.map[g]["male"]
        inst=self.map[g]["inst"]
        # фильтрация по whitelists
        vox=[v for v in vox if v in VALID_VOICES]
        inst=[i for i in inst if i in VALID_INSTRUMENTS]
        return vox, inst
    # профили пользователей
    def export_profile(self, path:str="profiles/default_profile.json"):
        _ensure_dir(os.path.dirname(path))
        with open(path,"w",encoding="utf-8") as f: json.dump(self.map,f,indent=2,ensure_ascii=False)
    def import_profile(self, path:str):
        with open(path,"r",encoding="utf-8") as f:
            user=json.load(f)
        self.map.update(user)

# ===============================
# ------- SUNO ADAPTER ----------
# ===============================

def soft_trim(text:str, max_len:int)->str:
    txt=re.sub(r"\s+"," ",text).strip()
    if len(txt)<=max_len: return txt
    # soft removal priority blocks
    for token in ["Philosophy:","Production:","Instruments:","Vocals:"]:
        if len(txt)<=max_len: break
        if token in txt:
            txt=re.sub(rf"{token}[^|]*\|?","",txt).strip(" |")
    if len(txt)>max_len: txt=txt[:max_len].rsplit(" ",1)[0]
    return txt

def build_suno_prompt(genre:str, style_words:str, vocals:List[str], instruments:List[str],
                      bpm:Optional[int], philosophy:str, version:str)->str:
    max_len=VERSION_LIMITS.get(version.lower(),"v5" and 1000)
    parts=[
        f"Genre: {genre}",
        f"Style: {style_words}",
        f"Vocals: {', '.join(vocals[:5])}",
        f"Instruments: {', '.join(instruments[:5])}",
        f"BPM: {bpm}" if bpm else "",
        f"Philosophy: {philosophy}",
        "Production: spatial depth, harmonic clarity, vocal intelligibility"
    ]
    prompt=" | ".join([p for p in parts if p])
    return soft_trim(prompt, max_len)

# ===============================
# ------- PIPELINE CORE ---------
# ===============================

@dataclass
class PipelineResult:
    genre:str; bpm:int; tonality:str
    vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]
    resonance:Dict[str,Any]; integrity:Dict[str,Any]
    tonesync:Dict[str,Any]; prompt:str

class StudioCore:
    def __init__(self, config:Optional[dict]=None):
        self.config=config or load_config()
        self.tlp=TruthLovePainEngine()
        self.emo=AutoEmotionalAnalyzer()
        self.freq=UniversalFrequencyEngine()
        self.integrity=IntegrityScanEngine()
        self.tsync=ToneSyncEngine()
        self.meter=LyricMeter()
        self.style=StyleMatrix()
        self.vocals=VocalProfileRegistry()
        self.rns=RNSSafety(self.config)

    def analyze(self, lyrics:str, prefer_gender:str="auto")->PipelineResult:
        tlp=self.tlp.analyze(lyrics)
        emotions=self.emo.analyze(lyrics)
        bpm_m=self.meter.bpm_from_density(lyrics)
        bpm=max(60, min(160, bpm_m))
        genre=self.style.genre(emotions, tlp)
        ton=self.style.tonality(emotions)
        vox,inst=self.vocals.get(genre, preferred_gender=prefer_gender)
        res=self.freq.resonance_profile(tlp)
        res["recommended_octaves"]=self.rns.clamp_octaves(res["recommended_octaves"])
        integ=self.integrity.analyze(lyrics)
        ts=self.tsync.sync(lyrics, emotions)
        version=self.config.get("suno_version","v5")
        philosophy="Truth × Love × Pain → Conscious Frequency. Healing-first, clarity over loudness."
        # style words:
        sw = self.style.recommend(emotions, tlp)
        prompt=build_suno_prompt(genre, sw, vox, inst, bpm, philosophy, version)
        return PipelineResult(genre,bpm,ton,vox,inst,tlp,emotions,res,integ,ts,prompt)

    # экспорт/импорт профилей
    def export_profiles(self, path:str="profiles/default_profile.json"):
        self.vocals.export_profile(path)
    def import_profiles(self, path:str):
        self.vocals.import_profile(path)

# ===============================
# -------------- DEMO -----------
# ===============================

def demo():
    cfg=load_config()
    core=StudioCore(cfg)
    sample = ("В небе летят не журавли, а ракеты. Пока лидеры жмут руки — мир горит. "
              "Но сердце помнит правду и любовь. Мы ищем частоту исцеления, а не разрушения.")
    result=core.analyze(sample, prefer_gender="male")
    print("=== StudioCore v4 DEMO ===")
    print("Genre:", result.genre, "| BPM:", result.bpm, "| Tonality:", result.tonality)
    print("Vocals:", ", ".join(result.vocals))
    print("Instruments:", ", ".join(result.instruments))
    print("TLP:", result.tlp)
    print("Resonance base:", f"{result.resonance['base_frequency']:.2f} Hz", "| Octaves:", result.resonance["recommended_octaves"])
    print("Integrity(avg sent len):", f"{result.integrity['form']['avg_sentence_len']:.2f}")
    print("\nSuno Prompt:\n", result.prompt)
    print("\nPrompt length:", len(result.prompt), f"/ {VERSION_LIMITS[cfg['suno_version']]}")

if __name__=="__main__":
    demo()
