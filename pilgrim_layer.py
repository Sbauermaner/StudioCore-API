from __future__ import annotations
from typing import Optional, Dict, Any
from StudioCore_Complete_v4 import StudioCore, load_config

ALLOWED_MODES = {"auto", "author", "healing", "dramatic", "ritual", "neutral"}

class PilgrimInterface:
    def __init__(self, config_path: str = "studio_config.json", default_mode: str = "auto"):
        self.core = StudioCore(load_config(config_path))
        self.mode = default_mode if default_mode in ALLOWED_MODES else "auto"

    def set_mode(self, mode: str):
        if mode in ALLOWED_MODES:
            self.mode = mode

    def analyze_lyrics(
        self,
        lyrics: str,
        prefer_gender: str = "auto",
        author_style: Optional[str] = None,
        force_voice: Optional[str] = None,
        genre_hint: Optional[str] = None,
        return_format: str = "json"  # "json" | "text"
    ) -> Dict[str, Any]:

        # режимы могут подсказать стиль
        if self.mode == "healing":
            author_style = (author_style or "") + " healing, compassionate, low density, warm harmonies"
        elif self.mode == "dramatic":
            author_style = (author_style or "") + " epic, dramatic swells, wide dynamics"
        elif self.mode == "ritual":
            author_style = (author_style or "") + " ritual/ancient tone, droning, throat hints"
        # neutral/auto — без доп. модификаций

        result = self.core.analyze(
            lyrics=lyrics,
            prefer_gender=prefer_gender,
            author_style=author_style,
            force_voice=force_voice,
            genre_hint=genre_hint
        )

        if return_format == "text":
            # Чистый текст + style prompt — удобно копировать в Suno
            text_block = result.formatted_text
            style_block = f"\n\n---\nSTYLE PROMPT → {result.prompt}\n"
            return {"text": text_block + style_block}

        # Полный JSON
        return {
            "genre": result.genre,
            "bpm": result.bpm,
            "tonality": result.tonality,
            "vocals": result.vocals,
            "instruments": result.instruments,
            "tlp": result.tlp,
            "emotions": result.emotions,
            "resonance": result.resonance,
            "integrity": result.integrity,
            "tonesync": result.tonesync,
            "sections": result.sections,
            "prompt": result.prompt,
            "formatted_text": result.formatted_text
        }