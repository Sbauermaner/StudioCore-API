from StudioCore_Complete_v4 import StudioCore, PipelineResult

class PilgrimInterface:
    """
    Pilgrim Layer связывает StudioCore и внешний API.
    Его задача — обернуть анализ ядра и подготовить данные для вывода
    в удобной форме (plain text, json, или UI).
    """

    def __init__(self):
        self.core = StudioCore()

    def process_lyrics(self, lyrics: str, gender: str = "auto", author_style: str = None) -> dict:
        """Запуск основного анализа лирики"""
        result: PipelineResult = self.core.analyze(
            lyrics=lyrics,
            prefer_gender=gender,
            author_style=author_style
        )

        # Подготовка итогового отчёта
        return {
            "genre": result.genre,
            "bpm": result.bpm,
            "tonality": result.tonality,
            "vocals": result.vocals,
            "instruments": result.instruments,
            "prompt": result.prompt,
            "skeleton_text": result.skeleton_text,
            "vocal_profile": result.vocal_profile,
            "integrity": result.integrity,
            "resonance": result.resonance,
            "tonesync": result.tonesync,
            "truth_love_pain": result.tlp,
            "emotions": result.emotions
        }

    def as_text(self, data: dict) -> str:
        """Формирует человекочитаемый ответ (для text/plain вывода)"""
        lines = [
            f"🎼 Genre: {data['genre']}",
            f"🎚 BPM: {data['bpm']}",
            f"🎵 Tonality: {data['tonality']}",
            "",
            "🧩 Vocal Profile:",
            f"  Type: {data['vocal_profile'].get('type')}",
            f"  Register: {data['vocal_profile'].get('register')}",
            f"  Phonation: {data['vocal_profile'].get('phonation')}",
            f"  Techniques: {', '.join(data['vocal_profile'].get('techniques', []))}",
            "",
            "📝 Lyric Skeleton:",
            data['skeleton_text'],
            "",
            "🎧 Style Prompt:",
            data['prompt']
        ]
        return "\n".join(lines)