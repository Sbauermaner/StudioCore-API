# StudioCore IMMORTAL v7.0 — StudioCore-API

Автор / Author: **Sergey Bauer (@Sbauermaner)**

> RU/EN bilingual README. Русский блок следует сразу после английских подзаголовков, чтобы документация была синхронной.

## 📚 Table of Contents
- [Philosophy / Философия](#-philosophy--философия)
- [Architecture & Evolution / Архитектура и эволюция](#-architecture--evolution--архитектура-и-эволюция)
- [Core Features / Ключевые особенности](#-core-features--ключевые-особенности)
- [Computation Details / Детали вычислений](#-computation-details--детали-вычислений)
- [Canonical Extended Prompt / Канонический расширенный промпт](#-canonical-extended-prompt--канонический-расширенный-промпт)
- [Suno v5 Optimization / Оптимизация под Suno v5](#-suno-v5-optimization--оптимизация-под-suno-v5)
- [Known Issues / Известные проблемы](#-known-issues--известные-проблемы)
- [Run Locally / Локальный запуск](#-run-locally--локальный-запуск)
- [Deploy to Hugging Face Spaces / Деплой в Hugging-Face-Spaces](#-deploy-to-hugging-face-spaces--деплой-в-hugging-face-spaces)
- [License / Лицензия](#-license--лицензия)

## 🧭 Philosophy / Философия
**Truth × Love × Pain = Conscious Frequency (CF).**
- EN: Every analysis projects lyrics onto the TLP axes; CF is the harmonic mean of the three normalized axes and drives downstream tone, BPM, and color safety models.
- RU: Любой текст раскладывается по осям Истина/Любовь/Боль; CF — гармоническое среднее нормализованных осей и влияет на тональность, BPM и частотную безопасность.

## 🏛 Architecture & Evolution / Архитектура и эволюция
- EN: `core_v6.py` is the request-scoped façade; it orchestrates text parsing, TLP/RDE/BPM/tone, fusion, FANF annotations, and Suno prompt building while remaining stateless after each call. Legacy `monolith_v4_3_1.py` stays as a fallback but is not extended.
- RU: `core_v6.py` — фасад на один запрос: парсинг текста, TLP/RDE/BPM/тональность, Fusion, FANF-аннотации и сборка Suno-промптов с очисткой состояния после вызова. Наследный монолит `monolith_v4_3_1.py` подключается только как резерв.
- EN: A cached `GenreUniverse` registry normalizes genre tags and domains for music/EDM/literature/drama and hybrids.
- RU: Кэширующий реестр `GenreUniverse` унифицирует жанровые теги и домены (music/EDM/литература/драма/гибриды).

## ✨ Core Features / Ключевые особенности
- **TLP → CF**: Keyword- and emotion-weighted Truth/Love/Pain vector with CF average; exposes dominant axis and balance.
- **RDE**: Resonance/Fracture/Entropy heuristics track repetition, structural variance, and token entropy.
- **ZeroPulse & Breathing cues**: Zero-pulse status and breathing sync are attached to diagnostics and FANF summaries when available.
- **GenreUniverse & Weights**: Domain-aware genre detection plus macro-genre normalization for prompts.
- **Diagnostics to Summary Block**: Unified `[TLP] [RDE] [Genre] [ZeroPulse] [ColorWave] [Integrity]` block for UI/CLI.
- **Fusion + Suno Adapter**: Optional fusion of BPM/key/genre plus Suno prompt builder with semantic compression and RNS safety tag.

## 🧮 Computation Details / Детали вычислений
- **TLP & Conscious Frequency**
  - EN: `TruthLovePainEngine.tlp_vector` scores keywords + emotion matrix, clamps to configured bounds, and sets `conscious_frequency` as the mean of the normalized axes.
  - RU: `TruthLovePainEngine.tlp_vector` суммирует ключевые слова + эмбед эмоций, зажимает по конфигу и пишет `conscious_frequency` как среднее осей.
- **BPM**
  - EN: `BPMEngine.compute_bpm_v2` estimates BPM from per-line syllable density and average line length, clamped to 40–200 BPM; emotional microshifts are ±3%.
  - RU: `BPMEngine.compute_bpm_v2` считает BPM по слоговой плотности и длине строк (ограничение 40–200), эмоциональный микросдвиг ±3%.
- **RDE / Resonance Dynamics**
  - EN: Resonance counts repeated tokens; Fracture uses line-length variance; Entropy derives from character-frequency entropy surrogate.
  - RU: Резонанс — повтор ключевых токенов; Фрактурность — дисперсия длины строк; Энтропия — суррогат символной энтропии.
- **Tonality & Resonance Profile**
  - EN: ToneSync builds a profile from inferred key + TLP + emotions; UniversalFrequencyEngine maps TLP to base Hz, harmonic shift, safe octaves, and RNS index.
  - RU: ToneSync собирает профиль из ключа + TLP + эмоций; UniversalFrequencyEngine проецирует TLP в базовую частоту, гармонический сдвиг, безопасные октавы и индекс RNS.
- **GenreUniverse / GenreWeights**
  - EN: Genres are canonicalized and domain-tagged; macro/sub-genre are normalized back into `style.genre` to keep prompts stable.
  - RU: Жанры канонизируются и получают доменные теги; макро/саб-жанр возвращается в `style.genre` для стабильных промптов.

## 🧾 Canonical Extended Prompt / Канонический расширенный промпт
- EN: FANF v8.1 assembles a Suno-safe extended block. Required order:
  1. `style_prompt`: `[GENRE: ...] [MOOD: ...] [BPM: ...] [KEY: ...] [CF: ...] [GENRE_UNIVERSE: ...] [FREQ: ...]`
  2. `lyrics_prompt`: per-section headers `[SECTION: mood=..., energy=..., arr=...]` followed by raw lines.
  3. `ui_text`: source text without bracketed metadata.
  4. `summary`: concatenated diagnostic blocks `[TLP] [RDE] [Genre] [ZeroPulse] [ColorWave] [Integrity]` + consistency/meta.
- RU: FANF v8.1 собирает расширенный Suno-блок. Порядок:
  1. `style_prompt`: `[GENRE: ...] [MOOD: ...] [BPM: ...] [KEY: ...] [CF: ...] [GENRE_UNIVERSE: ...] [FREQ: ...]`
  2. `lyrics_prompt`: заголовки секций `[SECTION: mood=..., energy=..., arr=...]` + строки текста.
  3. `ui_text`: исходник без скобочных метаданных.
  4. `summary`: слитые диагностические блоки `[TLP] [RDE] [Genre] [ZeroPulse] [ColorWave] [Integrity]` + consistency/meta.

### Example / Пример
```
[GENRE: adaptive]
[MOOD: neutral]
[BPM: 120] [KEY: Am] [CF: 0.73] [GENRE_UNIVERSE: {"domain": "music", ...}] [FREQ: {"base_hz": 450.1, ...}]
[VERSE: mood=neutral, energy=mid, arr=standard]
line one of lyrics
line two of lyrics
[TLP: 0.82/0.65/0.71 | CF 0.73]
[RDE: resonance=0.12, fracture=0.05, entropy=0.23]
[Genre: adaptive]
[ZeroPulse: False]
[ColorWave: blue, amber]
[Integrity: ok]
```

## 🎚 Suno v5 Optimization / Оптимизация под Suno v5
- EN: Use `build_suno_prompt` in `suno_style` mode to output `[GENRE] [MOOD] [INSTRUMENTATION] [VOCAL] [PRODUCTION] [BPM] [KEY]` with semantic compression; set vocal form to male/low descriptors for guttural timbre.
- RU: Используйте `build_suno_prompt` с вариантом `suno_style`, чтобы получить `[GENRE] [MOOD] [INSTRUMENTATION] [VOCAL] [PRODUCTION] [BPM] [KEY]` с семантическим сжатием; задайте вокал male/low для гортанного тембра.
- EN: Recommended sliders — higher Style Influence (~0.92) and conservative BPM (<120) to keep RNS safety (`RNS:safe` when key is friendly and BPM <120).
- RU: Рекомендованные ползунки — Style Influence ≈0.92 и сдержанный BPM (<120), чтобы RNS-тег оставался `RNS:safe` при дружелюбном ключе.

## 🐞 Known Issues / Известные проблемы
- EN: GenreUniverse is cached globally; changes to genre registry require process restart.
- RU: `GenreUniverse` кэшируется глобально — обновление реестра требует перезапуска процесса.
- EN: TLP keyword lists are hardcoded and narrow (e.g., rap/flow detection is shallow); emotional leakage across runs is avoided in the engines, but relying on keyword heuristics may misclassify edge cases.
- RU: Списки ключевых слов TLP жёстко зашиты и узкие (детектор рэпа/флоу слабый); утечек состояния нет, но эвристики могут ошибаться на пограничных текстах.
- EN: Suno prompt builder assumes presence of genre/BPM/key; missing fields fall back to `adaptive`/`auto`, which can reduce stylistic specificity.
- RU: Сборщик Suno-промптов ожидает жанр/BPM/тональность; при отсутствии откатывается к `adaptive`/`auto`, что снижает точность стиля.

## 🧪 Run Locally / Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py  # Gradio UI (Suno-ready)
```

## 🚀 Deploy to Hugging Face Spaces / Деплой в Hugging-Face-Spaces
- EN: Create a Space (Gradio). Copy repo contents; set `STUDIOCORE_LICENSE` env if needed. Install via `pip install -r requirements.txt`; set entrypoint to `python app.py`.
- RU: Создайте Space (Gradio), скопируйте репозиторий, установите `pip install -r requirements.txt`, при необходимости задайте `STUDIOCORE_LICENSE`, точка входа — `python app.py`.

## 📜 License / Лицензия
- Creative Commons **CC BY-NC-SA 4.0**. Non-commercial share-alike with attribution.
- RU: Запрещено военное/государственное использование и обучение AI на коде без письменного согласия автора.
