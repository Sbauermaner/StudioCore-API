import re
from typing import Dict, Any


class StyleMatrix:
    """
    Формирует полное стилевое описание из лирики.
    Работает по принципу самообучающегося ядра — без закреплённых жанров.
    """

    EMO_GROUPS = {
        "soft": ["love", "peace", "joy"],
        "dark": ["sadness", "pain", "fear"],
        "epic": ["anger", "epic"],
    }

    # -------------------------------------------------------
    # 1. Определение тонального профиля (лад)
    # -------------------------------------------------------
    def _tone_profile(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
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

    # -------------------------------------------------------
    # 2. Определение жанра (по структуре текста)
    # -------------------------------------------------------
    def _derive_genre(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        word_count = len(re.findall(r"\b\w+\b", text))
        sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
        avg_sent_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))

        density = min(word_count / 100.0, 10)
        emotional_range = (tlp.get("love", 0) + tlp.get("pain", 0) + tlp.get("truth", 0)) / 3

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

    # -------------------------------------------------------
    # 3. Автоматический подбор тональности (Key)
    # -------------------------------------------------------
    def _derive_key(self, tlp: Dict[str, float], bpm: int) -> str:
        """Подбирает тональность по эмоциям и ритму."""
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)

        # Основной лад
        if p > 0.45:
            mode = "minor"
        elif l > 0.55:
            mode = "major"
        else:
            mode = "modal"

        # Сетка тональностей по доминирующему параметру
        if t > 0.6 and l > 0.5:
            key = "E"
        elif l > 0.7:
            key = "G"
        elif p > 0.6:
            key = "A"
        elif t < 0.3 and l > 0.4:
            key = "D"
        elif p > 0.5 and l < 0.3:
            key = "F"
        elif bpm > 140 and l > 0.5:
            key = "C"
        else:
            key = "C#"

        return f"{key} {mode}"

    # -------------------------------------------------------
    # 4. Формирование визуального слоя
    # -------------------------------------------------------
    def _derive_visual(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        if p > l and p > t:
            return "rain, fog, silhouettes, slow motion"
        elif l > p and l > t:
            return "warm light, faces, sunrise, hands touching"
        elif t > 0.4:
            return "clear sky, horizon, open space"
        else:
            return "shifting colors, abstract movement"

    # -------------------------------------------------------
    # 5. Формирование смысловой дуги
    # -------------------------------------------------------
    def _derive_narrative(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        if tlp.get("pain", 0) > 0.6:
            return "suffering → awakening → transcendence"
        elif tlp.get("love", 0) > 0.6:
            return "loneliness → connection → unity"
        elif tlp.get("truth", 0) > 0.6:
            return "ignorance → revelation → wisdom"
        else:
            return "search → struggle → transformation"

    # -------------------------------------------------------
    # 6. Подбор вокальных техник
    # -------------------------------------------------------
    def _derive_techniques(self, emo: Dict[str, float], tlp: Dict[str, float]) -> list[str]:
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

    # -------------------------------------------------------
    # 7. Атмосфера
    # -------------------------------------------------------
    def _derive_atmosphere(self, emo: Dict[str, float]) -> str:
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

    # -------------------------------------------------------
    # 8. Главный метод
    # -------------------------------------------------------
    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        genre = self._derive_genre(text, emo, tlp)
        style = self._tone_profile(emo, tlp)
        key = self._derive_key(tlp, bpm)
        visual = self._derive_visual(emo, tlp)
        narrative = self._derive_narrative(text, emo, tlp)
        atmosphere = self._derive_atmosphere(emo)
        techniques = self._derive_techniques(emo, tlp)

        return {
            "genre": genre,
            "style": style,
            "key": key,
            "structure": "intro-verse-chorus-outro",
            "visual": visual,
            "narrative": narrative,
            "atmosphere": atmosphere,
            "techniques": techniques,
        }
