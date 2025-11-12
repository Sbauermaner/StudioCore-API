# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engines
v6.0 - AI-Powered Zero-Shot Classification Engine
Использует мультиязычную модель transformers для контекстного анализа.
"""

import math
from typing import Dict, Any, List

# Попытка импорта transformers. Hugging Face Spaces установит их из requirements.txt
try:
    from transformers import pipeline
except ImportError:
    print("="*50)
    print("❌ [EmotionEngine] КРИТИЧЕСКАЯ ОШИБКА: 'transformers' не найдены.")
    print("   Пожалуйста, добавьте 'transformers', 'sentencepiece' и 'torch' в requirements.txt")
    print("="*50)
    pipeline = None

# =====================================================
# 🧠 Загрузка мультиязычной ИИ-модели
# =====================================================
# Эта модель может классифицировать текст на 100+ языках
# по любым заданным меткам (zero-shot).
def load_classifier():
    if not pipeline:
        return None
    try:
        print("🧠 [EmotionEngine] Загрузка мультиязычной NLI-модели...")
        # Используем DeBERTa - она легче и быстрее, чем BART, для многоязычности
        classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        )
        print("✅ [EmotionEngine] Модель NLI (Zero-Shot) успешно загружена.")
        return classifier
    except Exception as e:
        print(f"❌ [EmotionEngine] КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить модель transformers.")
        print(f"   Ошибка: {e}")
        return None

# Загружаем модель один раз при старте
classifier = load_classifier()

# =====================================================
# 💠 Truth × Love × Pain Engine (AI-Powered)
# =====================================================
class TruthLovePainEngine:
    """Анализирует TLP через призму Zero-Shot NLI."""

    # Мы используем английские метки, так как модель лучше всего обучена на них,
    # но она поймет текст на любом языке.
    TLP_LABELS = ["truth", "love", "pain"]

    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"truth": 0.0, "love": 0.0, "pain": 0.0, "conscious_frequency": 0.0}

        try:
            # Модель анализирует текст и возвращает оценки для наших меток
            result = classifier(text, self.TLP_LABELS, multi_label=True)

            scores = {label: 0.0 for label in self.TLP_LABELS}
            for label, score in zip(result['labels'], result['scores']):
                scores[label] = score
            
            t = scores.get("truth", 0.0)
            l = scores.get("love", 0.0)
            p = scores.get("pain", 0.0)

            # Conscious Frequency = гармония трёх осей (старая формула)
            cf = 1.0 - (abs(t - l) + abs(l - p) * 0.35 + abs(t - p) * 0.25)
            cf = max(0.0, min(cf, 1.0))

            return {
                "truth": round(t, 3),
                "love": round(l, 3),
                "pain": round(p, 3),
                "conscious_frequency": round(cf, 3),
            }
        except Exception as e:
            print(f"❌ [TLP Engine] Ошибка во время NLI-анализа: {e}")
            return {"truth": 0.0, "love": 0.0, "pain": 0.0, "conscious_frequency": 0.0}


# =====================================================
# 💫 AutoEmotionalAnalyzer (AI-Powered)
# =====================================================
class AutoEmotionalAnalyzer:
    """Классификатор эмоционального поля на базе NLI (v6)."""

    EMO_LABELS = [
        "joy",       # Радость, счастье
        "sadness",   # Печаль, грусть
        "anger",     # Гнев, ярость
        "fear",      # Страх, тревога
        "peace",     # Мир, спокойствие
        "epic",      # Эпичность, героизм
        "awe"        # Восторг, удивление
    ]

    def _softmax(self, scores: List[float]) -> List[float]:
        exps = [math.exp(s) for s in scores]
        total = sum(exps) or 1.0
        return [e / total for e in exps]

    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"peace": 1.0} # Безопасный возврат

        try:
            result = classifier(text, self.EMO_LABELS, multi_label=True)
            
            # Применяем softmax, чтобы все оценки в сумме давали 1.0
            normalized_scores = self._softmax(result['scores'])

            final_scores = {label: 0.0 for label in self.EMO_LABELS}
            for label, score in zip(result['labels'], normalized_scores):
                final_scores[label] = round(score, 3)

            # Если сигналов нет — вернуть фоновое спокойствие
            if all(v < 0.1 for v in final_scores.values()):
                # Назначаем 'peace' по умолчанию, если нет явных эмоций
                final_scores = {label: 0.0 for label in self.EMO_LABELS}
                final_scores["peace"] = 1.0

            return final_scores
        
        except Exception as e:
            print(f"❌ [Emotion Analyzer] Ошибка во время NLI-анализа: {e}")
            return {"peace": 1.0}