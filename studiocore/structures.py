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
