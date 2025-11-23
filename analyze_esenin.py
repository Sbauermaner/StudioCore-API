#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Анализ текста Есенина через StudioCoreV6"""

import json
from studiocore.core_v6 import StudioCoreV6

text = """Не жалею, не зову, не плачу,

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

Буйство глаз и половодье чувств.



Я теперь скупее стал в желаньях,

Жизнь моя? иль ты приснилась мне?

Словно я весенней гулкой ранью

Проскакал на розовом коне.



Все мы, все мы в этом мире тленны,

Тихо льется с кленов листьев медь…

Будь же ты вовек благословенно,

Что пришло процвесть и умере"""

print("="*80)
print("АНАЛИЗ ТЕКСТА СЕРГЕЯ ЕСЕНИНА")
print("="*80)
print(f"\nВходной текст:\n{text}\n")
print("Выполняется анализ...\n")

try:
    core = StudioCoreV6()
    result = core.analyze(text)
    
    # Основные выходные данные
    print("="*80)
    print("ОСНОВНЫЕ ВЫХОДНЫЕ ДАННЫЕ")
    print("="*80)
    
    # FANF блок
    fanf = result.get("fanf", {})
    if fanf:
        print("\n📝 FANF OUTPUT:")
        print("-" * 80)
        if fanf.get("style_prompt"):
            print(f"Style Prompt:\n{fanf['style_prompt']}\n")
        if fanf.get("lyrics_prompt"):
            print(f"Lyrics Prompt:\n{fanf['lyrics_prompt']}\n")
        if fanf.get("ui_text"):
            print(f"UI Text (с аннотациями):\n{fanf['ui_text']}\n")
    
    # Style блок
    style = result.get("style", {})
    if style:
        print("\n🎨 STYLE:")
        print("-" * 80)
        print(f"Genre: {style.get('genre', 'N/A')}")
        print(f"BPM: {style.get('bpm', 'N/A')}")
        print(f"Key: {style.get('key', 'N/A')}")
        print(f"Mood: {style.get('mood', 'N/A')}")
        if style.get('color_wave'):
            print(f"Color Wave: {style['color_wave']}")
    
    # Emotion блок
    emotion = result.get("emotion", {})
    if emotion:
        print("\n💭 EMOTION PROFILE:")
        print("-" * 80)
        profile = emotion.get("profile", {})
        if profile:
            print("Топ-5 эмоций:")
            for emo, value in sorted(profile.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {emo}: {value:.3f}")
    
    # TLP блок
    tlp = result.get("tlp", {})
    if tlp:
        print("\n🎯 TLP (Truth, Love, Pain):")
        print("-" * 80)
        print(f"Truth: {tlp.get('truth', 0):.3f}")
        print(f"Love: {tlp.get('love', 0):.3f}")
        print(f"Pain: {tlp.get('pain', 0):.3f}")
        if tlp.get('conscious_frequency'):
            print(f"Conscious Frequency: {tlp['conscious_frequency']:.3f}")
    
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
        headers = structure.get("headers", [])
        if sections:
            print(f"Количество секций: {len(sections)}")
            for i, section in enumerate(sections, 1):
                # Пытаемся получить имя секции из headers
                tag = 'N/A'
                if i <= len(headers) and isinstance(headers[i-1], dict):
                    tag = headers[i-1].get('tag') or headers[i-1].get('label') or headers[i-1].get('name') or 'N/A'
                elif isinstance(section, dict):
                    tag = section.get('tag', 'N/A')
                
                line_count = 0
                if isinstance(section, str):
                    line_count = len(section.split('\n'))
                elif isinstance(section, dict):
                    line_count = section.get('line_count', len(section.get('lines', [])))
                
                print(f"  Секция {i}: {tag} ({line_count} строк)")
    
    # Сохраняем полный результат в JSON
    with open('analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print("✅ Анализ завершен успешно!")
    print("📄 Полный результат сохранен в: analysis_result.json")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Ошибка при анализе: {e}")
    import traceback
    traceback.print_exc()

