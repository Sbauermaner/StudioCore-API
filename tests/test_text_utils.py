import logging

from studiocore.text_utils import translate_text_for_analysis
import studiocore.text_utils as text_utils


def test_translate_text_for_analysis_warns_once(caplog):
    text_utils._translation_warning_emitted = False

    with caplog.at_level(logging.WARNING):
        translate_text_for_analysis("пример", "ru")
        translate_text_for_analysis("ещё", "ru")

    warnings = [
        record
        for record in caplog.records
        if "translate_text_for_analysis is not configured" in record.message
    ]
    assert len(warnings) == 1
