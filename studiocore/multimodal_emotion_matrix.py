# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
from typing import Any, Dict, List


class MultimodalEmotionMatrixV1:
    """
    Multimodal Emotional Matrix (M - E-M) v1.

    Сводит в единый эмоционально - музыкальный профиль:
    - phrase_emotions
    - section_emotions (SectionEmotionWave)
    - global_emotion_curve (GlobalEmotionCurve)
    - tlp_profile (TLP Engine)
    - dynamic_bias (emotion - driven BPM / KEY hints)
    - genre_hint, bpm_hint, key_hint (от существующих движков)
    - suno emotional annotations
    """

    def __init__(self, *, version: str = "v1") -> None:
        self.version = version

    def build_matrix(
        self,
        *,
        phrase_emotions: List[dict],
        section_emotions: List[dict],
        global_curve: Dict[str, Any],
        tlp_profile: Dict[str, float],
        dynamic_bias: Dict[str, Any],
        genre_hint: Any,
        bpm_hint: Any,
        key_hint: Any,
        suno_annotation: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Простая и безопасная агрегация без override пользовательских параметров.
        # Все рекомендации = hints, которые могут быть использованы Suno или StudioCore.
        # Никакого состояния — чистый stateless.

        dominant = global_curve.get("dominant_cluster")
        sections = global_curve.get("sections", [])

        # Определение доминирующих эмоций
        if tlp_profile:
            t = tlp_profile.get("truth", 0.0)
            l = tlp_profile.get("love", 0.0)  # noqa: E741
            p = tlp_profile.get("pain", 0.0)
            dominant_emotions = sorted(
                [("truth", t), ("love", l), ("pain", p)],
                key=lambda x: x[1],
                reverse=True,
            )
        else:
            dominant_emotions = []

        # Рекомендации по жанру
        if dominant == "rage":
            genre_primary = "extreme_adaptive_rage"
            sub = "dark_metal_core"
        elif dominant == "despair":
            genre_primary = "darkwave_cinematic"
            sub = "gothic_melancholic"
        elif dominant == "tender":
            genre_primary = "lyrical_ballad"
            sub = "neoclassical_soft"
        elif dominant == "hope":
            genre_primary = "ambient_orchestral"
            sub = "light_neo"
        elif dominant == "narrative":
            genre_primary = "poetic_narrative"
            sub = "acoustic_indie"
        else:
            genre_primary = "adaptive_hybrid"
            sub = None

        # BPM рекомендации
        bpm_rec = bpm_hint or 120.0
        if dynamic_bias:
            bpm_delta = dynamic_bias.get("bpm_delta", 0.0)
            bpm_rec = float(bpm_rec) + float(bpm_delta)

        # Key рекомендации
        key_mode = None
        if dynamic_bias:
            if dynamic_bias.get("key_hint") == "minor":
                key_mode = "minor"
            elif dynamic_bias.get("key_hint") == "major":
                key_mode = "major"

        # Вокал
        primary_emotion = dominant_emotions[0][0] if dominant_emotions else None
        if primary_emotion == "pain":
            vok = {
                "gender": "male",
                "intensity_curve": [sec.get("intensity", 0) for sec in sections],
                "notes": "distorted male low + aggressive fry layers",
            }
        elif primary_emotion == "love":
            vok = {
                "gender": "female",
                "intensity_curve": [sec.get("intensity", 0) for sec in sections],
                "notes": "soft airy female vocal, close mic",
            }
        elif primary_emotion == "truth":
            vok = {
                "gender": "male",
                "intensity_curve": [sec.get("intensity", 0) for sec in sections],
                "notes": "spoken baritone clarity",
            }
        else:
            vok = {
                "gender": "auto",
                "intensity_curve": [sec.get("intensity", 0) for sec in sections],
                "notes": "adaptive vocal blend",
            }

        # Инструменты
        if primary_emotion == "pain":
            inst = {
                "core": ["distorted_guitars", "heavy_drums"],
                "accent": ["sub_bass", "fry_noise"],
                "texture": ["industrial_air"],
            }
        elif primary_emotion == "love":
            inst = {
                "core": ["piano", "cello"],
                "accent": ["soft_pads"],
                "texture": ["warm_reverb"],
            }
        elif primary_emotion == "truth":
            inst = {
                "core": ["acoustic_guitar"],
                "accent": ["soft_percussion"],
                "texture": ["narrative_space"],
            }
        else:
            inst = {
                "core": ["hybrid_base"],
                "accent": [],
                "texture": [],
            }

        return {
            "version": self.version,
            "tlp": tlp_profile,
            "dominant_emotions": dominant_emotions,
            "global_curve": global_curve,
            "section_emotions": section_emotions,
            "dynamic_bias": dynamic_bias,
            "genre": {
                "primary": genre_primary,
                "subgenre": sub,
                "confidence": 1.0,
                "source": "emotion_matrix_v1",
            },
            "bpm": {
                "recommended": bpm_rec,
                "source": "emotion_matrix_v1",
            },
            "key": {
                "recommended": key_hint,
                "mode": key_mode,
                "source": "emotion_matrix_v1",
            },
            "vocals": vok,
            "instruments": inst,
            "suno_emotion_annotations": suno_annotation,
        }


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
