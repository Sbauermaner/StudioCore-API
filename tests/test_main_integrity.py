"""Integration tests for the StudioCore v6 maxi orchestrator."""
from __future__ import annotations

import importlib
import logging
import os
from typing import Iterable

import pytest
import requests

from studiocore import MONOLITH_VERSION, get_core
from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from studiocore.monolith_v6_0_0 import PatchedLyricMeter

try:
    from studiocore.logger import setup_logging

    setup_logging()
except Exception:  # pragma: no cover - logging is optional during tests
    logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

CORE_MODULES: Iterable[str] = (
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter",
)


@pytest.fixture(scope="module")
def core():
    engine = get_core()
    assert not getattr(engine, "is_fallback", False), "StudioCore fallback loaded"
    return engine


@pytest.fixture(scope="module")
def emo_engine() -> AutoEmotionalAnalyzer:
    return AutoEmotionalAnalyzer()


@pytest.fixture(scope="module")
def tlp_engine() -> TruthLovePainEngine:
    return TruthLovePainEngine()


def test_core_modules_importable():
    missing = []
    for module in CORE_MODULES:
        try:
            importlib.import_module(module)
        except Exception as exc:  # pragma: no cover - diagnostic path
            missing.append(f"{module}: {exc}")
    assert not missing, "\n".join(missing)


def test_prediction_pipeline(core, emo_engine, tlp_engine):
    sample = "Я встаю, когда солнце касается крыш и воздух поёт о свободе"
    emo = emo_engine.analyze(sample)
    tlp = tlp_engine.analyze(sample)

    rhythm = core.rhythm.analyze(
        sample,
        emotions=emo,
        tlp=tlp,
        cf=tlp.get("conscious_frequency"),
    )
    assert rhythm["global_bpm"] >= 60
    assert rhythm["sections"], "rhythm sections missing"

    bpm = int(round(rhythm["global_bpm"]))
    style = core.style.build(emo, tlp, sample, bpm, overlay={}, voice_hint=None)
    assert style["genre"]
    assert style["style"]

    result = core.analyze(sample)
    assert result["rhythm"]["section_order"]
    assert result["rhythm"]["global_bpm"] == pytest.approx(rhythm["global_bpm"], abs=0.01)
    assert result["style"]["genre"] == style["genre"]
    assert "annotated_text_ui" in result
    assert result["version"].startswith("v")


def test_patched_lyric_meter_bridge():
    meter = PatchedLyricMeter()
    text = "[BPM: 110]\nТихо падает снег, и я дышу в такт"
    analysis = meter.analyze(text)
    blend = analysis["header_bpm"] * 0.7 + analysis["estimated_bpm"] * 0.3
    assert analysis["header_bpm"] == pytest.approx(110, abs=0.5)
    assert analysis["global_bpm"] == pytest.approx(blend, abs=0.5)
    assert analysis["global_bpm"] > analysis["estimated_bpm"]
    assert "sections" in analysis


def test_api_endpoint_when_available():
    api_url = os.environ.get("STUDIOCORE_API_URL", "http://127.0.0.1:7860/api/predict")
    try:
        response = requests.post(api_url, json={"text": "health check"}, timeout=5)
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"StudioCore API not reachable: {exc}")

    assert response.status_code == 200
    data = response.json()
    assert "bpm" in data
    assert "style" in data
    log.info("API health check succeeded for %s (monolith=%s)", api_url, MONOLITH_VERSION)
