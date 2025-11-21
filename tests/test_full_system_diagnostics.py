# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from pathlib import Path
import subprocess
import textwrap


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_full_system_diagnostics_passes_for_valid_workflows():
    result = subprocess.run(
        ["python3", "main/full_system_diagnostics.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "✔ No workflow errors detected" in result.stdout


def test_full_system_diagnostics_fails_on_invalid_workflow():
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    bad_workflow = workflows_dir / "invalid.yml"
    bad_workflow.write_text(textwrap.dedent("""
        name: invalid workflow
        on: [push]
        jobs:
          bad:
            runs-on: ubuntu-latest
            steps:
              - run: echo "unterminated
              - run: [missing-closing-bracket
    """), encoding="utf-8")

    try:
        result = subprocess.run(
            ["python3", "main/full_system_diagnostics.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    finally:
        bad_workflow.unlink(missing_ok=True)

    assert result.returncode == 1
    assert "[YAML ERROR] invalid.yml" in result.stdout


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
