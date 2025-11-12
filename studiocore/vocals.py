# -*- coding: utf-8 -*-
"""
StudioCore v5 — Vocal Profile Registry (v2 - Расширенный инструментарий)
Определяет состав вокала (solo/duet/choir) и базовые инструменты.
"""

import re
from typing import Dict, Any, List, Tuple
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine # Используем "быстрый" движок

# =========================
# 1. Расширенный список инструментов
# =========================
VALID_VOICES = [
    "male","female","duet","trio","quartet","quintet","choir",
    "tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep",
    "whispered","warm","clear", "processed", "melodic rap", "layered harmonies",
    "ethereal"
]

VALID_INSTRUMENTS = [
    # Основа
    "guitar","piano","synth","bass","drums","percussion",
    # Струнные / Оркестр
    "strings","violin","cello","trumpet","horns", "french horn", "timpani",
    # Электроника (Новое)
    "synth lead", "808 bass", "riser", "FX", "trance pad", "house piano",
    "synth melody", "synth pad", "drum machine",
    # Акустика / Фолк
    "organ","harp","flute","acoustic guitar", "power chords", "tagelharpa",
    # Вокал как инструмент
    "choir","vocals","pad", "atmospheric pads"
]

# =========================
# 2. Расширенные карты инструментов (включая EDM)
# =========================
DEFAULT_VOCAL_MAP = {
    "rock": {
        "female": ["female", "emotional", "alto"],
        "male": ["male", "raspy", "tenor"],
        "inst": ["guitar", "drums", "bass", "piano", "power chords"]
    },
    "pop": {
        "female": ["female", "clear", "soprano"],
        "male": ["male", "soft", "tenor"],
        "inst": ["piano", "synth", "bass", "drums", "synth melody"]
    },
    "folk": {
        "female": ["female", "warm", "alto"],
        "male": ["male", "emotional", "baritone"],
        "inst": ["acoustic guitar", "strings", "flute", "percussion"]
    },
    "cinematic": {
        "female": ["female", "angelic", "soprano"],
        "male": ["male", "deep", "baritone"],
        "inst": ["strings", "piano", "choir", "drums", "french horn", "timpani"]
    },
    "electronic": {
        "female": ["female", "breathy", "ethereal"],
        "male": ["male", "soft", "processed"],
        "inst": ["synth", "synth pad", "bass", "drum machine", "FX"]
    },
    "ambient": {
        "female": ["female", "whispered", "ethereal"],
        "male": ["male", "soft", "breathy"],
        "inst": ["atmospheric pads", "piano", "strings", "synth pad"]
    },
    "orchestral": {
        "female": ["female", "angelic", "soprano"],
        "male": ["male", "deep", "bass"],
        "inst": ["strings", "choir", "horns", "percussion", "timpani", "cello"]
    },
    # НОВАЯ КАРТА
    "edm": {
        "female": ["female", "processed", "ethereal"],
        "male": ["male", "processed", "melodic rap"],
        "inst": ["synth lead", "808 bass", "drum machine", "riser", "FX", "trance pad"]
    }
}


class VocalProfileRegistry:
    """
    Определяет вокальную форму (solo, duet и т.д.) и набор инструментов
    на основе жанра, предпочтений и анализа текста.
    """
    def __init__(self, vocal_map: Dict[str, Any] | None = None):
        self.map = vocal_map or DEFAULT_VOCAL_MAP
        # Инициализируем анализаторы ОДИН РАЗ, чтобы не делать это при каждом вызове .get()
        self.emo_analyzer = AutoEmotionalAnalyzer()
        self.tlp_analyzer = TruthLovePainEngine()

    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str,Any]]) -> Dict[str,bool]:
        """ Ищет прямые указания на ансамбль (хор, дуэт и т.д.) """
        s = (text + " " + " ".join(s.get("tag","") for s in sections)).lower()
        return {
            "wants_choir": any(k in s for k in ["choir","хор","group","chorus","anthem"]),
            "wants_duet": any(k in s for k in ["duet","дуэт","duo","вместе", "вдвоем"]),
            "wants_trio": any(k in s for k in ["trio","трио"]),
            "wants_quartet": any(k in s for k in ["quartet","квартет"]),
            "wants_quintet": any(k in s for k in ["quintet","квинтет"]),
        }

    def _auto_form(self, emo: Dict[str,float], tlp: Dict[str,float], text: str) -> str:
        """ Автоматически определяет форму (solo/duet/...) на основе плотности и энергии """
        wc = len(text.split())
        cf = tlp.get("conscious_frequency", 0.5)
        energy = (tlp.get("love",0) + tlp.get("pain",0) + tlp.get("truth",0)) / 3

        if wc < 40 and energy < 0.3: return "solo"
        elif 40 <= wc < 80 or cf > 0.5: return "duet"
        elif 80 <= wc < 150 or (energy > 0.4 and cf > 0.6): return "trio"
        elif 150 <= wc < 250 or energy > 0.6: return "quartet"
        elif wc >= 250 or cf > 0.75 or emo.get("epic", 0) > 0.3: return "choir"
        return "solo"

    def _mixed_code(self, form: str, preferred_gender: str, text: str) -> str:
        """
        Создает код вокальной формы (solo_m, duet_mf, choir_mixed)
        на основе формы, предпочтений и намеков в тексте.
        """
        t = text.lower()
        # Ищем грамматику (добавлено в monolith, здесь ищем только прямые намеки)
        has_f = any(x in t for x in [" she ", "her ", "женщин", "девушк"])
        has_m = any(x in t for x in [" he ", "his ", "мужчин", "парень"])

        # 1. Принудительный выбор пользователя
        if preferred_gender in ("male", "female"):
            gender_code = "m" if preferred_gender == "male" else "f"
            if form == "solo": return f"solo_{gender_code}"
            if form == "duet": return f"duet_{gender_code}{gender_code}" # duet_mm или duet_ff
            # для хора/трио и т.д. оставляем mixed, если не указано иное
            if "choir" in form: return f"choir_{"male" if gender_code == 'm' else 'female'}"
            return f"{form}_{gender_code}" # trio_m

        # 2. Автоматический выбор (preferred_gender == "auto" или "mixed")
        if form == "solo":
            if has_f and not has_m: return "solo_f"
            if has_m and not has_f: return "solo_m"
            return "solo_auto" # По умолчанию (или если есть и M, и F в тексте)

        if form == "duet":
            if has_m and has_f: return "duet_mf"
            if has_f: return "duet_ff" # Только женские намеки
            if has_m: return "duet_mm" # Только мужские намеки
            return "duet_mf" # По умолчанию для дуэта

        if "choir" in form:
            if "женск" in t or "female choir" in t: return "choir_female"
            if "мужск" in t or "male choir" in t: return "choir_male"
            return "choir_mixed"

        # Для trio, quartet, quintet
        return f"{form}_mixed"

    def get(
        self,
        genre_full: str,
        preferred_gender: str,
        text: str,
        sections: List[Dict[str,Any]],
        vocal_profile_tags: Dict[str, str] # Новое: теги из monolith
    ) -> Tuple[List[str], List[str], str]:
        """
        Главный метод.
        vocal_profile_tags: {'male': 2, 'female': 1, 'mixed': 1} (пример)
        """
        # 1. Определяем базовый жанр для карты инструментов
        g = "edm" if "edm" in genre_full else \
            "cinematic" if "cinematic" in genre_full else \
            "orchestral" if "orchestral" in genre_full else \
            "rock" if "rock" in genre_full or "metal" in genre_full else \
            "pop" if "pop" in genre_full else \
            "folk" if "folk" in genre_full else \
            "ambient" if "ambient" in genre_full else \
            "lyrical" if "lyrical" in genre_full else "pop" # Запасной

        # Если карта для жанра не найдена (напр. 'lyrical'), используем 'pop'
        if g not in self.map:
            g = "pop"

        # 2. Определяем форму (solo/duet/choir)
        hints = self._detect_ensemble_hints(text, sections)
        form = "solo" # По умолчанию

        # Сначала проверяем теги из monolith (самый высокий приоритет)
        if vocal_profile_tags.get("mixed", 0) > 0:
            form = "duet"
        elif vocal_profile_tags.get("male", 0) > 0 and vocal_profile_tags.get("female", 0) > 0:
             form = "duet"
        
        # Затем проверяем прямые хинты (wants_choir и т.д.)
        for name in ["choir","quintet","quartet","trio","duet"]:
            if hints.get(f"wants_{name}"):
                form = name
                break # Важно: choir > duet

        # Если хинтов нет, используем авто-определение по TLP/длине
        if form == "solo" and not (vocal_profile_tags.get("male") or vocal_profile_tags.get("female")):
            emo = self.emo_analyzer.analyze(text)
            tlp = self.tlp_analyzer.analyze(text)
            form = self._auto_form(emo, tlp, text)

        # 3. Определяем состав (male/female/mixed)
        # Логика _mixed_code теперь учитывает теги из monolith
        
        # Определяем "предпочтительный" пол на основе грамматики
        auto_gender = "auto"
        if vocal_profile_tags.get("male", 0) > vocal_profile_tags.get("female", 0):
            auto_gender = "male"
        elif vocal_profile_tags.get("female", 0) > vocal_profile_tags.get("male", 0):
            auto_gender = "female"
        elif vocal_profile_tags.get("mixed", 0) > 0:
            auto_gender = "mixed"

        # preferred_gender от UI (auto/male/female) имеет приоритет над грамматикой
        final_gender_preference = preferred_gender if preferred_gender != "auto" else auto_gender
        if final_gender_preference == "mixed": final_gender_preference = "auto" # _mixed_code понимает 'auto'
        
        vocal_form = self._mixed_code(form, final_gender_preference, text)

        # 4. Собираем вокал и инструменты
        female_vox = self.map[g]["female"]
        male_vox = self.map[g]["male"]
        
        # Выбираем тембр
        if final_gender_preference == "female":
            vox = female_vox
        elif final_gender_preference == "male":
            vox = male_vox
        else: # auto или mixed
            # Если в форме есть и M, и F, смешиваем
            if "mf" in vocal_form:
                vox = male_vox + female_vox
            # Иначе берем по умолчанию (например, по эмоциям)
            else:
                emo = self.emo_analyzer.analyze(text)
                vox = (female_vox if (emo.get("joy",0)+emo.get("peace",0) >
                                      emo.get("anger",0)+emo.get("epic",0)) else male_vox)

        # 5. Очистка и возврат
        vox = [form] + vox
        vox = sorted(list(set(v for v in vox if v in VALID_VOICES or v.startswith(form))))[:6]
        inst = sorted(list(set(i for i in self.map[g]["inst"] if i in VALID_INSTRUMENTS)))[:6]
        
        return vox, inst, vocal_form