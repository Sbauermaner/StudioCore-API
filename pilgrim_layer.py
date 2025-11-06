from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple
from StudioCore_Complete_v4 import StudioCore  # ядро как есть

# Допустимые служебные теги, которые мы сохраняем и учитываем
ALLOWED_SECTION_TAGS = [
    "Intro","Verse","Pre-Chorus","Chorus","Bridge","Outro","Tag","Break","Hook"
]

class AutoPunctuation:
    # мягкая автопунктуация: только точки, запятые, дефис/тире, восклиц/вопрос
    def restore(self, text: str) -> str:
        t = text.replace("\r", "\n").strip()
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        fixed: List[str] = []
        for ln in lines:
            # дефисы: — или -
            ln = re.sub(r"\s*[-–—]\s*", " — ", ln)
            # если нет завершающего знака, добавим точку
            if not re.search(r"[.!?…]$", ln):
                ln += "."
            fixed.append(ln)
        # аккуратное объединение с пробелом
        return " ".join(fixed)

class StressMarker:
    vowels = "аеёиоуыэюяAEIOUYaeiouy"
    def mark_first_vowel(self, word: str) -> str:
        # помечаем первую гласную как ударную [A]
        for i, ch in enumerate(word):
            if ch in self.vowels:
                return word[:i] + "[" + ch.upper() + "]" + word[i+1:]
        return word
    def add_stress(self, text: str) -> str:
        tokens = re.split(r"(\s+)", text)
        out = []
        for tk in tokens:
            if tk.strip() and tk.strip().isalpha():
                out.append(self.mark_first_vowel(tk))
            else:
                out.append(tk)
        return "".join(out)

class SectionParser:
    """
    Умеет:
      - принимать авторские указания в строках вида:
        [Verse 1] [Tagelharpa + throat singing]
      - если явных тегов нет, бьет по 4 строки: Verse 1, Verse 2, …; каждый 3–5 блок — Chorus.
    """
    sec_pat = re.compile(r"^\s*\[(?P<label>[^\]]+)\]\s*(\[(?P<instr>[^\]]+)\])?\s*$")

    def parse(self, raw_text: str) -> Dict[str, str]:
        lines = [l for l in raw_text.splitlines()]
        out: Dict[str, List[str]] = {}
        cur = "Verse 1"
        idx = 1
        out[cur] = []
        for ln in lines:
            m = self.sec_pat.match(ln.strip())
            if m:
                label = m.group("label").strip()
                instr = m.group("instr")
                # нормализуем стандартные лейблы
                norm = self._normalize_label(label)
                cur = norm
                if instr:
                    cur += f" [{instr.strip()}]"
                if cur not in out:
                    out[cur] = []
                continue
            # обычная лирика
            if ln.strip():
                out[cur].append(ln.rstrip())
        # если авторских тегов не было, попробуем разложить автоматически
        if len(out) == 1 and "Verse 1" in out and len(out["Verse 1"]) > 4:
            auto = {}
            all_lines = out["Verse 1"]
            out.clear()
            for i in range(0, len(all_lines), 4):
                block = all_lines[i:i+4]
                tag = "Chorus" if (i // 4) % 3 == 1 else f"Verse {i//4 + 1}"
                auto.setdefault(tag, []).extend(block)
            out = auto
        # склейка
        return {k: "\n".join(v) for k, v in out.items()}

    def _normalize_label(self, label: str) -> str:
        l = label.lower()
        # поддержим варианты на русском и английском
        mapping = {
            "intro":"Intro","вступление":"Intro",
            "verse":"Verse","куплет":"Verse",
            "pre-chorus":"Pre-Chorus","prechorus":"Pre-Chorus","предприпев":"Pre-Chorus",
            "chorus":"Chorus","припев":"Chorus",
            "bridge":"Bridge","бридж":"Bridge",
            "outro":"Outro","финал":"Outro",
            "hook":"Hook","тэг":"Tag","tag":"Tag","break":"Break"
        }
        # если есть порядковый номер, сохраним его
        m = re.match(r"(verse|куплет)\s+(\d+)", l)
        if m:
            return f"Verse {m.group(2)}"
        return mapping.get(l, label)

class PilgrimInterface:
    """
    Слой: сырой текст → автопунктуация → расстановка ударений →
    разбор секций (включая авторские теги) → вызов ядра StudioCore →
    готовый style prompt и структура.
    """
    def __init__(self):
        self.core = StudioCore()
        self.punct = AutoPunctuation()
        self.stress = StressMarker()
        self.parser = SectionParser()

    def process_raw(self, raw_text: str, prefer_gender: str = "auto") -> Dict[str, Any]:
        raw = raw_text.strip()
        # не требуем JSON. Всё, что пришло, считаем лирикой.
        # 1) разметка секций (сохраняем авторские теги, инструменты)
        sections = self.parser.parse(raw)
        # 2) «поэтическая» автопунктуация
        clean_text = self.punct.restore(raw)
        # 3) ударения (упрощено и безопасно)
        stressed_text = self.stress.add_stress(clean_text)
        # 4) анализ ядром (ядро сохраняем как есть)
        res = self.core.analyze(stressed_text, prefer_gender=prefer_gender)
        # 5) сбор результата
        return {
            "genre": res.genre,
            "bpm": res.bpm,
            "tonality": res.tonality,
            "tlp": res.tlp,
            "emotions": res.emotions,
            "resonance": res.resonance,
            "integrity": res.integrity,
            "tonesync": res.tonesync,
            "sections": sections,              # скелет «как петь»
            "clean_text": clean_text,          # автопунктуация
            "stressed_text": stressed_text,    # ударения
            "style_prompt": res.prompt         # готовый prompt для Suno
        }
