#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексные тесты для анализа текста через StudioCore

Проверяет:
- Базовый анализ текста
- Различные типы текстов (эмоциональные, нейтральные, эпические)
- Граничные случаи (пустой текст, очень длинный текст)
- Все компоненты результата (emotions, TLP, BPM, key, style, vocal, structure, fanf)
- Проверку на наличие всех полей
- Проверку типов данных
- Проверку валидности значений
"""

import json
import sys
from typing import Dict, Any, Optional
from studiocore.core_v6 import StudioCoreV6


class TextAnalysisTester:
    """Класс для тестирования анализа текста."""

    def __init__(self):
        """Инициализация тестера."""
        self.core = StudioCoreV6()
        self.test_results = []

    def analyze_text(
        self, text: str, preferred_gender: str = "auto"
    ) -> Optional[Dict[str, Any]]:
        """Анализирует текст и возвращает результат."""
        try:
            result = self.core.analyze(text, preferred_gender=preferred_gender)
            return result
        except (ValueError, TypeError, RuntimeError, AttributeError) as e:
            print(f"❌ Ошибка при анализе: {e}")
            import traceback

            traceback.print_exc()
            return None
        except Exception as e:  # noqa: BLE001 - catch-all для тестов
            print(f"❌ Неожиданная ошибка при анализе: {e}")
            import traceback

            traceback.print_exc()
            return None

    def test_basic_analysis(self, text: str) -> bool:
        """Тест базового анализа текста."""
        print("\n" + "=" * 80)
        print("ТЕСТ 1: Базовый анализ текста")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            print("❌ Тест провален: результат анализа пуст")
            return False

        # Проверка основных полей
        required_fields = ["emotions", "bpm", "key", "structure", "style"]
        missing_fields = [field for field in required_fields if field not in result]

        if missing_fields:
            print(f"❌ Тест провален: отсутствуют поля: {missing_fields}")
            return False

        print("✅ Базовый анализ: все основные поля присутствуют")
        return True

    def test_emotions(self, text: str) -> bool:
        """Тест анализа эмоций."""
        print("\n" + "=" * 80)
        print("ТЕСТ 2: Анализ эмоций")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        emotions = result.get("emotions", {})
        if not emotions:
            print("❌ Тест провален: emotions отсутствует или пуст")
            return False

        # Проверка структуры emotions
        profile = emotions.get("profile", {})
        dominant = emotions.get("dominant")

        if not profile and not dominant:
            print("⚠️  Предупреждение: emotions не содержит profile или dominant")
        else:
            print(f"✅ Emotions: dominant = {dominant}")
            if profile:
                top_emotions = sorted(
                    profile.items(), key=lambda x: x[1], reverse=True
                )[:3]
                print(f"   Top emotions: {top_emotions}")

        return True

    def test_tlp(self, text: str) -> bool:
        """Тест анализа TLP (Truth, Love, Pain)."""
        print("\n" + "=" * 80)
        print("ТЕСТ 3: Анализ TLP")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        tlp = result.get("tlp", {})
        if not tlp:
            print("⚠️  Предупреждение: tlp отсутствует (известная проблема)")
            print("   TLP не рассчитывается в monolith_v4_3_1.py:536")
            return False

        truth = tlp.get("truth", 0)
        love = tlp.get("love", 0)
        pain = tlp.get("pain", 0)
        cf = tlp.get("conscious_frequency", 0)

        print(f"✅ TLP: Truth={truth:.3f}, Love={love:.3f}, Pain={pain:.3f}")
        print(f"   Conscious Frequency: {cf:.3f}")

        return True

    def test_rhythm_bpm(self, text: str) -> bool:
        """Тест анализа ритма и BPM."""
        print("\n" + "=" * 80)
        print("ТЕСТ 4: Анализ ритма и BPM")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        bpm = result.get("bpm")
        if not bpm:
            print("❌ Тест провален: bpm отсутствует")
            return False

        # BPM может быть int или dict
        if isinstance(bpm, dict):
            estimate = bpm.get("estimate")
            global_bpm = bpm.get("global_bpm")
            print(f"✅ BPM (dict): estimate={estimate}, global={global_bpm}")
        elif isinstance(bpm, (int, float)):
            print(f"✅ BPM (число): {bpm}")
        else:
            print(f"⚠️  BPM имеет неожиданный тип: {type(bpm)}")

        return True

    def test_tone_key(self, text: str) -> bool:
        """Тест анализа тональности и ключа."""
        print("\n" + "=" * 80)
        print("ТЕСТ 5: Анализ тональности и ключа")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        key = result.get("key")
        tone = result.get("tone", {})

        if key:
            print(f"✅ Key: {key}")
        else:
            print("⚠️  Key отсутствует или None")

        if tone:
            tone_key = tone.get("key")
            tone_mode = tone.get("mode")
            print(f"✅ Tone: key={tone_key}, mode={tone_mode}")
        else:
            print("⚠️  Tone отсутствует")

        return True

    def test_style_genre(self, text: str) -> bool:
        """Тест анализа стиля и жанра."""
        print("\n" + "=" * 80)
        print("ТЕСТ 6: Анализ стиля и жанра")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        style = result.get("style", {})
        if not style:
            print("❌ Тест провален: style отсутствует")
            return False

        genre = style.get("genre")
        style_type = style.get("style")
        mood = style.get("mood")
        visual = style.get("visual")
        narrative = style.get("narrative")

        print(f"✅ Style: genre={genre}, style={style_type}")
        print(f"   Mood: {mood}")
        print(f"   Visual: {visual}")
        print(f"   Narrative: {narrative}")

        # Проверка на FALLBACK значения
        if genre == "cinematic narrative" and style_type == "cinematic narrative":
            print("⚠️  Предупреждение: используются FALLBACK значения")
            print("   Style.build() не вызывается в monolith_v4_3_1.py:556-565")

        return True

    def test_structure(self, text: str) -> bool:
        """Тест анализа структуры."""
        print("\n" + "=" * 80)
        print("ТЕСТ 7: Анализ структуры")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        structure = result.get("structure", {})
        if not structure:
            print("❌ Тест провален: structure отсутствует")
            return False

        sections = structure.get("sections", [])
        section_count = structure.get("section_count", 0)
        layout = structure.get("layout")

        print(f"✅ Structure: {section_count} секций")
        print(f"   Layout: {layout}")

        if sections:
            print(f"   Первые секции:")
            for i, section in enumerate(sections[:3], 1):
                if isinstance(section, str):
                    print(f"      {i}. {section[:50]}...")
                elif isinstance(section, dict):
                    tag = section.get("tag", "N/A")
                    print(f"      {i}. {tag}")

        return True

    def test_vocal(self, text: str) -> bool:
        """Тест анализа вокала."""
        print("\n" + "=" * 80)
        print("ТЕСТ 8: Анализ вокала")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        vocal = result.get("vocal", {})
        if not vocal:
            print("⚠️  Предупреждение: vocal отсутствует")
            print("   Vocal allocator не вызывается в monolith_v4_3_1.py:248")
            return False

        gender = vocal.get("gender")
        vocal_type = vocal.get("type")
        style_vocal = vocal.get("style")

        print(f"✅ Vocal: gender={gender}, type={vocal_type}, style={style_vocal}")

        return True

    def test_fanf(self, text: str) -> bool:
        """Тест FANF аннотаций."""
        print("\n" + "=" * 80)
        print("ТЕСТ 9: FANF аннотации")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        fanf = result.get("fanf", {})
        if not fanf:
            print("⚠️  Предупреждение: fanf отсутствует")
            print("   FANF аннотации не генерируются")
            return False

        style_prompt = fanf.get("style_prompt")
        lyrics_prompt = fanf.get("lyrics_prompt")
        ui_text = fanf.get("ui_text")
        full_fanf = fanf.get("full")

        print(f"✅ FANF:")
        print(f"   Style Prompt: {len(style_prompt) if style_prompt else 0} символов")
        print(f"   Lyrics Prompt: {len(lyrics_prompt) if lyrics_prompt else 0} символов")
        print(f"   UI Text: {len(ui_text) if ui_text else 0} символов")
        print(f"   Full FANF: {len(full_fanf) if full_fanf else 0} символов")

        return True

    def test_color(self, text: str) -> bool:
        """Тест анализа цветов."""
        print("\n" + "=" * 80)
        print("ТЕСТ 10: Анализ цветов")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        style = result.get("style", {})
        color_wave = style.get("color_wave")

        if not color_wave:
            print("⚠️  Предупреждение: color_wave отсутствует")
            print("   Color resolution не вызывается")
            return False

        print(f"✅ Color Wave: {color_wave}")

        return True

    def test_rde(self, text: str) -> bool:
        """Тест анализа RDE (Resonance, Fracture, Entropy)."""
        print("\n" + "=" * 80)
        print("ТЕСТ 11: Анализ RDE")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        rde = result.get("rde", {})
        if not rde:
            print("⚠️  Предупреждение: rde отсутствует")
            print("   RDE анализ не выполняется")
            return False

        resonance = rde.get("resonance", 0)
        fracture = rde.get("fracture", 0)
        entropy = rde.get("entropy", 0)

        print(f"✅ RDE: Resonance={resonance:.3f}, Fracture={fracture:.3f}, Entropy={entropy:.3f}")

        return True

    def test_integrity(self, text: str) -> bool:
        """Тест integrity сканирования."""
        print("\n" + "=" * 80)
        print("ТЕСТ 12: Integrity сканирование")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        integrity = result.get("integrity", {})
        if not integrity:
            print("⚠️  Предупреждение: integrity отсутствует")
            print("   Integrity scan не вызывается в monolith_v4_3_1.py:230")
            return False

        print(f"✅ Integrity: {integrity}")

        return True

    def test_edge_cases(self) -> bool:
        """Тест граничных случаев."""
        print("\n" + "=" * 80)
        print("ТЕСТ 13: Граничные случаи")
        print("=" * 80)

        test_cases = [
            ("Пустой текст", ""),
            ("Очень короткий текст", "Привет"),
            ("Текст с эмодзи", "❤️ 💔 🔥 😭"),
            ("Текст со специальными символами", "!!! ??? ... ---"),
            ("Текст с BPM header", "[BPM: 120]\nТекст песни"),
            ("Текст с секциями", "[Verse]\nСтрока 1\n[Chorus]\nСтрока 2"),
        ]

        all_passed = True
        for name, text in test_cases:
            print(f"\n   Тест: {name}")
            result = self.analyze_text(text)
            if result:
                print(f"   ✅ {name}: анализ выполнен")
            else:
                print(f"   ❌ {name}: анализ провален")
                all_passed = False

        return all_passed

    def test_different_text_types(self) -> bool:
        """Тест различных типов текстов."""
        print("\n" + "=" * 80)
        print("ТЕСТ 14: Различные типы текстов")
        print("=" * 80)

        test_texts = {
            "Эмоциональный (любовь)": """Я вижу красные розы в глубоком синем море
Сердце бьется, как барабан в ночи
Любовь горит ярким пламенем""",
            "Эмоциональный (боль)": """Боль пронзает душу острым ножом
Слезы текут рекой по щекам
Сердце разбито на тысячи осколков""",
            "Эпический": """В битве за свободу мы стоим
Мечи сверкают в лучах солнца
Победа близка, мы не сдадимся""",
            "Нейтральный": """Сегодня обычный день
Ничего особенного не происходит
Все идет своим чередом""",
            "Русский текст": """Не жалею, не зову, не плачу,
Все пройдет, как с белых яблонь дым.
Увяданья золотом охваченный,
Я не буду больше молодым.""",
        }

        all_passed = True
        for name, text in test_texts.items():
            print(f"\n   Тест: {name}")
            result = self.analyze_text(text)
            if result:
                emotions = result.get("emotions", {})
                dominant = emotions.get("dominant", "N/A")
                bpm = result.get("bpm")
                if isinstance(bpm, dict):
                    bpm_val = bpm.get("estimate", "N/A")
                else:
                    bpm_val = bpm
                print(f"   ✅ {name}: dominant={dominant}, bpm={bpm_val}")
            else:
                print(f"   ❌ {name}: анализ провален")
                all_passed = False

        return all_passed

    def test_data_types(self, text: str) -> bool:
        """Тест типов данных в результате."""
        print("\n" + "=" * 80)
        print("ТЕСТ 15: Типы данных")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        # Проверка типов
        checks = [
            ("emotions", dict),
            ("bpm", (int, float, dict)),
            ("key", str),
            ("structure", dict),
            ("style", dict),
        ]

        all_passed = True
        for field, expected_type in checks:
            value = result.get(field)
            if value is None:
                print(f"⚠️  {field}: None (может быть допустимо)")
                continue

            if not isinstance(value, expected_type):
                print(f"❌ {field}: ожидался {expected_type}, получен {type(value)}")
                all_passed = False
            else:
                print(f"✅ {field}: тип корректен ({type(value).__name__})")

        return all_passed

    def test_json_serialization(self, text: str) -> bool:
        """Тест сериализации в JSON."""
        print("\n" + "=" * 80)
        print("ТЕСТ 16: JSON сериализация")
        print("=" * 80)

        result = self.analyze_text(text)
        if not result:
            return False

        try:
            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            print(f"✅ JSON сериализация успешна ({len(json_str)} символов)")

            # Проверка десериализации
            json.loads(json_str)
            print("✅ JSON десериализация успешна")

            return True
        except (TypeError, ValueError) as e:
            print(f"❌ JSON сериализация провалена: {e}")
            return False

    def run_all_tests(self, text: str) -> Dict[str, bool]:
        """Запускает все тесты."""
        print("\n" + "=" * 80)
        print("ЗАПУСК ВСЕХ ТЕСТОВ АНАЛИЗА ТЕКСТА")
        print("=" * 80)
        print(f"\nТестовый текст:\n{text}\n")

        tests = [
            ("Базовый анализ", self.test_basic_analysis),
            ("Эмоции", self.test_emotions),
            ("TLP", self.test_tlp),
            ("Ритм и BPM", self.test_rhythm_bpm),
            ("Тональность и ключ", self.test_tone_key),
            ("Стиль и жанр", self.test_style_genre),
            ("Структура", self.test_structure),
            ("Вокал", self.test_vocal),
            ("FANF", self.test_fanf),
            ("Цвета", self.test_color),
            ("RDE", self.test_rde),
            ("Integrity", self.test_integrity),
            ("Граничные случаи", lambda t: self.test_edge_cases()),
            ("Различные типы текстов", lambda t: self.test_different_text_types()),
            ("Типы данных", self.test_data_types),
            ("JSON сериализация", self.test_json_serialization),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                if test_name in ["Граничные случаи", "Различные типы текстов"]:
                    result = test_func(text)
                else:
                    result = test_func(text)
                results[test_name] = result
            except (ValueError, TypeError, RuntimeError, AttributeError, KeyError) as e:
                print(f"❌ Ошибка в тесте '{test_name}': {e}")
                import traceback

                traceback.print_exc()
                results[test_name] = False
            except Exception as e:  # noqa: BLE001 - catch-all для тестов
                print(f"❌ Неожиданная ошибка в тесте '{test_name}': {e}")
                import traceback

                traceback.print_exc()
                results[test_name] = False

        return results

    def print_summary(self, results: Dict[str, bool]):
        """Выводит сводку результатов тестов."""
        print("\n" + "=" * 80)
        print("СВОДКА РЕЗУЛЬТАТОВ ТЕСТОВ")
        print("=" * 80)

        total = len(results)
        passed = sum(1 for v in results.values() if v)
        failed = total - passed

        print(f"\nВсего тестов: {total}")
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {failed}")
        print(f"Процент успеха: {passed/total*100:.1f}%")

        print("\nДетали:")
        for test_name, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")

        print("\n" + "=" * 80)


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

    tester = TextAnalysisTester()
    results = tester.run_all_tests(text)
    tester.print_summary(results)

    # Возврат кода выхода
    failed_count = sum(1 for v in results.values() if not v)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
