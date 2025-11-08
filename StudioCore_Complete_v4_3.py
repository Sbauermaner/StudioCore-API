from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

from StudioCore_Complete_v4_3 import (
    STUDIOCORE_VERSION, VERSION_LIMITS,
    load_config, normalize_text_preserve_symbols, extract_sections,
    TruthLovePainEngine, AutoEmotionalAnalyzer, LyricMeter, UniversalFrequencyEngine,
    IntegrityScanEngine, StyleMatrix, VocalProfileRegistry, ToneSyncEngine,
    RNSSafety, build_suno_style_prompt, full_pipeline
)

app = FastAPI(title="StudioCore API", version=STUDIOCORE_VERSION)

# CORS для GPT Builder/веб-клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # при необходимости сузьте
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cfg = load_config()

# ------------------ MODELS ------------------

class FullAnalyzeIn(BaseModel):
    text: str
    author_style: Optional[str] = None
    gender: str = "male"
    prompt_limit: int = 1000

class QuickAnalyzeIn(BaseModel):
    text: str

class SunoPromptIn(BaseModel):
    text: str
    author_style: Optional[str] = None
    gender: str = "male"
    limit: int = 1000

# ------------------ ROUTES ------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "version": STUDIOCORE_VERSION, "suno_versions": VERSION_LIMITS}

@app.post("/analyze/quick")
def analyze_quick(payload: QuickAnalyzeIn):
    text = normalize_text_preserve_symbols(payload.text)
    tlp = TruthLovePainEngine().analyze(text)
    emo = AutoEmotionalAnalyzer().analyze(text)
    bpm = LyricMeter().bpm_from_density(text)
    genre = StyleMatrix().genre(emo, tlp, text, bpm)
    tonality = StyleMatrix().tonality(emo)
    return {
        "version": STUDIOCORE_VERSION,
        "genre": genre,
        "tonality": tonality,
        "bpm": bpm,
        "tlp": tlp,
        "emotions": emo
    }

@app.post("/analyze/sections")
def analyze_sections(payload: QuickAnalyzeIn):
    text = normalize_text_preserve_symbols(payload.text)
    sections = extract_sections(text)
    return {"sections": sections, "count": len(sections)}

@app.post("/analyze/full")
def analyze_full(payload: FullAnalyzeIn):
    res = full_pipeline(
        text=payload.text,
        author_style=payload.author_style,
        preferred_gender=payload.gender,
        prompt_limit=payload.prompt_limit
    )
    return res.__dict__

@app.post("/prompt/suno")
def build_suno_prompt_endpoint(payload: SunoPromptIn):
    text = normalize_text_preserve_symbols(payload.text)
    sections = extract_sections(text)
    tlp = TruthLovePainEngine().analyze(text)
    emo = AutoEmotionalAnalyzer().analyze(text)
    bpm = LyricMeter().bpm_from_density(text)
    genre = StyleMatrix().genre(emo, tlp, text, bpm)
    tonality = StyleMatrix().tonality(emo)
    voice, instruments = VocalProfileRegistry().get(genre, payload.gender, text, sections)
    rns_data = RNSSafety(cfg).mix_notes()
    style_line = StyleMatrix().recommend(emo, tlp, payload.author_style, sections)
    prompt = build_suno_style_prompt(
        text=text, tlp=tlp, emo=emo, bpm=bpm, genre=genre, tonality=tonality,
        voices=voice, instruments=instruments, rns=rns_data, style_line=style_line,
        limit=min(max(100, payload.limit), 1000)
    )
    return {
        "version": STUDIOCORE_VERSION,
        "limit": min(max(100, payload.limit), 1000),
        "bpm": bpm,
        "genre": genre,
        "tonality": tonality,
        "voice": voice,
        "instruments": instruments,
        "style_line": style_line,
        "prompt": prompt
    }
