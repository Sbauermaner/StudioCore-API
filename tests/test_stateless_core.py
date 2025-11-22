from studiocore.core_v6 import StudioCoreV6


def test_stateless_analysis_leak():
    core = StudioCoreV6()

    p1 = core.analyze("first text")
    p2 = core.analyze("second text")

    assert p1 != p2
    assert core.annotate_ui(p1) != core.annotate_ui(p2)
