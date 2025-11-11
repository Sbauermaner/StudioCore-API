# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5 — Expressive Adaptive Engine
Truth × Love × Pain = Conscious Frequency

Модуль инициализации ядра:
- подключает основные подмодули (emotion, rhythm, frequency, style, tone и т.д.)
- обеспечивает безопасный анализ текста без перегрузки памяти
- возвращает структурированные данные для Gradio и FastAPI
"""

from __future__ import annotations
import json, math, re
from pathlib import Path
from typing import Dict, Any

# === Версия ядра ===
STUDIOCORE_VERSION = "v5.0"

# === Импорт основных компонентов ===
try:
    from .emotion import EmotionAnalyzer
    from .rhythm import RhythmAnalyzer
    from .frequency import FrequencyEngine
    from .style import StyleMatrix
    from .tone import ToneSync
    from .vocals import VocalForm
except Exception as e:
    print(f"⚠️ Partial import warning: {e}")


# === Основной класс ядра ===
class StudioCore:
    """
    Центральное ядро StudioCore v5.
    Обеспечивает анализ текста с кросс-модульной синхронизацией:
    - EmotionAnalyzer → RhythmAnalyzer → FrequencyEngine → StyleMatrix → ToneSync
    """

    def __init__(self):
        self.version = STUDIOCORE_VERSION
        self.emotion = EmotionAnalyzer() if "EmotionAnalyzer" in globals() else None
        self.rhythm = RhythmAnalyzer() if "RhythmAnalyzer" in globals() else None
        self.freq = FrequencyEngine() if "FrequencyEngine" in globals() else None
        self.style = StyleMatrix() if "StyleMatrix" in globals() else None
        self.tone = ToneSync() if "ToneSync" in globals() else None
        self.vocals = VocalForm() if "VocalForm" in globals() else None

    # === Основной метод анализа ===
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {"error": "empty_input"}

        try:
            emotions = self.emotion.analyze(text) if self.emotion else {}
            bpm = self.rhythm.bpm_from_density(text) if self.rhythm else 120
            freq_data = self.freq.calculate(emotions, bpm) if self.freq else {}
            style = self.style.infer(text, emotions, bpm) if self.style else {}
            tone = self.tone.sync(emotions, freq_data) if self.tone else {}
            vocals = self.vocals.suggest(style, bpm) if self.vocals else []

            result = {
                "emotions": emotions,
                "bpm": bpm,
                "frequency": freq_data,
                "style": style,
                "tonesync": tone,
                "vocals": vocals,
                "tlp": self._calc_tlp(emotions),
                "version": self.version,
            }
            result["prompt_full"] = self._build_prompt(result)
            result["prompt_suno"] = self._compress_prompt(result)
            result["annotated_text"] = self._annotate(text, result)
            return result

        except Exception as e:
            return {"error": str(e)}

    # === Расчёт Truth × Love × Pain ===
    def _calc_tlp(self, emotions: Dict[str, float]) -> Dict[str, float]:
        love = emotions.get("love", 0.33)
        pain = emotions.get("pain", 0.33)
        truth = emotions.get("truth", 0.33)
        cf = min(1.0, (truth + love - pain + 1) / 3)
        return {"truth": truth, "love": love, "pain": pain, "conscious_frequency": cf}

    # === Построение полного промта ===
    def _build_prompt(self, data: Dict[str, Any]) -> str:
        try:
            return (
                f"[StudioCore v5 | BPM: {data.get('bpm', 0)}]\n"
                f"Genre: {data.get('style', {}).get('genre', 'unknown')}\n"
                f"Vocal: {data.get('style', {}).get('vocal_form', 'solo')}\n"
                f"Tone: {data.get('tonesync', {}).get('primary_color', 'neutral')}\n"
                f"TLP: Truth={data['tlp']['truth']:.2f}, Love={data['tlp']['love']:.2f}, Pain={data['tlp']['pain']:.2f}"
            )
        except Exception:
            return "⚠️ Prompt generation failed."

    # === Компрессированный промт (для Suno / API ≤ 1KB) ===
    def _compress_prompt(self, data: Dict[str, Any]) -> str:
        base = self._build_prompt(data)
        # Сжатие текста — убираем все пробелы и лишние переводы строк
        return re.sub(r"\s+", " ", base)[:950]

    # === Генерация аннотации ===
    def _annotate(self, text: str, data: Dict[str, Any]) -> str:
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        tone = data.get("tonesync", {}).get("primary_color", "neutral")
        bpm = data.get("bpm", 120)
        return (
            f"🎙️ Annotation: tone={tone}, bpm={bpm}, lines={len(lines)}\n"
            + "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines[:30]))
        )

    def annotate_text(self, text: str, *_, **__) -> str:
        """Совместимость с внешним вызовом app.py"""
        return self._annotate(text, self.analyze(text))
