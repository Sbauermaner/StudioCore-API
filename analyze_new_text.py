#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Анализ нового текста через StudioCoreV6"""

import json
import sys
from studiocore.core_v6 import StudioCoreV6

def analyze_text(text, preferred_gender="auto"):
    """Анализ текста через StudioCore"""
    print("=" * 80)
    print("АНАЛИЗ ТЕКСТА ЧЕРЕЗ STUDIOCORE")
    print("=" * 80)
    print("\nВыполняется анализ...\n")
    
    try:
        core = StudioCoreV6()
        result = core.analyze(text, preferred_gender=preferred_gender)
        
        if not result.get("ok", True):
            print(f"❌ Ошибка анализа: {result.get('error', 'Unknown error')}")
            return None
        
        print("✅ Анализ выполнен успешно!\n")
        print("=" * 80)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("=" * 80)
        
        # 1. TLP
        print("\n1. 🎯 TLP (Truth / Love / Pain):")
        print("-" * 80)
        tlp = result.get("tlp", {})
        print(f"   Truth: {tlp.get('truth', 0):.3f}")
        print(f"   Love: {tlp.get('love', 0):.3f}")
        print(f"   Pain: {tlp.get('pain', 0):.3f}")
        print(f"   Conscious Frequency: {tlp.get('conscious_frequency', 0):.3f}")
        
        # 2. Эмоции
        print("\n2. 💭 ЭМОЦИОНАЛЬНЫЙ ПРОФИЛЬ:")
        print("-" * 80)
        emotion = result.get("emotion", {})
        emotion_profile = emotion.get("profile", {})
        if emotion_profile:
            sorted_emotions = sorted(emotion_profile.items(), key=lambda x: x[1], reverse=True)
            print("   Топ-7 эмоций:")
            for i, (emotion_name, intensity) in enumerate(sorted_emotions[:7], 1):
                print(f"      {i}. {emotion_name}: {intensity:.3f}")
        
        # 3. BPM
        print("\n3. 🎵 BPM (Темп):")
        print("-" * 80)
        bpm = result.get("bpm", {})
        print(f"   Estimate: {bpm.get('estimate', '—')}")
        if isinstance(bpm, dict):
            flow_estimate = bpm.get("flow_estimate")
            if flow_estimate:
                print(f"   Flow Estimate: {flow_estimate}")
        
        # 4. Жанр и стиль
        print("\n4. 🎨 ЖАНР И СТИЛЬ:")
        print("-" * 80)
        style = result.get("style", {})
        print(f"   Genre: {style.get('genre', '—')}")
        print(f"   Macro Genre: {style.get('macro_genre', '—')}")
        print(f"   Mood: {style.get('mood', '—')}")
        color_wave = style.get("color_wave")
        if color_wave:
            print(f"   Color Wave: {color_wave}")
        
        # 5. Тональность
        print("\n5. 🎹 ТОНАЛЬНОСТЬ:")
        print("-" * 80)
        tonality = result.get("tonality", {})
        tone = result.get("tone", {})
        key = tonality.get("key") or tone.get("key", "—")
        mode = tonality.get("mode") or tone.get("mode", "—")
        print(f"   Key: {key}")
        print(f"   Mode: {mode}")
        if tonality.get('section_keys'):
            section_keys = tonality.get('section_keys', [])
            if section_keys:
                print(f"   Section Keys: {', '.join(str(k) for k in section_keys[:5])}")
        
        # 6. Вокал
        print("\n6. 🎤 ВОКАЛЬНЫЕ ХАРАКТЕРИСТИКИ:")
        print("-" * 80)
        vocal = result.get("vocal", {})
        print(f"   Gender: {vocal.get('gender', '—')}")
        print(f"   Type: {vocal.get('type', '—')}")
        print(f"   Tone: {vocal.get('tone', '—')}")
        print(f"   Style: {vocal.get('style', '—')}")
        techniques = vocal.get("techniques", [])
        if techniques:
            print(f"   Техники: {', '.join(techniques[:5])}")
        section_techniques = vocal.get("section_techniques", [])
        if section_techniques:
            print(f"   Техники по секциям: {', '.join(section_techniques[:5])}")
        
        # 7. Структура
        print("\n7. 📐 СТРУКТУРА:")
        print("-" * 80)
        structure = result.get("structure", {})
        sections = structure.get("sections", [])
        headers = structure.get("headers", [])
        print(f"   Количество секций: {len(sections)}")
        if headers:
            print("   Названия секций:")
            for i, h in enumerate(headers[:10], 1):
                tag = h.get("tag", "?")
                print(f"      {i}. {tag}")
        
        # 8. RDE
        print("\n8. 📊 RDE (Резонанс / Фрактура / Энтропия):")
        print("-" * 80)
        rde = result.get("rde", {})
        print(f"   Resonance: {rde.get('resonance', '—')}")
        print(f"   Fracture: {rde.get('fracture', '—')}")
        print(f"   Entropy: {rde.get('entropy', '—')}")
        
        # 9. Инструменты
        print("\n9. 🎸 ИНСТРУМЕНТЫ:")
        print("-" * 80)
        instrumentation = result.get("instrumentation", {})
        selection = instrumentation.get("selection", {})
        if selection:
            selected = selection.get("selected", [])
            palette = selection.get("palette", [])
            if selected:
                print(f"   Selected: {', '.join(selected[:8])}")
            if palette:
                print(f"   Palette: {', '.join(palette[:8])}")
            rationale = selection.get("rationale", "")
            if rationale:
                print(f"   Rationale: {rationale[:100]}...")
        else:
            print("   Инструменты не определены")
        
        # 10. FANF промпты
        print("\n10. 📝 FANF ПРОМПТЫ:")
        print("-" * 80)
        fanf = result.get("fanf", {})
        style_prompt = fanf.get("style_prompt", "")
        lyrics_prompt = fanf.get("lyrics_prompt", "")
        
        print("   Style Prompt:")
        if style_prompt:
            print(f"      {style_prompt[:250]}...")
        print()
        
        print("   Lyrics Prompt (первые 15 строк):")
        if lyrics_prompt:
            lines = lyrics_prompt.split("\n")
            for line in lines[:15]:
                if line.strip():
                    print(f"      {line[:80]}")
        
        # 11. Диагностика
        print("\n11. 🔍 ДИАГНОСТИКА:")
        print("-" * 80)
        diagnostics = result.get("diagnostics", {})
        tlp_block = diagnostics.get("tlp_block", "")
        rde_block = diagnostics.get("rde_block", "")
        if tlp_block:
            print(f"   {tlp_block}")
        if rde_block:
            print(f"   {rde_block}")
        
        # Сохранение результата
        output_file = "new_text_analysis_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("✅ АНАЛИЗ ЗАВЕРШЕН")
        print(f"💾 Полный результат сохранен в: {output_file}")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Текст передан как аргумент
        text = sys.argv[1]
        preferred_gender = sys.argv[2] if len(sys.argv) > 2 else "auto"
    else:
        # Интерактивный ввод
        print("Введите текст для анализа (или нажмите Enter для использования примера):")
        print("(Для многострочного ввода завершите ввод пустой строкой)")
        print()
        
        lines = []
        while True:
            try:
                line = input()
                if not line.strip() and lines:
                    break
                if line.strip():
                    lines.append(line)
            except EOFError:
                break
        
        if not lines:
            # Пример текста
            text = """В лесу родилась ёлочка,
В лесу она росла,
Зимой и летом стройная,
Зелёная была."""
            print("\nИспользуется пример текста...\n")
        else:
            text = "\n".join(lines)
        
        print("\nУкажите предпочтительный пол вокала (male/female/auto, по умолчанию auto):")
        preferred_gender = input().strip() or "auto"
    
    analyze_text(text, preferred_gender=preferred_gender)

