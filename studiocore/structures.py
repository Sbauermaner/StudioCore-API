# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

class PhraseEmotionPacket:
    def __init__(self, phrase: str, emotions: dict, weight: float, impact_zone: str, semantic_role: str):
        self.phrase = phrase
        self.emotions = emotions
        self.weight = weight
        self.impact_zone = impact_zone
        self.semantic_role = semantic_role

    def to_dict(self):
        return {
            "phrase": self.phrase,
            "emotions": self.emotions,
            "weight": self.weight,
            "impact_zone": self.impact_zone,
            "semantic_role": self.semantic_role,
        }


class SectionEmotionWave:
    def __init__(self, section, tlp_mean, cluster_peak, intensity, emotional_shape, hot_phrases):
        self.section = section
        self.tlp_mean = tlp_mean
        self.cluster_peak = cluster_peak
        self.intensity = intensity
        self.emotional_shape = emotional_shape
        self.hot_phrases = hot_phrases

    def to_dict(self):
        return {
            "section": self.section,
            "tlp_mean": self.tlp_mean,
            "cluster_peak": self.cluster_peak,
            "intensity": self.intensity,
            "emotional_shape": self.emotional_shape,
            "hot_phrases": self.hot_phrases,
        }
