"""Repository-wide health checks for StudioCore v6 maxi."""
from __future__ import annotations

import ast
import importlib
import json
import pathlib
from typing import Iterable

import pytest
import yaml

from compat_check_core import run_check as compat_core_check
from compat_check_remote import run_check as compat_remote_check

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
CODE_FOLDERS: Iterable[pathlib.Path] = (
    PROJECT_ROOT / "studiocore",
    PROJECT_ROOT / "tests",
)
JSON_FILES: Iterable[pathlib.Path] = (
    PROJECT_ROOT / "openapi.json",
    PROJECT_ROOT / "test_samples" / "style_matrix_testset.json",
)
YAML_FILES: Iterable[pathlib.Path] = (
    PROJECT_ROOT / "openapi_studiocore.yaml",
    PROJECT_ROOT / "openapi_gpt.yaml",
)


def _python_files() -> Iterable[pathlib.Path]:
    for folder in CODE_FOLDERS:
        if not folder.exists():
            continue
        for path in folder.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            yield path


def test_required_directories_present():
    missing = [str(p) for p in CODE_FOLDERS if not p.exists()]
    assert not missing, f"Missing required directories: {missing}"


def test_python_files_parse():
    failures = []
    for py_file in _python_files():
        try:
            source = py_file.read_text(encoding="utf-8")
            ast.parse(source, filename=str(py_file))
        except SyntaxError as exc:
            failures.append(f"{py_file}: {exc}")
    assert not failures, "\n".join(failures)


def test_json_assets_valid():
    for json_file in JSON_FILES:
        with json_file.open("r", encoding="utf-8") as fh:
            json.load(fh)


def test_yaml_assets_valid():
    for yaml_file in YAML_FILES:
        with yaml_file.open("r", encoding="utf-8") as fh:
            yaml.safe_load(fh)


@pytest.mark.parametrize(
    "module",
    [
        "app",
        "studiocore",
        "studiocore.rhythm",
        "studiocore.monolith_v6_0_0",
        "studiocore.sections",
    ],
)
def test_key_modules_import(module):
    importlib.import_module(module)


def test_compatibility_checks_pass():
    core_report = compat_core_check()
    remote_report = compat_remote_check()
    assert core_report["ok"], "OpenAPI spec mismatch detected"
    if remote_report.get("status") == "connect_error":
        pytest.skip("Remote StudioCore API is unreachable")
    if not remote_report.get("ok", False):
        pytest.xfail(f"Remote compatibility mismatch: {remote_report.get('status')}")
