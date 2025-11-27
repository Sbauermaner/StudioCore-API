#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки текста через StudioCore
"""

from studiocore.core_v6 import StudioCoreV6


def analyze_text(text, preferred_gender="auto"):
    """Анализ текста через StudioCore"""
    print("=" * 80)
    print("АНАЛИЗ ТЕКСТА ЧЕРЕЗ STUDIOCORE")
    print("=" * 80)
    print()

    core = StudioCoreV6()

    try:
        result = core.analyze(text, preferred_gender=preferred_gender)

        # Проверка успешности анализа
        if not result.get("ok", True):
            print(f"❌ Ошибка анализа: {result.get('error', 'Unknown error')}")
            return

        print("✅ Анализ выполнен успешно!")
        print()

        # 1. Структура
        print("1. СТРУКТУРА:")
        structure = result.get("structure", {})
        sections = structure.get("sections", [])
        headers = structure.get("headers", [])
        print(f"   Секций: {len(sections)}")
        if headers:
            print("   Названия секций:")
            for i, h in enumerate(headers[:5]):
                tag = h.get("tag", "?")
                print(f"      {i + 1}. {tag}")
        print()

        # 2. Эмоции
        print("2. ЭМОЦИИ:")
        emotion = result.get("emotion", {})
        emotion_profile = emotion.get("profile", {})
        if emotion_profile:
            dominant = (
                max(emotion_profile.items(), key=lambda x: x[1])[0]
                if emotion_profile
                else None
            )
            intensity = emotion_profile.get(dominant, 0) if dominant else 0
            print(f"   Доминирующая эмоция: {dominant}")
            print(f"   Интенсивность: {intensity:.3f}")
        print()

        # 3. TLP
        print("3. TLP (Truth / Love / Pain):")
        tlp = result.get("tlp", {})
        print(f"   Truth: {tlp.get('truth', 0):.2f}")
        print(f"   Love: {tlp.get('love', 0):.2f}")
        print(f"   Pain: {tlp.get('pain', 0):.2f}")
        print(f"   Conscious Frequency: {tlp.get('conscious_frequency', 0):.3f}")
        print()

        # 4. BPM
        print("4. BPM:")
        bpm = result.get("bpm", {})
        print(f"   Estimate: {bpm.get('estimate', '—')}")
        print()

        # 5. Жанр
        print("5. ЖАНР:")
        style = result.get("style", {})
        genre = style.get("genre", "—")
        macro_genre = style.get("macro_genre", "—")
        mood = style.get("mood", "—")
        print(f"   Genre: {genre}")
        print(f"   Macro Genre: {macro_genre}")
        print(f"   Mood: {mood}")

        # Domain genre
        diagnostics = result.get("diagnostics", {})
        genre_analysis = diagnostics.get("genre_analysis", {})
        domain_genre = genre_analysis.get("domain_genre", "—")
        genre_source = genre_analysis.get("genre_source", "—")
        print(f"   Domain Genre: {domain_genre}")
        print(f"   Genre Source: {genre_source}")
        print()

        # 6. Вокал
        print("6. ВОКАЛ:")
        vocal = result.get("vocal", {})
        gender = vocal.get("gender", "—")
        style_vocal = vocal.get("style", "—")
        section_techniques = vocal.get("section_techniques", [])
        print(f"   Gender: {gender}")
        print(f"   Style: {style_vocal}")
        if section_techniques:
            print(f"   Вокальные техники по секциям: {len(section_techniques)}")
            for i, tech in enumerate(section_techniques[:3]):
                print(f"      Section {i + 1}: {tech}")
        print()

        # 7. FANF
        print("7. FANF ПРОМПТЫ:")
        fanf = result.get("fanf", {})
        style_prompt = fanf.get("style_prompt", "")
        lyrics_prompt = fanf.get("lyrics_prompt", "")
        print(f"   Style Prompt: {len(style_prompt)} символов")
        if style_prompt:
            print(f"      {style_prompt[:100]}...")
        print(f"   Lyrics Prompt: {len(lyrics_prompt)} символов")
        if lyrics_prompt:
            lines = lyrics_prompt.split("\n")
            print("      Первые строки:")
            for line in lines[:3]:
                if line.strip():
                    print(f"      {line[:80]}")
        print()

        # 8. Тональность
        print("8. ТОНАЛЬНОСТЬ:")
        tone = result.get("tone", {})
        key = tone.get("key", "—")
        mode = tone.get("mode", "—")
        print(f"   Key: {key}")
        print(f"   Mode: {mode}")
        print()

        print("=" * 80)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)

        return result

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Пример текста для проверки
    test_text = """Не жалею, не зову, не плачу,
Все пройдет, как с белых яблонь дым.
Увяданья золотом охваченный,
Я не буду больше молодым.

Ты теперь не так уж будешь биться,
Сердце, тронутое холодком,
И страна березового ситца
Не заманит шляться босиком.

Дух бродяжий! ты все реже, реже
Расшевеливаешь пламень уст
О моя утраченная свежесть,
Буйство глаз и половодье чувств."""

    print("Введите текст для анализа (или нажмите Enter для использования примера):")
    user_text = input().strip()

    if not user_text:
        print("\nИспользуется пример текста (Есенин)...\n")
        text = test_text
    else:
        text = user_text

    analyze_text(text, preferred_gender="auto")
