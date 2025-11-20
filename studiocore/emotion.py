# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engines (v15 - Имена ИСПРАВЛЕНЫ)
Быстрый эвристический анализ (не ИИ) + Расширенные словари v3.
"""

import json
import os
import re
import math
from typing import Dict, Any, Optional
import logging

from studiocore.emotion_profile import EmotionVector, EmotionAggregator
from studiocore.emotion_dictionary_extended import EmotionLexiconExtended
from studiocore.structures import PhraseEmotionPacket

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.

# Получаем логгер для этого модуля
log = logging.getLogger(__name__)

# === Весовые карты ===
PUNCT_WEIGHTS = {"!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1}
EMOJI_WEIGHTS = {ch: 0.5 for ch in "❤💔💖🔥😭😢✨🌌🌅🌙🌈☀⚡💫"}


# =====================================================
# 💠 Truth × Love × Pain Engine (v3 Словари)
# =====================================================
class TruthLovePainEngine: # <-- v15: Оригинальное имя
    """Balances TLP axes using expanded v3 dictionaries."""

    # v3 - Расширенные словари с "корнями"
    TRUTH_WORDS = [
        "правд", "истин", "честн", "смысл", "знан", "позна", "созна", # ru
        "мудро", "осозна", "голос", "суть", "reason", "судьб",
        "truth", "honest", "real", "meaning", "wisdom", "soul", "mind", # en
        "see", "know", "understand", "realize", "reflect"
    ]

    LOVE_WORDS = [
        "люб", "нежн", "сердц", "забот", "свет", "тепл", "солнц", "жизн", # ru
        "мир", "надежд", "вер", "добр", "друг", "вмест", "простит", "дом",
        "love", "care", "unity", "light", "heart", "peace", "hope", "faith", # en
        "warm", "sun", "life", "friend", "together", "forgive", "home", "kind"
    ]

    PAIN_WORDS = [
        "боль", "страда", "мук", "горе", "плач", "слез", "рана", "потер", # ru
        "ненави", "гнев", "зл", "яд", "лож", "тьм", "мрак", "смерт", "крик",
        "холод", "пусто", "один", "тоск", "пепел", "кров", "воин", "бо", # (бой, боль...)
        "страх", "ужас", "тревог", "тону", "камен", "груз", "обман", "рухн",
        "pain", "hate", "fear", "lie", "dark", "death", "anger", "cry", "cold", # en
        "war", "suffer", "grief", "loss", "scream", "alone", "empty", "blood",
        "broken", "fall", "lost", "scared"
    ]

    def __init__(self):
        # Компилируем регекспы один раз для скорости
        self.TRUTH = re.compile(r"(" + "|".join(self.TRUTH_WORDS) + r")", re.I)
        self.LOVE = re.compile(r"(" + "|".join(self.LOVE_WORDS) + r")", re.I)
        self.PAIN = re.compile(r"(" + "|".join(self.PAIN_WORDS) + r")", re.I)
        log.debug(f"TLP Engine (v15) инициализирован с {len(self.TRUTH_WORDS)}+{len(self.LOVE_WORDS)}+{len(self.PAIN_WORDS)} словами.")

    def analyze(self, text: str) -> Dict[str, float]:
        log.debug(f"Вызов функции: TruthLovePainEngine.analyze")
        s = text.lower()

        truth_hits = len(self.TRUTH.findall(s))
        love_hits = len(self.LOVE.findall(s))
        pain_hits = len(self.PAIN.findall(s))

        total = truth_hits + love_hits + pain_hits

        log.debug(f"TLP хиты: T={truth_hits}, L={love_hits}, P={pain_hits}, Total={total}")

        if total == 0:
            # Если нет TLP слов, вычисляем "частоту" (CF)
            word_count = len(re.findall(r"[a-zа-яё]+", s))
            cf = 1.0 - min(1.0, word_count / 100.0) * 0.5
            truth, love, pain = 0.0, 0.0, 0.0
        else:
            # Нормализация
            truth = truth_hits / total
            love = love_hits / total
            pain = pain_hits / total

            # Гармония (Love, Truth) против Диссонанса (Pain)
            harmony = (love + truth) / 2
            dissonance = pain

            # CF = (Гармония - Диссонанс) + 0.5 (базовая линия)
            cf = max(0.0, min(1.0, (harmony - dissonance * 0.5 + 0.5)))

        result = {
            "truth": round(truth, 3),
            "love": round(love, 3),
            "pain": round(pain, 3),
            "conscious_frequency": round(cf, 3),
        }
        log.debug(f"TLP результат: {result}")
        return result

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )


# =====================================================
# 💫 AutoEmotionalAnalyzer (v3 Словари)
# =====================================================
class AutoEmotionalAnalyzer: # <-- v15: Оригинальное имя
    """Heuristic emotion-field classifier (v15, +Logging)."""

    EMO_FIELDS = {
        "joy": ["joy", "happy", "laugh", "смех", "рад", "улыб", "счаст", "весел", "hope", "bright", "солнц"],
        "sadness": ["sad", "печал", "груст", "слез", "плач", "cry", "lonely", "утрат", "страда", "тоск", "один"],
        "anger": ["anger", "rage", "злост", "гнев", "ярост", "fight", "burn", "ненави", "крик", "воин"],
        "fear": ["fear", "страх", "ужас", "паник", "тревог", "боят", "scared"],
        "peace": ["мир", "тишин", "calm", "still", "тихо", "равновес", "спокой", "умиротвор"],
        "epic": ["epic", "велич", "геро", "легенд", "immortal", "battle", "rise", "бог", "судьб", "огон", "шторм", "неб", "гимн"],
        "awe": ["восторг", "awe", "wow", "чудо", "вдохнов", "удив", "прекрас"],
        "neutral": [] # Остается пустым
    }

    def __init__(self):
        self.LEXICON = {}
        for field, tokens in self.EMO_FIELDS.items():
            if tokens:
                # v13: Компилируем регекспы для *корней* слов (быстрее и точнее)
                self.LEXICON[field] = re.compile(r"(" + "|".join(tokens) + r")", re.I)
        log.debug(f"AutoEmotionalAnalyzer (v15) инициализирован.")

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        if not scores:
            return {}
        max_score = max(scores.values()) if scores else 0
        try:
            exps = {k: math.exp(v - max_score) for k, v in scores.items()}
        except OverflowError:
            log.warning("Softmax Overflow. Используется линейная нормализация.")
            total = sum(v for v in scores.values() if v > 0) or 1.0
            return {k: max(0, v) / total for k, v in scores.items()}

        total = sum(exps.values()) or 1.0
        return {k: exps[k] / total for k in scores}

    def analyze(self, text: str) -> Dict[str, float]:
        log.debug(f"Вызов функции: AutoEmotionalAnalyzer.analyze")
        s = text.lower()

        # 1️⃣ Энергия пунктуации и эмодзи
        punct_energy = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in s)
        emoji_energy = sum(EMOJI_WEIGHTS.get(ch, 0.0) for ch in s)
        energy = min(1.0, (punct_energy + emoji_energy) ** 0.7)
        log.debug(f"Энергия пунктуации/эмодзи: {energy:.2f}")

        # 2️⃣ Подсчёт совпадений по токенам
        scores: Dict[str, float] = {}
        total_hits = 0
        for field, pattern in self.LEXICON.items():
            hits = len(pattern.findall(s))
            scores[field] = float(hits)
            total_hits += hits

        log.debug(f"Хиты по эмоциям (raw): {scores}")

        # 3️⃣ Усиление (Amplification)
        if energy > 0.1 and total_hits > 0:
            for field in scores:
                scores[field] *= (1 + energy ** 2)
            log.debug(f"Хиты по эмоциям (усиленные): {scores}")

        # 4️⃣ Нормализация (softmax)
        normalized = self._softmax(scores)

        # 5️⃣ Если сигналов нет — вернуть фоновое спокойствие
        if total_hits == 0 or all(v < 0.05 for v in normalized.values()):
            log.debug("Сигналы эмоций не найдены. Возврат 'peace'.")
            normalized = {"peace": 0.6, "joy": 0.3, "neutral": 0.1}

        # 6. Очистка (убираем 'neutral' и нули)
        final_scores = {k: round(v, 3) for k, v in normalized.items() if k != "neutral" and v > 0.001}
        log.debug(f"Результат EMO (финал): {final_scores}")
        return final_scores

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )


# =====================================================
# 🎼 EmotionModel v1 (66 → 12 → GENRE/BPM/KEY)
# =====================================================
_EMOTION_MODEL_CACHE: Optional[Dict[str, Any]] = None


def load_emotion_model() -> Dict[str, Any]:
    """Load and cache emotion_model_v1.json."""

    global _EMOTION_MODEL_CACHE
    if _EMOTION_MODEL_CACHE is not None:
        return _EMOTION_MODEL_CACHE

    model_path = os.path.join(os.path.dirname(__file__), "emotion_model_v1.json")
    try:
        with open(model_path, "r", encoding="utf-8") as fp:
            _EMOTION_MODEL_CACHE = json.load(fp)
    except FileNotFoundError:
        log.warning("emotion_model_v1.json not found; using empty model")
        _EMOTION_MODEL_CACHE = {"version": "0.0", "clusters": {}}
    return _EMOTION_MODEL_CACHE


class EmotionEngine:
    """Emotion inference pipeline that maps raw cues → clusters → genre/BPM/key."""

    def __init__(self) -> None:
        self.lexicon = EmotionLexiconExtended()
        self.auto_analyzer = AutoEmotionalAnalyzer()
        self.tlp_engine = TruthLovePainEngine()
        self._model = load_emotion_model()
        self._base_emotions = self._collect_base_emotions()
        self._phrase_packets: list[PhraseEmotionPacket] = []

    def _collect_base_emotions(self) -> list[str]:
        clusters = self._model.get("clusters", {})
        emotions: list[str] = []
        for cluster in clusters.values():
            emotions.extend(cluster.get("emotions", []))
        return sorted(set(emotions))

    def reset_phrase_packets(self) -> None:
        """Reset the internal phrase packet buffer."""

        self._phrase_packets = []

    def get_phrase_packets(self) -> list[PhraseEmotionPacket]:
        """Expose collected phrase packets for downstream consumers."""

        return list(self._phrase_packets)

    def analyze_phrase(self, phrase: str) -> PhraseEmotionPacket:
        """Phrase-level analyzer that leverages the v1 emotion model."""

        safe_phrase = phrase or ""
        normalized = " ".join(safe_phrase.lower().strip().split())

        # Semantic role detection (early to avoid failures later)
        semantic_role = "statement"
        if any(marker in safe_phrase.lower() for marker in ("как", "словно", "будто")):
            semantic_role = "metaphor"
        if any(ch in safe_phrase for ch in ("!", "?")):
            semantic_role = "exclamation"

        # Neutral fallback for empty input
        if not normalized:
            base_vector = {emotion: 0.0 for emotion in self._base_emotions}
            cluster_vector = {name: 0.0 for name in self._model.get("clusters", {})}
            tlp_profile = self.tlp_engine.analyze("")
            weight = 0.05
            impact_zone = "mixed"
        else:
            base_vector = self.build_raw_emotion_vector(normalized)
            cluster_vector = self.project_to_clusters(base_vector)

            # Normalize cluster values if they exceed 1.0
            max_cluster = max(cluster_vector.values()) if cluster_vector else 0.0
            if max_cluster > 1.0:
                cluster_vector = {k: round(v / max_cluster, 3) for k, v in cluster_vector.items()}

            tlp_profile = self.tlp_engine.analyze(normalized)

            base_energy = min(1.0, sum(base_vector.values())) if base_vector else 0.0
            weight = max(base_energy, max_cluster)
            if weight <= 0:
                weight = 0.05

            pain = tlp_profile.get("pain", 0.0)
            love = tlp_profile.get("love", 0.0)
            if pain > love and pain > 0.6:
                impact_zone = "pain"
            elif love > pain and love > 0.6:
                impact_zone = "love"
            else:
                impact_zone = "mixed"

        emotions_payload = {
            "base": base_vector,
            "clusters": cluster_vector,
            "tlp": tlp_profile,
        }

        packet = PhraseEmotionPacket(
            phrase=safe_phrase,
            emotions=emotions_payload,
            weight=float(min(1.0, weight)),
            impact_zone=impact_zone,
            semantic_role=semantic_role,
        )

        self._phrase_packets.append(packet)
        return packet

    def build_raw_emotion_vector(self, text: str) -> Dict[str, float]:
        """Build normalized raw emotion scores (0..1) for atomic emotions."""

        lowered = text.lower()
        raw_scores: Dict[str, float] = {emotion: 0.0 for emotion in self._base_emotions}

        # Direct keyword matching against the model emotions
        for emotion in self._base_emotions:
            token = emotion.replace("_", " ")
            pattern = re.escape(token)
            hits = len(re.findall(pattern, lowered))
            raw_scores[emotion] += float(hits)

        # Lexicon-driven boosts
        lexicon_result = self.lexicon.get_emotion(text)
        for bucket, active in lexicon_result.get("emotions", {}).items():
            if not active:
                continue
            for emotion in self._base_emotions:
                if bucket in emotion:
                    raw_scores[emotion] += 1.0

        # Heuristic analyzer (joy/sadness/etc.) mapped onto similar tokens
        auto_scores = self.auto_analyzer.analyze(text)
        for bucket, value in auto_scores.items():
            for emotion in self._base_emotions:
                if bucket in emotion:
                    raw_scores[emotion] += float(value) * 2.0

        max_score = max(raw_scores.values()) if raw_scores else 0.0
        if max_score <= 0:
            return raw_scores
        return {emotion: round(score / max_score, 3) for emotion, score in raw_scores.items()}

    def project_to_clusters(self, raw: Dict[str, float]) -> Dict[str, float]:
        clusters = self._model.get("clusters", {})
        projected: Dict[str, float] = {}
        for cluster_name, cluster_model in clusters.items():
            emotions = cluster_model.get("emotions", [])
            if not emotions:
                projected[cluster_name] = 0.0
                continue
            total = sum(raw.get(emotion, 0.0) for emotion in emotions)
            projected[cluster_name] = round(total / max(1, len(emotions)), 3)
        return projected

    def compute_genre_scores(self, clusters: Dict[str, float]) -> Dict[str, float]:
        genre_scores: Dict[str, float] = {}
        model_clusters = self._model.get("clusters", {})
        for cluster_name, value in clusters.items():
            cluster_model = model_clusters.get(cluster_name, {})
            for genre, bias in cluster_model.get("genre_bias", {}).items():
                genre_scores[genre] = genre_scores.get(genre, 0.0) + value * float(bias)

        max_score = max(genre_scores.values()) if genre_scores else 0.0
        if max_score <= 0:
            return {genre: 0.0 for genre in genre_scores}
        return {genre: round(score / max_score, 3) for genre, score in genre_scores.items()}

    def pick_final_genre(self, genre_scores: Dict[str, float], legacy_genre: Optional[str] = None) -> str:
        if not genre_scores:
            return legacy_genre or "unknown"

        sorted_genres = sorted(genre_scores.items(), key=lambda item: item[1], reverse=True)
        top_genres = [item[0] for item in sorted_genres[:3]]
        if legacy_genre and genre_scores.get(legacy_genre, 0.0) > 0 and legacy_genre in top_genres:
            return legacy_genre
        return sorted_genres[0][0]

    def compute_bpm_base(self, clusters: Dict[str, float]) -> float:
        aggression = clusters.get("rage", 0.0)
        sadness = clusters.get("sadness", 0.0)
        hope = clusters.get("hope", 0.0)
        awe = clusters.get("awe", 0.0)

        bpm = 92.0
        bpm += aggression * 40.0
        bpm -= sadness * 20.0
        bpm += hope * 15.0
        bpm += awe * 10.0

        model_clusters = self._model.get("clusters", {})
        delta = 0.0
        for cluster_name, value in clusters.items():
            cluster_model = model_clusters.get(cluster_name, {})
            delta += value * float(cluster_model.get("bpm_delta", 0.0))
        bpm += delta * 0.25

        bpm = max(60.0, min(190.0, bpm))
        return round(bpm, 2)

    def compute_key_and_mode(self, clusters: Dict[str, float]) -> Dict[str, str]:
        sadness = clusters.get("sadness", 0.0) + clusters.get("pain", 0.0) + clusters.get("disappointment", 0.0)
        love = clusters.get("love", 0.0)
        hope = clusters.get("hope", 0.0)
        tenderness = love  # tenderness nested in love cluster
        awe = clusters.get("awe", 0.0)
        rage = clusters.get("rage", 0.0)

        key_info: Dict[str, str] = {"scale": "minor" if sadness > 0.55 else "major"}
        if love + hope + tenderness > 0.55:
            key_info["scale"] = "major"
        if awe > 0.7:
            key_info["scale"] = "modal_phrygian_lydian"
            key_info["mode_hint"] = "phrygian"
        if rage > 0.7:
            key_info["scale"] = "minor_dark"
            key_info["mode_hint"] = "dark_minor"
        return key_info

    def build_emotion_profile(self, text: str, legacy_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raw = self.build_raw_emotion_vector(text)
        clusters = self.project_to_clusters(raw)
        genre_scores = self.compute_genre_scores(clusters)
        bpm = self.compute_bpm_base(clusters)
        key_info = self.compute_key_and_mode(clusters)

        profile = {
            "raw": raw,
            "clusters": clusters,
            "genre_scores": genre_scores,
            "bpm": bpm,
            "key": key_info,
        }

        if legacy_context:
            profile["legacy"] = legacy_context
        return profile

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
