from StudioCore_Complete_v4_3 import analyze_and_style
import json

if __name__ == "__main__":
    sample = """
    [Verse]
    Я сварю себе зелье из грёз,
    Заварю в нём щепотку души.
    Где избавлюсь от пролитых слёз —
    Неизведанный путь, опиши.
    """
    result = analyze_and_style(sample, preferred_vocal="female")
    print("\n🎧 StudioCore v4.3 — Local Test Result:\n")
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))
