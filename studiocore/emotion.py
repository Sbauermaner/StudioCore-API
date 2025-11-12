# -*- coding: utf-8 -*-
"""
StudioCore Emotion Engines (v11 - Inference API)
Использует Hugging Face Inference API (Zero-Shot) для
быстрого, мультиязычного анализа на CPU-спейсах.

ИСПРАВЛЕНИЕ (v11):
- Заменена удаленная модель (410 GONE) 'Narsil/deberta-v3-base-tasksource-nli'
- Новая модель: 'joeddav/xlm-roberta-large-xnli' (стабильная XNLI модель)

ТРЕБУЕТ СЕКРЕТА: HUGGING_FACE_TOKEN
"""

import os
import requests
import time
import math
from typing import Dict, Any

# =====================================================
# 🧠 ИИ-Движок (Inference API)
# =====================================================

# ИСПРАВЛЕНИЕ: Мы используем 'joeddav/xlm-roberta-large-xnli'
API_URL = "https://api-inference.huggingface.co/models/joeddav/xlm-roberta-large-xnli"
HF_TOKEN = os.environ.get("HUGGING_FACE_TOKEN") # Загружаем токен из Секретов

if not HF_TOKEN:
    print("⚠️ [EmotionEngine] ВНИМАНИЕ! Секрет 'HUGGING_FACE_TOKEN' не найден.")
    print("⚠️ [EmotionEngine] Анализ будет недоступен или очень медленным.")
else:
    print("✅ [EmotionEngine] Секрет 'HUGGING_FACE_TOKEN' успешно загружен.")


class NLIClassifier:
    """
    Класс-оболочка для обращения к HF Inference API.
    Гарантирует, что мы используем токен и обрабатываем ошибки/таймауты.
    """
    def __init__(self, api_url: str, token: str | None):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        print(f"🧠 [EmotionEngine] Инициализация клиента NLI. Токен {'загружен' if token else 'ОТСУТСТВУЕТ'}.")

    def query_api(self, payload: Dict[str, Any], retries: int = 3, delay: int = 5) -> Dict[str, Any]:
        """ Отправляет запрос к API с повторными попытками """
        if not self.headers:
            # Если токена нет, мы не можем сделать запрос.
            print("❌ [EmotionEngine] Ошибка: Запрос к API невозможен без HUGGING_FACE_TOKEN.")
            return {} # Возвращаем пустой результат

        try:
            # Увеличиваем таймаут соединения на всякий случай
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=25)
            
            # Обработка ошибок
            if response.status_code == 503: # Model is loading
                if retries > 0:
                    print(f"⏳ [EmotionEngine] Модель (xlm-roberta) на сервере HF загружается, ждем {delay}с...")
                    time.sleep(delay)
                    return self.query_api(payload, retries - 1, delay * 2)
                else:
                    print("❌ [EmotionEngine] Модель не смогла загрузиться вовремя на сервере HF.")
                    return {}
            
            response.raise_for_status() # Вызовет ошибку для 4xx/5xx (включая 410)
            return response.json()
        
        except requests.exceptions.ReadTimeout:
            print(f"❌ [EmotionEngine] API ReadTimeout (ожидание > {25}с).")
            return {}
        except Exception as e:
            print(f"❌ [EmotionEngine] Ошибка API: {e}")
            return {}

    def analyze(self, text: str, labels: list[str]) -> Dict[str, float]:
        """ Выполняет zero-shot классификацию через API """
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": labels, "multi_label": False},
        }
        
        result = self.query_api(payload)
        
        if not result or 'scores' not in result or 'labels' not in result:
            print(f"⚠️  [EmotionEngine] API вернул неверный формат: {result}")
            # Возвращаем заглушку, чтобы система не упала
            return {label: 0.0 for label in labels}

        # Собираем результат
        # result = {'sequence': '...', 'labels': ['love', 'truth', 'pain'], 'scores': [0.9, 0.05, 0.05]}
        scores_dict = {label: score for label, score in zip(result['labels'], result['scores'])}
        
        # Убедимся, что все запрошенные метки присутствуют
        final_scores = {label: scores_dict.get(label, 0.0) for label in labels}
        return final_scores

# --- Инициализация классификатора ---
try:
    classifier = NLIClassifier(API_URL, HF_TOKEN)
    print("✅ [EmotionEngine] ИИ-движок (Inference API) инициализирован.")
except Exception as e:
    print(f"❌ [EmotionEngine] Не удалось инициализировать NLIClassifier: {e}")
    classifier = None

# =====================================================
# 💠 Truth × Love × Pain Engine
# =====================================================
class TruthLovePainEngine:
    """
    (v7) Использует NLI-модель для определения TLP (Truth, Love, Pain).
    """
    def __init__(self):
        self.labels = ["truth", "love", "pain"]
        if not classifier:
            print("❌ [TLPEngine] КЛАССИФИКАТОР НЕ ЗАГРУЖЕН.")

    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"truth": 0.0, "love": 0.0, "pain": 0.0, "conscious_frequency": 0.0}

        # 1. Получаем TLP через ИИ
        scores = classifier.analyze(text, self.labels)
        
        truth = scores.get("truth", 0.0)
        love = scores.get("love", 0.0)
        pain = scores.get("pain", 0.0)

        # 2. Conscious Frequency = гармония трёх осей
        # (Эта логика остается неизменной)
        cf = 1.0 - (abs(truth - love) + abs(love - pain) * 0.35 + abs(truth - pain) * 0.25)
        cf = max(0.0, min(cf, 1.0))

        return {
            "truth": round(truth, 3),
            "love": round(love, 3),
            "pain": round(pain, 3),
            "conscious_frequency": round(cf, 3),
        }

# =====================================================
# 💫 AutoEmotionalAnalyzer
# =====================================================
class AutoEmotionalAnalyzer:
    """
    (v7) Использует NLI-модель для определения Эмоций.
    """
    def __init__(self):
        self.labels = ["joy", "sadness", "anger", "fear", "peace", "epic", "awe"]
        if not classifier:
            print("❌ [AutoEmotionalAnalyzer] КЛАССИФИКАТОР НЕ ЗАГРУЖЕН.")

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        """ Нормализует NLI-оценки, если они не нормализованы """
        total = sum(scores.values())
        if total == 0 or (0.99 < total < 1.01):
             return scores # Уже нормализованы
        
        exps = {k: math.exp(v) for k, v in scores.items()}
        total_exp = sum(exps.values()) or 1.0
        return {k: exps[k] / total_exp for k in scores}

    def analyze(self, text: str) -> Dict[str, float]:
        if not classifier:
            return {"neutral": 1.0}

        # 1. Получаем Эмоции через ИИ
        scores = classifier.analyze(text, self.labels)

        # 2. Нормализация (NLI API уже должен возвращать softmax)
        normalized = self._softmax(scores)

        # 3. Если сигналов нет — вернуть фоновое спокойствие
        if all(v < 0.05 for v in normalized.values()):
            return {"peace": 0.6, "joy": 0.3, "neutral": 0.1}

        return normalized