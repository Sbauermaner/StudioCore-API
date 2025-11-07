from __future__ import annotations
import re, json, os, math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

# ---------- CONFIG ----------
VERSION_LIMITS = {"v3":200,"v3.5":200,"v4":500,"v5":1000}
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
    }
}

def load_config(path: str = "studio_config.json") -> dict:
    if not os.path.exists(path):
        with open(path,"w",encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG,f,indent=2,ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

# ---------- TEXT ----------
PUNCT_WEIGHTS = {",":0.10,".":0.30,"!":0.50,"?":0.40,"…":0.60,"—":0.20,"–":0.20,":":0.25,";":0.20,"\"":0.05,"'":0.05,"(":0.05,")":0.05,"[":0.05,"]":0.05}
SAFE_KEEP = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))

SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def normalize_text(text: str) -> str:
    text = text.replace("\r\n","\n").replace("\r","\n")
    lines = [re.sub(r"[ \t]+"," ",ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

def extract_sections(text: str) -> List[Dict[str,Any]]:
    sections, cur = [], {"tag":"Body","lines":[]}
    for ln in text.split("\n"):
        m = SECTION_TAG_RE.match(ln)
        if m:
            if cur["lines"]: sections.append(cur)
            cur = {"tag":m.group(1).strip(),"lines":[]}
        else:
            cur["lines"].append(ln)
    if cur["lines"]: sections.append(cur)
    for s in sections:
        s["lines"] = [l for l in s["lines"] if l.strip()!=""]
    return sections

# ---------- ENGINES ----------
class TruthLovePain:
    t = ['truth','true','real','authentic','honest','истина','честно','реально','правда']
    l = ['love','care','heart','soul','compassion','unity','любовь','сердце','душа','забота','единство']
    p = ['pain','hurt','loss','tears','cry','grief','страдання','страдание','боль','печаль','слёзы','горе']
    def analyze(self, text:str)->Dict[str,float]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
        n = max(1,len(words))
        def sc(b): return sum(1 for w in words if w in b)/n
        tv, lv, pv = sc(self.t), sc(self.l), sc(self.p)
        cf = (tv*lv*max(pv,0.05))*10.0
        return {"truth":min(tv*5,1.0), "love":min(lv*5,1.0), "pain":min(pv*5,1.0), "conscious_frequency":min(cf,1.0)}

class Emo:
    base = {
        "joy": ['joy','happy','счаст','радость','улыб','smile','laugh'],
        "sadness": ['sad','грусть','печаль','слёзы','cry','tear'],
        "anger": ['anger','rage','ярость','злость','hate','furious'],
        "fear": ['страх','fear','паника','panic'],
        "peace": ['мир','спокой','тихо','calm','peace','still'],
        "epic": ['epic','геро','велич','монумент','anthem'],
        "love": ['love','любов']
    }
    def analyze(self,text:str)->Dict[str,float]:
        s = text.lower()
        raw = {k: sum(1 for t in v if t in s)/max(1,len(v)) for k,v in self.base.items()}
        punct = sum(PUNCT_WEIGHTS.get(ch,0.0) for ch in s)
        if punct>0:
            raw["anger"] += 0.2*punct
            raw["epic"]  += 0.3*punct
            raw["joy"]   += 0.2*punct
        tot = sum(raw.values()) or 1.0
        return {k: v/tot for k,v in raw.items()}

class Freq:
    base = 24.5
    mapping = {
        0: ("16-32Hz", "Subconscious","Deep meditation","#000080"),
        1: ("33-65Hz", "Body awareness","Physical presence","#4169E1"),
        2: ("66-130Hz","Emotional base","Feeling foundation","#00BFFF"),
        3: ("131-261Hz","Heart center","Emotional expression","#FF69B4"),
        4: ("262-523Hz","Voice of truth","Authentic communication","#FFD700"),
        5: ("524-1046Hz","Higher mind","Mental clarity","#90EE90"),
        6: ("1047-2093Hz","Intuitive wisdom","Inner knowing","#9370DB"),
        7: ("2094-4186Hz","Spiritual connection","Universal awareness","#FF4500"),
        8: ("4187-7902Hz","Cosmic unity","Transcendence","#FFFFFF")
    }
    def info(self,f:float)->Dict[str,Any]:
        for o,(rng,cons,state,color) in self.mapping.items():
            lo,hi = [float(x) for x in rng.replace("Hz","").split("-")]
            if lo<=f<=hi:
                return {"octave":o,"range":rng,"consciousness":cons,"state":state,"color":color}
        return {"octave":-1,"range":"Unknown","consciousness":"Unknown","state":"Unknown","color":"#000000"}
    def resonance(self, tlp:Dict[str,float])->Dict[str,Any]:
        base = self.base*(1.0+tlp["truth"])
        spread = tlp["love"]*2000.0
        mod = 1.0 + tlp["pain"]*0.5
        info = self.info(base)
        if tlp["conscious_frequency"]>0.7: rec=[4,5,6,7]
        elif tlp["conscious_frequency"]>0.3: rec=[2,3,4,5]
        else: rec=[1,2,3,4]
        return {"base_frequency":base,"harmonic_range":spread,"modulation_depth":mod,"info":info,"recommended_octaves":rec}

class Safety:
    def __init__(self,cfg:dict): self.cfg = cfg["safety"]
    def clamp(self, rec:List[int])->List[int]:
        safe=set(self.cfg["safe_octaves"])
        out=[o for o in rec if o in safe]
        return out or [2,3,4]

class Meter:
    vowels=set("aeiouyауоыиэяюёе")
    def syll(self,line:str)->int:
        w=line.lower()
        return max(1,sum(1 for ch in w if ch in self.vowels))
    def bpm(self,text:str)->int:
        lines=[l for l in text.split("\n") if l.strip()]
        if not lines: return 100
        avg=sum(self.syll(l) for l in lines)/len(lines)
        bpm=140 - min(60,(avg-8)*6)
        punct_boost = sum(PUNCT_WEIGHTS.get(ch,0.0) for ch in text)
        bpm = bpm + min(20, punct_boost*4.0)
        return max(60,min(160,int(bpm)))

class Style:
    def genre(self, emo:Dict[str,float], tlp:Dict[str,float])->str:
        if emo.get("anger",0)>0.3 and emo.get("epic",0)>0.2: return "metal"
        if emo.get("joy",0)>0.3 and emo.get("love",0)>0.2:   return "pop"
        if emo.get("peace",0)>0.3 and emo.get("love",0)>0.2: return "ambient"
        if emo.get("peace",0)>0.3 and tlp.get("truth",0)>0.2:return "folk"
        if emo.get("sadness",0)>0.3 and tlp.get("truth",0)>0.2:return "classical"
        return "rock"
    def tonality(self,emo:Dict[str,float])->str:
        pos = emo.get("joy",0)+emo.get("love",0)+emo.get("peace",0)
        neg = emo.get("sadness",0)+emo.get("anger",0)+emo.get("fear",0)
        if pos>neg*1.3: return "major"
        if neg>pos*1.3: return "minor"
        return "modal"
    def recommend(self,emo,tlp,author_style=None,sections=None)->str:
        base = author_style.strip() if author_style else None
        if not base:
            if tlp["truth"]>0.7 and tlp["love"]>0.7: base="uplifting cinematic with warm harmonies"
            elif tlp["pain"]>0.7 and tlp["truth"]>0.6: base="raw emotional rock with open space"
            elif emo.get("epic",0)>0.4: base="anthemic arrangement with wide dynamics"
            else: base="healing, clarity, compassionate space"
        hints=[]
        if sections:
            for s in sections:
                tag=s.get("tag","")
                if any(k in tag.lower() for k in ["tagelharpa","throat","choir","chant","blast","drum","duet","a cappella"]):
                    hints.append(tag)
        if hints:
            base = f"{base}; hints: "+", ".join(sorted(set(hints))[:4])
        return base

VALID_VOICES = ["male","female","duet","choir","tenor","soprano","alto","baritone","bass","raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","warm","clear"]
VALID_INSTRUMENTS = ["guitar","piano","synth","bass","drums","strings","violin","cello","trumpet","saxophone","organ","harp","choir","pad","flute","horns","percussion","tagelharpa"]

DEFAULT_VOCAL_MAP = {
    "metal":{"female":["female","powerful","alto"],"male":["male","powerful","baritone"],"inst":["guitar","drums","strings","choir"]},
    "rock":{"female":["female","emotional","alto"],"male":["male","raspy","tenor"],"inst":["guitar","drums","bass","piano"]},
    "pop":{"female":["female","clear","soprano"],"male":["male","soft","tenor"],"inst":["piano","synth","bass","drums"]},
    "folk":{"female":["female","warm","alto"],"male":["male","emotional","baritone"],"inst":["guitar","strings","flute"]},
    "classical":{"female":["soprano","angelic"],"male":["tenor","baritone"],"inst":["strings","piano","choir"]},
    "electronic":{"female":["female","breathy"],"male":["male","soft"],"inst":["synth","pad","bass","drums"]},
    "ambient":{"female":["female","whispered"],"male":["male","soft"],"inst":["pad","piano","strings"]},
    "orchestral":{"female":["female","angelic"],"male":["male","deep"],"inst":["strings","choir","horns","percussion"]}
}

class VocalRegistry:
    def __init__(self): self.map=DEFAULT_VOCAL_MAP
    def auto_gender(self, text:str)->str:
        s=text.lower()
        if "[duet]" in s or "duet" in s: return "duet"
        if "choir" in s or "[choir]" in s: return "choir"
        # простая эвристика по местоимениям/лексике
        if re.search(r"\b(she|her|queen|goddess)\b",s): return "female"
        if re.search(r"\b(he|his|king|father)\b",s): return "male"
        # по эмоциям: мягкий/интимный -> female; агрессивный -> male
        if any(k in s for k in ["tender","soft","whisper","angelic"]): return "female"
        if any(k in s for k in ["rage","roar","growl","war"]): return "male"
        return "male"
    def get(self, genre:str, preferred:str, text:str)->Tuple[List[str],List[str]]:
        g = genre if genre in self.map else "rock"
        if preferred in ("female","male"): vox = self.map[g][preferred]
        elif preferred in ("duet","choir"): vox = [preferred]
        else:
            auto = self.auto_gender(text)
            vox = self.map[g]["female"] if auto=="female" else (["choir"] if auto=="choir" else (["duet"] if auto=="duet" else self.map[g]["male"]))
        inst=self.map[g]["inst"]
        vox=[v for v in vox if v in VALID_VOICES]
        inst=[i for i in inst if i in VALID_INSTRUMENTS]
        return vox,inst

def soft_trim(txt:str, max_len:int)->str:
    t=re.sub(r"\s+"," ",txt).strip()
    if len(t)<=max_len: return t
    for token in ["Philosophy:","Production:","Instruments:","Vocals:"]:
        if len(t)<=max_len: break
        if token in t:
            t=re.sub(rf"{token}[^|]*\|?","",t).strip(" |")
    if len(t)>max_len:
        t=t[:max_len].rsplit(" ",1)[0]
    return t

def build_prompt(genre:str, style_words:str, vocals:List[str], instruments:List[str], bpm:Optional[int], philosophy:str, version:str)->str:
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
    return soft_trim(" | ".join([p for p in parts if p]), max_len)

def make_skeleton(text:str)->str:
    lines=[l.strip() for l in text.split("\n") if l.strip()]
    if not lines: return ""
    blocks=[]
    chunk=[]
    for ln in lines:
        chunk.append(ln)
        if len(chunk)>=4:
            blocks.append(chunk); chunk=[]
    if chunk: blocks.append(chunk)
    out=[]
    for i,b in enumerate(blocks,1):
        tag="Chorus" if i==2 else ("Bridge" if i==3 else f"Verse {1 if i==1 else i}")
        out.append(f"[{tag}]")
        out.extend(b)
        out.append("")
    return "\n".join(out).strip()

@dataclass
class PipelineResult:
    genre:str; bpm:int; tonality:str; vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]; resonance:Dict[str,Any]
    sections:List[Dict[str,Any]]; mode:str; prompt:str; skeleton:str

class StudioCore:
    def __init__(self, config:Optional[dict]=None):
        self.cfg= config or load_config()
        self.tlp=TruthLovePain(); self.emo=Emo(); self.freq=Freq()
        self.meter=Meter(); self.style=Style(); self.vox=VocalRegistry()
        self.safe=Safety(self.cfg)

    def _decide_mode(self, em:Dict[str,float], tlp:Dict[str,float])->str:
        if tlp["pain"]>0.4 and tlp["truth"]>0.2: return "pain→light"
        if em.get("anger",0)>0.3: return "rage→truth"
        if em.get("peace",0)>0.35 and (em.get("love",0)>0.2 or tlp["conscious_frequency"]>0.4): return "healing"
        if tlp["truth"]>0.3 and em.get("fear",0)<0.1: return "ritual"
        if em.get("fear",0)<0.05 and tlp["pain"]<0.05: return "sacred_silence"
        return "neutral"

    def analyze(self, lyrics:str, prefer_gender:str="auto", author_style:Optional[str]=None)->PipelineResult:
        raw=normalize_text(lyrics)
        sections=extract_sections(raw)
        tlp=self.tlp.analyze(raw)
        emotions=self.emo.analyze(raw)
        bpm=self.meter.bpm(raw)
        genre=self.style.genre(emotions,tlp)
        ton=self.style.tonality(emotions)
        vox,inst=self.vox.get(genre, preferred=prefer_gender, text=raw)
        # hints из секций
        tag_text=" ".join([s["tag"] for s in sections])
        if re.search(r"tagelharpa",tag_text,re.I) and "tagelharpa" not in inst:
            inst=(inst+["tagelharpa"])[:5]
        res=self.freq.resonance(tlp); res["recommended_octaves"]=self.safe.clamp(res["recommended_octaves"])
        mode=self._decide_mode(emotions,tlp)
        philosophy="Truth × Love × Pain → Conscious Frequency. Healing-first, clarity over loudness."
        style_words=self.style.recommend(emotions,tlp,author_style,sections)
        prompt=build_prompt(genre,style_words,vox,inst,bpm,philosophy,self.cfg.get("suno_version","v5"))
        skeleton=make_skeleton(raw)
        return PipelineResult(genre,bpm,ton,vox,inst,tlp,emotions,res,sections,mode,prompt,skeleton)

    # удобный текстовый вывод
    def format_text_output(self, pr:PipelineResult)->str:
        lines=[]
        lines.append("# VOCAL DELIVERY (guide)")
        lines.append("(whisper → speak → sing → belt → release; breath marks: / )\n")
        lines.append(pr.skeleton)
        lines.append("\n# STYLE PROMPT")
        lines.append(pr.prompt + f" | Mode: {pr.mode} | Key: {pr.tonality}")
        return "\n".join(lines).strip()
