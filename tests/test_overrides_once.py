# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from copy import deepcopy

from studiocore.core_v6 import StudioCoreV6
from studiocore.user_override_manager import UserOverrideManager, UserOverrides


def test_apply_user_overrides_once_idempotent_and_recalculates_bpm_curve():
    core = StudioCoreV6()
    manager = UserOverrideManager(
        UserOverrides(bpm=95.0, vocal_profile={"tone": "airy"}, genre="edm")
    )

    payload = {
        "vocal": {"tone": "bright", "intensity_curve": [0.4, 0.6]},
        "bpm": {"estimate": 120.0, "curve": [120.0, 118.0]},
        "style": {"genre": "rock"},
        "structure": {"sections": ["line a", "line b"]},
    }

    adjustments_first = core._apply_user_overrides_once(payload, manager)

    assert payload["_overrides_applied"] is True
    assert adjustments_first["bpm"]["estimate"] == 95.0
    assert len(adjustments_first["bpm"]["curve"]) == len(payload["structure"]["sections"])
    assert all(abs(value - 95.0) <= 5 for value in adjustments_first["bpm"]["curve"])
    assert payload["override_debug"]["applied_overrides"]["style"]["genre"] == "edm"

    snapshot_before_second = deepcopy(payload)
    adjustments_second = core._apply_user_overrides_once(payload, manager)

    assert adjustments_second == adjustments_first
    assert payload == snapshot_before_second

    adjustments_second["bpm"]["estimate"] = 130.0
    assert (
        payload["override_debug"]["applied_overrides"]["bpm"]["estimate"]
        == adjustments_first["bpm"]["estimate"]
    )

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
