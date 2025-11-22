# StudioCore v7.0 IMMORTAL · README (November 2025)

**Author / Автор:** Sergey Bauer (Сергей Бауэр)

> Truth × Love × Pain = Conscious Frequency

---

## Table of Contents / Оглавление
- [Philosophy / Философия](#philosophy--философия)
- [Architecture & Evolution / Архитектура и эволюция](#architecture--evolution--архитектура-и-эволюция)
- [Core Features / Особенности](#core-features--особенности)
- [Canonical Extended Prompt Format / Канонический расширенный формат](#canonical-extended-prompt-format--канонический-расширенный-формат)
- [Suno v5 Optimization / Оптимизация под Suno v5](#suno-v5-optimization--оптимизация-под-suno-v5)
- [Known Issues / Известные проблемы](#known-issues--известные-проблемы)
- [Run Locally / Локальный запуск](#run-locally--локальный-запуск)
- [Deploy to Hugging Face Spaces / Деплой в Hugging-Face-Spaces](#deploy-to-hugging-face-spaces--деплой-в-hugging-face-spaces)
- [License / Лицензия](#license--лицензия)

---

## Philosophy / Философия
**Conscious Frequency (CF)** is the emergent harmonic of **Truth**, **Love**, and **Pain**. StudioCore analyzes lyrics along these axes, balancing factual clarity, empathy, and tension. High CF (>0.7) implies complex orchestration and richer color/tone mapping; low CF (<0.3) prefers sparse structures.

**Conscious Frequency (CF)** — гармонический результат осей **Истина**, **Любовь** и **Боль**. Высокий CF (>0.7) ведёт к сложным оркестровкам и насыщенной цвето-тональной картине, низкий CF (<0.3) — к минимализму.

---

## Architecture & Evolution / Архитектура и эволюция
- **Monolith Lineage:** v4.3.11 (legacy God Object), v5.x resonance engines, v6 wrapper (current), merged here as **StudioCore v7.0 IMMORTAL** with stateless request handling and Suno adapters.【F:studiocore/core_v6.py†L96-L151】【F:studiocore/core_v6.py†L424-L492】 
- **Core Wrapper (core_v6.py):** Stateless façade that instantiates per-request engines (text structure, TLP, BPM, RDE, Genre Router, ToneSync, Integrity) to avoid state bleed between calls.【F:studiocore/core_v6.py†L424-L492】 
- **TLP Engine:** Heuristic axis detector with keyword + emotion fusion; clamps outputs via config bounds and derives CF as the mean of normalized axes.【F:studiocore/tlp_engine.py†L31-L71】 
- **Frequency/Resonance:** UniversalFrequencyEngine maps TLP into harmonic shifts, safe octaves, and RNS safety indices (432.1Hz base).【F:studiocore/frequency.py†L33-L86】【F:studiocore/frequency.py†L88-L141】 
- **ToneSync:** Converts key + CF into synesthetic color/resonance signatures and supports semitone shifts; maps keys to harmonic colors and Earth harmony anchors.【F:studiocore/tone.py†L1-L78】 
- **Genre Universe & Weights:** Global registry of music/EDM/literary/dramatic/hybrid genres loaded statelessly; domain weight tables map feature vectors to domains and fallback genres.【F:studiocore/genre_universe_loader.py†L19-L120】【F:studiocore/genre_weights.py†L33-L128】 
- **Suno/FANF Layer:** Adapter builds Suno v5 prompts with semantic compression, RNS tags, and version-aware limits; FANF annotations render cinematic + resonance headers for UI/Suno.【F:studiocore/adapter.py†L1-L120】【F:studiocore/fanf_annotation.py†L1-L79】

---

## Core Features / Особенности
- **TLP & Conscious Frequency:** `TruthLovePainEngine.tlp_vector()` scores axes via lyric heuristics and emotion blending; CF is `(truth + love + pain)/3`. Frequency engine projects CF into base Hz, harmonic shift, RNS safety, and safe octaves.【F:studiocore/tlp_engine.py†L31-L71】【F:studiocore/frequency.py†L88-L141】
- **RDE (Resonance Dynamics & Energy):** BPM micro-shifts and rhythm density are computed by BPMEngine using syllable density/length heuristics; emotional arousal can shift BPM ±3%.【F:studiocore/bpm_engine.py†L13-L59】【F:studiocore/bpm_engine.py†L72-L82】
- **ZeroPulse / Breathing cues:** Integrated via logical engines and exposed in diagnostics summary blocks for timing-aware prompts (see `core_v6._build_summary_block`).【F:studiocore/core_v6.py†L54-L94】
- **GenreUniverse & GenreWeights:** Universe loader registers canonical + alias sets; weights engine maps feature maps to domains with thresholds and fallbacks, enabling multi-domain tagging and hybrid detection.【F:studiocore/genre_universe_loader.py†L19-L200】【F:studiocore/genre_weights.py†L33-L128】
- **Canonical Extended Prompt:** FANF + Suno adapters emit structured blocks (`[GenreFusion …]`, `[VocalTexture …]`, section cues, ZeroPulse, color wave). See canonical format below.
- **Breathing & Section Intelligence:** Section parser plus breathing/command interpreters derive section metadata and annotations passed into FANF builder for dynamic choir activation and section intensity labels.【F:studiocore/fanf_annotation.py†L79-L162】
- **Color & Tone Sync:** ToneSync ties keys to color palettes; emotion curves drive section color waves and Synesthetic resonance headers.【F:studiocore/tone.py†L23-L78】

---

## Canonical Extended Prompt Format / Канонический расширенный формат
Output assembled by `FANFAnnotationEngine` + Suno adapter (line breaks preserved):

```text
[GenreFusion: <genre> / <mood> | BPM: <bpm> | Key/Mode: <anchor> <mode> | A=<base_hz> Hz | Conscious Frequency: <cf>]
[VocalTexture: <texture> + <ChoirLayers|Solo> | ChoirLayers + InstrumentBlend: <palette> | FX: <fx> | Atmosphere: <atm> ]
[Section:<1> INTENSITY:<LOW/MID/MAX>; hot phrase: "<line>" → emphasize with vocal stress / pause]
[ZeroPulse: <markers>]
[ColorWave: <palette>]
[Suno Prompt]
[GENRE: <resolved genre>]
[MOOD: <atmosphere>]
[INSTRUMENTATION: <list>]
[VOCAL: <profile>]
[PRODUCTION: <visual/production>]
[BPM: <bpm>]
[KEY: <key>]
```

Используйте квадратные скобки и отдельные строки строго в таком порядке. Ветка `suno_style` сжимает блоки семантически, сохраняя значения версий и RNS-тег.

---

## Suno v5 Optimization / Оптимизация под Suno v5
- **Version limits:** Prompt length is capped per version (`v5`: 1000 chars) via semantic compression.【F:studiocore/adapter.py†L15-L86】
- **Style Influence:** Keep **92–96%** style influence to preserve GenreFusion cues; lower risks losing ZeroPulse/Breath cues.
- **Male guttural / fry:** Ensure TLP Pain ≥0.6 or lyric markers for aggression; Emotion-driven Suno adapter will choose `"distorted male low + aggressive fry"` and heavy guitars when pain dominates.【F:studiocore/suno_annotations.py†L15-L61】【F:studiocore/suno_annotations.py†L87-L118】
- **RNS Safety:** `rns_safety_tag` injects safe keys (A/E/D/G) and flags BPM over 120 as `watch`; keep BPM <118 for maximum safety.【F:studiocore/adapter.py†L88-L118】
- **Production sliders:**
  - **Instrumental intensity:** favor MAX only when section intensity >0.8; otherwise MID to keep mix clean.
  - **Vocal presence:** start at 65–70% to let guttural layers cut through without pumping compressors.
  - **Reverb/Space:** wide cathedral only when `ChoirLayers active` or gothic keywords; default to medium room.

---

## Known Issues / Известные проблемы
- **Stateful caches:** Global `_GENRE_UNIVERSE` cache in `core_v6` is shared across requests; fresh genre patches require process restart.【F:studiocore/core_v6.py†L30-L43】
- **Tag leakage risk:** Preserved tags from `extract_commands_and_tags` are merged into structure context and may persist in diagnostics when reused externally; callers must deep-copy results before mutation.【F:studiocore/core_v6.py†L451-L468】
- **Hard-coded defaults:** Keyword sets for TLP, choir triggers, and safety tags live in code (e.g., choir keywords, truth/love/pain tokens). Config externalization is recommended to avoid frozen vocabularies.【F:studiocore/tlp_engine.py†L39-L55】【F:studiocore/fanf_annotation.py†L24-L62】
- **Weak rap detector:** Rap/hip-hop detection relies on limited keyword and rhythm-density heuristics; high-speed syllabic verse in other genres can misclassify BPM/genre.【F:studiocore/bpm_engine.py†L13-L47】【F:studiocore/genre_universe_loader.py†L70-L108】
- **Hot phrase bleed:** Section hot-phrase annotations are taken verbatim; aggressive test strings ("Убей их всех") propagate into prompts if not filtered upstream.【F:tests/test_emotion_curve.py†L15-L24】【F:studiocore/fanf_annotation.py†L123-L161】
- **Legacy fallback:** Monolith v4.3.11 remains as fallback; some legacy paths keep magic numbers and Russian-only labels, which can surface in diagnostics when new engines fail.

---

## Run Locally / Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py  # launches FastAPI app
```

---

## Deploy to Hugging Face Spaces / Деплой в Hugging Face Spaces
1. Create a **Gradio/Spaces** Python space.
2. Copy repository files and set `app.py` as the entrypoint.
3. Set environment variable `STUDIOCORE_LICENSE` (non-empty string) for compliance hooks.【F:studiocore/core_v6.py†L367-L383】
4. Enable persistent storage if you plan to ship extended genre packs; otherwise, restart after updates to refresh `_GENRE_UNIVERSE` cache.

---

## License / Лицензия
**CC BY-NC-SA 4.0** — attribution, non-commercial, share-alike. Дополнительный запрет на военное или государственное применение; AI training on this codebase is prohibited without explicit written permission (see license headers).【F:studiocore/core_v6.py†L358-L365】
