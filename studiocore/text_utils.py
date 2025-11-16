# -*- coding: utf-8 -*-
import re
from typing import Any, Dict, List, Tuple

# Разрешённые символы (для подсказок и визуальных тегов; сами по себе не используются для фильтрации)
PUNCTUATION_SAFE = set(list(",.;:!?…—–()[]\"'“”‘’*•‧·_/|"))
EMOJI_SAFE = set(list("♡♥❤❥❣☀☁☂☮☯☾☽★☆✨⚡☼⚔⚖⚙⚗⚛✝✟✞✡☠☢☣❄☃"))

# [Verse 1 – soft], [Chorus], [Bridge x2] и т.п.
SECTION_TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")

# Альтернативные заголовки секций: "Припев:", "Chorus:", "Verse 2:", "## Bridge", "# Outro" и т.п.
SECTION_COLON_RE = re.compile(
    r"^\s*(?:#{1,3}\s*)?([A-Za-zА-Яа-яЁё0-9 _\-/]+?)\s*[:：]\s*$"
)

# Дополнительная поддержка заголовков без скобок
SECTION_BARE_RE = re.compile(r"^\s*([A-Za-zА-Яа-яЁё0-9 _\-/]+?)\s*$")

ALLOWED_HEADERS = {
    "INTRO",
    "VERSE",
    "VERSE 1",
    "VERSE 2",
    "VERSE 3",
    "CHORUS",
    "CHORUS 1",
    "CHORUS 2",
    "FINAL CHORUS",
    "BRIDGE",
    "HOOK",
    "HOOK/REFRAIN",
    "REFRAIN",
    "OUTRO",
    "PONT",
    "PONTE",
}

HEADER_CONVERSIONS = {
    "verse": "VERSE",
    "куплет": "VERSE",
    "strophe": "VERSE",
    "chorus": "CHORUS",
    "припев": "CHORUS",
    "приpев": "CHORUS",
    "bridge": "BRIDGE",
    "бридж": "BRIDGE",
    "hook": "HOOK",
    "hook/refrain": "HOOK/REFRAIN",
    "рефрен": "HOOK",
    "insane": "HOOK",
    "final chorus": "FINAL CHORUS",
    "финальный припев": "FINAL CHORUS",
    "ponte": "PONTE",
    "pont": "PONT",
    "outro": "OUTRO",
    "intro": "INTRO",
}

SECTION_KEYWORDS = {
    "ru": {"куплет": "verse", "припев": "chorus", "бридж": "bridge", "финал": "outro", "рефрен": "hook"},
    "de": {"strophe": "verse", "refrain": "chorus", "brucke": "bridge", "schluss": "outro", "schlus": "outro"},
}

LAST_PARSED_SECTIONS: List[Dict[str, Any]] = []

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


def detect_language(text: str) -> Dict[str, Any]:
    """Простейшее определение языка (en/ru/de) по алфавиту."""
    counts = {"latin": 0, "cyrillic": 0, "german": 0}
    for ch in text:
        if "а" <= ch.lower() <= "я" or ch.lower() in {"ё"}:
            counts["cyrillic"] += 1
        elif ch.lower() in {"ä", "ö", "ü", "ß"}:
            counts["german"] += 1
        elif "a" <= ch.lower() <= "z":
            counts["latin"] += 1
    total = max(sum(counts.values()), 1)
    if counts["cyrillic"] > counts["latin"] * 1.2 and counts["cyrillic"] >= counts["german"]:
        language = "ru"
    elif counts["german"] >= counts["cyrillic"] and counts["german"] > 5:
        language = "de"
    else:
        language = "en"
    confidence = round(counts.get("cyrillic" if language == "ru" else "german" if language == "de" else "latin", 0) / total, 3)
    return {"language": language, "confidence": confidence, "counts": counts}


def translate_text_for_analysis(text: str, language: str) -> str:
    """Перевод ключевых структурных слов в английские аналоги."""
    replacements = SECTION_KEYWORDS.get(language)
    if not replacements:
        return text
    translated = text
    for native, english in replacements.items():
        translated = re.sub(rf"\b{native}\b", english, translated, flags=re.IGNORECASE)
    return translated


def _canonicalize_header(label: str) -> str | None:
    if not label:
        return None
    cleaned = re.split(r"[–—-/:]", label, 1)[0].strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    lower = cleaned.lower()
    canonical = HEADER_CONVERSIONS.get(lower, cleaned.upper())
    if canonical in ALLOWED_HEADERS:
        return canonical
    if canonical.startswith("VERSE ") and canonical.split()[-1].isdigit():
        number = canonical.split()[-1]
        key = f"VERSE {number}"
        if key in ALLOWED_HEADERS:
            return key
        if "VERSE" in ALLOWED_HEADERS:
            return "VERSE"
    if canonical.startswith("CHORUS ") and canonical.split()[-1].isdigit():
        number = canonical.split()[-1]
        key = f"CHORUS {number}"
        if key in ALLOWED_HEADERS:
            return key
        if "CHORUS" in ALLOWED_HEADERS:
            return "CHORUS"
    return None


def _match_section_header(line: str) -> Tuple[str | None, str | None]:
    stripped = line.strip()
    if not stripped:
        return None, None
    for regex in (SECTION_TAG_RE, SECTION_COLON_RE, SECTION_BARE_RE):
        match = regex.match(stripped)
        if match:
            header = match.group(1)
            canonical = _canonicalize_header(header)
            if canonical:
                return canonical, stripped
    return None, None


def _finalize_section(current: Dict[str, Any], sections: List[Dict[str, Any]]) -> None:
    lines = [ln for ln in current.get("lines", []) if ln.strip()]
    if not lines:
        return
    section = {"tag": current["tag"], "lines": lines, "meta": current.get("meta", {}).copy()}
    sections.append(section)


def _split_long_sections(sections: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    if limit <= 0:
        return sections
    output: List[Dict[str, Any]] = []
    for section in sections:
        lines = section.get("lines", [])
        if len(lines) <= limit:
            output.append(section)
            continue
        chunk_index = 0
        while lines:
            chunk = lines[:limit]
            lines = lines[limit:]
            new_meta = section.get("meta", {}).copy()
            if chunk_index:
                new_meta["segment"] = chunk_index + 1
            output.append({"tag": section["tag"], "lines": chunk, "meta": new_meta})
            chunk_index += 1
    return output


def extract_sections(text: str) -> List[Dict[str, Any]]:
    """Жёсткий парсер секций по спецификации Codex."""
    sections: List[Dict[str, Any]] = []
    header_counts: Dict[str, int] = {}
    current = {"tag": "BODY", "lines": [], "meta": {"isolated": False}}
    seen_chorus = 0

    for raw_line in text.split("\n"):
        normalized_header, raw_value = _match_section_header(raw_line)
        if normalized_header:
            _finalize_section(current, sections)
            header_counts[normalized_header] = header_counts.get(normalized_header, 0) + 1
            meta = {
                "raw": raw_value,
                "occurrence": header_counts[normalized_header],
                "isolated": normalized_header in {"HOOK", "HOOK/REFRAIN", "BRIDGE"},
            }
            if normalized_header == "FINAL CHORUS" and seen_chorus == 0:
                meta["requires_anchor"] = True
            if normalized_header.startswith("CHORUS") and normalized_header != "FINAL CHORUS":
                seen_chorus += 1
            current = {"tag": normalized_header, "lines": [], "meta": meta}
            continue

        current.setdefault("lines", []).append(raw_line)

    _finalize_section(current, sections)

    if not sections:
        body_lines = [ln for ln in text.split("\n") if ln.strip()]
        if body_lines:
            sections = [{"tag": "BODY", "lines": body_lines, "meta": {"fallback": True}}]

    sections = _split_long_sections(sections, limit=20)

    global LAST_PARSED_SECTIONS
    LAST_PARSED_SECTIONS = [
        {"tag": section["tag"], "lines": list(section.get("lines", [])), "meta": dict(section.get("meta", {}))}
        for section in sections
    ]

    return sections


# Доп. утилита: плоский список строк (иногда удобно для метрик/рифмы)
def flatten_sections_to_lines(sections: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for s in sections:
        out.extend(s.get("lines", []))
    return out


def get_last_section_metadata() -> List[Dict[str, Any]]:
    """Возвращает копию последних разобранных секций (для диагностики)."""
    return [
        {"tag": section.get("tag"), "lines": list(section.get("lines", [])), "meta": dict(section.get("meta", {}))}
        for section in LAST_PARSED_SECTIONS
    ]

# === v16: ИСПРАВЛЕНИЕ ImportError ===
# Эта функция была в monolith_v4_3_1.py, но monolith v6 вызывает ее отсюда.
def extract_raw_blocks(text: str) -> List[str]:
    """Разделяет текст на блоки по пустой строке, игнорируя теги."""
    text_no_tags = re.sub(r"^\s*\[[^\]]+\]\s*$", "TAG_PLACEHOLDER", text, flags=re.MULTILINE)
    text_no_tags = re.sub(r"^\s*\([^\)]+\)\s*$", "HINT_PLACEHOLDER", text_no_tags, flags=re.MULTILINE)
    blocks = re.split(r"\n\s*\n", text_no_tags.strip())
    cleaned_blocks = []
    for block in blocks:
        clean_block = block.replace("TAG_PLACEHOLDER", "").replace("HINT_PLACEHOLDER", "").strip()
        if clean_block:
            cleaned_blocks.append(clean_block)
    return cleaned_blocks
