import logging

from studiocore.text_utils import translate_text_for_analysis


def test_translate_text_for_analysis_passthrough_languages(caplog):
    for lang in ("ru", "en", "multilingual"):
        with caplog.at_level(logging.INFO):
            translated, was_translated = translate_text_for_analysis("пример", lang)

        assert translated == "пример"
        assert was_translated is False
        assert not [
            record for record in caplog.records if "Simulating translation" in record.message
        ]
        caplog.clear()


def test_translate_text_for_analysis_simulates_for_unsupported(caplog):
    with caplog.at_level(logging.INFO):
        translated, was_translated = translate_text_for_analysis("texto", "es")

    assert translated == "texto"
    assert was_translated is False
    assert any(
        "Translation not available" in record.message for record in caplog.records
    )
