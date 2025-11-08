from StudioCore_Complete_v4_3 import StudioCore

class PilgrimInterface:
    def __init__(self):
        self.core = StudioCore()
        self.mode = "pilgrim"

    def set_mode(self, mode: str):
        if mode not in ["auto", "pilgrim", "healing", "dramatic", "neutral"]:
            raise ValueError("Invalid mode")
        self.mode = mode

    def process(self, text: str, gender: str = "auto"):
        result = self.core.analyze(text=text, preferred_gender=gender)
        result_dict = result.__dict__
        result_dict["pilgrim_mode"] = self.mode
        result_dict["timestamp"] = __import__("datetime").datetime.now().isoformat()
        return result_dict