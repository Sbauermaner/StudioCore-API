from __future__ import annotations
import re, json, math, os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

# ------------ CONFIG ------------
VERSION_LIMITS = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
DEFAULT_CONFIG = {
    "suno_version": "v5",
    "safety": {
        "max_peak_db": -1.0,
        "max_rms_db": -14.0,
        "avoid_freq_bands_hz": [18.0, 30.0],
        "safe_octaves": [2,3,4,5],
        "max_session_minutes": 20,
        "fade_in_ms": 1000,
        "fade_out_ms": 1500
    },
    "pilgrim_modes": {
        "auto": True,
        "author": True,
        "healing": True,
        "dramatic": True,
        "ritual": True,
        "neutral": True,
        "pain-transmute": True,
        "rage-to-truth": True,
        "sacred-silence": True
    }
}

def _ensure_dir(p): os.makedirs(p, exist_ok=True)
def load_config(path: str="studio_config.json")->dict:
    if not os.path.exists(path):
        with open(path,"w",encoding="utf-8") as f: json.dump(DEFAULT_CONFIG,f,indent=2,ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path,"r",encoding="utf-8") as f: return json.load(f)
def save_config(cfg:dict, path: str="studio_config.json"):
    with open(path,"w",encoding="utf-8") as f: json.dump(cfg,f,indent=2,ensure_ascii=False)

# ------------ ENGINES ------------
class TruthLovePainEngine:
    _truth = ['truth','true','real','authentic','honest','истина','честно','реально','правда']
    _love  = ['love','care','heart','soul','compassion','unity','любовь','сердце','душа','забота','единство']
    _pain  = ['pain','hurt','loss','tears','cry','grief','страдание','боль','печаль','слёзы','горе']
    def analyze(self, text: str)->Dict[str,float]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ']+", text.lower())
        n = max(1,len(words))
        def score(bag): return sum(1 for w in words if w in bag)/n
        t,l,p = score(self._truth), score(self._love), score(self._pain)
        cf = (t*l*max(p,0.05))*10.0
        return {"truth": min(t*5,1.0), "love": min(l*5,1.0), "pain": min(p*5,1.0), "conscious_frequency": min(cf,1.0)}

class AutoEmotionalAnalyzer:
    dicts = {
        "joy": ['joy','happy','счаст','радость','улыб','smile','laugh'],
        "sadness": ['sad','грусть','печаль','слёзы','cry','tear'],
        "anger": ['anger','rage','ярость','злость','hate','furious'],
        "fear": ['страх','fear','паника','panic'],
        "peace": ['мир','спокой','тихо','calm','peace','still'],
        "epic": ['epic','геро','велич','монумент','anthem'],
        "truth": TruthLovePainEngine._truth,
        "love": TruthLovePainEngine._love,
        "pain": TruthLovePainEngine._pain
    }
    def analyze(self,text:str)->Dict[str,float]:
        s=text.lower()
        raw={k: sum(1 for t in v if t in s)/max(1,len(v)) for k,v in self.dicts.items()}
        total=sum(raw.values()) or 1.0
        return {k: v/total for k,v in raw.items()}

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

class RNSSafety:
    def __init__(self, config:dict): self.cfg=config["safety"]
    def clamp_octaves(self, rec:List[int])->List[int]:
        safe=set(self.cfg["safe_octaves"])
        filt=[o for o in rec if o in safe]
        return filt or [2,3,4]

class IntegrityScanEngine:
    def analyze(self, text:str)->Dict[str,Any]:
        words=re.findall(r"[^\s]+", text)
        sents=re.split(r"[.!?]+", text)
        form={"word_count":len(words),
              "sentence_count":len([s for s in sents if s.strip()]),
              "avg_sentence_len": (len(words)/max(1,len(sents)))}
        emo=AutoEmotionalAnalyzer().analyze(text)
        tlp=TruthLovePainEngine().analyze(text)
        ref_words=set("i me my myself я мне ясам сам себя думаю чувствую знаю понимаю".split())
        tokens=set(re.findall(r"[a-zA-Zа-яА-ЯёЁ']+", text.lower()))
        reflection=len(tokens & ref_words)/max(1,len(tokens))
        return {"form":form,"essence":{"emotions":emo,"tlp":tlp},"reflection":{"self_awareness":reflection}}

class ToneSyncEngine:
    def colors_for_primary(self, emo:Dict[str,float])->List[str]:
        m=max(emo, key=emo.get)
        cmap={"joy":["#FFD700","#FF6B6B"],"sadness":["#4169E1","#87CEEB"],"anger":["#DC143C","#8B0000"],
              "love":["#FF69B4","#FF1493"],"peace":["#98FB98","#F0FFF0"],"truth":["#FFFFFF","#000000"]}
        return cmap.get(m,["#808080","#A9A9A9"])
    def sync(self, text:str, emo:Dict[str,float])->Dict[str,Any]:
        colors=self.colors_for_primary(emo)
        intensity=sum(emo.values())/len(emo)
        balance=1.0 - (sum(abs(v-intensity) for v in emo.values())/len(emo))
        prof={"brightness":emo.get("joy",0)+emo.get("truth",0),
              "warmth":emo.get("love",0)+emo.get("peace",0),
              "depth":emo.get("sadness",0)+emo.get("fear",0),
              "intensity":emo.get("anger",0)+emo.get("epic",0)}
        sync = 1.0 - abs(balance - 0.66)
        return {"visual":{"palette":colors,"balance":balance},"audio":prof,"sync_score":max(0.0,min(sync,1.0))}

class LyricMeter:
    vowels=set("aeiouyауоыиэяюёе")
    def syllables(self,line:str)->int:
        w=line.lower()
        return max(1, sum(1 for ch in w if ch in self.vowels))
    def bpm_from_density(self, text:str)->int:
        lines=[l for l in text.splitlines() if l.strip()]
        if not lines: return 100
        avg = sum(self.syllables(l) for l in lines)/len(lines)
        bpm = int(140 - min(60, (avg-8)*6))
        return max(60, min(160, bpm))

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
    def recommend(self, emo:Dict[str,float], tlp:Dict[str,float], modes:Dict[str,bool])->str:
        # базовая логика + моды
        if modes.get("healing"): return "healing, clarity, compassionate space"
        if modes.get("dramatic"): return "anthemic dynamics with stark contrasts"
        if tlp["truth"]>0.7 and tlp["love"]>0.7: return "uplifting cinematic with warm harmonies"
        if tlp["pain"]>0.7 and tlp["truth"]>0.6: return "raw emotional rock with open space"
        if emo.get("epic",0)>0.4: return "anthemic arrangement with wide dynamics"
        return "balanced production with vocal clarity"

VALID_VOICES = [
    "male","female","duet","tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","clear","warm"
]
VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","strings","violin","cello","trumpet",
    "saxophone","organ","harp","choir","vocals","pad","flute","horns","percussion","war drums","tagelharpa","throat singing"
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
    def __init__(self): self.map=DEFAULT_VOCAL_MAP
    def get(self, genre:str, preferred_gender:str="auto")->Tuple[List[str],List[str]]:
        g=genre if genre in self.map else "rock"
        if preferred_gender=="female": vox=self.map[g]["female"]
        elif preferred_gender=="male": vox=self.map[g]["male"]
        else: vox=self.map[g]["male"]
        inst=self.map[g]["inst"]
        vox=[v for v in vox if v in VALID_VOICES]
        inst=[i for i in inst if i in VALID_INSTRUMENTS]
        return vox, inst

# ------------ SUNO PROMPT ------------
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
    max_len=VERSION_LIMITS.get(version.lower(), 1000)
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

# ------------ STRUCTURE OVERLAY ------------
def apply_structure(lyrics:str,
                    author_structure:Optional[List[Dict[str,str]]] = None,
                    auto_chorus_threshold:int = 2)->str:
    """
    Если автор дал структуру: вставляем метки [Section] + {Annotation}.
    Если нет: пытаемся авто-распознать повторяющиеся строки как припев.
    """
    lines=[l.rstrip() for l in lyrics.splitlines()]
    out=[]
    if author_structure:
        # ожидаем список словарей: {"tag":"Verse 1", "hint":"Tagelharpa + throat singing"}
        # секции разделяются пустыми строками
        i=0
        for sec in author_structure:
            tag = sec.get("tag","Section")
            hint = sec.get("hint","")
            out.append(f"[{tag}]" + (f" [{hint}]" if hint else ""))
            # собираем следующие непустые строки до пустой
            while i < len(lines) and lines[i].strip():
                out.append(lines[i]); i+=1
            # пропускаем возможные пустые между секциями
            while i < len(lines) and not lines[i].strip():
                i+=1
        # если остались строки — добавим их как Outro
        rest=[l for l in lines[i:] if l.strip()]
        if rest:
            out.append("[Outro]")
            out.extend(rest)
        return "\n".join(out)
    # авто-распознавание (простое): ищем самый частый 1–2 строки блока
    from collections import Counter
    blocks=[]
    buf=[]
    for l in lines + [""]:
        if l.strip(): buf.append(l)
        else:
            if buf: blocks.append("\n".join(buf)); buf=[]
    cnt=Counter(blocks)
    chorus = None
    for b, c in cnt.most_common():
        if c >= auto_chorus_threshold and len(b.splitlines())<=4:
            chorus=b; break
    v_idx=1
    for b in blocks:
        if chorus and b==chorus:
            out.append("[Chorus]")
            out.extend(b.splitlines())
        else:
            out.append(f"[Verse {v_idx}]")
            out.extend(b.splitlines())
            v_idx+=1
    return "\n".join(out)

# ------------ PIPELINE ------------
@dataclass
class PipelineResult:
    genre:str; bpm:int; tonality:str
    vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]
    resonance:Dict[str,Any]; integrity:Dict[str,Any]
    tonesync:Dict[str,Any]; prompt:str
    structured_lyrics:str

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

    def analyze(self,
                lyrics:str,
                prefer_gender:str="auto",
                modes:Optional[Dict[str,bool]]=None,
                author_style:Optional[str]=None,
                author_structure:Optional[List[Dict[str,str]]]=None)->PipelineResult:
        cfg_modes=self.config.get("pilgrim_modes",{})
        if modes: cfg_modes={**cfg_modes, **modes}
        tlp=self.tlp.analyze(lyrics)
        emotions=self.emo.analyze(lyrics)
        bpm=max(60, min(160, self.meter.bpm_from_density(lyrics)))
        genre=self.style.genre(emotions, tlp)
        ton=self.style.tonality(emotions)

        vox,inst=self.vocals.get(genre, preferred_gender=prefer_gender)

        # режимы влияют на инструменты/вокал
        if cfg_modes.get("ritual"):
            if "tagelharpa" in VALID_INSTRUMENTS and "tagelharpa" not in inst:
                inst = (inst + ["tagelharpa"])[:5]
            if "throat singing" in VALID_INSTRUMENTS and "throat singing" not in inst:
                inst = (inst + ["throat singing"])[:5]
        if cfg_modes.get("dramatic"):
            if "choir" not in inst: inst=(inst+["choir"])[:5]
            if "war drums" in VALID_INSTRUMENTS and "war drums" not in inst:
                inst=(inst+["war drums"])[:5]
        if cfg_modes.get("healing"):
            # смещение к мягким тембрам
            if "pad" not in inst: inst=(inst+["pad"])[:5]
            if "female" not in vox: vox=(vox+["female","warm"])[:5]

        res=self.freq.resonance_profile(tlp)
        res["recommended_octaves"]=self.rns.clamp_octaves(res["recommended_octaves"])
        integ=self.integrity.analyze(lyrics)
        ts=self.tsync.sync(lyrics, emotions)

        version=self.config.get("suno_version","v5")
        if author_style:
            style_words = author_style
        else:
            style_words = self.style.recommend(emotions, tlp, cfg_modes)

        philosophy="Truth × Love × Pain → Conscious Frequency. Healing-first, clarity over loudness."
        prompt=build_suno_prompt(genre, style_words, vox, inst, bpm, philosophy, version)

        structured=apply_structure(lyrics, author_structure=author_structure)
        return PipelineResult(genre,bpm,ton,vox,inst,tlp,emotions,res,integ,ts,prompt,structured)