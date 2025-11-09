import re
from typing import Dict, List

PUNCT_WEIGHTS = {",":0.10,".":0.30,"!":0.50,"?":0.40,"…":0.60,"—":0.20,"–":0.20,":":0.25,";":0.20,'"':0.05,"'":0.05,"(":0.05,")":0.05,"[":0.05,"]":0.05}
EMOJI_WEIGHTS = {ch: 0.40 for ch in "♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"}

class TruthLovePainEngine:
    """
    Semantic emotional analyzer (Truth × Love × Pain)
    Works not by keyword hits, but by emotional context in full sentences.
    """

    _truth_kw = ['truth','real','authentic','honest','искрен','правд','честн','реальн','истин']
    _love_kw  = ['love','care','heart','soul','compassion','единств','люб','сердц','душ','свет']
    _pain_kw  = ['pain','hurt','loss','tears','cry','grief','страд','боль','печал','слез','горе']

    def analyze(self, text: str) -> Dict[str, float]:
        s = text.lower()
        sentences = re.split(r"[.!?;]+", s)
        n = max(1, len(sentences))

        truth_score, love_score, pain_score = 0.0, 0.0, 0.0

        for sent in sentences:
            neg = 1.0
            if any(w in sent for w in ['не ', 'no ', "n't", 'без ']):
                neg = 0.7  # ослабляем смысл, если есть отрицание

            t = sum(1 for w in self._truth_kw if w in sent)
            l = sum(1 for w in self._love_kw if w in sent)
            p = sum(1 for w in self._pain_kw if w in sent)

            length_factor = min(len(sent.split()) / 10, 1.5)
            sentence_weight = (t + l + p) * neg * length_factor

            truth_score += t * neg * length_factor
            love_score  += l * neg * length_factor
            pain_score  += p * neg * length_factor

        # нормализация
        total = max(1.0, truth_score + love_score + pain_score)
        t_norm = truth_score / total
        l_norm = love_score / total
        p_norm = pain_score / total

        conscious_freq = (t_norm * l_norm * max(p_norm, 0.05)) * 10.0

        return {
            "truth": round(min(t_norm * 5, 1.0), 2),
            "love": round(min(l_norm * 5, 1.0), 2),
            "pain": round(min(p_norm * 5, 1.0), 2),
            "conscious_frequency": round(min(conscious_freq, 1.0), 2)
        }


class AutoEmotionalAnalyzer:
    """
    Detects dominant emotional tone (joy, sadness, anger, fear, peace, epic)
    based on keywords, punctuation, and intensity.
    """
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
