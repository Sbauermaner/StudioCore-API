# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
SpiritualEmotionMap v2 — формула духовной эмоциональной оценки.

Оси:
- faith (вера)
- doubt (сомнение)
- repentance (покаяние)
- divine_tension (борьба света / тьмы)
- mystical_intensity (ощущение чуда)
- moral_weight (нравственный вес)
- eschatology (вечность, смерть, царство)
- spiritual_relevance (общая сила духовной темы)

Этот модуль работает НА ВСЕХ текстах, но включает
духовную ось только если релевантность > 0.2.
"""

import re


class SpiritualEmotionMap:
    def __init__(self):
        self.axes = {
            "faith": 0.0,
            "doubt": 0.0,
            "repentance": 0.0,
            "divine_tension": 0.0,
            "mystical_intensity": 0.0,
            "moral_weight": 0.0,
            "eschatology": 0.0,
            "spiritual_relevance": 0.0,
        }

        # ключевые слова — маркеры духовной семантики
        self.keywords = {
            "faith": [
                "бог",
                "господ",
                "отец небес",
                "вера",
                "ангел",
                "дух",
                "свят",
                "молитв",
                "псалм",
                "храм",
            ],
            "doubt": [
                "сомнен",
                "я ли",
                "зачем я",
                "почему я",
                "не слышу",
                "не вижу",
                "потеря",
                "боль",
            ],
            "repentance": [
                "грех",
                "прости",
                "покаян",
                "раская",
                "вину",
                "искуплен",
                "каюсь",
            ],
            "divine_tension": [
                "тьма",
                "свет",
                "дьявол",
                "сатан",
                "борьба",
                "лев рыкающий",
                "искушение",
                "демон",
                "битва",
            ],
            "mystical_intensity": [
                "тайна",
                "чудо",
                "видение",
                "сон",
                "знамение",
                "сошествие",
                "озарение",
                "пророчество",
            ],
            "moral_weight": [
                "правда",
                "совесть",
                "справедлив",
                "милосерд",
                "добро",
                "зло",
                "грех",
                "суд",
                "заповедь",
            ],
            "eschatology": [
                "вечность",
                "смерт",
                "ад",
                "рай",
                "судный день",
                "конец времен",
                "второе пришествие",
                "царь грядет",
            ],
        }

    # --- Подсчёт совпадений ---

    def count_matches(self, text, word_list):
        count = 0
        for w in word_list:
            found = len(re.findall(w, text.lower()))
            count += found
        return count

    # --- Основная формула ---

    def compute(self, text: str):
        total_hits = 0

        # анализ каждой оси
        for axis, words in self.keywords.items():
            hits = self.count_matches(text, words)
            self.axes[axis] = min(1.0, hits * 0.15)  # нормализация
            total_hits += hits

        # вычисление глобальной релевантности
        self.axes["spiritual_relevance"] = min(1.0, total_hits * 0.05)

        # если низкая духовная релевантность — оси почти обнуляются
        if self.axes["spiritual_relevance"] < 0.2:
            for key in self.axes:
                if key != "spiritual_relevance":
                    self.axes[key] *= self.axes["spiritual_relevance"]

        return self.axes


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
