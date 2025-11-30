import json
import random
from pathlib import Path
from typing import List, Dict

class InstrumentEngine:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "instruments.json"
        self.db = self._load_db()
        
    def _load_db(self) -> Dict[str, List[str]]:
        if not self.db_path.exists():
            return {"synths": ["Basic Synth"], "orchestral": ["Piano"], "drums": ["Drum Kit"]}
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"synths": ["Fallback Synth"]}

    def select_instruments(self, genre_profile: str, energy: float, mood: str) -> List[str]:
        selection = []
        
        # Основные инструменты по энергии
        if energy > 0.6:
            selection.append(random.choice(self.db.get("drums", ["Drums"])))
            if "Rock" in genre_profile or "Metal" in genre_profile:
                selection.append(random.choice(self.db.get("guitars", ["Distorted Guitar"])))
                # Добавляем больше гитар для рока/метала
                if len(selection) < 10:
                    selection.append(random.choice(self.db.get("guitars", ["Distorted Guitar"])))
            else:
                selection.append(random.choice(self.db.get("synths", ["Bass Synth"])))
        else:
            selection.append(random.choice(self.db.get("orchestral", ["Piano"])))
        
        # Атмосферные инструменты по настроению
        if "Dark" in mood or "Mystic" in mood or "Eerie" in mood:
            selection.append(random.choice(self.db.get("atmosphere", ["Pad"])))
            if len(selection) < 10:
                selection.append(random.choice(self.db.get("atmosphere", ["Pad"])))
        elif "Ethnic" in genre_profile or "Folk" in genre_profile:
            selection.append(random.choice(self.db.get("ethnic", ["Flute"])))
            if len(selection) < 10:
                selection.append(random.choice(self.db.get("ethnic", ["Flute"])))
        
        # Дополнительные инструменты по жанру и энергии
        if energy > 0.4:
            if "Electronic" in genre_profile or "Cyber" in genre_profile:
                selection.append(random.choice(self.db.get("synths", ["Lead Synth"])))
                # Добавляем больше синтезаторов для электроники
                while len(selection) < 10:
                    synth = random.choice(self.db.get("synths", ["Synth"]))
                    if synth not in selection:
                        selection.append(synth)
            elif "Orchestral" in genre_profile:
                selection.append(random.choice(self.db.get("orchestral", ["Violin"])))
                # Добавляем больше оркестровых инструментов
                while len(selection) < 10:
                    orch = random.choice(self.db.get("orchestral", ["Strings"]))
                    if orch not in selection:
                        selection.append(orch)
            else:
                selection.append(random.choice(self.db.get("guitars", ["Acoustic Guitar"])))
                # Добавляем больше гитар для других жанров
                while len(selection) < 10:
                    guitar = random.choice(self.db.get("guitars", ["Guitar"]))
                    if guitar not in selection:
                        selection.append(guitar)
        
        # Дополняем до 10 инструментов из разных категорий
        categories = ["synths", "orchestral", "guitars", "ethnic", "drums", "atmosphere"]
        while len(selection) < 10:
            category = random.choice(categories)
            if category in self.db and self.db[category]:
                instrument = random.choice(self.db[category])
                if instrument not in selection:
                    selection.append(instrument)
            # Защита от бесконечного цикла
            if len(selection) >= 10 or all(len(self.db.get(cat, [])) == 0 for cat in categories):
                break
        
        return list(set(selection))[:10]
