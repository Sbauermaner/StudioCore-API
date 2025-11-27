#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для анализа текста через StudioCoreV6
Использование: python3 test_analysis.py
"""

import json
import sys
from studiocore.core_v6 import StudioCoreV6


def analyze_text(text: str) -> dict:
    """Анализирует текст и возвращает полный результат."""
    core = StudioCoreV6()
    result = core.analyze(text)
    return result


def print_main_outputs(result: dict):
    """Выводит основные выходные данные в читаемом формате."""
    print("\n" + "=" * 80)
    print("ОСНОВНЫЕ ВЫХОДНЫЕ ДАННЫЕ")
    print("=" * 80)

    # FANF блок
    fanf = result.get("fanf", {})
    if fanf:
        print("\n📝 FANF OUTPUT:")
        print("-" * 80)
        if fanf.get("style_prompt"):
            print(f"Style Prompt: {fanf['style_prompt']}")
        if fanf.get("lyrics_prompt"):
            print(f"Lyrics Prompt: {fanf['lyrics_prompt']}")
        if fanf.get("ui_text"):
            print(f"\nUI Text (с аннотациями):\n{fanf['ui_text']}")
        if fanf.get("full"):
            print(f"\nFull FANF:\n{fanf['full']}")

    # Style блок
    style = result.get("style", {})
    if style:
        print("\n🎨 STYLE:")
        print("-" * 80)
        print(f"Genre: {style.get('genre', 'N/A')}")
        print(f"BPM: {style.get('bpm', 'N/A')}")
        print(f"Key: {style.get('key', 'N/A')}")
        print(f"Mood: {style.get('mood', 'N/A')}")
        if style.get("color_wave"):
            print(f"Color Wave: {style['color_wave']}")

    # Emotion блок
    emotion = result.get("emotion", {})
    if emotion:
        print("\n💭 EMOTION:")
        print("-" * 80)
        profile = emotion.get("profile", {})
        if profile:
            print("Emotion Profile:")
            for emo, value in sorted(profile.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]:
                print(f"  {emo}: {value:.3f}")

    # TLP блок
    tlp = result.get("tlp", {})
    if tlp:
        print("\n🎯 TLP (Truth, Love, Pain):")
        print("-" * 80)
        print(f"Truth: {tlp.get('truth', 0):.3f}")
        print(f"Love: {tlp.get('love', 0):.3f}")
        print(f"Pain: {tlp.get('pain', 0):.3f}")

    # Vocal блок
    vocal = result.get("vocal", {})
    if vocal:
        print("\n🎤 VOCAL:")
        print("-" * 80)
        print(f"Gender: {vocal.get('gender', 'N/A')}")
        print(f"Type: {vocal.get('type', 'N/A')}")
        print(f"Tone: {vocal.get('tone', 'N/A')}")
        print(f"Style: {vocal.get('style', 'N/A')}")

    # Structure блок
    structure = result.get("structure", {})
    if structure:
        print("\n📐 STRUCTURE:")
        print("-" * 80)
        sections = structure.get("sections", [])
        if sections:
            print(f"Количество секций: {len(sections)}")
            for i, section in enumerate(sections[:3], 1):  # Показываем первые 3
                print(
                    f"  Секция {i}: {section.get('tag', 'N/A')} ({section.get('line_count', 0)} строк)"
                )


def print_json_output(result: dict):
    """Выводит полный JSON результат."""
    print("\n" + "=" * 80)
    print("ПОЛНЫЙ JSON РЕЗУЛЬТАТ")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    """Главная функция."""
    if len(sys.argv) > 1:
        # Текст из аргументов командной строки
        text = " ".join(sys.argv[1:])
    else:
        # Пример текста по умолчанию
        text = """[Verse 1]
Я вижу красные розы в глубоком синем море
Сердце бьется, как барабан в ночи
Любовь горит ярким пламенем
Боль пронзает душу острым ножом

[Chorus]
Это правда, что я чувствую
Любовь и боль переплетены
В этом мире нет ничего простого
Только эмоции правят мной"""

    print("=" * 80)
    print("АНАЛИЗ ТЕКСТА ЧЕРЕЗ STUDIOCORE V6")
    print("=" * 80)
    print(f"\nВходной текст:\n{text}\n")

    try:
        # Анализ
        print("Выполняется анализ...")
        result = analyze_text(text)

        # Вывод основных данных
        print_main_outputs(result)

        # Вывод полного JSON (закомментировано по умолчанию)
        # print_json_output(result)

        print("\n" + "=" * 80)
        print("✅ Анализ завершен успешно!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Ошибка при анализе: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
