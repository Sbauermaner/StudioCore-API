import re
from typing import Dict, List

PUNCT_WEIGHTS = {",":0.10,".":0.30,"!":0.50,"?":0.40,"…":0.60,"—":0.20,"–":0.20,":":0.25,";":0.20,'"':0.05,"'":0.05,"(":0.05,")":0.05,"[":0.05,"]":0.05}
EMOJI_WEIGHTS = {ch: 0.40 for ch in "♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"}

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
        raw = {k: sum(1 for t in v if t in s) / max(1, len(v)) for k,v in self.base_dicts.items()}
        punct_intensity = sum(PUNCT_WEIGHTS.get(ch,0.0)+EMOJI_WEIGHTS.get(ch,0.0) for ch in s)
        if punct_intensity>0:
            raw["anger"]+=0.3*punct_intensity
            raw["epic"]+=0.4*punct_intensity
            raw["joy"]+=0.3*punct_intensity
        total = sum(raw.values()) or 1.0
        return {k:v/total for k,v in raw.items()}
