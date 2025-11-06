from __future__ import annotations
from typing import Optional, Dict, Any
import re

from StudioCore_Complete_v4 import StudioCore

SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def _smart_strip(s: str) -> str:
    # Нормализация, сохраняющая переносы строк и спецсимволы
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in s.split("\n")]
    return "\n".join(lines).strip()

def _inject_minimal_skeleton(text: str) -> str:
    """Если пользователь вставил чистый текст без скелета — добавим мягкий каркас."""
    if SECTION_TAG_RE.search(text):
        return text  # скелет уже есть
    blocks = [blk.strip() for blk in text.split("\n\n") if blk.strip()]
    if not blocks:
        return text
    out = []
    if blocks:
        out.append("[Verse 1]")
        out.append(blocks[0])
    if len(blocks) >= 2:
        out.append("")
        out.append("[Chorus]")
        out.append(blocks[1])
    for i, blk in enumerate(blocks[2:], start=2):
        out.append("")
        out.append(f"[Verse {i}]")
        out.append(blk)
    return "\n".join(out)

class PilgrimInterface:
    """
    Тонкий слой над StudioCore для «чистого» UX:
    - принимает сырую лирику (без JSON, без скобок),
    - при необходимости добавляет скелет,
    - прокидывает author_style (если нужно),
    - возвращает полноценно собранный результат ядра.
    """
    def __init__(self, core: Optional[StudioCore] = None):
        self.core = core or StudioCore()

    def analyze_plain(
        self,
        lyrics_raw: str,
        prefer_gender: str = "auto",
        author_style: Optional[str] = None,
        autoskeleton: bool = True
    ) -> Dict[str, Any]:
        text = _smart_strip(lyrics_raw or "")
        if autoskeleton:
            text = _inject_minimal_skeleton(text)

        res = self.core.analyze(
            lyrics=text,
            prefer_gender=prefer_gender,
            author_style=author_style
        )

        # Дополнительно вернём «чистый» скелет для пользователя
        return {
            "genre": res.genre,
            "bpm": res.bpm,
            "tonality": res.tonality,
            "vocals": res.vocals,
            "instruments": res.instruments,
            "tlp": res.tlp,
            "emotions": res.emotions,
            "resonance": res.resonance,
            "integrity": res.integrity,
            "tonesync": res.tonesync,
            "sections": res.sections,
            "prompt": res.prompt,
            "skeleton_text": text
        }

    def analyze_structured(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        lyrics = payload.get("lyrics", "")
        prefer_gender = payload.get("prefer_gender", "auto")
        author_style = payload.get("author_style")
        autoskeleton = bool(payload.get("autoskeleton", True))
        return self.analyze_plain(
            lyrics_raw=lyrics,
            prefer_gender=prefer_gender,
            author_style=author_style,
            autoskeleton=autoskeleton
        )