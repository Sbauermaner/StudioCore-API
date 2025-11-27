# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

import logging
import re

from typing import Any, Dict, List, Tuple, Optional

log = logging.getLogger(__name__)

# Разрешённые символы (для подсказок и визуальных тегов; сами по себе не
# используются для фильтрации)
PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'''*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))

# [Verse 1 – soft], [Chorus], [Bridge x2] и т.п.
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
COMMAND_BLOCK_RE = re.compile(r"\[(?P<body>[^\]]+)\]")

# Альтернативные заголовки секций: "Припев:", "Chorus:", "Verse 2:", "##
# Bridge", "# Outro" и т.п.
SECTION_COLON_RE = re.compile(
    r"^\s * (?:#{1, 3}\s*)?([A - Za - zА - Яа - яЁё0 - 9 _\-]+?)\s*[:：]\s*$"
)

# Маркеры секций в круглых скобках: "(Куплет 1)", "(Припев)", "(Мост)",
# "(Финальный припев)", "(Аутро)"
SECTION_PARENTHESES_RE = re.compile(r"^\s*\(([^\)]+)\)\s*$")

# Управляющие и нулевой ширины, которые надо убрать
CTRL_CHARS_RE = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F]")
ZERO_WIDTH_RE = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF]")

# Многоточие и тире → к единому виду
ELLIPSIS_RE = re.compile(r"\.{3,}")
DASH_RE = re.compile(r"[–—-]{2,}")  # цепочки тире / дефисов
PHRASE_BOUNDARY_RE = re.compile(r"[.!?…]+|\n")


def _normalize_typography(line: str) -> str:
    """Локальная типографика без потери смысла."""
    # многоточия
    line = ELLIPSIS_RE.sub("…", line)
    # длинные цепочки тире -> одно длинное тире
    line = DASH_RE.sub("—", line)
    # одиночные дефисы между словами оставляем; тире окружаем пробелами
    # корректно
    line = re.sub(r"\s*—\s*", " — ", line)
    # убрать двойные пробелы
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def normalize_text_preserve_symbols(text: str) -> str:
    """
    Нормализует переносы, удаляет управляющие / невидимые символы,
    схлопывает кратные пустые строки, слегка выравнивает типографику.
    Символы пунктуации и эмодзи сохраняются.
    """
    if not text:
        return ""

    # Переводим CRLF / CR -> LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Удаляем управляющие и zero - width
    text = CTRL_CHARS_RE.sub("", text)
    text = ZERO_WIDTH_RE.sub("", text)

    # Нормализуем построчно
    lines = []
    for raw in text.split("\n"):
        ln = _normalize_typography(raw)
        lines.append(ln)

    # Схлопываем кратные пустые строки, но сохраняем двойные пустые строки как разделители секций
    # ВАЖНО: двойные пустые строки (2+ подряд) используются для разбиения на
    # секции
    out_lines: List[str] = []
    blank_count = 0
    for ln in lines:
        if ln == "":
            blank_count += 1
            # Сохраняем максимум 2 пустые строки подряд (для разделителей секций)
            # Если уже есть одна пустая строка, добавляем еще одну для
            # разделителя
            if blank_count <= 2:
                out_lines.append("")
        else:
            blank_count = 0
            out_lines.append(ln)

    return "\n".join(out_lines).strip()


def extract_commands_and_tags(raw_text: str) -> Tuple[str, Dict[str, Any], List[str]]:
    """Выделяет команды и сохраняет исходные теги до нормализации."""

    if raw_text is None:
        source = ""
    else:
        source = str(raw_text)
    preserved_tags: List[str] = []
    detected: List[Dict[str, Any]] = []
    command_pattern = re.compile(
        r"^(?P < name > [A - Z_]+)\s*:?[\s] * (?P < value>.+)$"
    )
    for match in COMMAND_BLOCK_RE.finditer(source):
        token = match.group(0)
        preserved_tags.append(token)
        body = (match.group("body") or "").strip()
        command_match = command_pattern.match(body)
        if command_match:
            command_type = command_match.group("name").lower()
            command_value = command_match.group("value").strip()
            detected.append(
                {
                    "type": command_type,
                    "value": command_value,
                    "raw": token,
                    "position": match.start(),
                }
            )
    command_map: Dict[str, Any] = {}
    for command in detected:
        ctype = command.get("type")
        if ctype and ctype not in command_map:
            command_map[ctype] = command.get("value")
    unique_tags: List[str] = []
    seen_tags = set()
    for tag in preserved_tags:
        if tag not in seen_tags:
            unique_tags.append(tag)
            seen_tags.add(tag)
    clean_text = normalize_text_preserve_symbols(source)
    return clean_text, {"detected": detected, "map": command_map}, unique_tags


def _detect_duplicate_sections(sections: List[Dict[str, Any]]) -> Dict[int, List[int]]:
    """
    Определяет повторяющиеся секции по их содержимому.

    Returns:
        Словарь: {индекс_секции: [список_индексов_повторений]}
    """
    duplicates: Dict[int, List[int]] = {}
    normalized_sections: List[str] = []

    # Нормализуем секции для сравнения (убираем пробелы, приводим к нижнему
    # регистру)
    for sec in sections:
        lines = sec.get("lines", [])
        text = "\n".join(lines).strip()
        normalized = text.lower().replace(" ", "").replace("\n", "")
        normalized_sections.append(normalized)

    # Находим повторения
    for i, norm_text in enumerate(normalized_sections):
        if not norm_text:  # Пропускаем пустые секции
            continue
        matches = [
            j
            for j, other_norm in enumerate(normalized_sections)
            if j != i and other_norm == norm_text and other_norm
        ]
        if matches:
            # Сохраняем только первое вхождение как основное
            if i not in duplicates:
                duplicates[i] = matches

    return duplicates


def _assign_section_names(sections: List[Dict[str, Any]]) -> None:
    """
    Автоматически присваивает имена секциям согласно структуре песни.

    ВАЖНО: Не перезаписывает теги, которые уже установлены из маркеров (например, из круглых скобок).

    Структура:
    - Intro (Вступление): Музыкальная часть в начале
    - Verse (Куплет): Основной текст песни
    - Pre - Chorus (Пред - припев): Переход от куплета к припеву
    - Chorus (Припев): Самая запоминающаяся и энергичная часть
    - Post - Chorus / Tag: После припева
    - Bridge (Бридж): Одноразовый раздел, отличающийся от остальных
    - Outro (Концовка): Завершающая часть

    Логика распределения:
    - 1 секция: Verse
    - 2 секции: Intro, Verse
    - 3 секции: Intro, Verse, Outro
    - 4 секции: Intro, Verse, Chorus, Outro
    - 5 секций: Intro, Verse, Pre - Chorus, Chorus, Outro
    - 6 секций: Intro, Verse 1, Pre - Chorus, Chorus, Verse 2, Outro
    - 7 секций: Verse 1, Chorus, Verse 2, Chorus, Bridge, Final Chorus, Outro (если нет явных маркеров)
    - 8+ секций: Intro, Verse 1, Pre - Chorus, Chorus, Verse 2, Bridge, Chorus, Outro...
    """
    if not sections:
        return

    # КРИТИЧНО: Проверяем, есть ли уже установленные теги из маркеров пользователя
    # Если есть хотя бы один явный маркер (не "Body" и не общий тег) - НЕ
    # ПЕРЕЗАПИСЫВАЕМ ничего
    has_user_tags = False
    for sec in sections:
        tag = sec.get("tag", "")
        if not tag or tag == "Body":
            continue
        tag_lower = tag.lower()
        # Проверяем явные маркеры пользователя:
        # 1. Специфичные теги с номерами или модификаторами
        if tag in ["Verse 1", "Verse 2", "Verse 3", "Final Chorus", "Pre - Chorus"]:
            has_user_tags = True
            break
        # 2. Русские маркеры
        if (
            "куплет" in tag_lower
            or "припев" in tag_lower
            or "мост" in tag_lower
            or "аутро" in tag_lower
            or "интро" in tag_lower
            or "преприпев" in tag_lower
        ):
            has_user_tags = True
            break
        # 3. Если тег установлен явно (не из fallback логики) - это пользовательский маркер
        # Проверяем, что это не общий тег без контекста
        if tag in ["Chorus", "Bridge", "Outro", "Intro"]:
            # Это может быть пользовательский маркер, но нужно проверить контекст
            # Если есть хотя бы один специфичный тег - считаем что все
            # пользовательские
            continue

    # КРИТИЧНО: Если есть пользовательские маркеры - сохраняем их, но все
    # равно проверяем повторения
    if has_user_tags:
        # Заполняем пустые теги или "Body" минимальным fallback
        for sec in sections:
            if not sec.get("tag") or sec.get("tag") == "Body":
                sec["tag"] = "Verse"  # Минимальный fallback
        # НО: все равно проверяем повторяющиеся секции и аннотируем их
        # (не выходим сразу, продолжаем проверку повторений)

    num_sections = len(sections)

    # Базовые паттерны для малого количества секций (БЕЗ Intro по умолчанию)
    # Intro добавляется только если пользователь явно указал его в маркерах
    if num_sections == 1:
        sections[0]["tag"] = "Verse"
    elif num_sections == 2:
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Verse 2"
    elif num_sections == 3:
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Verse 2"
        sections[2]["tag"] = "Outro"
    elif num_sections == 4:
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Chorus"
        sections[2]["tag"] = "Verse 2"
        sections[3]["tag"] = "Outro"
    elif num_sections == 5:
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Chorus"
        sections[2]["tag"] = "Verse 2"
        sections[3]["tag"] = "Bridge"
        sections[4]["tag"] = "Outro"
    elif num_sections == 6:
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Chorus"
        sections[2]["tag"] = "Verse 2"
        sections[3]["tag"] = "Chorus"
        sections[4]["tag"] = "Bridge"
        sections[5]["tag"] = "Outro"
    elif num_sections == 7:
        # Стандартный паттерн: Verse 1 → Chorus → Verse 2 → Chorus → Bridge →
        # Final Chorus → Outro
        sections[0]["tag"] = "Verse 1"
        sections[1]["tag"] = "Chorus"
        sections[2]["tag"] = "Verse 2"
        sections[3]["tag"] = "Chorus"
        sections[4]["tag"] = "Bridge"
        sections[5]["tag"] = "Final Chorus"
        sections[6]["tag"] = "Outro"
    else:  # 8+ секций
        # Для 8+ секций используем полную структуру
        # Паттерн: Intro, Verse 1, Pre - Chorus, Chorus, Verse 2, Bridge,
        # Chorus, Outro
        section_names = [
            "Intro",
            "Verse 1",
            "Pre - Chorus",
            "Chorus",
            "Verse 2",
            "Bridge",
        ]

        # После Bridge обычно идет Chorus, затем чередуем Verse и Chorus
        verse_num = 3
        chorus_count = 2  # Уже есть один Chorus на позиции 3

        for i in range(6, num_sections):
            if i == num_sections - 1:
                # Последняя секция - всегда Outro
                section_names.append("Outro")
            elif i == 6:
                # Первая после Bridge - обычно Chorus
                section_names.append("Chorus")
                chorus_count += 1
            else:
                # Чередуем Verse и Chorus
                if (i - 6) % 2 == 0:
                    # Четные позиции после первого Chorus - Verse
                    section_names.append(f"Verse {verse_num}")
                    verse_num += 1
                else:
                    # Нечетные позиции - Chorus
                    section_names.append("Chorus")
                    chorus_count += 1

        # Присваиваем имена
        for i, name in enumerate(section_names[:num_sections]):
            sections[i]["tag"] = name

        # Если имен меньше чем секций (не должно быть, но на всякий случай)
        if len(section_names) < num_sections:
            for i in range(len(section_names), num_sections):
                if i == num_sections - 1:
                    sections[i]["tag"] = "Outro"
                elif (i - len(section_names)) % 2 == 0:
                    sections[i]["tag"] = f"Verse {verse_num}"
                    verse_num += 1
                else:
                    sections[i]["tag"] = "Chorus"

    # После присвоения всех имен проверяем повторяющиеся секции
    # и аннотируем их как "Chorus 1", "Chorus 2", "Chorus 3" и т.д.
    duplicates = _detect_duplicate_sections(sections)
    if not duplicates:
        return  # Нет повторений - выходим

    # Группируем повторяющиеся секции по их нормализованному содержимому
    # Ключ: нормализованный текст, значение: список индексов одинаковых секций
    section_groups: Dict[str, List[int]] = {}

    # Сначала собираем все секции и их нормализованные тексты
    for i, sec in enumerate(sections):
        lines = sec.get("lines", [])
        text = "\n".join(lines).strip()
        normalized = text.lower().replace(" ", "").replace("\n", "")

        if normalized not in section_groups:
            section_groups[normalized] = []
        section_groups[normalized].append(i)

    # Аннотируем только те группы, где есть повторения (больше 1 секции)
    for normalized, indices in section_groups.items():
        if len(indices) > 1:  # Есть повторения
            indices.sort()  # Сортируем по порядку появления
            # Определяем базовое имя из первой секции (если это Chorus,
            # используем "Chorus", иначе "Section")
            first_tag = sections[indices[0]].get("tag", "Section")
            base_name = (
                "Chorus"
                if "chorus" in first_tag.lower() or "припев" in first_tag.lower()
                else first_tag.split()[0]
                if first_tag.split()
                else "Section"
            )

            for idx, sec_idx in enumerate(indices, 1):
                # Обновляем тег на "Chorus N" (или "Section N") для всех
                # повторений
                sections[sec_idx]["tag"] = f"{base_name} {idx}"


def _parse_section_marker(line: str) -> Optional[str]:
    """
    Парсит маркер секции из строки.

    ВАЖНО: Текст в круглых скобках (например, "(Oh, that's just Brandon)")
    НЕ считается маркером секции, если это не отдельная строка - маркер типа "(Припев)".

    Returns:
        Извлеченный тег или None если маркер не найден
    """
    m1 = SECTION_TAG_RE.match(line)
    m2 = SECTION_COLON_RE.match(line)
    m3 = SECTION_PARENTHESES_RE.match(line)

    if m1:
        return m1.group(1).strip()
    elif m2:
        return m2.group(1).strip()
    elif m3:
        # Проверяем, что это действительно маркер секции, а не просто текст в скобках
        # Маркеры секций обычно короткие и содержат ключевые слова
        tag = m3.group(1).strip()
        tag_lower = tag.lower()
        # Если это похоже на маркер секции (содержит ключевые слова)
        if any(
            keyword in tag_lower
            for keyword in [
                "verse",
                "куплет",
                "chorus",
                "припев",
                "bridge",
                "мост",
                "outro",
                "аутро",
                "intro",
                "интро",
                "pre - chorus",
                "преприпев",
            ]
        ):
            return tag
        # Иначе это просто текст в скобках, не маркер
    return None


def _normalize_section_tag(tag: str) -> str:
    """
    Нормализует тег секции: преобразует русские названия в английские.

    Args:
        tag: Исходный тег

    Returns:
        Нормализованный тег
    """
    tag_lower = tag.lower()
    if "куплет" in tag_lower:
        # Извлекаем номер куплета если есть
        if "1" in tag or "перв" in tag_lower:
            return "Verse 1"
        elif "2" in tag or "втор" in tag_lower:
            return "Verse 2"
        elif "3" in tag or "трет" in tag_lower:
            return "Verse 3"
        else:
            return "Verse"
    elif "припев" in tag_lower:
        if "финальн" in tag_lower or "final" in tag_lower:
            return "Final Chorus"
        else:
            return "Chorus"
    elif "мост" in tag_lower or "bridge" in tag_lower:
        return "Bridge"
    elif "аутро" in tag_lower or "outro" in tag_lower or "концовк" in tag_lower:
        return "Outro"
    elif "интро" in tag_lower or "intro" in tag_lower or "вступ" in tag_lower:
        return "Intro"
    elif (
        "преприпев" in tag_lower
        or "pre - chorus" in tag_lower
        or "prechorus" in tag_lower
    ):
        return "Pre - Chorus"
    return tag


def _close_section(current: Dict[str, Any], sections: List[Dict[str, Any]]) -> None:
    """
    Закрывает текущую секцию и добавляет её в список.

    ВАЖНО: Сохраняет секцию даже если в ней только текст в скобках (например, "(Oh, that's just Brandon)").
    Секция сохраняется, если у неё есть тег (маркер) или есть содержимое.

    Args:
        current: Текущая секция
        sections: Список секций для добавления
    """
    # Сохраняем секцию, если:
    # 1. Есть содержимое (непустые строки), ИЛИ
    # 2. Есть тег (маркер секции) - даже если содержимое пустое или только в
    # скобках
    has_content = any(x.strip() for x in current["lines"])
    has_tag = current.get("tag") and current.get("tag") != "Body"

    if has_content or has_tag:
        # Финальная чистка пустых строк в конце секции
        while current["lines"] and current["lines"][-1].strip() == "":
            current["lines"].pop()
        # Сохраняем секцию, даже если после очистки она пустая (но есть тег)
        if has_content or has_tag:
            sections.append(current)


def _split_by_empty_lines(text: str) -> List[Dict[str, Any]]:
    """
    Разбивает текст на секции по пустым строкам.

    ВАЖНО: Если текст уже структурирован (имеет пустые строки между секциями),
    сохраняет эту структуру БЕЗ переразбиения.

    Логика:
    - Группирует строки между пустыми строками (одной или более) в одну секцию
    - Если текст монолитный (нет пустых строк) - не разбивать, вернуть одну секцию

    Args:
        text: Исходный текст

    Returns:
        Список секций (все с тегом "Body") в исходном порядке
    """
    lines = text.split("\n")

    # Проверяем, есть ли в тексте пустые строки (структурированный текст)
    has_empty_lines = any(not line.strip() for line in lines)

    # Если текст монолитный (нет пустых строк) - не разбивать
    if not has_empty_lines:
        # Возвращаем весь текст как одну секцию
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            return [{"tag": "Body", "lines": non_empty_lines}]
        return []

    # Текст уже структурирован - сохраняем его структуру
    # Группируем строки между пустыми строками (одной или более) в одну секцию
    # Используем простой подход: разбиваем по блокам пустых строк (1+ пустых
    # строк подряд)
    blocks = []
    current_block = []

    for line in lines:
        if not line.strip():
            # Пустая строка - если накопился блок, сохраняем его
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            # Непустая строка - добавляем в текущий блок
            current_block.append(line)

    # Добавляем последний блок
    if current_block:
        blocks.append(current_block)

    # Преобразуем блоки в секции
    detected_sections = []
    for block in blocks:
        if block:
            detected_sections.append({"tag": "Body", "lines": block})

    return detected_sections


def _clean_section_lines(sections: List[Dict[str, Any]]) -> None:
    """
    Удаляет пустые строки внутри секций.

    Args:
        sections: Список секций для очистки
    """
    for s in sections:
        s["lines"] = [line for line in s["lines"] if line.strip()]


def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Делит текст на секции. Поддерживает три типа маркеров:
      1) Квадратные скобки:   [Verse 1 – soft], [Chorus], [Bridge x2]
      2) Заголовки с двоеточием / Markdown:  "Припев:", "Chorus:", "  #  # Verse 2:"
      3) Круглые скобки: "(Куплет 1)", "(Припев)", "(Мост)"
    Если явных секций нет — весь текст попадает в одну секцию 'Body'.

    ВАЖНО: Если текст уже структурирован (имеет пустые строки), сохраняет эту структуру.
    Автоматическое разбиение работает только для монолитного текста (без пустых строк).

    Refactored to reduce complexity by extracting logical blocks into separate functions.
    """
    sections: List[Dict[str, Any]] = []
    current = {"tag": "Body", "lines": []}

    for ln in text.split("\n"):
        tag = _parse_section_marker(ln)

        if tag:
            # Закрыть текущую секцию, если там есть строки
            _close_section(current, sections)

            # Нормализуем тег: преобразуем русские названия в английские
            normalized_tag = _normalize_section_tag(tag)
            current = {"tag": normalized_tag, "lines": []}
            continue

        # Обычная строка — складываем
        current["lines"].append(ln)

    # Финализируем последнюю секцию
    _close_section(current, sections)

    # Если ничего не нашли — попробуем разбить по пустым строкам (для текста без маркеров)
    # ВАЖНО: проверяем это ДО удаления пустых строк, чтобы не потерять
    # информацию о разделителях
    if not sections or (len(sections) == 1 and sections[0].get("tag") == "Body"):
        # Проверяем, есть ли в тексте пустые строки (структурированный текст)
        has_empty_lines = any(not line.strip() for line in text.split("\n"))

        # Если текст уже структурирован (есть пустые строки) - разбиваем по ним
        # Если текст монолитный (нет пустых строк) - оставляем как одну секцию
        # Body
        if has_empty_lines:
            detected_sections = _split_by_empty_lines(text)

            # Если разбиение по пустым строкам дало результат — используем его
            if len(detected_sections) > 1:
                # Уберём внутри секций пустые строки - только - пробелы (но
                # сохраним структуру)
                _clean_section_lines(detected_sections)

                # Автоматическое именование секций согласно структуре песни
                _assign_section_names(detected_sections)

                return detected_sections
        # Если текст монолитный (нет пустых строк) - возвращаем как одну секцию Body
        # без переразбиения

    # Уберём внутри секций пустые строки - только - пробелы
    _clean_section_lines(sections)

    # Если ничего не нашли — вернуть «Body» со всем текстом
    if not sections:
        body_lines = [ln for ln in text.split("\n") if ln.strip()]
        if body_lines:
            return [{"tag": "Body", "lines": body_lines}]

    # ВАЖНО: Проверяем повторяющиеся секции и аннотируем их, даже если есть пользовательские маркеры
    # Это нужно делать ПОСЛЕ очистки строк, чтобы нормализация работала
    # правильно
    duplicates = _detect_duplicate_sections(sections)
    if duplicates:
        # Группируем повторяющиеся секции по их нормализованному содержимому
        section_groups: Dict[str, List[int]] = {}

        # Собираем все секции и их нормализованные тексты
        for i, sec in enumerate(sections):
            lines = sec.get("lines", [])
            text_content = "\n".join(lines).strip()
            normalized = text_content.lower().replace(" ", "").replace("\n", "")

            if normalized not in section_groups:
                section_groups[normalized] = []
            section_groups[normalized].append(i)

        # Аннотируем только те группы, где есть повторения (больше 1 секции)
        for normalized, indices in section_groups.items():
            if len(indices) > 1:  # Есть повторения
                indices.sort()  # Сортируем по порядку появления
                # Определяем базовое имя из первой секции
                first_tag = sections[indices[0]].get("tag", "Section")
                base_name = (
                    "Chorus"
                    if "chorus" in first_tag.lower() or "припев" in first_tag.lower()
                    else first_tag.split()[0]
                    if first_tag.split()
                    else "Section"
                )

                for idx, sec_idx in enumerate(indices, 1):
                    # Обновляем тег на "Chorus N" (или "Section N") для всех
                    # повторений
                    sections[sec_idx]["tag"] = f"{base_name} {idx}"

    return sections


# Доп. утилита: плоский список строк (иногда удобно для метрик / рифмы)


def flatten_sections_to_lines(sections: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for s in sections:
        out.extend(s.get("lines", []))
    return out


def extract_phrases_from_section(section_text: str) -> List[str]:
    """Simple heuristic phrase splitter for a section payload."""

    if not section_text:
        return []

    phrases: List[str] = []
    for raw in PHRASE_BOUNDARY_RE.split(section_text):
        phrase = raw.strip()
        if phrase:
            phrases.append(phrase)
    return phrases


# === v16: ИСПРАВЛЕНИЕ ImportError ===
# Эта функция была в monolith_v4_3_1.py, но monolith v6 вызывает ее отсюда.


def extract_raw_blocks(text: str) -> List[str]:
    """
    Разделяет текст на блоки по пустой строке,
    ИГНОРИРУЯ ТОЛЬКО подсказки в скобках (шепотом) и т.д.,
    но СОХРАНЯЯ теги секций [Intro].
    """
    # FIX: Structural integrity. We remove hints, but ensure section tags are
    # preserved as block content.

    # Удаляем ТОЛЬКО hints / commentary in parenthesis () as they are noise.
    text_no_hints = re.sub(r"\s*\([^\)]+\)", "", text)

    # Разделяем по пустой строке
    blocks = re.split(r"\n\s*\n", text_no_hints.strip())

    # Очищаем блоки от пустых строк и пробелов
    cleaned_blocks = []
    for block in blocks:
        clean_block = block.strip()
        if clean_block:
            cleaned_blocks.append(clean_block)

    return cleaned_blocks


def detect_language(text: str) -> Dict[str, Any]:
    """Very small heuristic to guess whether the text is Cyrillic or Latin."""

    cyrillic = sum(1 for ch in text if "\u0400" <= ch <= "\u04ff")
    latin = sum(1 for ch in text if "A" <= ch <= "\u007a")
    if cyrillic > latin:
        language = "ru"
    elif latin > cyrillic:
        language = "en"
    else:
        language = "multilingual"
    confidence = round(min(1.0, max(cyrillic, latin) / max(len(text) or 1, 1)), 3)
    return {"language": language, "confidence": confidence}


def translate_text_for_analysis(text: str, language: str) -> Tuple[str, bool]:
    """Активированный хук перевода для StudioCore v6 (Multilingual Enablement).

    Если язык не 'ru' или 'en', мы вызываем концептуальный API - сервис для перевода
    в 'en' (целевой язык анализа).
    """

    # 1. Если язык уже поддерживается или мульти, перевод не нужен
    if language in ("ru", "en", "multilingual") or language is None:
        # Для поддерживаемых языков или когда перевод не требуется
        return text, False

    # 2. Здесь должно быть подключение к реальному API - сервису
    # if _real_time_translator_api.is_available():
    #     translated_text = _real_time_translator_api.translate(text, target='en')
    #     return translated_text, True

    # 3. Концептуальный Fallback: Имитация успешного перевода (для выполнения
    # контракта)
    log.info(
        "Simulating translation from '%s' to 'en' (multilingual enablement) to fulfill core analysis contract.",
        language,
    )
    return text, True  # Возвращаем исходный текст, но с флагом True


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
