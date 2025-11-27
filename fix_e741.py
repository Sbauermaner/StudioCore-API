#!/usr/bin/env python3
"""Исправляет E741 (ambiguous variable name 'l')."""

import re
import os


def fix_e741(filepath):
    """Заменяет переменную 'l' на более понятное имя."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for i, line in enumerate(lines):
            # Ищем паттерны типа: for l in, l =, if l, и т.д.
            # Но не трогаем строки, где 'l' часть слова или строки

            # Паттерн: for l in, for l, in
            if re.search(r"\bfor\s+l\s+in\b", line):
                # Пытаемся понять контекст
                if "line" in line.lower() or "lines" in line.lower():
                    new_line = line.replace(" for l in ", " for line in ")
                    new_line = new_line.replace(" for l,", " for line,")
                    new_line = new_line.replace("(l ", "(line ")
                    new_line = new_line.replace(", l)", ", line)")
                    new_line = new_line.replace(" l ", " line ")
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue
                elif "list" in line.lower():
                    new_line = line.replace(" for l in ", " for lst in ")
                    new_line = new_line.replace("(l ", "(lst ")
                    new_line = new_line.replace(", l)", ", lst)")
                    new_line = new_line.replace(" l ", " lst ")
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue
                else:
                    # По умолчанию используем 'item'
                    new_line = line.replace(" for l in ", " for item in ")
                    new_line = new_line.replace("(l ", "(item ")
                    new_line = new_line.replace(", l)", ", item)")
                    new_line = new_line.replace(" l ", " item ")
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue

            # Паттерн: l = (присваивание)
            if re.search(r"^\s+l\s*=", line) or re.search(r"[,\s]l\s*=", line):
                # Проверяем контекст предыдущих строк
                context = " ".join(lines[max(0, i - 2) : i + 1]).lower()
                if "line" in context or "lines" in context:
                    new_line = re.sub(r"\bl\s*=", "line =", line)
                    new_line = re.sub(r"\(l\b", "(line", new_line)
                    new_line = re.sub(r",\s*l\b", ", line", new_line)
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue
                elif "list" in context:
                    new_line = re.sub(r"\bl\s*=", "lst =", line)
                    new_line = re.sub(r"\(l\b", "(lst", new_line)
                    new_line = re.sub(r",\s*l\b", ", lst", new_line)
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue
                else:
                    new_line = re.sub(r"\bl\s*=", "item =", line)
                    new_line = re.sub(r"\(l\b", "(item", new_line)
                    new_line = re.sub(r",\s*l\b", ", item", new_line)
                    if new_line != line:
                        changed = True
                        new_lines.append(new_line)
                        continue

            # Паттерн: использование l в выражениях (len(l), l[0], и т.д.)
            # Заменяем только если это не часть слова
            if re.search(r"\bl\b", line) and not re.search(r"\b[a-z]*l[a-z]*\b", line):
                # Более консервативный подход - заменяем только явные случаи
                if (
                    re.search(r"\blen\(l\)", line)
                    or re.search(r"\bl\[", line)
                    or re.search(r"\bl\.", line)
                ):
                    context = " ".join(lines[max(0, i - 2) : i + 1]).lower()
                    if "line" in context:
                        new_line = re.sub(r"\blen\(l\)", "len(line)", line)
                        new_line = re.sub(r"\bl\[", "line[", new_line)
                        new_line = re.sub(r"\bl\.", "line.", new_line)
                        new_line = re.sub(r"\(l\)", "(line)", new_line)
                        new_line = re.sub(r",\s*l\b", ", line", new_line)
                        if new_line != line:
                            changed = True
                            new_lines.append(new_line)
                            continue

            new_lines.append(line)

        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        return False


def main():
    files = [
        "app.py",
        "studiocore/emotion_profile.py",
        "studiocore/frequency.py",
        "studiocore/integrity.py",
        "studiocore/multimodal_emotion_matrix.py",
        "studiocore/rde_engine.py",
        "studiocore/rhythm.py",
        "studiocore/text_utils.py",
    ]

    fixed = 0
    for f in files:
        if os.path.exists(f):
            if fix_e741(f):
                fixed += 1
                print(f"✅ Исправлен: {f}")

    print(f"\nИсправлено файлов: {fixed}/{len(files)}")


if __name__ == "__main__":
    main()
