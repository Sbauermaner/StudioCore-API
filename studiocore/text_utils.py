# -*- coding: utf-8 -*-
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

    # Схлопываем кратные пустые строки
    out_lines: List[str] = []
    prev_blank = False
    for ln in lines:
        if ln == "":
            if not prev_blank:
                out_lines.append("")
            prev_blank = True
        else:
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
    clean_text = normalize_text_preserve_symbols(source)
    return clean_text, {"detected": detected, "map": command_map}, preserved_tags


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

# === v16: ИСПРАВЛЕНИЕ ImportError ===
# Эта функция была в monolith_v4_3_1.py, но monolith v6 вызывает ее отсюда.
def extract_raw_blocks(text: str) -> List[str]:
    """
    Разделяет текст на блоки по пустой строке, 
    ИГНОРИРУЯ теги [Intro], (шепотом) и т.д.
    """
    # Заменяем [Tag] и (hint) на заглушки, чтобы re.split их не видел
    text_no_tags = re.sub(r"^\s*\[[^\]]+\]\s*$", "TAG_PLACEHOLDER", text, flags=re.MULTILINE)
    text_no_tags = re.sub(r"^\s*\([^\)]+\)\s*$", "HINT_PLACEHOLDER", text_no_tags, flags=re.MULTILINE)
    
    # Разделяем по пустой строке
    blocks = re.split(r"\n\s*\n", text_no_tags.strip())
    
    # Очищаем блоки от заглушек (на всякий случай) и пустых строк
    cleaned_blocks = []
    for block in blocks:
        clean_block = block.replace("TAG_PLACEHOLDER", "").replace("HINT_PLACEHOLDER", "").strip()
        if clean_block:
            cleaned_blocks.append(clean_block)

    return cleaned_blocks


def detect_language(text: str) -> Dict[str, Any]:
    """Very small heuristic to guess whether the text is Cyrillic or Latin."""

    cyrillic = sum(1 for ch in text if "\u0400" <= ch <= "\u04FF")
    latin = sum(1 for ch in text if "A" <= ch <= "z")
    if cyrillic > latin:
        language = "ru"
    elif latin > cyrillic:
        language = "en"
    else:
        language = "multilingual"
    confidence = round(min(1.0, max(cyrillic, latin) / max(len(text) or 1, 1)), 3)
    return {"language": language, "confidence": confidence}


def translate_text_for_analysis(text: str, language: str) -> str:
    """Placeholder translation hook for StudioCore v6."""

    log.warning(
        "translate_text_for_analysis is not configured; returning source text for language '%s'", language
    )
    return text