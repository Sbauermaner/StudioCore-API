# -*- coding: utf-8 -*-
"""
🧠 StudioCore Core Compatibility Check (OpenAPI diff)
Author: Bauer Synesthetic Studio
"""
from __future__ import annotations
import os
from typing import Any, Dict
from compat_base import load_openapi, normalize_openapi, dict_diff, save_report

# Пути к файлам OpenAPI (замени на свои при необходимости)
OPENAPI_LEFT = os.environ.get("OPENAPI_LEFT", "openapi.json")
OPENAPI_RIGHT = os.environ.get("OPENAPI_RIGHT", "openapi_studiocore.yaml")


def run_check() -> Dict[str, Any]:
    left_doc, lf = load_openapi(OPENAPI_LEFT)
    right_doc, rf = load_openapi(OPENAPI_RIGHT)

    nl = normalize_openapi(left_doc)
    nr = normalize_openapi(right_doc)

    diff = dict_diff(nl, nr)
    ok = (diff == {})

    report = {
        "ok": ok,
        "summary": "schemas are compatible" if ok else "schemas differ",
        "files": {"left": OPENAPI_LEFT, "right": OPENAPI_RIGHT, "formats": [lf, rf]},
        "diff": diff,
    }

    save_report("compat_report_openapi.json", report)
    print("\n=== OpenAPI DIFF RESULT ===")
    print("Status:", "✅ OK" if ok else "⚠️ DIFFERENCES FOUND")
    if not ok:
        print("Diff:", diff)
    return report


if __name__ == "__main__":
    run_check()
