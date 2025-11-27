# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore import (
    LOADER_STATUS,
    MONOLITH_VERSION,
    STUDIOCORE_VERSION,
    get_core,
    loader_diagnostics,
)


def test_get_core_produces_instance():
    core = get_core()
    assert hasattr(core, "analyze")
    assert LOADER_STATUS["active"] in {"v6", "v5", "monolith", "fallback"}


def test_loader_diagnostics_shape():
    diag = loader_diagnostics()
    assert diag.engine_order
    assert isinstance(diag.errors, tuple)
    assert diag.monolith_version == MONOLITH_VERSION
    assert diag.active in {None, "v6", "v5", "monolith", "fallback"}
    assert STUDIOCORE_VERSION.startswith("v6")


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
