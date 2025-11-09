from typing import Dict, List, Optional, Any

class StyleMatrix:
    """
    Определяет музыкальный жанр, тональность, вокальные техники и стиль аранжировки
    по эмоциям (emo) и философским показателям (tlp).
    """

    # Ключевые слова для явного определения жанра
    GENRE_KEYWORDS = {
        "hip hop": ["hip hop","boom bap","trap","808","bars","эмси","рэп"],
        "rap":     ["rap","рэп","читка","bars","flow"],
        "metal":   ["metal","грор","гроул","growl","blast","scream","скрим"],
        "rock":    ["rock","рок","гитара","риф"],
        "pop":     ["pop","поп","hook","radio","chorus"],
        "folk":    ["folk","фолк","акуст","балада","tagelharpa"],
        "classical":["classical","оркестр","симф","кантата","оратория"],
        "electronic":["edm","electronic","techno","house","trance","dubstep","808","synthwave"],
        "ambient": ["ambient","drone","pad","атмосф"],
        "jazz":    ["jazz","свинг","скэт","blue note","bebop"],
        "blues":   ["blues","блюз","shuffle","12 bar"],
        "orchestral":["orchestral","кино","cinematic","трейлер","score"],
        "reggae":  ["reggae","дагг","ска","offbeat"],
        "country": ["country","банжо","steel","honky tonk"],
        "punk":    ["punk","панк","diy","fast"],
        "indie":   ["indie","инди"]
    }

    def _keyword_genre_boost(self, text: str) -> Optional[str]:
        """Возвращает жанр, если он явно упомянут ключевыми словами в тексте."""
        s = text.lower()
        for g, kws in self.GENRE_KEYWORDS.items():
            if any(kw in s for kw in kws):
                return g
        return None

    def genre(self,
              emo: Dict[str, float],
              tlp: Dict[str, float],
              text: str = "",
              bpm: Optional[int] = None) -> str:
        """
        Выводит жанр на основе эмоций/TLP и (опционально) BPM.
        Приоритет: явные ключевые слова > эвристики по emo/tlp/bpm.
        """
        g_kw = self._keyword_genre_boost(text)
        if g_kw:
            return g_kw

        anger = emo.get("anger", 0.0)
        epic = emo.get("epic", 0.0)
        joy = emo.get("joy", 0.0)
        love = emo.get("love", 0.0)
        peace = emo.get("peace", 0.0)
        sadness = emo.get("sadness", 0.0)

        if anger > 0.30 and epic > 0.20:
            return "metal"
        if joy > 0.30 and love > 0.20:
            return "pop"
        if peace > 0.30 and love > 0.20:
            return "ambient"
        if peace > 0.30 and tlp.get("truth", 0.0) > 0.20:
            return "folk"
        if sadness > 0.30 and tlp.get("truth", 0.0) > 0.20:
            return "classical"

        if bpm is not None:
            if bpm >= 135 and (anger + epic) > 0.40:
                return "punk"
            if bpm <= 80 and sadness > 0.25:
                return "blues"

        return "rock"

    def tonality(self, emo: Dict[str, float]) -> str:
        """
        Оценивает тональность (major/minor/modal) по балансу эмоций.
        """
        pos = emo.get("joy", 0.0) + emo.get("love", 0.0) + emo.get("peace", 0.0)
        neg = emo.get("sadness", 0.0) + emo.get("anger", 0.0) + emo.get("fear", 0.0)

        if pos > neg * 1.3:
            return "major"
        if neg > pos * 1.3:
            return "minor"
        return "modal"

    def techniques(self, emo: Dict[str, float], text: str) -> List[str]:
        """
        Рекомендует вокальные техники по эмоциям и явным упоминаниям в тексте.
        Возвращает до 6 техник без повторов.
        """
        s = text.lower()
        t: List[str] = []

        explicit = {
            "growl": ["growl", "гроул"],
            "scream": ["scream", "скрим", "крик"],
            "belt": ["belt", "бэлт"],
            "falsetto": ["falsetto", "фальцет"],
            "vibrato": ["vibrato", "вибрато"],
            "fry": ["fry", "штробас", "вокальный фрай"],
            "twang": ["twang", "твэнг"],
            "legato": ["legato", "легато"],
            "staccato": ["staccato", "стаккато"],
            "runs": ["runs", "риффы", "пассажи"],
            "yodel": ["yodel", "йодль"],
            "distortion": ["distortion", "дисторшн"],
            "scat": ["scat", "скэт"],
            "sprechstimme": ["sprech", "шпрехштимме"]
        }

        for k, kws in explicit.items():
            if any(kw in s for kw in kws):
                t.append(k)

        if emo.get("anger", 0.0) > 0.30:
            t += ["distortion", "fry", "twang"]
        if emo.get("epic", 0.0) > 0.30:
            t += ["belt", "vibrato"]
        if emo.get("sadness", 0.0) > 0.30:
            t += ["legato", "falsetto"]
        if emo.get("joy", 0.0) > 0.30:
            t += ["runs", "vibrato"]
        if emo.get("peace", 0.0) > 0.30:
            t += ["legato"]

        seen, out = set(), []
        for x in t:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out[:6]

    def recommend(self,
                  emo: Dict[str, float],
                  tlp: Dict[str, float],
                  author_style: Optional[str] = None,
                  sections: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Генерирует краткое стилевое описание/подсказку аранжировки.
        Учитывает author_style, либо выводит из TLP/emo + секции.
        """
        base = None

        if author_style:
            base = author_style.strip()
        else:
            if tlp.get("truth", 0.0) > 0.7 and tlp.get("love", 0.0) > 0.7:
                base = "uplifting cinematic with warm harmonies"
            elif tlp.get("pain", 0.0) > 0.7 and tlp.get("truth", 0.0) > 0.6:
                base = "raw emotional rock with open space"
            elif emo.get("epic", 0.0) > 0.4:
                base = "anthemic arrangement with wide dynamics"
            else:
                base = "healing, clarity, compassionate space"

        tag_hints: List[str] = []
        if sections:
            for s in sections:
                tag = s.get("tag", "")
                if any(k in tag.lower() for k in ["tagelharpa", "throat", "choir", "chant", "blast", "drum"]):
                    tag_hints.append(tag)

        if tag_hints:
            base = f"{base}; hints: " + ", ".join(sorted(set(tag_hints))[:4])

        return base
