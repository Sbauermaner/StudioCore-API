import re
import math
from typing import Dict, Any

class StyleMatrix:
    """
    Dynamically derives 'genre', 'style', 'visual', 'narrative', and 'atmosphere'
    from emotional ratios (Truth × Love × Pain) and linguistic/structural patterns.
    No fixed genres or templates.
    """

    # вспомогательные весовые коэффициенты
    EMO_GROUPS = {
        "soft": ["love", "peace", "joy"],
        "dark": ["sadness", "pain", "fear"],
        "epic": ["anger", "epic"],
    }

    def _tone_profile(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        """Определяет тональность по эмоциональному спектру."""
        dominant = max(emo, key=emo.get)
        cf = tlp.get("conscious_frequency", 0.0)

        if dominant in ("joy", "peace") and cf > 0.3:
            return "majestic major"
        elif dominant in ("sadness", "pain") or tlp.get("pain", 0) > 0.3:
            return "melancholic minor"
        elif dominant in ("anger", "epic") and cf > 0.5:
            return "dramatic harmonic minor"
        else:
            return "neutral modal"

    def _derive_genre(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        """Самостоятельно формирует 'жанр' из структуры речи и эмоциональных волн."""
        word_count = len(re.findall(r"\b\w+\b", text))
        avg_sent_len = sum(len(s.split()) for s in re.split(r"[.!?]", text) if s.strip()) / max(1, len(re.split(r"[.!?]", text)))

        # плотность ритма
        density = min(word_count / 100.0, 10)
        emotional_range = (tlp.get("love", 0) + tlp.get("pain", 0) + tlp.get("truth", 0)) / 3

        # вычисляем жанровый архетип
        if emotional_range > 0.7 and density < 2:
            base = "orchestral poetic"
        elif density > 6 and tlp.get("pain", 0) > 0.4:
            base = "dark rhythmic"
        elif density > 5 and tlp.get("love", 0) > 0.4:
            base = "dynamic emotional"
        elif avg_sent_len > 12:
            base = "cinematic narrative"
        else:
            base = "lyrical adaptive"

        # корректировка по доминирующему чувству
        dominant = max(emo, key=emo.get)
        if dominant == "anger":
            mood = "dramatic"
        elif dominant == "fear":
            mood = "mystic"
        elif dominant == "joy":
            mood = "uplifting"
        elif dominant == "sadness":
            mood = "melancholic"
        elif dominant == "epic":
            mood = "heroic"
        else:
            mood = "reflective"

        return f"{base} {mood}".strip()

    def _derive_visual(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        """Формирует визуальный слой из эмоциональных центров."""
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        if p > l and p > t:
            return "rain, fog, silhouettes, slow motion"
        elif l > p and l > t:
            return "warm light, faces, sunrise, hands touching"
        elif t > 0.4:
            return "clear sky, horizon, open space"
        else:
            return "shifting colors, abstract movement"

    def _derive_narrative(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        """Собирает смысловую дугу — нарратив."""
        if tlp.get("pain", 0) > 0.6:
            return "suffering → awakening → transcendence"
        elif tlp.get("love", 0) > 0.6:
            return "loneliness → connection → unity"
        elif tlp.get("truth", 0) > 0.6:
            return "ignorance → revelation → wisdom"
        else:
            return "search → struggle → transformation"

    def _derive_techniques(self, emo: Dict[str, float], tlp: Dict[str, float]) -> list[str]:
        """Подбирает вокальные техники по эмоциональному диапазону."""
        tech = []
        if emo.get("anger", 0) > 0.4:
            tech += ["belt", "rasp", "grit"]
        if emo.get("sadness", 0) > 0.3 or tlp.get("pain", 0) > 0.4:
            tech += ["vibrato", "soft cry"]
        if emo.get("joy", 0) > 0.3:
            tech += ["falsetto", "bright tone"]
        if emo.get("epic", 0) > 0.4:
            tech += ["choral layering"]
        return tech or ["neutral tone"]

    def _derive_atmosphere(self, emo: Dict[str, float]) -> str:
        """Формирует описание атмосферы."""
        dominant = max(emo, key=emo.get)
        if dominant in ("joy", "peace"):
            return "serene and hopeful"
        elif dominant in ("sadness", "pain"):
            return "introspective and melancholic"
        elif dominant == "anger":
            return "intense and cathartic"
        elif dominant == "epic":
            return "monumental and triumphant"
        else:
            return "mysterious and reflective"

    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        """Главная функция — собирает весь стилевой профиль без шаблонов."""
        genre = self._derive_genre(text, emo, tlp)
        tone = self._tone_profile(emo, tlp)
        visual = self._derive_visual(emo, tlp)
        narrative = self._derive_narrative(text, emo, tlp)
        atmosphere = self._derive_atmosphere(emo)
        techniques = self._derive_techniques(emo, tlp)

        return {
            "genre": genre,
            "style": tone,
            "visual": visual,
            "narrative": narrative,
            "atmosphere": atmosphere,
            "techniques": techniques,
            "structure": "intro-verse-chorus-outro",
            "key": "auto",  # подбирается динамически, не фиксируется
        }
