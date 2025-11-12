# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engine (v12 - Local MiniLM AI)
Использует облегченную локальную модель (Plan B)
"""

import os
import requests
import time
from typing import Dict, Any, List

# === ИСПОЛЬЗОВАНИЕ ЛОКАЛЬНОЙ МОДЕЛИ ===
# Мы используем локальную 'pipeline' из transformers.
# Это медленнее, чем API, но надежнее.
try:
    from transformers import pipeline
    # Используем "облегченную" (Mini) модель, чтобы она работала на CPU
    MODEL_NAME = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"
    print("🧠 [EmotionEngine] Загрузка локальной 'Mini' NLI-модели...")
    # device="cpu" гарантирует, что он не будет пытаться использовать GPU
    classifier = pipeline("zero-shot-classification", model=MODEL_NAME, device="cpu")
    print(f"✅ [EmotionEngine] Локальная модель '{MODEL_NAME}' успешно загружена.")
    _USE_API = False
except ImportError:
    print("❌ [EmotionEngine] ОШИБКА: 'transformers' или 'torch' не установлены.")
    print("❌ [EmotionEngine] TLP-анализ будет отключен.")
    classifier = None
    _USE_API = False
except Exception as e:
    # Ошибка при загрузке модели (например, нет сети в Hugging Face)
    print(f"❌ [EmotionEngine] ОШИБКА ЗАГРУЗКИ МОДЕЛИ: {e}")
    classifier = None
    _USE_API = False


# === Метки ===
TLP_LABELS = ["truth", "love", "pain"]
EMO_LABELS = ["joy", "sadness", "anger", "fear", "peace", "epic"]

class AutoEmotionalAnalyzer:
    """v12: Анализатор EMO (Радость, Грусть...)"""
    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"neutral": 1.0}

        try:
            # multi_label=True, так как в тексте может быть и радость, и страх
            output = classifier(text, EMO_LABELS, multi_label=True)
            
            scores = {label: 0.0 for label in EMO_LABELS}
            if output and 'labels' in output and 'scores' in output:
                for label, score in zip(output['labels'], output['scores']):
                    scores[label] = score
                return scores
            else:
                print("⚠️  [EmotionEngine] EMO: Модель вернула неверный формат.")
                return {"neutral": 1.0}
        except Exception as e:
            print(f"❌ [EmotionEngine] EMO Ошибка: {e}")
            return {"neutral": 1.0}

class TruthLovePainEngine:
    """v12: Анализатор TLP (Истина, Любовь, Боль)"""
    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"truth": 0.33, "love": 0.33, "pain": 0.33, "conscious_frequency": 0.5}

        try:
            # multi_label=False, чтобы TLP конкурировали друг с другом
            output = classifier(text, TLP_LABELS, multi_label=False)
            
            scores = {label: 0.0 for label in TLP_LABELS}
            if output and 'labels' in output and 'scores' in output:
                # 'output' уже отсортирован по убыванию
                scores[output['labels'][0]] = output['scores'][0]
                scores[output['labels'][1]] = output['scores'][1]
                scores[output['labels'][2]] = output['scores'][2]
            else:
                 print("⚠️  [EmotionEngine] TLP: Модель вернула неверный формат.")
                 return {"truth": 0.33, "love": 0.33, "pain": 0.33, "conscious_frequency": 0.5}

            t, l, p = scores.get("truth", 0.0), scores.get("love", 0.0), scores.get("pain", 0.0)
            
            # Сознательная частота (CF)
            cf = 1.0 - (abs(t - l) * 0.5 + abs(l - p) * 0.5 + abs(t - p) * 0.5)
            cf = max(0.0, min(cf, 1.0))

            return {
                "truth": round(t, 3),
                "love": round(l, 3),
                "pain": round(p, 3),
                "conscious_frequency": round(cf, 3),
            }
        except Exception as e:
            print(f"❌ [EmotionEngine] TLP Ошибка: {e}")
            return {"truth": 0.33, "love": 0.33, "pain": 0.33, "conscious_frequency": 0.5}