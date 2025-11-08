import json
from typing import Dict, Any
from StudioCore_Complete_v4_3 import analyze_and_style, STUDIOCORE_VERSION


def analyze_text(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core function that receives JSON from FastAPI, runs full analysis,
    and returns structured JSON response.
    """
    # --- Base parameters ---
    lyrics = payload.get("lyrics", "").strip()
    prefer_gender = payload.get("preferred_gender", "auto").lower()
    author_style = payload.get("author_style", None)
    version = payload.get("suno_version", "v5")

    if not lyrics:
        return {
            "error": "No lyrics provided",
            "status": "failed",
            "engine": STUDIOCORE_VERSION
        }

    # --- Run main pipeline ---
    result = analyze_and_style(
        raw_text=lyrics,
        suno_version=version,
        preferred_vocal=prefer_gender,
        author_style_hint=author_style
    )

    # --- Build output JSON ---
    response = {
        "status": "ok",
        "engine": STUDIOCORE_VERSION,
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "vocals": result.vocals,
        "instruments": result.instruments,
        "techniques": result.techniques,
        "tlp": result.tlp,
        "emotions": result.emotions,
        "resonance": result.resonance,
        "tonesync": result.tonesync,
        "style_prompt": result.prompt,
        "safety_notes": result.safety_notes,
        "integrity": result.integrity
    }

    return response


def to_pretty_json(data: Dict[str, Any]) -> str:
    """Utility: safe formatted JSON for logs or debug."""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)