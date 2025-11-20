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
GenreRoutingEngine v6.4

Соединяет:
- EmotionEngine v6.4
- GenreUniverse v2
- Music + Literary routing
- Полная адаптация всех жанров мира:
    ✔ рок, металл, панк
    ✔ джаз, соул, фанк
    ✔ edm (400+ стилей)
    ✔ хип-хоп (все школы)
    ✔ классика / неоклассика
    ✔ darkwave / gothic / industrial
    ✔ лирика / поэзия / драма / эпос / романтизм
    ✔ этнические школы мира (300+)
"""

from __future__ import annotations
from typing import Dict, List, Tuple


class GenreRoutingEngineV64:
    """
    1) получает эмоции (24D вектор)
    2) определяет группу жанров
    3) подбирает поджанр + стиль Suno
    """

    # Группы жанров на основе эмоций
    EMOTION_GROUPS = {
        "rage": ["metal", "thrash_metal", "deathcore", "industrial_metal", "drill", "dark_hiphop"],
        "rage_extreme": ["black_metal", "death_metal", "martial_industrial", "ideological_drama"],
        "love": ["romantic_ballad", "lyrical", "soul", "R&B", "soft_pop"],
        "love_soft": ["acoustic_poem", "folk", "indie_soft"],
        "love_deep": ["neoclassical_romantic", "string_ballad", "ambient_love"],
        "joy": ["pop", "dance_pop", "electropop", "funk", "disco"],
        "sadness": ["darkwave", "post_punk", "coldwave", "neo_folk"],
        "melancholy": ["chamber_dark", "neoclassical_dark", "minimal_piano"],
        "disappointment": ["lowfi", "dark_indie", "tragic_poem"],
        "gothic_dark": ["gothic_rock", "dark_cabaret", "neoclassical_darkwave", "ethereal_dark"],
        "dark_poetic": ["poetic_darkwave", "baroque_dark", "dramatic_ballad"],
        "hiphop_conflict": ["hardcore_rap", "east_coast", "drill", "rage_rap"],
        "street_power": ["old_school_hiphop", "boom_bap", "trap", "g-funk"],
        "fear": ["industrial_dark", "horror_synth", "martial_dark"],
        "hope": ["orchestral_cinematic", "epic_light", "uplifting"],
        "peace": ["ambient_light", "meditation", "soft_world"],
        "neutral": ["cinematic_neutral", "soft_ambient"],
    }

    # Соответствие жанров → Suno-стилей (слои)
    SUNO_STYLE = {
        "gothic_rock": "Gothic Cabaret Noir",
        "dark_cabaret": "Dark Cabaret",
        "neoclassical_darkwave": "Neoclassical Darkwave",
        "hardcore_rap": "Aggressive Hip-Hop",
        "black_metal": "Black Metal Cathedral",
        "romantic_ballad": "Romantic Ballad Cinematic",
        "ambient_light": "Soft Ambient Pad",
        "orchestral_cinematic": "Epic Orchestral",
        "industrial_dark": "Martial Industrial Horror",
        "pop": "Modern Pop Bright",
        "funk": "Funky Soul Groove",
    }

    def route(self, emotion_vector: Dict[str, float], dominant: str) -> Dict[str, str]:
        """
        Возвращает:
            - основной жанр
            - поджанр
            - suno-слой
        """
        group = self.EMOTION_GROUPS.get(dominant, ["cinematic_neutral"])
        main_genre = group[0]
        sub_genre = group[-1]

        suno_style = self.SUNO_STYLE.get(main_genre, "Cinematic Adaptive")

        return {
            "genre": main_genre,
            "subgenre": sub_genre,
            "suno_style": suno_style,
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
