# -*- coding: utf-8 -*-
"""
⚙️ Общие утилиты для compatibility-check скриптов StudioCore.
Author: Bauer Synesthetic Studio
"""
from __future__ import annotations
import json, os
from datetime import datetime
from typing import Any, Dict, Tuple


def save_report(filename: str, data: Dict[str, Any]) -> str:
    """Сохраняет JSON-отчёт с таймстампом."""
    data = dict(data)
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📁 Report saved → {filename}")
    return filename


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_openapi(path: str) -> Tuple[Dict[str, Any], str]:
    """Загружает OpenAPI из JSON или YAML. Возвращает (dict, format)."""
    text = _read_text(path)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".json",):
        return json.loads(text), "json"

    try:
        import yaml  # type: ignore
        return yaml.safe_load(text), "yaml"
    except Exception:
        raise RuntimeError(
            f"YAML required to read {path}. Please install PyYAML: pip install pyyaml"
        )


def normalize_openapi(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Оставляем только важные поля для сравнения."""
    return {
        "openapi": str(doc.get("openapi", "")),
        "info": {
            "title": doc.get("info", {}).get("title", ""),
            "version": str(doc.get("info", {}).get("version", "")),
        },
        "servers": [s.get("url") for s in doc.get("servers", [])],
        "paths": doc.get("paths", {}),
    }


def dict_diff(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Сравнивает два OpenAPI-документа и возвращает различия."""
    out: Dict[str, Any] = {"info": {}, "servers": {}, "paths": {}}

    # info
    if a["info"] != b["info"]:
        out["info"] = {"left": a["info"], "right": b["info"]}

    # servers
    if a["servers"] != b["servers"]:
        out["servers"] = {"left": a["servers"], "right": b["servers"]}

    # paths
    paths_a = set(a["paths"].keys())
    paths_b = set(b["paths"].keys())
    only_left = sorted(list(paths_a - paths_b))
    only_right = sorted(list(paths_b - paths_a))
    both = sorted(list(paths_a & paths_b))

    paths_details = {}
    if only_left:
        paths_details["only_left"] = only_left
    if only_right:
        paths_details["only_right"] = only_right

    method_keys = ("get", "post", "put", "patch", "delete")
    for p in both:
        la = a["paths"].get(p, {})
        lb = b["paths"].get(p, {})
        meths_a = sorted([m for m in la.keys() if m.lower() in method_keys])
        meths_b = sorted([m for m in lb.keys() if m.lower() in method_keys])
        if meths_a != meths_b:
            paths_details[p] = {"methods_left": meths_a, "methods_right": meths_b}

    if paths_details:
        out["paths"] = paths_details

    return {k: v for k, v in out.items() if v}
