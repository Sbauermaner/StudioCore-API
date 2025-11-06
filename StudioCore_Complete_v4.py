# -*- coding: utf-8 -*-
"""
StudioCore_Complete_v4 — Core (compact, full-logic kept)
Do not rename this file.
"""

from __future__ import annotations
import re, json, math, os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

# ===============================
# ---------- CONFIG -------------
# ===============================

VERSION_LIMITS = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
DEFAULT_CONFIG = {
    "suno_version": "v5",
    "safety": {
        "max_peak_db": -1.0,
        "max_rms_db": -14.0,
        "avoid_freq_bands_hz": [18.0, 30.0],
        "safe_octaves": [2, 3, 4, 5],
        "max_session_minutes": 20,
        "fade_in_ms": 1000,
        "fade_out_ms": 1500
    }
}

def load_config(path: str = "studio_config.json") -> dict:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===============================
# ---- TEXT NORMALIZATION -------
# ===============================

PUNCT_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))
PUNCT_WEIGHTS = {
    ",": 0.10, ".": 0.30, "!": 0.50, "?": 0.40, "…": 0.60,
    "—": 0.20, "–": 0.20, ":": 0.25, ";": 0.20, "\"": 0.05, "'": 0.05,
    "(": 0.05, ")": 0.05, "[": 0.05, "]": 0.05
}
EMOJI_WEIGHTS = {ch: 0.40 for ch in EMOJI_SAFE}
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

def ensure_line_punct(line: str) -> str:
    if not line: return line
    if line[-1] in ".!?…—–:;," or line.strip().endswith(("—","–")): return line
    return line + "."

def extract_sections(text: str) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    current = {"tag": "Body", "lines": []}
    for ln in text.split("\n"):
        m = SECTION_TAG_RE.match(ln)
        if m:
            if current["lines"]: sections.append(current)
            current = {"tag": m.group(1).strip(), "lines": []}
        else:
            if ln.strip() != "": current["lines"].append(ln)
    if current["lines"]: sections.append(current)
    return sections

# ===============================
# ----- PHILOSOPHY CORE ---------
# ===============================

class TruthLovePainEngine:
    _truth = ['truth','true','real','authentic','honest','истина','честно','реально','правда']
    _love  = ['love','care','heart','soul','compassion','unity','любовь','сердце','душа','забота','единство']
    _pain  = ['pain','hurt','loss','tears','cry','grief','страдание','боль','печаль','слёзы','горе']

    def analyze(self, text: str) -> Dict[str, float]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
        n = max(1, len(words))
        def score(bag): return sum(1 for w in words if w in bag)/n
        t, l, p = score(self._truth), score(self._love), score(self._pain)
        cf = (t*l*max(p,0.05))*10.0
        return {"truth": min(t*5,1.0), "love": min(l*5,1.0), "pain": min(p*5,1.0), "conscious_frequency": min(cf,1.0)}

# ===============================
# ----- EMOTION ANALYZER --------
# ===============================

class AutoEmotionalAnalyzer:
    base_dicts = {
        "joy":     ['joy','happy','счаст','радость','улыб','smile','laugh'],
        "sadness": ['sad','грусть','печаль','слёзы','cry','tear'],
        "anger":   ['anger','rage','ярость','злость','hate','furious'],
        "fear":    ['страх','fear','паника','panic'],
        "peace":   ['мир','спокой','тихо','calm','peace','still'],
        "epic":    ['epic','геро','велич','монумент','anthem']
    }
    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        raw = {k: sum(1 for t in v if t in s)/max(1,len(v)) for k,v in self.base_dicts.items()}
        punct_intensity = 0.0
        for ch in s:
            if ch in PUNCT_WEIGHTS: punct_intensity += PUNCT_WEIGHTS[ch]
            if ch in EMOJI_WEIGHTS: punct_intensity += EMOJI_WEIGHTS[ch]
        if punct_intensity > 0:
            raw["anger"] += 0.3 * punct_intensity
            raw["epic"]  += 0.4 * punct_intensity
            raw["joy"]   += 0.3 * punct_intensity
        total = (sum(raw.values()) or 1.0)
        return {k: v/total for k,v in raw.items()}

# ===============================
# ----- FREQUENCY ENGINE --------
# ===============================

class UniversalFrequencyEngine:
    base = 24.5
    mapping = {
        0: ("16-32Hz","Subconscious","Deep meditation","#000080"),
        1: ("33-65Hz","Body awareness","Physical presence","#4169E1"),
        2: ("66-130Hz","Emotional base","Feeling foundation","#00BFFF"),
        3: ("131-261Hz","Heart center","Emotional expression","#FF69B4"),
        4: ("262-523Hz","Voice of truth","Authentic communication","#FFD700"),
        5: ("524-1046Hz","Higher mind","Mental clarity","#90EE90"),
        6: ("1047-2093Hz","Intuitive wisdom","Inner knowing","#9370DB"),
        7: ("2094-4186Hz","Spiritual connection","Universal awareness","#FF4500"),
        8: ("4187-7902Hz","Cosmic unity","Transcendence","#FFFFFF")
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
        info = self.consciousness_info(base)
        if tlp["conscious_frequency"]>0.7: rec=[4,5,6,7]
        elif tlp["conscious_frequency"]>0.3: rec=[2,3,4,5]
        else: rec=[1,2,3,4]
        return {"base_frequency":base,"harmonic_range":spread,"modulation_depth":mod,"info":info,"recommended_octaves":rec}

# ===============================
# ---------- RNS SAFETY ---------
# ===============================

class RNSSafety:
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
        words=re.findall(r"[^\s]+", text)
        sents=re.split(r"[.!?]+", text)
        form={"word_count":len(words),"sentence_count":len([s for s in sents if s.strip()]),"avg_sentence_len": (len(words)/max(1,len(sents)))}
        emo=AutoEmotionalAnalyzer().analyze(text)
        tlp=TruthLovePainEngine().analyze(text)
        ref_words=set("i me my myself я мне меня сам себя думаю чувствую знаю понимаю".split())
        tokens=set(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()))
        reflection=len(tokens & ref_words)/max(1,len(tokens))
        return {"form":form,"essence":{"emotions":emo,"tlp":tlp},"reflection":{"self_awareness":reflection}}

# ===============================
# --------- TONESYNC ------------
# ===============================

class ToneSyncEngine:
    def colors_for_primary(self, emo:Dict[str,float])->List[str]:
        m=max(emo, key=emo.get)
        cmap={"joy":["#FFD700","#FF6B6B"],"sadness":["#4169E1","#87CEEB"],"anger":["#DC143C","#8B0000"],
              "love":["#FF69B4","#FF1493"],"peace":["#98FB98","#F0FFF0"],"epic":["#FFFFFF","#AAAAAA"]}
        return cmap.get(m,["#808080","#A9A9A9"])
    def sync(self, text:str, emo:Dict[str,float])->Dict[str,Any]:
        colors=self.colors_for_primary(emo)
        intensity=sum(emo.values())/len(emo)
        balance=1.0 - (sum(abs(v-intensity) for v in emo.values())/len(emo))
        prof={"brightness":emo.get("joy",0)+emo.get("epic",0)*0.3,
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
    def bpm_from_density(self, text:str)->int:
        lines=[l for l in text.split("\n") if l.strip()]
        if not lines: return 100
        avg = sum(self.syllables(l) for l in lines)/len(lines)
        bpm = 140 - min(60, (avg-8)*6)
        punct_boost = sum(PUNCT_WEIGHTS.get(ch,0.0) for ch in text)
        bpm = bpm + min(20, punct_boost * 4.0)
        return max(60, min(160, int(bpm)))

# ===============================
# -------- STYLE MATRIX ---------
# ===============================

class StyleMatrix:
    def genre(self, emo:Dict[str,float], tlp:Dict[str,float])->str:
        if emo.get("anger",0)>0.3 and emo.get("epic",0)>0.2: return "metal"
        if emo.get("joy",0)>0.3 and emo.get("love",0)>0.2:   return "pop"
        if emo.get("peace",0)>0.3 and emo.get("love",0)>0.2: return "ambient"
        if emo.get("peace",0)>0.3 and emo.get("truth",0)>0.2:return "folk"
        if emo.get("sadness",0)>0.3 and emo.get("truth",0)>0.2:return "classical"
        return "rock"
    def tonality(self, emo:Dict[str,float])->str:
        pos=emo.get("joy",0)+emo.get("love",0)+emo.get("peace",0)
        neg=emo.get("sadness",0)+emo.get("anger",0)+emo.get("fear",0)
        if pos>neg*1.3: return "major"
        if neg>pos*1.3: return "minor"
        return "modal"
    def recommend(self, emo:Dict[str,float], tlp:Dict[str,float], author_style:Optional[str]=None, sections:Optional[List[Dict[str,Any]]]=None)->str:
        base = (author_style.strip() if author_style else None)
        if not base:
            if tlp["truth"]>0.7 and tlp["love"]>0.7: base="uplifting cinematic with warm harmonies"
            elif tlp["pain"]>0.7 and tlp["truth"]>0.6: base="raw emotional rock with open space"
            elif emo.get("epic",0)>0.4: base="anthemic arrangement with wide dynamics"
            else: base="healing, clarity, compassionate space"
        tag_hints=[]
        if sections:
            for s in sections:
                tag=s.get("tag","")
                if any(k in tag.lower() for k in ["tagelharpa","throat","choir","chant","blast","drum"]):
                    tag_hints.append(tag)
        if tag_hints: base=f"{base}; hints: "+", ".join(sorted(set(tag_hints))[:4])
        return base

# ===============================
# ---- VOCAL / INSTRUMENT MAP ---
# ===============================

VALID_VOICES = [
    "male","female","duet","tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","warm","clear","choir"
]
VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello","trumpet",
    "saxophone","organ","harp","choir","vocals","pad","flute","horns","percussion","tagelharpa"
]
DEFAULT_VOCAL_MAP = {
    "metal":      {"female":["female","powerful","alto"], "male":["male","powerful","baritone"], "inst":["guitar","drums","strings","choir"]},
    "rock":       {"female":["female","emotional","alto"], "male":["male","raspy","tenor"], "inst":["guitar","drums","bass","piano"]},
    "pop":        {"female":["female","clear","soprano"],  "male":["male","soft","tenor"], "inst":["piano","synth","bass","drums"]},
    "folk":       {"female":["female","warm","alto"],      "male":["male","emotional","baritone"], "inst":["guitar","strings","flute"]},
    "classical":  {"female":["soprano","angelic"],         "male":["tenor","baritone"], "inst":["strings","piano","choir"]},
    "electronic": {"female":["female","breathy"],          "male":["male","soft"], "inst":["synth","pad","bass","drums"]},
    "ambient":    {"female":["female","whispered"],        "male":["male","soft"], "inst":["pad","piano","strings"]},
    "orchestral": {"female":["female","angelic"],          "male":["male","deep"], "inst":["strings","choir","horns","percussion"]}
}
class VocalProfileRegistry:
    def __init__(self): self.map=DEFAULT_VOCAL_MAP
    def get(self, genre:str, preferred_gender:str="auto")->Tuple[List[str],List[str]]:
        g=genre if genre in self.map else "rock"
        if preferred_gender=="female": vox=self.map[g]["female"]
        elif preferred_gender=="male": vox=self.map[g]["male"]
        elif preferred_gender=="duet": vox=list(dict.fromkeys(self.map[g]["male"]+["female","duet"]))
        elif preferred_gender=="choir": vox=list(dict.fromkeys(self.map[g]["male"]+["choir"]))
        else: vox=self.map[g]["male"]
        inst=self.map[g]["inst"]
        vox=[v for v in vox if v in VALID_VOICES]
        inst=[i for i in inst if i in VALID_INSTRUMENTS]
        return vox, inst

# ===============================
# ------- SUNO ADAPTER ----------
# ===============================

def soft_trim(text:str, max_len:int)->str:
    txt=re.sub(r"\s+"," ",text).strip()
    if len(txt)<=max_len: return txt
    for token in ["Philosophy:","Production:","Instruments:","Vocals:"]:
        if len(txt)<=max_len: break
        if token in txt:
            txt=re.sub(rf"{token}[^|]*\|?","",txt).strip(" |")
    if len(txt)>max_len: txt=txt[:max_len].rsplit(" ",1)[0]
    return txt

def build_suno_prompt(genre:str, style_words:str, vocals:List[str], instruments:List[str],
                      bpm:Optional[int], philosophy:str, version:str)->str:
    max_len=VERSION_LIMITS.get(version.lower(),1000)
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
# ------- RHYME / SKELETON ------
# ===============================

def rhyme_tail(w:str)->str:
    w=w.lower()
    w=re.sub(r"[^a-zа-яё]+","",w)
    return w[-3:] if len(w)>=3 else w

def make_skeleton(text:str, prefer_gender:str, genre_hint:str, emo:Dict[str,float])->str:
    lines=[ln.strip() for ln in text.split("\n") if ln.strip()]
    # авто-пунктуация построчно
    lines=[ensure_line_punct(ln) for ln in lines]

    # примитивный припев: ищем повторяющиеся или самые «сильные» строки
    chorus_idx=[]
    if len(lines)>=4:
        seen={}
        for i,ln in enumerate(lines):
            key=rhyme_tail(ln.split()[-1]) if ln.split() else ""
            seen.setdefault(key, []).append(i)
        # выберем ключ с наибольшим повтором
        key=max(seen, key=lambda k: len(seen[k])) if seen else None
        chorus_idx=(seen.get(key,[])[:2] if key else [])

    blocks=[]
    i=0; verse_num=1; used_chorus=False
    while i < len(lines):
        # Verse блок 2–4 строки
        chunk=lines[i:i+4]; i+=len(chunk)
        tag=f"[Verse {verse_num}]"
        voice_hint="(male emotional tenor)" if prefer_gender=="male" else "(female warm alto)" if prefer_gender=="female" else "(duet / adaptive)"
        blocks.append(f"{tag} {voice_hint}\n" + "\n".join(chunk))
        verse_num+=1
        # Вставим припев, если найден и ещё не вставляли
        if chorus_idx and not used_chorus:
            ch_lines=[lines[j] for j in chorus_idx]
            blocks.append("[Chorus] (strong, open chest)\n" + "\n".join(ch_lines))
            used_chorus=True

    # если не вставили — сгенерируем мягкий припев из самой сильной строки
    if not used_chorus and lines:
        strongest=max(lines, key=lambda ln: sum(PUNCT_WEIGHTS.get(ch,0.0) for ch in ln))
        blocks.append("[Chorus] (anthemic focus)\n"+ strongest)

    return "\n\n".join(blocks)

# ===============================
# ------- PIPELINE CORE ---------
# ===============================

@dataclass
class PipelineResult:
    genre:str; bpm:int; tonality:str
    vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]
    resonance:Dict[str,Any]; integrity:Dict[str,Any]
    tonesync:Dict[str,Any]; sections:List[Dict[str,Any]]
    prompt:str

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

    def analyze(self, lyrics:str, prefer_gender:str="auto", author_style:Optional[str]=None, genre_hint:Optional[str]=None)->PipelineResult:
        raw=normalize_text(lyrics)
        sections=extract_sections(raw)
        tlp=self.tlp.analyze(raw)
        emotions=self.emo.analyze(raw)
        bpm=max(60,min(160,self.meter.bpm_from_density(raw)))
        genre = (genre_hint or self.style.genre(emotions, tlp))
        ton=self.style.tonality(emotions)
        vox,inst=self.vocals.get(genre, preferred_gender=prefer_gender)
        # tag instruments
        tag_text=" ".join([s["tag"] for s in sections])
        if re.search(r"tagelharpa", tag_text, flags=re.I) and "tagelharpa" not in inst:
            inst=(inst+["tagelharpa"])[:5]
        res=self.freq.resonance_profile(tlp)
        res["recommended_octaves"]=self.rns.clamp_octaves(res["recommended_octaves"])
        integ=self.integrity.analyze(raw)
        ts=self.tsync.sync(raw, emotions)
        version=self.config.get("suno_version","v5")
        philosophy="Truth × Love × Pain → Conscious Frequency. Healing-first, clarity over loudness."
        sw=self.style.recommend(emotions, tlp, author_style=author_style, sections=sections)
        prompt=build_suno_prompt(genre, sw, vox, inst, bpm, philosophy, version)
        return PipelineResult(genre,bpm,ton,vox,inst,tlp,emotions,res,integ,ts,sections,prompt)
