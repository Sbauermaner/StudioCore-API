class StyleMatrix:
    """Generates structured style logic based on emotional and TLP analysis."""

    def genre(self, emo: dict, tlp: dict, text: str, bpm: int) -> str:
        if emo.get("epic", 0) > 0.3 and tlp["pain"] > 0.4:
            return "symphonic gothic metal"
        if emo.get("peace", 0) > 0.4 and tlp["love"] > 0.5:
            return "ambient spiritual"
        if bpm > 120 and emo.get("anger", 0) > 0.3:
            return "industrial rock"
        if emo.get("sadness", 0) > 0.4:
            return "darkwave ballad"
        if emo.get("joy", 0) > 0.5:
            return "pop electronic"
        return "cinematic alternative"

    def tonality(self, emo: dict) -> str:
        if emo.get("sadness", 0) > 0.4 or emo.get("pain", 0) > 0.4:
            return "minor"
        if emo.get("joy", 0) > 0.5:
            return "major"
        return "C# minor"

    def techniques(self, emo: dict, text: str) -> list:
        out = ["belt", "vibrato"]
        if emo.get("anger", 0) > 0.4:
            out.append("growl")
        if emo.get("sadness", 0) > 0.5:
            out.append("legato")
        if "шёпот" in text or "whisper" in text:
            out.append("whisper")
        return out

    def structure(self, emo: dict, tlp: dict) -> str:
        if emo.get("epic", 0) > 0.5:
            return "intro-verse1-chorus-verse2-bridge-final chorus-outro"
        if emo.get("sadness", 0) > 0.4:
            return "intro-verse1-chorus-verse2-chorus-outro"
        return "intro-verse-chorus-bridge-chorus-outro"

    def visuals(self, emo: dict, tlp: dict) -> dict:
        if tlp["pain"] > 0.6:
            return {
                "visual": "ruined castle under blood moon, spectral knightess, medieval tragedy",
                "narrative": "tragedy → rebirth → transcendence",
                "atmosphere": "misty, cinematic, ethereal darkness"
            }
        if tlp["love"] > 0.6:
            return {
                "visual": "sunrise through clouds, glowing field, unity of souls",
                "narrative": "loneliness → compassion → healing",
                "atmosphere": "warm light, harmonic resonance"
            }
        return {
            "visual": "dreamlike landscape, shifting geometry",
            "narrative": "search → conflict → realization",
            "atmosphere": "abstract, introspective"
        }

    def build(self, emo: dict, tlp: dict, text: str, bpm: int) -> dict:
        genre = self.genre(emo, tlp, text, bpm)
        tone = self.tonality(emo)
        structure = self.structure(emo, tlp)
        tech = self.techniques(emo, text)
        visuals = self.visuals(emo, tlp)
        return {
            "genre": genre,
            "key": tone,
            "structure": structure,
            "techniques": tech,
            "visual": visuals["visual"],
            "narrative": visuals["narrative"],
            "atmosphere": visuals["atmosphere"]
        }
