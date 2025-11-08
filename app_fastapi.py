from fastapi import FastAPI, Body
from StudioCore_Complete_v4_3 import (
    normalize_text_preserve_symbols,
    extract_sections,
    TruthLovePainEngine,
    AutoEmotionalAnalyzer,
    LyricMeter,
    UniversalFrequencyEngine,
    IntegrityScanEngine,
    StyleMatrix,
    VocalProfileRegistry,
    ToneSyncEngine,
    load_config,
    RNSSafety,
)

app = FastAPI(title="StudioCore API", version="4.3")

@app.get("/")
def root():
    return {"status": "ok", "message": "StudioCore API v4.3 is running"}

@app.post("/analyze")
def analyze_text(data: dict = Body(...)):
    text = data.get("text", "")
    config = load_config()

    tlp = TruthLovePainEngine().analyze(text)
    emo = AutoEmotionalAnalyzer().analyze(text)
    bpm = LyricMeter().bpm_from_density(text)
    freq = UniversalFrequencyEngine().resonance_profile(tlp)
    integrity = IntegrityScanEngine().analyze(text)
    genre = StyleMatrix().genre(emo, tlp, text, bpm)
    tonality = StyleMatrix().tonality(emo)
    vox, inst = VocalProfileRegistry().get(genre, "auto", text, extract_sections(text))
    tone = ToneSyncEngine()
    audio_prof = tone.audio_profile(emo)
    visual_prof = tone.visual_profile(emo)
    sync = tone.sync_score(audio_prof, visual_prof)
    safety = RNSSafety(config).mix_notes()

    return {
        "tlp": tlp,
        "emotion": emo,
        "bpm": bpm,
        "genre": genre,
        "tonality": tonality,
        "frequency_profile": freq,
        "vocal_instruments": {"voices": vox, "instruments": inst},
        "tone_sync": {
            "audio": audio_prof,
            "visual": visual_prof,
            "sync_score": sync
        },
        "integrity": integrity,
        "safety": safety
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=8000, reload=True)
