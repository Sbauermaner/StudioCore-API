# -*- coding: utf-8 -*-
"""
🛰️ StudioCore Remote Compatibility Check
Author: Bauer Synesthetic Studio
"""
from __future__ import annotations

import os
from typing import Any, Dict

import requests

from compat_base import save_report

API_URL = os.environ.get("STUDIOCORE_API_URL", "https://sbauer8-studiocore-api.hf.space/api/predict")

TEST_TEXT = """Вся моя жизнь — как быль или небыль,
Вся моя жизнь — по краю скользить.
Но я молю открыть в сердце двери,
Я так хочу твоей женщиной быть…"""


def _report(payload: Dict[str, Any]) -> Dict[str, Any]:
    save_report("remote_compatibility_full_report.json", payload)
    return payload


def run_check() -> Dict[str, Any]:
    print("🧩 Remote API:", API_URL)
    try:
        r = requests.post(API_URL, json={"text": TEST_TEXT}, timeout=60)
    except Exception as e:
        print("❌ Connect error:", e)
        return _report({"ok": False, "status": "connect_error", "error": str(e)})

    if r.status_code != 200:
        print(f"❌ API {r.status_code}: {r.text}")
        return _report({"ok": False, "status": "http_error", "code": r.status_code, "body": r.text})

    try:
        data = r.json()
    except Exception:
        print("⚠️ JSON decode error")
        return _report({"ok": False, "status": "json_error", "body": r.text})

    summary = data.get("summary", "")
    annotated = data.get("annotated_text", "")
    full_prompt = data.get("prompt_full", "")
    suno_prompt = data.get("prompt_suno", "")

    ok_summary = "Жанр" in summary or "Genre" in summary
    ok_ann = "[" in annotated
    ok_full = len(full_prompt) > 50
    ok_suno = len(suno_prompt) > 50
    has_tlp = any(k in summary for k in ("Truth", "Love", "Pain", "Conscious Frequency"))
    has_tonesync = "ToneSync" in suno_prompt

    all_ok = all([ok_summary, ok_ann, ok_full, ok_suno, has_tlp, has_tonesync])

    print("\n=== 🧠 RUNTIME CHECK ===")
    print("summary:", "OK" if ok_summary else "NO")
    print("annotated:", "OK" if ok_ann else "NO")
    print("full_prompt:", "OK" if ok_full else "SHORT")
    print("suno_prompt:", "OK" if ok_suno else "SHORT")
    print("TLP:", has_tlp)
    print("ToneSync:", has_tonesync)
    print("→", "✅ StudioCore runtime OK" if all_ok else "⚠️ Runtime mismatches")

    return _report({
        "ok": all_ok,
        "status": "ok" if all_ok else "mismatch",
        "checks": {
            "summary_ok": ok_summary,
            "annotated_ok": ok_ann,
            "full_prompt_ok": ok_full,
            "suno_prompt_ok": ok_suno,
            "has_tlp": has_tlp,
            "has_tonesync": has_tonesync,
        },
        "preview": {
            "summary": summary[:300],
            "annotated_head": "\n".join(annotated.splitlines()[:8]),
        }
    })


if __name__ == "__main__":
    run_check()
