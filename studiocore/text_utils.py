# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Any

# Разрешённые символы (для подсказок и визуальных тегов; сами по себе не используются для фильтрации)
PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))

# [Verse 1 – soft], [Chorus], [Bridge x2] и т.п.
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

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
