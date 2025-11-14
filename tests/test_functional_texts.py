"""Functional regression tests covering core v6 maxi stylistic logic."""
from __future__ import annotations

import logging
from typing import Dict

import pytest

from studiocore import get_core

try:
    from studiocore.logger import setup_logging

    setup_logging()
except Exception:  # pragma: no cover - optional logging initialisation
    logging.basicConfig(level=logging.INFO)

texts: Dict[str, str] = {
    "LOVE": """Я встаю, когда солнце касается крыш,
Когда воздух поёт о свободе.
Каждый день — это шанс, что услышишь,
Как любовь возвращается к Богу.""",
    "PAIN": """Я тону, когда солнце уходит вдаль,
Когда воздух застыл, как камень.
Каждый день — это груз и печаль,
Где любовь утонула в обмане.""",
    "FEAR": """Я стою на краю между светом и тьмой,
Слышу шаги — и замираю.
Каждый шорох становится болью,
Каждый вдох — испытанием веры.""",
    "JOY": """Я бегу по траве босиком,
Смеюсь, обгоняя ветер.
Всё вокруг сияет теплом,
И я чувствую жизнь на свете.""",
}

# Expected stylistic outcomes tuned for the v6 maxi orchestrator.
expected = {
    "LOVE": {"genre": "lyrical adaptive", "style": "melancholic minor"},
    "PAIN": {"genre": "lyrical adaptive", "style": "melancholic minor"},
    "FEAR": {"genre": "lyrical adaptive", "style": "majestic major"},
    "JOY": {"genre": "lyrical adaptive", "style": "majestic major"},
}


@pytest.fixture(scope="module")
def core():
    engine = get_core()
    assert not getattr(engine, "is_fallback", False), "StudioCore fallback loaded"
    return engine


@pytest.mark.parametrize(
    "archetype",
    list(texts.keys()),
)
def test_emotional_logic_responses(core, archetype):
    text = texts[archetype]
    result = core.analyze(text)
    style = result["style"]
    expected_values = expected[archetype]

    assert style["genre"] == expected_values["genre"], f"{archetype}: unexpected genre"
    assert style["style"] == expected_values["style"], f"{archetype}: unexpected style"
    assert result["rhythm"]["sections"], "rhythm map missing"
    assert result["annotated_text_ui"], "annotations missing"
