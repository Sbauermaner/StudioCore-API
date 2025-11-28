from studiocore.core_v6 import StudioCoreV6


def test_stateless_analysis_leak():
    """Test that analyze() returns different results for different inputs (stateless)."""
    core = StudioCoreV6()

    p1 = core.analyze("first text")
    p2 = core.analyze("second text")

    assert p1 != p2
    # Use annotated_text_ui from results instead of calling non-existent annotate_ui()
    assert p1.get("annotated_text_ui") != p2.get("annotated_text_ui")
