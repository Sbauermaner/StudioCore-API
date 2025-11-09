import re
from typing import List, Dict, Any

PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

def normalize_text_preserve_symbols(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip()

def extract_sections(text: str) -> List[Dict[str, Any]]:
    sections = []
    current = {"tag": "Body", "lines": []}
    for ln in text.split("\n"):
        m = SECTION_TAG_RE.match(ln)
        if m:
            if current["lines"]:
                sections.append(current)
            current = {"tag": m.group(1).strip(), "lines": []}
        else:
            current["lines"].append(ln)
    if current["lines"]:
        sections.append(current)
    for s in sections:
        s["lines"] = [l for l in s["lines"] if l.strip()]
    return sections
