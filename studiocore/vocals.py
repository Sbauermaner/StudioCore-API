# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
StudioCore v5 — Vocal Profile Registry (v9 - AttributeError ИСПРАВЛЕН)
v9: Исправлена ошибка 'list' object has no attribute 'get'
"""

import re
from typing import Dict, Any, List, Tuple
# v15: Исправлен ImportError (имена классов теперь правильные)
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine 
import logging

log = logging.getLogger(__name__)

# =========================
# 1. Расширенный список инструментов
# =========================
VALID_VOICES = [
    "male","female","duet","trio","quartet","quintet","choir",
    "tenor","soprano","alto","baritone","bass",
    "raspy","breathy","powerful","soft","emotional","angelic","deep",
    "whispered","warm","clear", "processed", "melodic rap", "layered harmonies",
    "ethereal", "solo"
]

VALID_INSTRUMENTS = [
    "guitar","piano","synth","bass","drums","percussion",
    "strings","violin","cello","trumpet","horns", "french horn", "timpani", "orchestral strings",
    "synth lead", "808 bass", "riser", "FX", "trance pad", "house piano",
    "synth melody", "synth pad", "drum machine", "atmospheric pads", "synth bass",
    "organ","harp","flute","acoustic guitar", "power chords", "tagelharpa",
    "choir","vocals","pad", 
]

# =========================
# 2. Расширенные карты инструментов (v8: +lyrical, +edm)
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
        "inst": ["strings", "piano", "choir", "drums", "french horn", "timpani", "orchestral strings", "atmospheric pads"]
    },
    "electronic": {
        "female": ["female", "breathy", "ethereal"],
        "male": ["male", "soft", "processed"],
        "inst": ["synth", "synth pad", "bass", "drum machine", "FX"]
    },
    "edm": {
        "female": ["female", "processed", "ethereal"],
        "male": ["male", "processed", "melodic rap"],
        "inst": ["synth lead", "808 bass", "drum machine", "riser", "FX", "trance pad", "synth bass"]
    },
    # v8: ИСПРАВЛЕНО WARNING
    "lyrical": {
        "female": ["female", "emotional", "soprano"],
        "male": ["male", "warm", "baritone"],
        "inst": ["piano", "strings", "acoustic guitar", "cello"]
    },
    "default": {
        "female": ["female", "emotional"],
        "male": ["male", "emotional"],
        "inst": ["piano", "guitar", "bass", "drums"]
    }
}


class VocalProfileRegistry:
    """
    (v9) Определяет вокальную форму (solo, duet и т.д.) и набор инструментов
    на основе жанра, предпочтений и анализа текста.
    """
    def __init__(self, vocal_map: Dict[str, Any] | None = None):
        self.map = vocal_map or DEFAULT_VOCAL_MAP
        try:
            # v15: Исправлен ImportError
            self.emo_analyzer = AutoEmotionalAnalyzer()
            self.tlp_analyzer = TruthLovePainEngine()
            log.debug("VocalProfileRegistry успешно инициализировал Emo/TLP движки.")
        except Exception as e:
            log.error(f"VocalProfileRegistry НЕ СМОГ инициализировать Emo/TLP: {e}")
            self.emo_analyzer = None
            self.tlp_analyzer = None


    def _detect_ensemble_hints(self, text: str, sections: List[Dict[str,Any]]) -> Dict[str,bool]:
        """ Ищет прямые указания на ансамбль (хор, дуэт и т.д.) """
        log.debug("Вызов функции: _detect_ensemble_hints")
        s = (text + " " + " ".join(s.get("tag","") for s in sections)).lower()
        hints = {
            "wants_choir": any(k in s for k in ["choir","хор","group","chorus","anthem"]),
            "wants_duet": any(k in s for k in ["duet","дуэт","duo","вместе", "вдвоем"]),
            "wants_trio": any(k in s for k in ["trio","трио"]),
            "wants_quartet": any(k in s for k in ["quartet","квартет"]),
            "wants_quintet": any(k in s for k in ["quintet","квинтет"]),
        }
        log.debug(f"Результат _detect_ensemble_hints: {hints}")
        return hints

    def _auto_form(self, emo: Dict[str,float], tlp: Dict[str,float], text: str) -> str:
        """ Автоматически определяет форму (solo/duet/...) на основе плотности и энергии """
        log.debug("Вызов функции: _auto_form")
        if not emo or not tlp:
            log.warning("_auto_form не получил emo/tlp, возврат 'solo'")
            return "solo"
            
        wc = len(text.split())
        cf = tlp.get("conscious_frequency", 0.5)
        energy = (tlp.get("love",0) + tlp.get("pain",0) + tlp.get("truth",0)) / 3

        if wc < 40 and energy < 0.3: form = "solo"
        elif 40 <= wc < 80 or cf > 0.5: form = "duet"
        elif 80 <= wc < 150 or (energy > 0.4 and cf > 0.6): form = "trio"
        elif 150 <= wc < 250 or energy > 0.6: form = "quartet"
        elif wc >= 250 or cf > 0.75 or emo.get("epic", 0) > 0.3: form = "choir"
        else: form = "solo"
        
        log.debug(f"Результат _auto_form: {form} (WC={wc}, CF={cf:.2f}, E={energy:.2f})")
        return form

    def _mixed_code(self, form: str, preferred_gender: str, text: str) -> str:
        """
        v8: Исправлена логика 'duet_ff'.
        """
        log.debug(f"Вызов функции: _mixed_code (Form={form}, PrefGender={preferred_gender})")
        t = text.lower()
        has_f = any(x in t for x in [" she ", "her ", "женщин", "девушк"])
        has_m = any(x in t for x in [" he ", "his ", "мужчин", "парень"])

        # 1. Принудительный выбор пользователя
        if preferred_gender in ("male", "female"):
            gender_code = "m" if preferred_gender == "male" else "f"
            if form == "solo": return f"solo_{gender_code}"
            
            # v8: Если пользователь выбрал M или F, но форма - ДУЭТ (из хинта или грамматики),
            # мы ПРЕДПОЛАГАЕМ, что это M/F дуэт, чтобы он звучал интереснее.
            # (Раньше здесь было duet_mm или duet_ff, что было ошибкой)
            if form == "duet": 
                log.debug("Логика _mixed_code: UI-хинт (M/F) + форма (Duet) = duet_mf")
                return "duet_mf" 
            
            if "choir" in form: 
                # v5: Исправлена ошибка f-string
                return f"choir_{'male' if gender_code == 'm' else 'female'}"
            
            return f"{form}_{gender_code}"

        # 2. Автоматический выбор (preferred_gender == "auto" или "mixed")
        if form == "solo":
            if has_f and not has_m: return "solo_f"
            if has_m and not has_f: return "solo_m"
            return "solo_auto" 

        if form == "duet":
            if has_m and has_f: return "duet_mf"
            if has_f: return "duet_ff" # (Только если есть "она", но нет "он")
            if has_m: return "duet_mm" # (Только если есть "он", но нет "она")
            return "duet_mf" # По умолчанию (если нет грамматики)

        if "choir" in form:
            # v5: Исправлена ошибка 'в' на 'in'
            if "мужск" in t or "male choir" in t: return "choir_male"
            if "женск" in t or "female choir" in t: return "choir_female"
            return "choir_mixed"

        return f"{form}_mixed"

    def get(
        self,
        genre_full: str,
        preferred_gender: str,
        text: str,
        sections: List[Dict[str,Any]], # (Устарело, но оставлено для API)
        vocal_profile_tags: List[Dict[str, Any]] # v4.3: Приходит из monolith (СПИСОК)
    ) -> Tuple[List[str], List[str], str]:
        
        log.debug(f"Вызов функции: VocalProfileRegistry.get (Genre={genre_full}, PrefGender={preferred_gender})")
        
        # 1. Определяем базовый жанр для карты инструментов
        # v8: 'lyrical' теперь приоритетнее 'default'
        g = "edm" if "edm" in genre_full else \
            "cinematic" if "cinematic" in genre_full else \
            "orchestral" if "orchestral" in genre_full else \
            "rock" if "rock" in genre_full or "metal" in genre_full else \
            "pop" if "pop" in genre_full else \
            "folk" if "folk" in genre_full else \
            "ambient" if "ambient" in genre_full else \
            "lyrical" if "lyrical" in genre_full else "default" 

        if g not in self.map:
            log.warning(f"Жанр '{g}' не найден в vocal_map, используется 'default'")
            g = "default"
        log.debug(f"Выбранная карта инструментов: {g}")

        # 2. Определяем форму (solo/duet/choir)
        hints = self._detect_ensemble_hints(text, sections)
        form = "solo" 
        
        log.debug(f"Теги вокала из monolith (список): {vocal_profile_tags}")
        
        # === v9: ИСПРАВЛЕНИЕ AttributeError: 'list' object has no attribute 'get' ===
        # Мы должны сперва подсчитать теги из списка, который прислал monolith
        summed_tags = {"male": 0, "female": 0, "mixed": 0, "auto": 0}
        if isinstance(vocal_profile_tags, list):
            for profile in vocal_profile_tags: 
                # (v9.1) Убедимся, что profile - это dict
                if isinstance(profile, dict):
                    gender = profile.get("gender", "auto")
                    if gender in summed_tags:
                        summed_tags[gender] += 1
                    else:
                        summed_tags["auto"] += 1
                else:
                    log.warning(f"Элемент в vocal_profile_tags не dict: {profile}")
        else:
            log.warning(f"vocal_profile_tags не является списком! Получен: {type(vocal_profile_tags)}")
            
        log.debug(f"Подсчитанные теги (словарь): {summed_tags}")
        # === Конец исправления v9 ===

        # v4.3: Новая логика определения формы (v9: использует summed_tags)
        if summed_tags.get("mixed", 0) > 0:
            form = "duet"
        elif summed_tags.get("male", 0) > 0 and summed_tags.get("female", 0) > 0:
             form = "duet"
        elif summed_tags.get("male", 0) > 2 or summed_tags.get("female", 0) > 2:
             form = "trio" # (Если один пол доминирует в 3+ секциях)
        
        # Хинты (duet, choir) из текста имеют приоритет
        for name in ["choir","quintet","quartet","trio","duet"]:
            if hints.get(f"wants_{name}"):
                form = name
                break 
        log.debug(f"Форма после хинтов: {form}")

        # Если все еще solo, используем старый метод auto_form
        if form == "solo" and \
           not (summed_tags.get("male") or summed_tags.get("female")):
            
            if self.emo_analyzer and self.tlp_analyzer:
                emo = self.emo_analyzer.analyze(text)
                tlp = self.tlp_analyzer.analyze(text)
                form = self._auto_form(emo, tlp, text)
            else:
                log.warning("Emo/TLP анализаторы не загружены, _auto_form пропущен.")
        log.debug(f"Финальная форма: {form}")

        # 3. Определяем состав (male/female/mixed)
        # v9: использует summed_tags
        auto_gender = "auto"
        if summed_tags.get("male", 0) > summed_tags.get("female", 0):
            auto_gender = "male"
        elif summed_tags.get("female", 0) > summed_tags.get("male", 0):
            auto_gender = "female"
        elif summed_tags.get("mixed", 0) > 0:
            auto_gender = "mixed"
        log.debug(f"Грамматический пол: {auto_gender}")

        # UI (preferred_gender) имеет высший приоритет
        final_gender_preference = preferred_gender if preferred_gender != "auto" else auto_gender
        if final_gender_preference == "mixed": final_gender_preference = "auto" 
        log.debug(f"Финальный пол (с учетом UI): {final_gender_preference}")
        
        vocal_form = self._mixed_code(form, final_gender_preference, text)
        log.debug(f"Финальный код формы: {vocal_form}")

        # 4. Собираем вокал и инструменты
        female_vox = self.map[g]["female"]
        male_vox = self.map[g]["male"]
        
        if final_gender_preference == "female":
            vox = female_vox
        elif final_gender_preference == "male":
            vox = male_vox
        else: # auto
            if "mf" in vocal_form: # duet_mf
                vox = male_vox + female_vox
            else:
                emo = self.emo_analyzer.analyze(text) if self.emo_analyzer else {}
                vox = (female_vox if (emo.get("joy",0)+emo.get("peace",0) >
                                      emo.get("anger",0)+emo.get("epic",0)) else male_vox)
        
        # 5. Очистка и возврат
        vox = [form] + vox
        vox = sorted(list(set(v for v in vox if v in VALID_VOICES)))[:6]
        inst = sorted(list(set(i for i in self.map[g]["inst"] if i in VALID_INSTRUMENTS)))[:6]
        
        log.debug(f"Возврат: Vox={vox}, Inst={inst}, Form={vocal_form}")
        return vox, inst, vocal_form

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
