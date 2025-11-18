---
title: StudioCore v6.3 MAXI — Adaptive Orchestrator
emoji: 🎧
colorFrom: blue
colorTo: pink
sdk: docker
sdk_version: 5.49.1
app_file: app.py
pinned: true
license: mit
author: Bauer Synesthetic Studio
---

# 🎧 StudioCore API by Bauer
### *StudioCore v6.3 MAXI · Truth × Love × Pain = Conscious Frequency*

> Текущее ядро: **v6.3-maxi**  
> Monolith fallback: **v4.3.1**  
> OpenAPI: [`openapi_main.json`](./openapi_main.json) • [`openapi_gpt.yaml`](./openapi_gpt.yaml)

---

## 💡 Что нового в MAXI

StudioCore MAXI — это объединённое ядро, собранное из всех веток `codex/*`.  
Основные изменения:

- ⚙️ **Унифицированный загрузчик** с приоритетом v6 → v5 → monolith → fallback и детальными диагностическими данными.
- 🧠 **StudioCoreV6** теперь напрямую интегрирует SectionParser, BPM/TLP/RDE движки, REM/ZeroPulse синхронизацию, Suno-аннотации и систему пользовательских overrides.
- 🎛 **Логические движки** разбиты на независимые подсистемы (эмоции, дыхание, стиль, тональность, инструменты, команды, семантика).
- 📚 **Новые публичные обёртки**: `bpm_engine`, `tlp_engine`, `rde_engine`, `section_parser`.
- 🧪 **Обновлённый тестовый комплект** (`pytest`) проверяет загрузчик, BPM, секции и полный v6 pipeline.

---

## 🧱 Структура модулей

```
studiocore/
├── __init__.py              # MAXI-loader + diagnostics
├── core_v6.py               # Композитный оркестратор
├── logical_engines.py       # Все базовые движки и эвристики
├── bpm_engine.py            # Публичный BPM helper
├── tlp_engine.py            # Truth × Love × Pain helper
├── rde_engine.py            # Rhythm × Dynamics × Emotion synthesis
├── section_parser.py        # Sections + annotations + adjustments
├── monolith_v4_3_1.py       # Последний monolith fallback
├── *.py                     # Genre, style, tone, instrument, rhythm, text utils
└── tests/*                  # Унаследованные legacy тесты удалены
```

---

## 🔁 Загрузчик и цепочка fallback

1. `StudioCoreV6` (версия `v6.3-maxi`).
2. `StudioCoreV5` (если доступен в monolith).
3. `StudioCore` из `monolith_v4_3_1.py`.
4. `StudioCoreFallback`.

Каждая попытка фиксируется в `LOADER_STATUS`, а объект `loader_diagnostics()` возвращает полную структуру (версия, активный модуль, ошибки, порядок).

---

## 🎚 Активные движки

- **Emotion + Color** — `AutoEmotionalAnalyzer` + `ColorEmotionEngine`.
- **Truth × Love × Pain** — философский анализ с доминантой и балансом.
- **BPM/Rhythm** — `LyricMeter`, дыхательные поправки, poly-rhythm детектор.
- **RDE Synthesis** — объединяет BPM, дыхание, эмоции и инструментальный профиль.
- **Sections & Commands** — автоматическое разбиение, аннотации, SectionIntelligence.
- **Tonality & Style** — Mode detection, ключи по секциям, StyleMatrix heuristics.
- **User Overrides** — `UserOverrideManager` + `UserAdaptiveSymbiosisEngine`.

---

## 🔍 Диагностика

- `python -m compileall .` — проверка импортов/синтаксиса.
- `pytest -q` — быстрые smoke-тесты (loader, BPM helper, секции, полный pipeline, RDE/TLP).
- `codex runtime-checks` — расширенные сценарии из каталога `codex`.

---

## 🚀 Быстрый старт

```bash
pip install -r requirements.txt
python -m compileall .
pytest -q
uvicorn app:app --reload --port 7860
```

API endpoints (FastAPI + Gradio):

- `GET /status` — актуальное состояние загрузчика и активного ядра.
- `GET /version` — версии и цепочка fallback.
- `GET /diagnostics` — полная структура `loader_diagnostics()`.
- `POST /api/predict` — основное ядро (StudioCoreV6) с Truth × Love × Pain и Suno annotations.

---

## 🧑‍💻 Авторы

Bauer Synesthetic Studio • SBauermaner  
MIT License © 2025 — допустимо использование в исследовательских и креативных проектах при указании авторства.
