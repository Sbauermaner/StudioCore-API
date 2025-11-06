from typing import Optional
from StudioCore_Complete_v4 import StudioCore, make_skeleton

class PilgrimInterface:
    def __init__(self):
        self.core = StudioCore()

    def analyze_to_objects(self, lyrics: str, prefer_gender: str = "auto",
                           author_style: Optional[str] = None,
                           genre_hint: Optional[str] = None) -> dict:
        result = self.core.analyze(lyrics, prefer_gender=prefer_gender,
                                   author_style=author_style, genre_hint=genre_hint)
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
            "prompt": result.prompt
        }

    def analyze_to_text(self, lyrics: str, prefer_gender: str = "auto",
                        author_style: Optional[str] = None,
                        genre_hint: Optional[str] = None) -> str:
        r = self.core.analyze(lyrics, prefer_gender=prefer_gender,
                              author_style=author_style, genre_hint=genre_hint)
        skeleton = make_skeleton(lyrics, prefer_gender, genre_hint or r.genre, r.emotions)
        out = []
        out.append(skeleton)
        out.append("")
        out.append("Style Prompt:")
        out.append(r.prompt)
        return "\n".join(out).strip()
