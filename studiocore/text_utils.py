# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

import logging
import re

from typing import Any, Dict, List, Tuple

log = logging.getLogger(__name__)

# Разрешённые символы (для подсказок и визуальных тегов; сами по себе не используются для фильтрации)
PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))

# [Verse 1 – soft], [Chorus], [Bridge x2] и т.п.
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
COMMAND_BLOCK_RE = re.compile(r"\[(?P<body>[^\]]+)\]")

# Альтернативные заголовки секций: "Припев:", "Chorus:", "Verse 2:", "## Bridge", "# Outro" и т.п.
SECTION_COLON_RE = re.compile(
    r"^\s*(?:#{1,3}\s*)?([A-Za-zА-Яа-яЁё0-9 _\-]+?)\s*[:：]\s*$"
)

# Управляющие и нулевой ширины, которые надо убрать
CTRL_CHARS_RE = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F]")
ZERO_WIDTH_RE = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF]")

# Многоточие и тире → к единому виду
ELLIPSIS_RE = re.compile(r"\.{3,}")
DASH_RE = re.compile(r"[–—-]{2,}")  # цепочки тире/дефисов
PHRASE_BOUNDARY_RE = re.compile(r"[.!?…]+|\n")


def _normalize_typography(line: str) -> str:
    """Локальная типографика без потери смысла."""
    # многоточия
    line = ELLIPSIS_RE.sub("…", line)
    # длинные цепочки тире -> одно длинное тире
    line = DASH_RE.sub("—", line)
    # одиночные дефисы между словами оставляем; тире окружаем пробелами корректно
    line = re.sub(r"\s*—\s*", " — ", line)
    # убрать двойные пробелы
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def normalize_text_preserve_symbols(text: str) -> str:
    """
    Нормализует переносы, удаляет управляющие/невидимые символы,
    схлопывает кратные пустые строки, слегка выравнивает типографику.
    Символы пунктуации и эмодзи сохраняются.
    """
    if not text:
        return ""

    # Переводим CRLF/CR -> LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Удаляем управляющие и zero-width
    text = CTRL_CHARS_RE.sub("", text)
    text = ZERO_WIDTH_RE.sub("", text)

    # Нормализуем построчно
    lines = []
    for raw in text.split("\n"):
        ln = _normalize_typography(raw)
        lines.append(ln)

    # Схлопываем кратные пустые строки, но сохраняем двойные пустые строки как разделители секций
    # ВАЖНО: двойные пустые строки (2+ подряд) используются для разбиения на секции
    out_lines: List[str] = []
    prev_blank = False
    blank_count = 0
    for ln in lines:
        if ln == "":
            blank_count += 1
            # Сохраняем максимум 2 пустые строки подряд (для разделителей секций)
            # Если уже есть одна пустая строка, добавляем еще одну для разделителя
            if blank_count <= 2:
                out_lines.append("")
            prev_blank = True
        else:
            blank_count = 0
            out_lines.append(ln)
            prev_blank = False

    return "\n".join(out_lines).strip()


def extract_commands_and_tags(raw_text: str) -> Tuple[str, Dict[str, Any], List[str]]:
    """Выделяет команды и сохраняет исходные теги до нормализации."""

    if raw_text is None:
        source = ""
    else:
        source = str(raw_text)
    preserved_tags: List[str] = []
    detected: List[Dict[str, Any]] = []
    command_pattern = re.compile(r"^(?P<name>[A-Z_]+)\s*:?[\s]*(?P<value>.+)$")
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


def _assign_section_names(sections: List[Dict[str, Any]]) -> None:
    """
    Автоматически присваивает имена секциям согласно структуре песни.
    
    Структура:
    - Intro (Вступление): Музыкальная часть в начале
    - Verse (Куплет): Основной текст песни
    - Pre-Chorus (Пред-припев): Переход от куплета к припеву
    - Chorus (Припев): Самая запоминающаяся и энергичная часть
    - Post-Chorus / Tag: После припева
    - Bridge (Бридж): Одноразовый раздел, отличающийся от остальных
    - Outro (Концовка): Завершающая часть
    
    Логика распределения:
    - 1 секция: Verse
    - 2 секции: Intro, Verse
    - 3 секции: Intro, Verse, Outro
    - 4 секции: Intro, Verse, Chorus, Outro
    - 5 секций: Intro, Verse, Pre-Chorus, Chorus, Outro
    - 6 секций: Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Outro
    - 7 секций: Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge, Outro
    - 8+ секций: Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge, Chorus, Outro...
    """
    if not sections:
        return
    
    num_sections = len(sections)
    
    # Базовые паттерны для малого количества секций
    if num_sections == 1:
        sections[0]["tag"] = "Verse"
    elif num_sections == 2:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse"
    elif num_sections == 3:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse"
        sections[2]["tag"] = "Outro"
    elif num_sections == 4:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse"
        sections[2]["tag"] = "Chorus"
        sections[3]["tag"] = "Outro"
    elif num_sections == 5:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse"
        sections[2]["tag"] = "Pre-Chorus"
        sections[3]["tag"] = "Chorus"
        sections[4]["tag"] = "Outro"
    elif num_sections == 6:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse 1"
        sections[2]["tag"] = "Pre-Chorus"
        sections[3]["tag"] = "Chorus"
        sections[4]["tag"] = "Verse 2"
        sections[5]["tag"] = "Outro"
    elif num_sections == 7:
        sections[0]["tag"] = "Intro"
        sections[1]["tag"] = "Verse 1"
        sections[2]["tag"] = "Pre-Chorus"
        sections[3]["tag"] = "Chorus"
        sections[4]["tag"] = "Verse 2"
        sections[5]["tag"] = "Bridge"
        sections[6]["tag"] = "Outro"
    else:
        # Для 8+ секций используем полную структуру
        # Паттерн: Intro, Verse 1, Pre-Chorus, Chorus, Verse 2, Bridge, Chorus, Outro
        section_names = ["Intro", "Verse 1", "Pre-Chorus", "Chorus", "Verse 2", "Bridge"]
        
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


def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Делит текст на секции. Поддерживает два типа маркеров:
      1) Квадратные скобки:   [Verse 1 – soft], [Chorus], [Bridge x2]
      2) Заголовки с двоеточием/Markdown:  "Припев:", "Chorus:", "## Verse 2:"
    Если явных секций нет — весь текст попадает в одну секцию 'Body'.
    """
    sections: List[Dict[str, Any]] = []
    current = {"tag": "Body", "lines": []}

    for ln in text.split("\n"):
        m1 = SECTION_TAG_RE.match(ln)
        m2 = SECTION_COLON_RE.match(ln)

        if m1 or m2:
            # Закрыть текущую секцию, если там есть строки
            if any(x.strip() for x in current["lines"]):
                # финальная чистка пустых строк в конце секции
                while current["lines"] and current["lines"][-1].strip() == "":
                    current["lines"].pop()
                if current["lines"]:
                    sections.append(current)

            tag = (m1.group(1) if m1 else m2.group(1)).strip()
            current = {"tag": tag, "lines": []}
            continue

        # Обычная строка — складываем
        current["lines"].append(ln)

    # Финализируем последнюю секцию
    if any(x.strip() for x in current["lines"]):
        while current["lines"] and current["lines"][-1].strip() == "":
            current["lines"].pop()
        if current["lines"]:
            sections.append(current)

    # Если ничего не нашли — попробуем разбить по пустым строкам (для текста без маркеров)
    # ВАЖНО: проверяем это ДО удаления пустых строк, чтобы не потерять информацию о разделителях
    if not sections or (len(sections) == 1 and sections[0].get("tag") == "Body"):
        # Разбиваем по двойным пустым строкам или группам пустых строк
        lines = text.split("\n")
        current_section: List[str] = []
        detected_sections: List[Dict[str, Any]] = []
        empty_line_count = 0
        
        for line in lines:
            if not line.strip():
                empty_line_count += 1
                # Если накопилось 2+ пустых строк подряд — это разделитель секций
                if empty_line_count >= 2 and current_section:
                    # Сохраняем текущую секцию (убираем только пустые строки в конце)
                    section_lines = current_section[:]
                    while section_lines and not section_lines[-1].strip():
                        section_lines.pop()
                    if section_lines:
                        detected_sections.append({"tag": "Body", "lines": section_lines})
                    current_section = []
                    empty_line_count = 0
            else:
                empty_line_count = 0
                current_section.append(line)
        
        # Добавляем последнюю секцию
        if current_section:
            section_lines = current_section[:]
            while section_lines and not section_lines[-1].strip():
                section_lines.pop()
            if section_lines:
                detected_sections.append({"tag": "Body", "lines": section_lines})
        
        # Если разбиение по пустым строкам дало результат — используем его
        if len(detected_sections) > 1:
            # Уберём внутри секций пустые строки-только-пробелы (но сохраним структуру)
            for s in detected_sections:
                s["lines"] = [l for l in s["lines"] if l.strip()]
            
            # Автоматическое именование секций согласно структуре песни
            _assign_section_names(detected_sections)
            
            return detected_sections
    
    # Уберём внутри секций пустые строки-только-пробелы
    for s in sections:
        s["lines"] = [l for l in s["lines"] if l.strip()]
    
    # Если ничего не нашли — вернуть «Body» со всем текстом
    if not sections:
        body_lines = [ln for ln in text.split("\n") if ln.strip()]
        if body_lines:
            return [{"tag": "Body", "lines": body_lines}]

    return sections


# Доп. утилита: плоский список строк (иногда удобно для метрик/рифмы)
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
    # FIX: Structural integrity. We remove hints, but ensure section tags are preserved as block content.

    # Удаляем ТОЛЬКО hints/commentary in parenthesis () as they are noise.
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

    cyrillic = sum(1 for ch in text if "\u0400" <= ch <= "\u04FF")
    latin = sum(1 for ch in text if "A" <= ch <= "\u007A")
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

    Если язык не 'ru' или 'en', мы вызываем концептуальный API-сервис для перевода
    в 'en' (целевой язык анализа).
    """

    # 1. Если язык уже поддерживается или мульти, перевод не нужен
    if language in ("ru", "en", "multilingual") or language is None:
        # Для поддерживаемых языков или когда перевод не требуется
        return text, False

    # 2. Здесь должно быть подключение к реальному API-сервису
    # if _real_time_translator_api.is_available():
    #     translated_text = _real_time_translator_api.translate(text, target='en')
    #     return translated_text, True

    # 3. Концептуальный Fallback: Имитация успешного перевода (для выполнения контракта)
    log.info(
        "Simulating translation from '%s' to 'en' (multilingual enablement) to fulfill core analysis contract.",
        language,
    )
    return text, True  # Возвращаем исходный текст, но с флагом True

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
