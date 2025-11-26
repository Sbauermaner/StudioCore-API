# -*- coding: utf-8 -*-
"""
StudioCore IMMORTAL v7 — Premium UI v3 (Impulse Analysis Panel)
Автор: Сергей Бауэр (@Sbauermaner)
"""

from __future__ import annotations

import json
import traceback
from typing import Any, Dict, List, Tuple
import gradio
import gradio as gr

from studiocore.core_v6 import StudioCoreV6

engine = StudioCoreV6()

def _safe_get(d, path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
        if cur is None:
            return default
    return cur

def extract_main_outputs(result):
    fanf = result.get("fanf", {}) if isinstance(result.get("fanf"), dict) else {}
    style_prompt = fanf.get("style_prompt") or result.get("style_prompt") or ""
    lyrics_prompt = fanf.get("lyrics_prompt") or result.get("lyrics_prompt") or ""
    ui_text = fanf.get("ui_text") or result.get("annotated_text") or ""
    fanf_text = (
        fanf.get("full")
        or fanf.get("summary")
        or fanf.get("annotated_text_fanf")
        or ui_text
    )
    try:
        summary_json = json.dumps(result, ensure_ascii=False, indent=2)
    except Exception:
        summary_json = str(result)
    return style_prompt, lyrics_prompt, ui_text, fanf_text, summary_json

def build_core_pulse_timeline(result):
    diagnostics = result.get("diagnostics", {}) or {}
    engines = diagnostics.get("engines", {}) if isinstance(diagnostics.get("engines"), dict) else {}

    stages = [
        ("TEXT", "text"),
        ("STRUCTURE", "structure"),
        ("TLP", "tlp"),
        ("EMOTION", "emotion"),
        ("RDE", "rde"),
        ("BPM", "bpm"),
        ("TONE", "tone"),
        ("GENRE", "genre"),
        ("STYLE", "style"),
        ("FANF", "fanf"),
    ]

    def status_to_color(status):
        if status is None:
            return "#555555"
        s = str(status).lower()
        if "error" in s or "fail" in s:
            return "#cc3333"
        if "warn" in s:
            return "#ffcc33"
        if "fallback" in s:
            return "#aa55ff"
        if "ok" in s or "success" in s:
            return "#33aa55"
        return "#777777"

    html = ["<div style='display:flex;gap:8px;align-items:center;font-family:monospace;'>"]
    for label, key in stages:
        status = None
        if isinstance(engines.get(key), dict):
            status = engines[key].get("status")
        elif isinstance(engines.get(key), str):
            status = engines[key]
        color = status_to_color(status)
        html.append(f"""
        <div style="display:flex;flex-direction:column;align-items:center;">
          <div style="width:22px;height:22px;border-radius:6px;background:{color};box-shadow:0 0 6px rgba(0,0,0,0.4);"></div>
          <div style="font-size:10px;margin-top:3px;">{label}</div>
        </div>
        """)
    html.append("</div>")
    return "\n".join(html)

def build_tlp_pulse_text(result):
    tlp = result.get("tlp", {}) if isinstance(result.get("tlp"), dict) else {}
    truth = tlp.get("truth", 0.0)
    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    cf = tlp.get("conscious_frequency", tlp.get("cf", 0.0))
    def bar(v):
        v = max(0.0, min(1.0, float(v)))
        l = int(v * 20)
        return "█" * l + "·" * (20 - l)
    return "\n".join([
        f"Truth: {truth:.2f} |{bar(truth)}|",
        f"Love : {love:.2f} |{bar(love)}|",
        f"Pain : {pain:.2f} |{bar(pain)}|",
        "",
        f"Conscious Frequency (CF): {cf:.3f}",
    ])

def build_rde_section_text(result):
    rde = result.get("rde", {}) if isinstance(result.get("rde"), dict) else {}
    rhythm = rde.get("rhythm", "—")
    dynamics = rde.get("dynamics", "—")
    emotion = rde.get("emotion", "—")
    structure = result.get("structure", {}) if isinstance(result.get("structure"), dict) else {}
    section_list = structure.get("sections") or []
    headers = structure.get("headers") or []
    
    # Получаем информацию о вокальных техниках и эмоциях секций
    fanf = result.get("fanf", {}) if isinstance(result.get("fanf"), dict) else {}
    lyrics_sections = fanf.get("lyrics_sections") or []
    if not lyrics_sections:
        # Пытаемся получить из другого места
        lyrics_data = result.get("lyrics", {}) if isinstance(result.get("lyrics"), dict) else {}
        lyrics_sections = lyrics_data.get("sections", [])
    
    lines = [
        "RDE (Rhythm / Dynamics / Emotion):",
        f"  Rhythm  : {rhythm}",
        f"  Dynamics: {dynamics}",
        f"  Emotion : {emotion}",
        "",
        f"Detected sections: {len(section_list)}"
    ]
    
    if section_list:
        for i, sec in enumerate(section_list):
            # Получаем имя секции из headers если доступно
            section_name = "?"
            if i < len(headers) and isinstance(headers[i], dict):
                section_name = headers[i].get("tag") or headers[i].get("label") or headers[i].get("name") or f"Section {i+1}"
            else:
                section_name = f"Section {i+1}"
            
            # Подсчитываем количество строк в секции
            if isinstance(sec, str):
                line_count = len(sec.split("\n"))
            elif isinstance(sec, dict):
                line_count = sec.get("line_count", len(sec.get("lines", [])))
            else:
                line_count = 0
            
            # Получаем вокальную технику и эмоцию для секции
            vocal_tech = "—"
            section_emotion = "—"
            if i < len(lyrics_sections) and isinstance(lyrics_sections[i], dict):
                vocal_tech = lyrics_sections[i].get("vocal_technique", "—")
                section_emotion = lyrics_sections[i].get("emotion", "—")
            
            section_info = f"  {i+1}. {section_name} ({line_count} строк)"
            if vocal_tech != "—":
                section_info += f" | Vocal: {vocal_tech}"
            if section_emotion != "—":
                section_info += f" | Emotion: {section_emotion}"
            
            lines.append(section_info)
    else:
        lines.append("  (no explicit sections)")
    
    return "\n".join(lines)

def build_tone_bpm_text(result):
    tone = result.get("tone", {}) if isinstance(result.get("tone"), dict) else {}
    style = result.get("style", {}) if isinstance(result.get("style"), dict) else {}
    bpm_val = result.get("bpm", "—")
    key_root = tone.get("key_root") or style.get("key_root")
    key_mode = tone.get("key_mode") or style.get("mode")
    key_full = tone.get("key_full") or style.get("key")
    color_sig = tone.get("color_signature") or style.get("color")
    resonance = tone.get("resonance_hz", "—")
    safe_octaves = tone.get("safe_octaves", [])
    return "\n".join([
        "Tone / Key / BPM:",
        f"  BPM: {bpm_val}",
        f"  Key root: {key_root or 'auto'}",
        f"  Mode: {key_mode or 'auto'}",
        f"  Key full: {key_full or 'auto'}",
        "",
        f"  Color signature: {color_sig or 'n/a'}",
        f"  Resonance Hz   : {resonance}",
        f"  Safe octaves   : {safe_octaves or 'n/a'}",
    ])

def build_genre_vocal_text(result):
    genre = result.get("genre", {}) if isinstance(result.get("genre"), dict) else {}
    style = result.get("style", {}) if isinstance(result.get("style"), dict) else {}
    vocal = result.get("vocal", {}) if isinstance(result.get("vocal"), dict) else {}
    primary = genre.get("primary") or style.get("genre")
    secondary = genre.get("secondary")
    hybrid = genre.get("hybrid")
    gender = vocal.get("gender") or result.get("final_gender_preference")
    form = vocal.get("form") or style.get("vocal_form")
    texture = vocal.get("texture")
    # Добавляем информацию о вокальных техниках для секций
    section_techniques = vocal.get("section_techniques", [])
    techniques_info = ""
    if section_techniques:
        techniques_info = "\n\nVocal Techniques by Section:"
        for idx, tech in enumerate(section_techniques):
            techniques_info += f"\n  Section {idx+1}: {tech}"
    return "\n".join([
        "Genre Fusion:",
        f"  Primary  : {primary or '—'}",
        f"  Secondary: {secondary or '—'}",
        f"  Hybrid   : {hybrid or '—'}",
        "",
        "Vocal Profile:",
        f"  Gender : {gender or 'auto'}",
        f"  Form   : {form or 'adaptive'}",
        f"  Texture: {texture or '—'}",
    ]) + techniques_info

def build_breath_map_text(result):
    diagnostics = result.get("diagnostics", {}) or {}
    breath = diagnostics.get("breathing") or diagnostics.get("zero_pulse") or {}
    if not breath:
        return "Breathing / ZeroPulse map не предоставлен ядром."
    lines = ["Breathing / ZeroPulse map:"]
    for k, v in breath.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)

def run_full_analysis(text, gender):
    if not text.strip():
        msg = "⚠️ Введите текст."
        return ("", "", "", "",
                "<div style='color:#ffcc33'>Empty input</div>",
                msg, "", "")
    try:
        result = engine.analyze(
            text=text,
            preferred_gender=gender if gender != "auto" else None,
        )
    except Exception as e:
        tb = traceback.format_exc()
        err = f"<div style='color:#ff5555'>Exception: {e}</div>"
        return ("", "", "", "", err, tb, "", "")
    style_p, lyrics_p, ui_t, fanf_t, summary_json = extract_main_outputs(result)
    pulse_html = build_core_pulse_timeline(result)
    tlp_pulse = build_tlp_pulse_text(result)
    rde_section = build_rde_section_text(result)
    tone_bpm = build_tone_bpm_text(result)
    genre_vocal = build_genre_vocal_text(result)
    lower_panel = "\n\n".join([
        tone_bpm, "", genre_vocal, "", build_breath_map_text(result)
    ])
    return (
        style_p,
        lyrics_p,
        ui_t,
        fanf_t,
        pulse_html,
        tlp_pulse,
        rde_section,
        lower_panel,
    )

def run_raw_diagnostics(text):
    if not text.strip():
        return {"error": "Пустой ввод."}
    try:
        result = engine.analyze(text=text, preferred_gender=None)
        return result if isinstance(result, dict) else {"raw_result": str(result)}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

theme_kwargs = {}
if gradio.__version__ >= "4.0.0":
    theme_kwargs["theme"] = gr.themes.Soft()

with gr.Blocks(title="StudioCore IMMORTAL v7 – Impulse Analysis", **theme_kwargs) as demo:

    gr.Markdown("# StudioCore IMMORTAL v7.0 — Impulse Analysis Engine")

    with gr.Row():
        with gr.Column(scale=3):
            txt_input = gr.Textbox(label="Введите текст", lines=14)
        with gr.Column(scale=1):
            gender_radio = gr.Radio(["auto", "male", "female"], value="auto", label="Пол вокала")
            analyze_btn = gr.Button("Анализировать", variant="primary")
            core_status_box = gr.Markdown("Готово к анализу.")

    gr.Markdown("## Core Pulse Timeline")
    pulse_html = gr.HTML("<div>Ожидание анализа…</div>")

    gr.Markdown("## Основные результаты")
    with gr.Tab("Style / Lyrics"):
        with gr.Row():
            style_out = gr.Textbox(label="Style Prompt", lines=8, show_copy_button=True)
            lyrics_out = gr.Textbox(label="Lyrics Prompt", lines=12, show_copy_button=True)

    with gr.Tab("Annotated UI / FANF"):
        with gr.Row():
            ui_text_out = gr.Textbox(label="Аннотированный текст", lines=14, show_copy_button=True)
            fanf_out = gr.Textbox(label="FANF", lines=14, show_copy_button=True)

    with gr.Tab("Impulse Panels"):
        with gr.Row():
            tlp_pulse_out = gr.Textbox(label="TLP Pulse", lines=8)
            rde_section_out = gr.Textbox(label="RDE / Sections", lines=8)
        lower_panel = gr.Textbox(label="Tone / BPM / Genre / Vocal / Breathing", lines=12)

    with gr.Tab("Diagnostics / JSON"):
        diag_input = gr.Textbox(label="Текст", lines=4)
        diag_btn = gr.Button("Диагностика")
        diag_json_out = gr.JSON(label="JSON")

    def _on_analyze(text, gender):
        style_p, lyrics_p, ui_t, fanf_t, pulse, tlp_txt, rde_txt, lower_txt = run_full_analysis(text, gender)
        return (
            style_p, lyrics_p, ui_t, fanf_t,
            pulse, tlp_txt, rde_txt, lower_txt,
            "Статус: готово."
        )

    analyze_btn.click(
        fn=_on_analyze,
        inputs=[txt_input, gender_radio],
        outputs=[style_out, lyrics_out, ui_text_out, fanf_out,
                 pulse_html, tlp_pulse_out, rde_section_out,
                 lower_panel, core_status_box],
    )

    diag_btn.click(fn=run_raw_diagnostics, inputs=[diag_input], outputs=[diag_json_out])

if __name__ == "__main__":
    import os
    # Конфигурация для деплоя
    server_port = int(os.getenv("PORT", 7860))
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    share = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=share
    )
