from __future__ import annotations
import re, json, math, os, hashlib, datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

# ===============================
# ------------ CONFIG -----------
# ===============================

STUDIOCORE_VERSION = "v4.3"
VERSION_LIMITS = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
DEFAULT_CONFIG = {
    "suno_version": "v5",
    "safety": {
        "max_peak_db": -1.0,      # рекомендация к продакшену
        "max_rms_db": -14.0,      # рекомендация к продакшену
        "avoid_freq_bands_hz": [18.0, 30.0],  # суб-НЧ зона
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
# ------ TEXT & SECTIONS --------
# ===============================

PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))
PUNCT_WEIGHTS = {",":0.10,".":0.30,"!":0.50,"?":0.40,"…":0.60,"—":0.20,"–":0.20,":":0.25,";":0.20,'"':0.05,"'":0.05,"(":0.05,")":0.05,"[":0.05,"]":0.05}
EMOJI_WEIGHTS = {ch: 0.40 for ch in EMOJI_SAFE}
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def normalize_text_preserve_symbols(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

def extract_sections(text: str) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    current = {"tag": "Body", "lines": []}
    for ln in text.split("\n"):
        m = SECTION_TAG_RE.match(ln)
        if m:
            if current["lines"]:
                sections.append(current)
            current = {"tag": m.group(1).strip(), "lines": []}
        else:
            current["lines"].append(ln)
    if current["lines"]:
        sections.append(current)
    for s in sections:
        s["lines"] = [l for l in s["lines"] if l.strip()]
    return sections

# ===============================
# ------ CORE PHILOSOPHY TLP ----
# ===============================

class TruthLovePainEngine:
    """Truth recognizes, Love connects, Pain transforms → Conscious Frequency."""
    _truth = ['truth','true','real','authentic','honest','истина','честно','реально','правда']
    _love  = ['love','care','heart','soul','compassion','unity','любовь','сердце','душа','забота','единство']
    _pain  = ['pain','hurt','loss','tears','cry','grief','страдание','боль','печаль','слёзы','горе']

    def analyze(self, text: str) -> Dict[str, float]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
        n = max(1, len(words))
        def score(bag): return sum(1 for w in words if w in bag) / n
        t, l, p = score(self._truth), score(self._love), score(self._pain)
        cf = (t * l * max(p, 0.05)) * 10.0
        return {
            "truth": min(t * 5, 1.0),
            "love": min(l * 5, 1.0),
            "pain": min(p * 5, 1.0),
            "conscious_frequency": min(cf, 1.0)
        }

# ===============================
# ------- EMOTION ANALYZER ------
# ===============================

class AutoEmotionalAnalyzer:
    base_dicts = {
        "joy": ['joy','happy','счаст','радость','улыб','smile','laugh'],
        "sadness": ['sad','грусть','печаль','слёзы','cry','tear'],
        "anger": ['anger','rage','ярость','злость','hate','furious'],
        "fear": ['страх','fear','паника','panic'],
        "peace": ['мир','спокой','тихо','calm','peace','still'],
        "epic": ['epic','геро','велич','монумент','anthem']
    }
    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        raw = {k: sum(1 for t in v if t in s) / max(1, len(v)) for k, v in self.base_dicts.items()}
        punct_intensity = 0.0
        for ch in s:
            if ch in PUNCT_WEIGHTS:  punct_intensity += PUNCT_WEIGHTS[ch]
            if ch in EMOJI_WEIGHTS:  punct_intensity += EMOJI_WEIGHTS[ch]
        if punct_intensity > 0:
            raw["anger"] += 0.30 * punct_intensity
            raw["epic"]  += 0.40 * punct_intensity
            raw["joy"]   += 0.30 * punct_intensity
        total = sum(raw.values()) or 1.0
        return {k: v / total for k, v in raw.items()}

# ===============================
# ------- LYRIC METER / BPM -----
# ===============================

class LyricMeter:
    vowels = set("aeiouyауоыиэяюёе")
    def syllables(self, line: str) -> int:
        w = line.lower()
        return max(1, sum(1 for ch in w if ch in self.vowels))
    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines: return 100
        avg = sum(self.syllables(l) for l in lines) / len(lines)
        bpm = 140 - min(60, (avg - 8) * 6)
        punct_boost = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)
        bpm = bpm + min(20, punct_boost * 4.0)
        return max(60, min(160, int(bpm)))

# ===============================
# ------- FREQUENCY ENGINE ------
# ===============================

class UniversalFrequencyEngine:
    base = 24.5
    mapping = {
        0: ("16-32Hz", "Subconscious", "Deep meditation", "#000080"),
        1: ("33-65Hz", "Body awareness", "Physical presence", "#4169E1"),
        2: ("66-130Hz","Emotional base","Feeling foundation","#00BFFF"),
        3: ("131-261Hz","Heart center","Emotional expression","#FF69B4"),
        4: ("262-523Hz","Voice of truth","Authentic communication","#FFD700"),
        5: ("524-1046Hz","Higher mind","Mental clarity","#90EE90"),
        6: ("1047-2093Hz","Intuitive wisdom","Inner knowing","#9370DB"),
        7: ("2094-4186Hz","Spiritual connection","Universal awareness","#FF4500"),
        8: ("4187-7902Hz","Cosmic unity","Transcendence","#FFFFFF")
    }
    def consciousness_info(self, f: float) -> Dict[str, Any]:
        for octv, (rng, cons, state, color) in self.mapping.items():
            mn, mx = map(float, rng.replace("Hz", "").split("-"))
            if mn <= f <= mx:
                return {"octave": octv, "range": rng, "consciousness": cons, "state": state, "color": color}
        return {"octave": -1, "range": "Unknown", "consciousness": "Unknown", "state": "Unknown", "color": "#000000"}
    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        base = self.base * (1.0 + tlp["truth"])
        spread = tlp["love"] * 2000.0
        mod = 1.0 + tlp["pain"] * 0.5
        info = self.consciousness_info(base)
        if tlp["conscious_frequency"] > 0.7: rec = [4, 5, 6, 7]
        elif tlp["conscious_frequency"] > 0.3: rec = [2, 3, 4, 5]
        else: rec = [1, 2, 3, 4]
        return {"base_frequency": base, "harmonic_range": spread, "modulation_depth": mod,
                "info": info, "recommended_octaves": rec}

# ===============================
# ----------- RNS SAFETY --------
# ===============================

class RNSSafety:
    """Резонансная безопасность: кламп октав, служебные метки для микса."""
    def __init__(self, config: dict): self.cfg = config["safety"]
    def clamp_octaves(self, rec: List[int]) -> List[int]:
        safe = set(self.cfg["safe_octaves"])
        filt = [o for o in rec if o in safe]
        return filt or [2, 3, 4]
    def mix_notes(self) -> Dict[str, Any]:
        return {
            "max_peak_db": self.cfg["max_peak_db"],
            "max_rms_db": self.cfg["max_rms_db"],
            "fade_in_ms": self.cfg["fade_in_ms"],
            "fade_out_ms": self.cfg["fade_out_ms"],
            "avoid_freq_bands_hz": self.cfg["avoid_freq_bands_hz"]
        }

# ===============================
# ---------- INTEGRITY SCAN -----
# ===============================

class IntegrityScanEngine:
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"[^\s]+", text)
        sents = re.split(r"[.!?]+", text)
        form = {
            "word_count": len(words),
            "sentence_count": len([s for s in sents if s.strip()]),
            "avg_sentence_len": (len(words) / max(1, len(sents)))
        }
        emo = AutoEmotionalAnalyzer().analyze(text)
        tlp = TruthLovePainEngine().analyze(text)
        ref_words = set("i me my myself я мне меня сам себя думаю чувствую знаю понимаю".split())
        tokens = set(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()))
        reflection = len(tokens & ref_words) / max(1, len(tokens))
        return {"form": form, "essence": {"emotions": emo, "tlp": tlp}, "reflection": {"self_awareness": reflection}}

# ===============================
# ------- VOCAL / INSTRUMENT ----
# ===============================

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
    def __init__(self): self.map = DEFAULT_VOCAL_MAP
    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str,Any]]) -> Dict[str, bool]:
        s = (text + " " + " ".join(s.get("tag","") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir","chant","хор","сканд","group"]),
            "wants_duet":  any(k in s for k in ["duet","дуэт","duo","вместе"]),
        }
    def get(self, genre: str, preferred_gender: str, text: str, sections: List[Dict[str,Any]]) -> Tuple[List[str], List[str]]:
        g = genre if genre in self.map else "rock"
        hints = self._detect_ensemble_hints(text, sections)
        if preferred_gender == "female": vox = self.map[g]["female"]
        elif preferred_gender == "male": vox = self.map[g]["male"]
        elif preferred_gender == "duet": vox = ["duet"] + self.map[g]["female"][:1] + self.map[g]["male"][:1]
        elif preferred_gender == "choir": vox = ["choir"] + ["male","female"]
        else:
            emo = AutoEmotionalAnalyzer().analyze(text)
            if (emo.get("love",0)+emo.get("peace",0)) > (emo.get("anger",0)+emo.get("epic",0)):
                vox = self.map[g]["female"]
            else:
                vox = self.map[g]["male"]
        if hints["wants_choir"] and "choir" not in vox: vox = ["choir"] + vox
        if hints["wants_duet"]  and "duet"  not in vox: vox = ["duet"]  + vox
        inst = list(self.map[g]["inst"])
        tag_text = " ".join([s["tag"] for s in sections]).lower()
        if "tagelharpa" in tag_text and "tagelharpa" not in inst: inst.append("tagelharpa")
        vox  = [v for v in vox if v in VALID_VOICES][:6]
        inst = [i for i in inst if i in VALID_INSTRUMENTS][:6]
        return vox, inst

# ===============================
# --------- STYLE MATRIX --------
# ===============================

class StyleMatrix:
    GENRE_KEYWORDS = {
        "hip hop": ["hip hop","boom bap","trap","808","bars","эмси","рэп"],
        "rap":     ["rap","рэп","читка","bars","flow"],
        "metal":   ["metal","грор","гроул","growl","blast","scream","скрим"],
        "rock":    ["rock","рок","гитара","риф"],
        "pop":     ["pop","поп","hook","radio","chorus"],
        "folk":    ["folk","фолк","акуст","балада","tagelharpa"],
        "classical":["classical","оркестр","симф","кантата","оратория"],
        "electronic":["edm","electronic","techno","house","trance","dubstep","808","synthwave"],
        "ambient": ["ambient","drone","pad","атмосф"],
        "jazz":    ["jazz","свинг","скэт","blue note","bebop"],
        "blues":   ["blues","блюз","shuffle","12 bar"],
        "orchestral":["orchestral","кино","cinematic","трейлер","score"],
        "reggae":  ["reggae","дагг","ска","offbeat"],
        "country": ["country","банжо","steel","honky tonk"],
        "punk":    ["punk","панк","diy","fast"],
        "indie":   ["indie","инди"]
    }
    def _keyword_genre_boost(self, text: str) -> Optional[str]:
        s = text.lower()
        for g, kws in self.GENRE_KEYWORDS.items():
            if any(kw in s for kw in kws): return g
        return None
    def genre(self, emo: Dict[str,float], tlp: Dict[str,float], text: str="", bpm: Optional[int]=None) -> str:
        g_kw = self._keyword_genre_boost(text)
        if g_kw: return g_kw
        anger, epic, joy, love, peace, sadness = [emo.get(k,0) for k in ["anger","epic","joy","love","peace","sadness"]]
        if anger>0.30 and epic>0.20: return "metal"
        if joy>0.30 and love>0.20:   return "pop"
        if peace>0.30 and love>0.20: return "ambient"
        if peace>0.30 and tlp.get("truth",0)>0.20: return "folk"
        if sadness>0.30 and tlp.get("truth",0)>0.20: return "classical"
        if bpm is not None:
            if bpm >= 135 and anger+epic > 0.4: return "punk"
            if bpm <= 80 and sadness > 0.25:   return "blues"
        return "rock"
    def tonality(self, emo: Dict[str,float]) -> str:
        pos = emo.get("joy",0)+emo.get("love",0)+emo.get("peace",0)
        neg = emo.get("sadness",0)+emo.get("anger",0)+emo.get("fear",0)
        if pos > neg*1.3: return "major"
        if neg > pos*1.3: return "minor"
        return "modal"
    def techniques(self, emo: Dict[str,float], text: str) -> List[str]:
        s = text.lower()
        t: List[str] = []
        explicit = {
            "growl":["growl","гроул"], "scream":["scream","скрим","крик"],
            "belt":["belt","бэлт"], "falsetto":["falsetto","фальцет"], "vibrato":["vibrato","вибрато"],
            "fry":["fry","штробас","вокальный фрай"], "twang":["twang","твэнг"],
            "legato":["legato","легато"], "staccato":["staccato","стаккато"],
            "runs":["runs","риффы","пассажи"], "yodel":["yodel","йодль"],
            "distortion":["distortion","дисторшн"], "scat":["scat","скэт"],
            "sprechstimme":["sprech","шпрехштимме"]
        }
        for k, kws in explicit.items():
            if any(kw in s for kw in kws): t.append(k)
        if emo.get("anger",0) > 0.30: t += ["distortion","fry","twang"]
        if emo.get("epic",0)  > 0.30: t += ["belt","vibrato"]
        if emo.get("sadness",0)> 0.30: t += ["legato","falsetto"]
        if emo.get("joy",0)   > 0.30: t += ["runs","vibrato"]
        if emo.get("peace",0) > 0.30: t += ["legato"]
        seen, out = set(), []
        for x in t:
            if x not in seen:
                seen.add(x); out.append(x)
        return out[:6]
    def recommend(self, emo: Dict[str,float], tlp: Dict[str,float],
                  author_style: Optional[str]=None, sections: Optional[List[Dict[str, Any]]]=None) -> str:
        base = None
        if author_style:
            base = author_style.strip()
        else:
            if tlp["truth"]>0.7 and tlp["love"]>0.7:
                base = "uplifting cinematic with warm harmonies"
            elif tlp["pain"]>0.7 and tlp["truth"]>0.6:
                base = "raw emotional rock with open space"
            elif emo.get("epic",0)>0.4:
                base = "anthemic arrangement with wide dynamics"
            else:
                base = "healing, clarity, compassionate space"
        tag_hints = []
        if sections:
            for s in sections:
                tag = s.get("tag","")
                if any(k in tag.lower() for k in ["tagelharpa","throat","choir","chant","blast","drum"]):
                    tag_hints.append(tag)
        if tag_hints:
            base = f"{base}; hints: " + ", ".join(sorted(set(tag_hints))[:4])
        return base

# ===============================
# --------- TONESYNC ENGINE -----
# ===============================

class ToneSyncEngine:
    def colors_for_primary(self, emo: Dict[str,float]) -> List[str]:
        primary = max(emo, key=emo.get) if emo else "peace"
        cmap = {
            "joy": ["#FFD700","#FF6B6B"],
            "sadness": ["#4169E1","#87CEEB"],
            "anger": ["#DC143C","#8B0000"],
            "love": ["#FF69B4","#FF1493"],
            "peace": ["#98FB98","#F0FFF0"],
            "epic": ["#FFA500","#FF4500"],
            "fear": ["#6A5ACD","#2F4F4F"]
        }
        return cmap.get(primary, ["#808080","#A9A9A9"])
    def audio_profile(self, emo: Dict[str,float]) -> Dict[str,float]:
        return {
            "brightness": emo.get("joy",0)+emo.get("truth",0),
            "warmth": emo.get("love",0)+emo.get("peace",0),
            "depth": emo.get("sadness",0)+emo.get("fear",0),
            "intensity": emo.get("anger",0)+emo.get("epic",0)
        }
    def visual_profile(self, emo: Dict[str,float]) -> Dict[str,Any]:
        return {
            "palette": self.colors_for_primary(emo),
            "movement": "sharp" if emo.get("anger",0)>0.3 else ("flow" if emo.get("joy",0)>0.3 else "calm"),
            "balance": 1.0 - (sum(abs(v - (sum(emo.values())/max(1,len(emo)))) for v in emo.values())/max(1,len(emo)))
        }
    def sync_score(self, audio: Dict[str,float], visual: Dict[str,Any]) -> float:
        # Простая косинусная близость по brightness/warmth/depth/intensity vs flow/sharp
        a = [audio["brightness"], audio["warmth"], audio["depth"], audio["intensity"]]
        # сопоставляем movement к intensity/brightness
        mv = visual["movement"]
        b = [1.0 if mv=="flow" else 0.6, 1.0 if mv=="flow" else 0.6, 0.8 if mv=="calm" else 0.6, 1.0 if mv=="sharp" else 0.6]
        dot = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a)) or 1.0
        nb = math.sqrt(sum(x*x for x in b)) or 1.0
        return max(0.0, min(1.0, dot/(na*nb)))

# ===============================
# ---------- SUNO ADAPTER -------
# ===============================

def soft_trim(text: str, max_len: int) -> str:
    txt = re.sub(r"\s+", " ", text).strip()
    if len(txt) <= max_len: return txt
    for token in ["Techniques:","Philosophy:","Production:","Instruments:","Vocals:","Genre:","Style:","BPM:"]:
        if len(txt)<=max_len: break
        if token in txt:
            txt = re.sub(rf"{token}[^|]*\|?", "", txt).strip(" |")
    if len(txt) > max_len:
        txt = txt[:max_len].rsplit(" ", 1)[0]
    return txt

def build_suno_prompt(
    genre: str, style_words: str, vocals: List[str], instruments: List[str],
    bpm: Optional[int], philosophy: str, techniques: List[str], version: str
) -> str:
    max_len = VERSION_LIMITS.get(version.lower(), 1000)
    parts = [
        f"Genre: {genre}",
        f"Style: {style_words}",
        f"Vocals: {', '.join(vocals[:6])}",
        f"Instruments: {', '.join(instruments[:6])}",
        f"Techniques: {', '.join(techniques[:6])}" if techniques else "",
        f"BPM: {bpm}" if bpm else "",
        f"Philosophy: {philosophy}",
        "Production: spatial depth, harmonic clarity, vocal intelligibility"
    ]
    prompt = " | ".join([p for p in parts if p])
    return soft_trim(prompt, max_len)

# ===============================
# --------- PROFILES I/O --------
# ===============================

def export_profile(path: str, payload: Dict[str, Any]) -> str:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path

def import_profile(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===============================
# ---------- PIPELINE CORE ------
# ===============================

@dataclass
class PipelineResult:
    genre: str
    bpm: int
    tonality: str
    vocals: List[str]
    instruments: List[str]
    techniques: List[str]
    tlp: Dict[str, float]
    emotions: Dict[str, float]
    resonance: Dict[str, Any]
    integrity: Dict[str, Any]
    tonesync: Dict[str, Any]
    sections: List[Dict[str, Any]]
    prompt: str
    safety_notes: Dict[str, Any]

def analyze_and_style(
    raw_text: str,
    *,
    suno_version: str = "v5",
    preferred_vocal: Optional[str] = None,
    author_style_hint: Optional[str] = None
) -> PipelineResult:
    cfg = load_config()
    suno_version = suno_version or cfg.get("suno_version","v5")

    text = normalize_text_preserve_symbols(raw_text)
    sections = extract_sections(text)

    tlp = TruthLovePainEngine().analyze(text)
    emo = AutoEmotionalAnalyzer().analyze(text)
    bpm = LyricMeter().bpm_from_density(text)

    style = StyleMatrix()
    genre = style.genre(emo, tlp, text=text, bpm=bpm)
    tonality = style.tonality(emo)
    techniques = style.techniques(emo, text)
    style_words = style.recommend(emo, tlp, author_style_hint, sections)

    voxreg = VocalProfileRegistry()
    vocals, instruments = voxreg.get(genre, preferred_vocal or "auto", text, sections)

    freq = UniversalFrequencyEngine()
    resonance = freq.resonance_profile(tlp)

    safety = RNSSafety(cfg)
    resonance["recommended_octaves"] = safety.clamp_octaves(resonance["recommended_octaves"])
    safety_notes = safety.mix_notes()

    integ = IntegrityScanEngine().analyze(text)
    tone = ToneSyncEngine()
    audio_p = tone.audio_profile(emo)
    visual_p = tone.visual_profile(emo)
    sync_score = tone.sync_score(audio_p, visual_p)
    tonesync = {"audio": audio_p, "visual": visual_p, "sync_score": sync_score}

    philosophy = f"Truth{tlp['truth']:.2f}-Love{tlp['love']:.2f}-Pain{tlp['pain']:.2f}"
    prompt = build_suno_prompt(genre, style_words, vocals, instruments, bpm, philosophy, techniques, suno_version)

    return PipelineResult(
        genre=genre, bpm=bpm, tonality=tonality, vocals=vocals, instruments=instruments,
        techniques=techniques, tlp=tlp, emotions=emo, resonance=resonance,
        integrity=integ, tonesync=tonesync, sections=sections, prompt=prompt,
        safety_notes=safety_notes
    )

# ===============================
# -------------- DEMO -----------
# ===============================

if __name__ == "__main__":
    demo_text = """[Verse]
We don't need much to be happy,
A little spark, a little glow.
[Chorus]
Hands together, hearts are steady,
Let the gentle rivers flow."""
    out = analyze_and_style(demo_text, preferred_vocal="female")
    print("StudioCore v4.3 | Suno Prompt:\n", out.prompt)
    print("\n— Genre:", out.genre, "| BPM:", out.bpm, "| Tonality:", out.tonality)
    print("— Vocals:", out.vocals)
    print("— Instruments:", out.instruments)
    print("— Techniques:", out.techniques)
    print("— Safety:", out.safety_notes)
