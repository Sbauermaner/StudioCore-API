import re


# === Semantic compression logic ===
def semantic_compress(text: str, max_len: int = 1000) -> str:
    """
    Compresses text meaningfully without losing structure.
    Keeps key tokens and section headers (Genre, Style, BPM, Engine).
    """
    if len(text) <= max_len:
        return text.strip()

    # Убираем лишние прилагательные и повторяющиеся пробелы
    text = re.sub(
        r"\b(beautiful|incredible|powerful|very|extremely|deeply|really|highly|amazingly|strongly)\b",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Сохраняем начало каждой смысловой линии
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    compressed, total = [], 0
    for p in parts:
        if total + len(p) < max_len - 50:
            compressed.append(p)
            total += len(p)
        else:
            break

    return " ".join(compressed).strip() + "…"


# === Universal prompt builder ===
def build_suno_prompt(*args, mode: str = "full"):
    """
    Universal StudioCore prompt builder.

    Supports both API versions:
      - NEW: build_suno_prompt(style_data: dict, vocals: list, instruments: list, bpm: int, philosophy: str, version: str, mode='full'|'suno')
      - LEGACY: build_suno_prompt(genre: str, style_words: str, vocals: list, instruments: list, bpm: int, philosophy: str, techniques: list, version: str, mode='full'|'suno')
    """

    # Detect call type
    if len(args) >= 6 and isinstance(args[0], dict):
        # --- New API (v5) ---
        style_data, vocals, instruments, bpm, philosophy, version = args[:6]
        s = {
            "genre": style_data.get("genre", "unknown"),
            "key": style_data.get("key", "C# minor"),
            "structure": style_data.get("structure", "intro-verse-chorus-outro"),
            "techniques": style_data.get("techniques", []),
            "visual": style_data.get("visual", ""),
            "narrative": style_data.get("narrative", ""),
            "atmosphere": style_data.get("atmosphere", ""),
        }

    elif len(args) >= 8 and isinstance(args[0], str):
        # --- Legacy API (v4.3) ---
        genre, style_words, vocals, instruments, bpm, philosophy, techniques, version = args[:8]
        s = {
            "genre": genre,
            "key": "C# minor",
            "structure": "intro-verse-chorus-outro",
            "techniques": techniques or [],
            "visual": "",
            "narrative": "",
            "atmosphere": "",
        }
    else:
        raise ValueError(
            "build_suno_prompt: unsupported signature. Use either (style_data, vocals, instruments, bpm, philosophy, version[, mode]) or (genre, style_words, vocals, instruments, bpm, philosophy, techniques, version[, mode])."
        )

    # --- Build full prompt ---
    prompt = (
        f"Genre: {s['genre']} | Key: {s['key']} | BPM: {bpm}\n"
        f"Structure: {s['structure']}\n"
        f"Vocals: {', '.join(vocals)} | Techniques: {', '.join(s.get('techniques', []))}\n"
        f"Instruments: {', '.join(instruments)}\n"
        f"Visual: {s.get('visual','')}\n"
        f"Narrative: {s.get('narrative','')}\n"
        f"Atmosphere: {s.get('atmosphere','')}\n"
        f"Philosophy: {philosophy}\n"
        f"Engine: StudioCore {version} adaptive emotional system"
    ).strip()

    # --- Compress if needed (Suno mode) ---
    if mode == "suno":
        return semantic_compress(prompt, 1000)

    return prompt
