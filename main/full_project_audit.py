"""
Full project audit utility.

Runs Python bytecode compilation across the repository, validates
structured configuration files, and confirms key scripts are present
and executable. Use this locally to mirror CI safety checks.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _run_compile_check() -> tuple[bool, str]:
    """Compile all Python files and return success flag with output."""

    proc = subprocess.run(
        [sys.executable, "-m", "compileall", ".", "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part)
    return proc.returncode == 0, output


def _validate_structured_files() -> list[str]:
    """Validate OpenAPI files can be parsed as JSON/YAML."""

    errors: list[str] = []

    openapi_json = ROOT / "openapi.json"
    if openapi_json.exists():
        try:
            json.loads(openapi_json.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic output only
            errors.append(f"[OPENAPI] Invalid JSON: {exc}")
    else:
        errors.append("[MISSING] openapi.json not found")

    openapi_yaml = ROOT / "openapi.yaml"
    if openapi_yaml.exists():
        try:
            yaml.safe_load(openapi_yaml.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic output only
            errors.append(f"[OPENAPI] Invalid YAML: {exc}")
    else:
        errors.append("[MISSING] openapi.yaml not found")

    return errors


def _check_required_assets() -> list[str]:
    """Confirm critical scripts and config files exist and are usable."""

    errors: list[str] = []

    required = {
        "run_full_diag.sh": ROOT / "run_full_diag.sh",
        "full_system_diagnostics.py": ROOT / "main" / "full_system_diagnostics.py",
        "auto_log_cleaner.py": ROOT / "main" / "auto_log_cleaner.py",
        "app.py": ROOT / "app.py",
        "requirements.txt": ROOT / "requirements.txt",
    }

    for label, path in required.items():
        if not path.exists():
            errors.append(f"[MISSING] {label} not found at {path.relative_to(ROOT)}")

    run_full_diag = required["run_full_diag.sh"]
    if run_full_diag.exists() and not run_full_diag.stat().st_mode & 0o100:
        errors.append("[PERMISSIONS] run_full_diag.sh is not executable")

    return errors


def _check_requirements_duplicates() -> list[str]:
    """Detect duplicated requirement entries to avoid resolver issues."""

    path = ROOT / "requirements.txt"
    if not path.exists():
        return []

    errors: list[str] = []
    seen: set[str] = set()
    duplicates: set[str] = set()

    for line in path.read_text(encoding="utf-8").splitlines():
        normalized = line.strip()
        if not normalized or normalized.startswith("#"):
            continue

        if normalized.lower() in seen:
            duplicates.add(normalized)
        else:
            seen.add(normalized.lower())

    if duplicates:
        errors.append(f"[REQUIREMENTS] Duplicate entries detected: {', '.join(sorted(duplicates))}")

    return errors


def full_project_audit() -> int:
    print(">>> Starting full project audit...\n")

    compile_ok, compile_output = _run_compile_check()
    errors: list[str] = []

    if compile_ok:
        print("✔ All Python files compiled successfully.")
    else:
        print("❌ Compile errors found:")
        print(compile_output)
        errors.append("Python bytecode compilation failed (see output above).")

    errors.extend(_validate_structured_files())
    errors.extend(_check_required_assets())
    errors.extend(_check_requirements_duplicates())

    if errors:
        print("\n❌ Audit completed with issues:")
        for err in errors:
            print("-", err)
        return 1

    print("\n✔ Full project audit complete — no blocking issues detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(full_project_audit())
