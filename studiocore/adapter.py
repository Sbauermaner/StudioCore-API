mport re

def semantic_compress(text: str, max_len: int = 1000) -> str:
    """
    Compresses text meaningfully, keeping structure and key terms.
    Strategy:
      - Keep only first phrase of each section
      - Remove filler adjectives/adverbs
      - Preserve keywords like Genre, Style, BPM, Engine
    """
    if len(text) <= max_len:
        return text.strip()

    # Убираем повторы, длинные прилагательные
    text = re.sub(r"\b(beautiful|incredible|powerful|very|extremely|deeply|really|highly)\b", "", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Если всё ещё длинно — оставляем начало каждой смысловой линии
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    compressed = []
    total = 0
    for p in parts:
        if total + len(p) < max_len - 50:
            compressed.append(p)
            total += len(p)
        else:
            break
    return " ".join(compressed).strip() + "…"


def build_suno_prompt(style_data: dict, vocals: list, instruments: list, bpm: int, philosophy: str, version: str, mode: str = "full") -> str:
    """
    Builds full StudioCore prompt or compressed Suno version.
    """
    s = style_data
    prompt = (
        f"Genre: {s['genre']} | Key: {s['key']} | BPM: {bpm}\n"
        f"Structure: {s['structure']}\n"
        f"Vocals: {', '.join(vocals)} | Techniques: {', '.join(s['techniques'])}\n"
        f"Instruments: {', '.join(instruments)}\n"
        f"Visual: {s['visual']}\n"
        f"Narrative: {s['narrative']}\n"
        f"Atmosphere: {s['atmosphere']}\n"
        f"Philosophy: {philosophy}\n"
        f"Engine: StudioCore {version} adaptive emotional system"
    )

    if mode == "suno":
        return semantic_compress(prompt, 1000)
    return prompt
