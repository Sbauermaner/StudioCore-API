from __future__ import annotations

import os, re, json, math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# ===============================
# --------- CONFIG --------------
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
        "fade_out_ms": 1500,
    },
}

def load_config(path: str = "studio_config.json") -> dict:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ===============================
# ----- TEXT NORMALIZATION ------
# ===============================

PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))
LINE_BREAKS = {"\n"}

PUNCT_WEIGHTS = {
    ",": 0.10, ".": 0.30, "!": 0.50, "?": 0.40, "…": 0.60,
    "—": 0.20, "–": 0.20, ":": 0.25, ";": 0.20, "\"": 0.05, "'": 0.05,
    "(": 0.05, ")": 0.05, "[": 0.05, "]": 0.05
}
EMOJI_WEIGHTS = {ch: 0.40 for ch in EMOJI_SAFE}

SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def normalize_text_preserve_symbols(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

def extract_sections(text: str) -> List[Dict[str, Any]]:
    """[Verse], [Chorus], [Bridge] и кастомные теги."""
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
        s["lines"] = [l for l in s["lines"] if l.strip() != ""]
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
        raw = {k: sum(1 for t in v if t in s) / max(1, len(v)) for k, v in self.base_dicts.items()}

        punct_intensity = 0.0
        for ch in s:
            if ch in PUNCT_WEIGHTS:
                punct_intensity += PUNCT_WEIGHTS[ch]
            if ch in EMOJI_WEIGHTS:
                punct_intensity += EMOJI_WEIGHTS[ch]
        if punct_intensity > 0:
            raw["anger"] += 0.25 * punct_intensity
            raw["epic"]  += 0.45 * punct_intensity
            raw["joy"]   += 0.30 * punct_intensity

        total = sum(raw.values()) or 1.0
        return {k: max(0.0, v / total) for k, v in raw.items()}

    def entropy(self, em: Dict[str, float]) -> float:
        e = 0.0
        for p in em.values():
            if p > 0:
                e -= p * math.log(p)
        return e

# ===============================
# ----- FREQUENCY ENGINE --------
# ===============================

class UniversalFrequencyEngine:
    base = 24.5
    mapping = {
        0: ("16-32Hz",    "Subconscious",         "Deep meditation",      "#000080"),
        1: ("33-65Hz",    "Body awareness",       "Physical presence",    "#4169E1"),
        2: ("66-130Hz",   "Emotional base",       "Feeling foundation",   "#00BFFF"),
        3: ("131-261Hz",  "Heart center",         "Emotional expression", "#FF69B4"),
        4: ("262-523Hz",  "Voice of truth",       "Authentic communication", "#FFD700"),
        5: ("524-1046Hz", "Higher mind",          "Mental clarity",       "#90EE90"),
        6: ("1047-2093Hz","Intuitive wisdom",     "Inner knowing",        "#9370DB"),
        7: ("2094-4186Hz","Spiritual connection", "Universal awareness",  "#FF4500"),
        8: ("4187-7902Hz","Cosmic unity",         "Transcendence",        "#FFFFFF"),
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
# ---------- RNS SAFETY ---------
# ===============================

class RNSSafety:
    def __init__(self, config: dict): self.cfg = config["safety"]
    def check_band(self, freq: float) -> bool:
        lo, hi = self.cfg["avoid_freq_bands_hz"][0], self.cfg["avoid_freq_bands_hz"][1]
        return not (lo <= freq <= hi)
    def suggested_gain_db(self) -> Tuple[float, float]:
        return (self.cfg["max_peak_db"], self.cfg["max_rms_db"])
    def session_limit(self) -> int: return self.cfg["max_session_minutes"]
    def fade_edges_ms(self) -> Tuple[int, int]: return self.cfg["fade_in_ms"], self.cfg["fade_out_ms"]
    def clamp_octaves(self, rec: List[int]) -> List[int]:
        safe = set(self.cfg["safe_octaves"])
        filt = [o for o in rec if o in safe]
        return filt or [2, 3, 4]

# ===============================
# ------- INTEGRITY SCAN --------
# ===============================

class IntegrityScanEngine:
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"[^\s]+", text)
        sents = re.split(r"[.!?]+", text)
        form = {
            "word_count": len(words),
            "sentence_count": len([s for s in sents if s.strip()]),
            "avg_sentence_len": (len(words) / max(1, len(sents))),
        }
        emo = AutoEmotionalAnalyzer().analyze(text)
        tlp = TruthLovePainEngine().analyze(text)
        ref_words = set("i me my myself я мне меня сам себя думаю чувствую знаю понимаю".split())
        tokens = set(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()))
        reflection = len(tokens & ref_words) / max(1, len(tokens))
        return {"form": form, "essence": {"emotions": emo, "tlp": tlp}, "reflection": {"self_awareness": reflection}}

# ===============================
# --------- TONESYNC ------------
# ===============================

class ToneSyncEngine:
    def colors_for_primary(self, emo: Dict[str, float]) -> List[str]:
        m = max(emo, key=emo.get)
        cmap = {
            "joy": ["#FFD700", "#FF6B6B"], "sadness": ["#4169E1", "#87CEEB"],
            "anger": ["#DC143C", "#8B0000"], "love": ["#FF69B4", "#FF1493"],
            "peace": ["#98FB98", "#F0FFF0"], "epic": ["#FFFFFF", "#AAAAAA"],
        }
        return cmap.get(m, ["#808080", "#A9A9A9"])
    def sync(self, text: str, emo: Dict[str, float]) -> Dict[str, Any]:
        colors = self.colors_for_primary(emo)
        intensity = sum(emo.values()) / len(emo)
        balance = 1.0 - (sum(abs(v - intensity) for v in emo.values()) / len(emo))
        prof = {
            "brightness": emo.get("joy", 0) + emo.get("epic", 0) * 0.3,
            "warmth": emo.get("love", 0) + emo.get("peace", 0),
            "depth": emo.get("sadness", 0) + emo.get("fear", 0),
            "intensity": emo.get("anger", 0) + emo.get("epic", 0),
        }
        sync = 1.0 - abs(balance - 0.66)
        return {"visual": {"palette": colors, "balance": balance}, "audio": prof,
                "sync_score": max(0.0, min(sync, 1.0))}

# ===============================
# ------ LYRIC METER / BPM ------
# ===============================

class LyricMeter:
    vowels = set("aeiouyауоыиэяюёе")
    def syllables(self, line: str) -> int:
        w = line.lower()
        return max(1, sum(1 for ch in w if ch in self.vowels))
    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 100
        avg = sum(self.syllables(l) for l in lines) / len(lines)
        bpm = 140 - min(60, (avg - 8) * 6)
        punct_boost = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)
        bpm = bpm + min(20, punct_boost * 4.0)
        return max(60, min(160, int(bpm)))

# ===============================
# -------- STYLE MATRIX ---------
# ===============================

class StyleMatrix:
    def genre(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        if emo.get("anger", 0) > 0.35 and emo.get("epic", 0) > 0.25: return "metal"
        if emo.get("joy", 0) > 0.35 and emo.get("love", 0) > 0.25:   return "pop"
        if emo.get("peace", 0) > 0.35 and emo.get("love", 0) > 0.25: return "ambient"
        if emo.get("peace", 0) > 0.30 and tlp.get("truth", 0) > 0.20:return "folk"
        if emo.get("sadness", 0) > 0.35 and tlp.get("truth", 0) > 0.20:return "classical"
        if emo.get("epic", 0) > 0.40: return "orchestral"
        return "rock"

    def tonality(self, emo: Dict[str, float]) -> str:
        pos = emo.get("joy", 0) + emo.get("love", 0) + emo.get("peace", 0)
        neg = emo.get("sadness", 0) + emo.get("anger", 0) + emo.get("fear", 0)
        if pos > neg * 1.3: return "major"
        if neg > pos * 1.3: return "minor"
        return "modal"

    def recommend(self, emo: Dict[str, float], tlp: Dict[str, float],
                  author_style: Optional[str] = None, sections: Optional[List[Dict[str, Any]]] = None) -> str:
        base = None
        if author_style:
            base = author_style.strip()
        else:
            if tlp["truth"] > 0.7 and tlp["love"] > 0.7: base = "uplifting cinematic with warm harmonies"
            elif tlp["pain"] > 0.7 and tlp["truth"] > 0.6: base = "raw emotional rock with open space"
            elif emo.get("epic", 0) > 0.4: base = "anthemic arrangement with wide dynamics"
            elif emo.get("peace", 0) > 0.35: base = "healing, clarity, compassionate space"
            else: base = "modern hybrid rock with vocal clarity"
        tag_hints = []
        if sections:
            for s in sections:
                tag = s.get("tag", "")
                if any(k in tag.lower() for k in ["tagelharpa", "throat", "choir", "chant", "blast", "drum"]):
                    tag_hints.append(tag)
        if tag_hints:
            base = f"{base}; hints: " + ", ".join(sorted(set(tag_hints))[:4])
        return base

# ===============================
# ---- VOCAL / INSTRUMENT MAP ---
# ===============================

VALID_VOICES = [
    "male","female","duet","tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep","whispered","warm","clear",
    "choir"
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
    "orchestral": {"female":["female","angelic"],          "male":["male","deep"], "inst":["strings","choir","horns","percussion"]},
}

class VocalProfileRegistry:
    def __init__(self): self.map = DEFAULT_VOCAL_MAP
    def get(self, genre: str, preferred_gender: str = "auto") -> Tuple[List[str], List[str]]:
        g = genre if genre in self.map else "rock"
        if preferred_gender == "female": vox = self.map[g]["female"]
        elif preferred_gender == "male": vox = self.map[g]["male"]
        else: vox = self.map[g]["male"]
        inst = self.map[g]["inst"]
        vox = [v for v in vox if v in VALID_VOICES]
        inst = [i for i in inst if i in VALID_INSTRUMENTS]
        return vox, inst

# ===============================
# --------- VOCAL MATRIX --------
# ===============================

class VocalMatrixAI:
    """
    Автоматический выбор вокала:
      • тип: solo / duet / choir
      • пол: male / female (или смешанный)
      • регистры: chest/head/mix + falsetto/whistle (по необходимости)
      • фонация: breathy / clean / pressed / flow
      • техники: growl, scream, belt, fry, vibrato, legato/staccato, twang, distortion
    """
    TECH_KEYWORDS = {
        "growl": ["growl","рык","рыча","гроу"],
        "scream": ["scream","крик","крич"],
        "belt": ["belt","бельт","бэлтинг","мощн","powerful"],
        "fry": ["фрай","fry","raspy","хрип"],
        "falsetto": ["falsetto","фальцет"],
        "vibrato": ["vibrato","вибрато","дрож"],
        "twang": ["twang","твэнг","резк"],
        "distortion": ["distortion","дисторш"],
        "legato": ["legato","легато","плавн"],
        "staccato": ["staccato","стаккато","коротк"],
        "yodel": ["йодл","yodel"],
        "scat": ["scat","скэт"],
        "sprech": ["sprech","шпрех"],
    }

    def _has_any(self, text: str, keys: List[str]) -> bool:
        t = text.lower()
        return any(k in t for k in keys)

    def _duet_score(self, text: str) -> float:
        # признаки диалога/обращения и повторов
        lines = [l.strip().lower() for l in text.split("\n") if l.strip()]
        repeats = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i-1])
        call_resp = sum(1 for l in lines if l.startswith("you ") or l.startswith("ты ") or "your" in l or "твой" in l)
        we_together = len(re.findall(r"\b(we|together|вместе|мы)\b", " ".join(lines)))
        return repeats*0.4 + call_resp*0.6 + we_together*0.6

    def _choir_score(self, emotions: Dict[str, float]) -> float:
        return emotions.get("epic", 0) * 0.7 + emotions.get("love", 0) * 0.3

    def analyze(self, text: str, emotions: Dict[str, float], tlp: Dict[str, float]) -> Dict[str, Any]:
        t = text.lower()

        # Пол и манера (эвристики)
        male_bias   = emotions.get("anger", 0) + emotions.get("epic", 0) + (1 if "man" in t or "male" in t else 0)
        female_bias = emotions.get("love", 0) + emotions.get("peace", 0) + (1 if "woman" in t or "female" in t else 0)
        gender = "male" if male_bias > female_bias * 1.1 else ("female" if female_bias > male_bias * 1.1 else "auto")

        duet_s = self._duet_score(text)
        choir_s = self._choir_score(emotions)
        vtype = "choir" if choir_s > 0.55 else ("duet" if duet_s > 0.65 else "solo")

        # Регистр и фонация
        high_content = len(re.findall(r"\b(high|высок|sky|лети|fly)\b", t))
        soft_tokens  = len(re.findall(r"\b(soft|тихо|шёпот|whisper|breath)\b", t))
        press_tokens = len(re.findall(r"\b(крик|scream|напряж|press|сил|power)\b", t))

        register = "mix"
        if high_content >= 2:
            register = "head"
        elif emotions.get("anger", 0) + emotions.get("epic", 0) > 0.6:
            register = "chest"

        phonation = "flow"
        if soft_tokens > press_tokens * 1.2:
            phonation = "breathy"
        elif press_tokens > soft_tokens * 1.2:
            phonation = "pressed"

        # Техники из лексики + эмоций/пунктуации
        techniques: List[str] = []
        for name, keys in self.TECH_KEYWORDS.items():
            if self._has_any(t, keys):
                techniques.append(name)

        # эвристики по эмоциям
        if emotions.get("anger", 0) > 0.35 and "growl" not in techniques:
            techniques.append("distortion")
        if emotions.get("epic", 0) > 0.35 and "belt" not in techniques:
            techniques.append("belt")
        if emotions.get("love", 0) + emotions.get("peace", 0) > 0.45 and "legato" not in techniques:
            techniques.append("legato")
        if emotions.get("fear", 0) + emotions.get("sadness", 0) > 0.45 and "vibrato" not in techniques:
            techniques.append("vibrato")

        # Чистка/порядок
        order = ["belt","growl","scream","fry","falsetto","vibrato","twang","distortion","legato","staccato","yodel","scat","sprech"]
        techniques = [t for t in order if t in techniques][:6]

        # Итоговая рекомендованная связка голосов
        voices = []
        if vtype == "choir":
            voices = ["choir","male","female"]
        elif vtype == "duet":
            voices = ["duet","male","female"]
        else:
            # solo — выбираем по bias
            voices = ["male"] if gender in ["male","auto"] else ["female"]
        return {
            "type": vtype,
            "gender_auto": gender,
            "register": register,
            "phonation": phonation,
            "techniques": techniques,
            "voices_hint": voices
        }

# ===============================
# ------- SUNO ADAPTER ----------
# ===============================

def soft_trim(text: str, max_len: int) -> str:
    txt = re.sub(r"\s+", " ", text).strip()
    if len(txt) <= max_len:
        return txt
    for token in ["Philosophy:", "Production:", "Instruments:", "Vocals:"]:
        if len(txt) <= max_len: break
        if token in txt:
            txt = re.sub(rf"{token}[^|]*\|?", "", txt).strip(" |")
    if len(txt) > max_len:
        txt = txt[:max_len].rsplit(" ", 1)[0]
    return txt

def build_suno_prompt(genre: str, style_words: str, vocals: List[str], instruments: List[str],
                      bpm: Optional[int], philosophy: str, version: str,
                      vocal_matrix: Optional[Dict[str, Any]] = None) -> str:
    max_len = VERSION_LIMITS.get(version.lower(), 1000)
    vextra = ""
    if vocal_matrix:
        # короткая вставка о регистрах/технике в промт стайла (без перегруза)
        tech = ", ".join(vocal_matrix.get("techniques", [])[:3])
        reg  = vocal_matrix.get("register", "")
        pho  = vocal_matrix.get("phonation", "")
        hints = " / ".join([x for x in [reg, pho, tech] if x])
        if hints:
            vextra = f" | Vocal detail: {hints}"
    parts = [
        f"Genre: {genre}",
        f"Style: {style_words}",
        f"Vocals: {', '.join(vocals[:5])}",
        f"Instruments: {', '.join(instruments[:5])}",
        f"BPM: {bpm}" if bpm else "",
        f"Philosophy: {philosophy}",
        "Production: spatial depth, harmonic clarity, vocal intelligibility",
    ]
    prompt = " | ".join([p for p in parts if p]) + vextra
    return soft_trim(prompt, max_len)

# ===============================
# ------- PIPELINE CORE ---------
# ===============================

@dataclass
class PipelineResult:
    genre: str
    bpm: int
    tonality: str
    vocals: List[str]
    instruments: List[str]
    tlp: Dict[str, float]
    emotions: Dict[str, float]
    resonance: Dict[str, Any]
    integrity: Dict[str, Any]
    tonesync: Dict[str, Any]
    sections: List[Dict[str, Any]]
    prompt: str
    vocal_profile: Dict[str, Any]
    skeleton_text: str  # готовый «чистый текст» для пользователя

def _auto_split_to_skeleton(raw: str) -> List[Dict[str, Any]]:
    """
    Если пользователь дал «голый» текст без тегов — аккуратно собираем:
      Verse 1 -> Chorus -> Verse 2 -> Verse 3 -> Bridge? -> Final Chorus -> Outro
    Блоки определяются по длине строк + повторяемости мотивов.
    """
    lines = [l for l in raw.split("\n") if l.strip()]
    if not lines:
        return [{"tag":"Verse 1","lines":[]}]
    # простая эвристика: каждые 4 строки — строфа; похожие строфы -> chorus
    stanzas: List[List[str]] = []
    buf: List[str] = []
    for ln in lines:
        buf.append(ln)
        if len(buf) >= 4:
            stanzas.append(buf)
            buf = []
    if buf: stanzas.append(buf)
    # ищем самый «повторимый» stanza как припев
    def norm_block(b): return " ".join([re.sub(r"\W+"," ",x.lower()).strip() for x in b])
    scores = {}
    for i, st in enumerate(stanzas):
        key = norm_block(st)
        scores[key] = scores.get(key, 0) + 1
    chorus_key = None
    if scores:
        chorus_key = max(scores, key=scores.get) if max(scores.values())>1 else None
    sections: List[Dict[str, Any]] = []
    vcount, ccount = 0, 0
    for i, st in enumerate(stanzas, 1):
        key = norm_block(st)
        if chorus_key and key == chorus_key:
            ccount += 1
            sections.append({"tag": "Chorus", "lines": st})
        else:
            vcount += 1
            sections.append({"tag": f"Verse {vcount}", "lines": st})
    return sections

def _render_skeleton(secs: List[Dict[str, Any]], vmeta: Dict[str, Any]) -> str:
    """
    Чистый текст: заголовки секций + краткие подсказки по исполнению (но без JSON).
    """
    hint = []
    if vmeta.get("type") in ("duet","choir"):
        hint.append(vmeta["type"])
    if vmeta.get("register"):  hint.append(vmeta["register"])
    if vmeta.get("phonation"): hint.append(vmeta["phonation"])
    if vmeta.get("techniques"):
        hint.extend(vmeta["techniques"][:2])
    suffix = (" (" + " / ".join(hint) + ")") if hint else ""

    out_lines: List[str] = []
    for s in secs:
        tag = s.get("tag","Section")
        out_lines.append(f"[{tag}]{suffix}")
        for ln in s.get("lines",[]):
            out_lines.append(ln)
        out_lines.append("")  # пустая строка между секциями
    return "\n".join(out_lines).rstrip()

class StudioCore:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or load_config()
        self.tlp = TruthLovePainEngine()
        self.emo = AutoEmotionalAnalyzer()
        self.freq = UniversalFrequencyEngine()
        self.integrity = IntegrityScanEngine()
        self.tsync = ToneSyncEngine()
        self.meter = LyricMeter()
        self.style = StyleMatrix()
        self.vocals = VocalProfileRegistry()
        self.rns = RNSSafety(self.config)
        self.vocal_matrix = VocalMatrixAI()

    def analyze(self, lyrics: str, prefer_gender: str = "auto",
                author_style: Optional[str] = None) -> PipelineResult:
        raw = normalize_text_preserve_symbols(lyrics)

        # Если пользователь уже разметил секции — используем; иначе строим скелет
        sections = extract_sections(raw)
        if len(sections) == 1 and sections[0]["tag"] == "Body":
            sections = _auto_split_to_skeleton(raw)

        tlp = self.tlp.analyze(raw)
        emotions = self.emo.analyze(raw)
        bpm = max(60, min(160, self.meter.bpm_from_density(raw)))
        genre = self.style.genre(emotions, tlp)
        ton = self.style.tonality(emotions)

        # VocalMatrixAI
        vmeta = self.vocal_matrix.analyze(raw, emotions, tlp)

        # База голосов и инструментов по жанру
        vox, inst = self.vocals.get(genre, preferred_gender=prefer_gender if prefer_gender!="auto" else vmeta.get("gender_auto","auto"))
        # Тонкие правки по подсказкам VocalMatrixAI
        if vmeta.get("type") == "choir" and "choir" not in vox:
            vox = (["choir"] + vox)[:5]
            if "choir" not in inst: inst = (inst + ["choir"])[:5]
        if vmeta.get("type") == "duet" and "duet" not in vox:
            vox = (["duet"] + vox)[:5]
        if "fry" in vmeta.get("techniques", []) and "raspy" not in vox:
            vox = (["raspy"] + vox)[:5]
        if "belt" in vmeta.get("techniques", []) and "powerful" not in vox:
            vox = (["powerful"] + vox)[:5]

        # Расширение инструментов по тегам
        tag_text = " ".join([s["tag"] for s in sections])
        if re.search(r"tagelharpa", tag_text, flags=re.I) and "tagelharpa" not in inst:
            inst = (inst + ["tagelharpa"])[:5]

        res = self.freq.resonance_profile(tlp)
        res["recommended_octaves"] = self.rns.clamp_octaves(res["recommended_octaves"])
        integ = self.integrity.analyze(raw)
        ts = self.tsync.sync(raw, emotions)

        version = self.config.get("suno_version", "v5")
        philosophy = "Truth × Love × Pain → Conscious Frequency. Healing-first, clarity over loudness."
        sw = self.style.recommend(emotions, tlp, author_style=author_style, sections=sections)
        prompt = build_suno_prompt(genre, sw, vox, inst, bpm, philosophy, version, vocal_matrix=vmeta)

        # Чистый текстовый скелет с короткими вокальными подсказками
        skeleton_text = _render_skeleton(sections, vmeta)

        return PipelineResult(genre, bpm, ton, vox, inst, tlp, emotions, res, integ, ts, sections, prompt, vmeta, skeleton_text)