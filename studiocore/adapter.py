def build_suno_prompt(genre: str,
                      style_words: str,
                      voices: list,
                      instruments: list,
                      bpm: int,
                      philosophy: str,
                      techniques: list,
                      version: str) -> str:
    """
    Собирает финальный Suno prompt на основе анализа StudioCore.
    """
    prompt = (
        f"Style: {genre}, {style_words}. "
        f"Vocals: {', '.join(voices)}. "
        f"Instruments: {', '.join(instruments)}. "
        f"Vocal techniques: {', '.join(techniques)}. "
        f"Tempo: {bpm} BPM. "
        f"{philosophy}. "
        f"Engine: StudioCore {version} adaptive emotional system."
    )
    return soft_trim(prompt, 1000)
