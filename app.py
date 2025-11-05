from __future__ import annotations
import re, json, math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

import gradio as gr

# ===============================
# -------- v4 ANALYTICS ---------
# ===============================

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
    }
}

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
        s=text.lower(); raw={k: sum(1 for t in v if t in s)/max(1,len(v)) for k,v in self.dicts.items()}
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
    def __init__(self, config:dict=DEFAULT_CONFIG): self.cfg=config["safety"]
    def clamp_octaves(self, rec:List[int])->List[int]:
        safe=set(self.cfg["safe_octaves"])
        filt=[o for o in rec if o in safe]
        return filt or [2,3,4]

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
    def recommend(self, emo:Dict[str,float], tlp:Dict[str,float])->str:
        if tlp["truth"]>0.7 and tlp["love"]>0.7: return "uplifting cinematic with warm harmonies"
        if tlp["pain"]>0.7 and tlp["truth"]>0.6: return "raw emotional rock with open space"
        if emo.get("epic",0)>0.4: return "anthemic arrangement with wide dynamics"
        return "balanced production with vocal clarity"

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
# -------- v5 COMPOSER ----------
# ===============================

SECTION_ALIASES = {
    "verse": ["verse","куплет","strofa","stropha","строфа"],
    "pre":   ["pre-chorus","pre chorus","pre","пред-припев","предприпев"],
    "chorus":["chorus","припев","hook","рефрен"],
    "bridge":["bridge","бридж","middle8","мидл"],
    "outro": ["outro","финал","кодa","кода"],
    "intro": ["intro","вступ","вступление"]
}

def _norm_sec_name(raw:str)->str:
    s=raw.lower()
    for k,vals in SECTION_ALIASES.items():
        if any(v in s for v in vals): return k
    return raw.strip()

DIRECTIVE_FALLBACK = {
    "intro":  "whisper, light pad, sparse percussion",
    "verse":  "calm, narrative, low register, close mic",
    "pre":    "build tension, chest voice, add toms",
    "chorus": "full energy, belting, wide stereo, strings + drums",
    "bridge": "drop energy, airy/whisper, long reverb tail",
    "outro":  "fade emotion, gentle sustain, soft adlibs"
}

def parse_author_headers(lyrics:str)->List[Dict[str,Any]]:
    """
    Парсит авторские теги формата:
    [Verse 1] [Tagelharpa + throat singing]
    <строки...>
    """
    lines = lyrics.splitlines()
    blocks=[]
    cur={"name":"verse","title":"Verse 1","directives":"","lines":[]}
    verse_idx=1
    for ln in lines:
        if re.match(r"^\s*\[.+?\]\s*$", ln.strip()):
            tags = re.findall(r"\[(.+?)\]", ln.strip())
            if tags:
                # если уже были строки — закрываем блок
                if cur["lines"]:
                    blocks.append(cur); verse_idx+=1
                # первый тег как название секции, второй — директивы
                title = tags[0].strip()
                name  = _norm_sec_name(title)
                directives = tags[1].strip() if len(tags)>1 else ""
                cur = {"name":name, "title":title, "directives":directives, "lines":[]}
        else:
            cur["lines"].append(ln)
    if cur["lines"]:
        blocks.append(cur)
    # если тегов не было вовсе — автосегментация блоками по 8 строк
    if not blocks:
        pure=[l for l in lines if l.strip()!=""]
        if not pure: return []
        chunks=[pure[i:i+8] for i in range(0,len(pure),8)]
        blocks=[]
        for i,ch in enumerate(chunks,1):
            sec="chorus" if i%2==0 else "verse"
            blocks.append({"name":sec,"title":f"{sec.title()} {i}","directives":"","lines":ch})
    return blocks

def english_annotation_for(name:str, custom:str)->str:
    base = DIRECTIVE_FALLBACK.get(name.lower(), "balanced delivery")
    if custom:
        return f"{custom} (author directives); {base}"
    return base

def build_annotated_lyrics(blocks:List[Dict[str,Any]])->str:
    out=[]
    for b in blocks:
        ann = english_annotation_for(b["name"], b.get("directives","").strip())
        header = f"[{b['title']} — {ann}]"
        out.append(header)
        out.extend(b["lines"])
        out.append("")  # пустая строка-разделитель
    return "\n".join(out).strip()

@dataclass
class PipelineResult:
    genre:str; bpm:int; tonality:str
    vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]
    resonance:Dict[str,Any]; prompt:str
    structure:List[Dict[str,Any]]; annotated_lyrics:str

def analyze_and_compose(lyrics:str, preferred_gender:str="auto")->PipelineResult:
    # v4 анализ
    tlp = TruthLovePainEngine().analyze(lyrics)
    emo = AutoEmotionalAnalyzer().analyze(lyrics)
    bpm = LyricMeter().bpm_from_density(lyrics)
    genre = StyleMatrix().genre(emo, tlp)
    tonality = StyleMatrix().tonality(emo)
    vox, inst = VocalProfileRegistry().get(genre, preferred_gender=preferred_gender)
    res = UniversalFrequencyEngine().resonance_profile(tlp)
    res["recommended_octaves"] = RNSSafety().clamp_octaves(res["recommended_octaves"])
    style_words = StyleMatrix().recommend(emo, tlp)
    philosophy = "Truth × Love × Pain → Conscious Frequency. Clarity over loudness."
    prompt = build_suno_prompt(genre, style_words, vox, inst, bpm, philosophy, "v5")
    # v5 структура
    blocks = parse_author_headers(lyrics)
    annotated = build_annotated_lyrics(blocks)
    return PipelineResult(
        genre=genre, bpm=bpm, tonality=tonality,
        vocals=vox, instruments=inst,
        tlp=tlp, emotions=emo, resonance=res, prompt=prompt,
        structure=blocks, annotated_lyrics=annotated
    )

# ===============================
# -------- Gradio UI ------------
# ===============================

CSS = """
#title {font-size: 20px; font-weight: 700; margin-bottom: 12px}
.small {font-size: 12px; opacity: .8}
"""

with gr.Blocks(css=CSS) as demo:
    gr.Markdown("<div id='title'>StudioCore v5 • Composer + Suno Prompt</div>")
    with gr.Row():
        lyrics = gr.Textbox(label="Lyrics (вставь текст с тегами [Verse], [Chorus] и доп. директивами во 2-х скобках)",
                            lines=16, placeholder="[Verse 1] [Tagelharpa + throat singing]\nстроки...\n[Chorus] [Blast beats + group chanting]\nстроки...")
        gender = gr.Radio(choices=["auto","male","female"], value="auto", label="Preferred vocal gender")
    run = gr.Button("Analyze & Compose", variant="primary")

    with gr.Row():
        prompt = gr.Textbox(label="Suno Style Prompt", lines=3, show_copy_button=True)
    with gr.Row():
        annotated = gr.Textbox(label="Annotated Lyrics (headers for Suno performance)", lines=16, show_copy_button=True)
    with gr.Accordion("Details", open=False):
        meta = gr.JSON(label="Structure & Analysis JSON")

    def _run(lyrics:str, gender:str):
        if not lyrics.strip():
            return ("", "", {"error":"empty lyrics"})
        r = analyze_and_compose(lyrics, gender)
        meta_out = {
            "genre": r.genre, "bpm": r.bpm, "tonality": r.tonality,
            "vocals": r.vocals, "instruments": r.instruments,
            "tlp": r.tlp, "emotions": r.emotions, "resonance": r.resonance,
            "structure": r.structure
        }
        return r.prompt, r.annotated_lyrics, meta_out

    run.click(_run, inputs=[lyrics, gender], outputs=[prompt, annotated, meta])

demo.queue(concurrency_count=1).launch()