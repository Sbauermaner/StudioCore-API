import re
from typing import Dict, Any
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine

class IntegrityScanEngine:
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"[^\s]+", text)
        sents = re.split(r"[.!?]+", text)
        form = {
            "word_count": len(words),
            "sentence_count": len([s for s in sents if s.strip()]),
            "avg_sentence_len": len(words)/max(1, len(sents))
        }
        emo = AutoEmotionalAnalyzer().analyze(text)
        tlp = TruthLovePainEngine().analyze(text)
        ref_words = set("i me my myself я мне меня сам себя думаю чувствую знаю понимаю".split())
        tokens = set(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower()))
        reflection = len(tokens & ref_words)/max(1, len(tokens))
        return {"form": form,"essence": {"emotions": emo,"tlp": tlp},"reflection": {"self_awareness": reflection}}
