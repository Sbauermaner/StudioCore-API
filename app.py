# -*- coding: utf-8 -*-
"""
StudioCore IMMORTAL v7 — Premium UI v3 (Impulse Analysis Panel)

Gradio-based web interface for StudioCore text analysis engine.
Provides interactive UI for analyzing lyrics and generating style prompts.

Автор: Сергей Бауэр (@Sbauermaner)
"""

import json
import logging
import traceback
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


def extract_main_outputs(analysis_result):
    """Task 11.1: Safely extract main outputs with defaults for missing optional fields."""
    if not isinstance(analysis_result, dict):
        return "", "", "", "", "{}"

    # Task 11.1: Safe extraction with defaults
    fanf = (
        analysis_result.get("fanf", {})
        if isinstance(analysis_result.get("fanf"), dict)
        else {}
    )

    # Try multiple possible locations for style_prompt
    style_prompt = (
        fanf.get("style_prompt")
        or fanf.get("suno_style_prompt")
        or analysis_result.get("style_prompt")
        or analysis_result.get("suno_style_prompt")
        or analysis_result.get("fanf", {}).get("suno_style_prompt", "")
        or ""
    )

    # If style_prompt is still empty, construct it from available data
    if not style_prompt:
        style = (
            analysis_result.get("style", {})
            if isinstance(analysis_result.get("style"), dict)
            else {}
        )
        genre = style.get("genre") or style.get("style") or "adaptive"
        
        # Try to get mood from multiple sources
        mood = (
            style.get("mood")
            or style.get("atmosphere")
            or (analysis_result.get("emotions", {}) if isinstance(analysis_result.get("emotions"), dict) else {}).get("dominant")
            or "neutral"
        )
        
        bpm = analysis_result.get("bpm")
        if isinstance(bpm, dict):
            bpm_val = bpm.get("estimate") or bpm.get("target_bpm") or bpm
        else:
            bpm_val = bpm or "auto"
        
        key = analysis_result.get("key")
        if isinstance(key, dict):
            key_val = key.get("key") or key.get("key_root") or "auto"
        else:
            key_val = key or "auto"
        
        # Build style prompt string
        style_parts = []
        if genre and genre != "adaptive":
            style_parts.append(f"Genre: {genre}")
        if mood and mood != "neutral":
            style_parts.append(f"Mood: {mood}")
        if bpm_val and bpm_val != "auto" and bpm_val is not None:
            style_parts.append(f"BPM: {bpm_val}")
        if key_val and key_val != "auto" and key_val is not None:
            style_parts.append(f"Key: {key_val}")
        
        if style_parts:
            style_prompt = " | ".join(style_parts)
        else:
            style_prompt = "Genre: adaptive | Mood: neutral | BPM: auto | Key: auto"

    # Try multiple possible locations for lyrics_prompt
    lyrics_prompt = (
        fanf.get("lyrics_prompt")
        or fanf.get("suno_lyrics_prompt")
        or analysis_result.get("lyrics_prompt")
        or analysis_result.get("suno_lyrics_prompt")
        or analysis_result.get("fanf", {}).get("suno_lyrics_prompt", "")
        or ""
    )
    
    # If lyrics_prompt is still empty, use annotated_text_suno
    if not lyrics_prompt:
        lyrics_prompt = (
            analysis_result.get("annotated_text_suno")
            or analysis_result.get("annotated_text_ui")
            or ""
        )

    ui_text = (
        fanf.get("ui_text")
        or analysis_result.get("annotated_text")
        or analysis_result.get("annotated_text_ui")
        or ""
    )
    fanf_text = (
        fanf.get("full")
        or fanf.get("summary")
        or fanf.get("annotated_text_fanf")
        or ui_text
        or ""
    )
    try:
        summary_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        # Log the error but continue with fallback
        summary_json = str(analysis_result) if analysis_result else "{}"
        logging.getLogger(__name__).warning(
            "Failed to serialize result to JSON: %s", e
        )
    return style_prompt, lyrics_prompt, ui_text, fanf_text, summary_json


def build_core_pulse_timeline(analysis_result):
    """Build HTML timeline visualization for core pulse stages."""
    diagnostics = analysis_result.get("diagnostics", {}) or {}
    engines = (
        diagnostics.get("engines", {})
        if isinstance(diagnostics.get("engines"), dict)
        else {}
    )

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

    html = [
        "<div style='display:flex;gap:8px;align-items:center;font-family:monospace;'>"
    ]
    for label, key in stages:
        status = None
        # Task 15.1: Use .get() with defaults to prevent KeyErrors
        engine_data = engines.get(key)
        if isinstance(engine_data, dict):
            status = engine_data.get("status")
        elif isinstance(engine_data, str):
            status = engine_data
        color = status_to_color(status)
        html.append(
            f"""
        <div style="display:flex;flex-direction:column;"
             "align-items:center;">
          <div style="width:22px;height:22px;border-radius:6px;"
               "background:{color};box-shadow:0 0 6px rgba(0,0,0,0.4);"></div>
          <div style="font-size:10px;margin-top:3px;">{label}</div>
        </div>
        """
        )
    html.append("</div>")
    return "\n".join(html)


def build_tlp_pulse_text(analysis_result):
    """Task 11.1: Safely build TLP pulse text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "TLP Pulse: No data available"

    tlp = (
        analysis_result.get("tlp", {})
        if isinstance(analysis_result.get("tlp"), dict)
        else {}
    )
    truth = tlp.get("truth", 0.0)
    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    cf = tlp.get("conscious_frequency", tlp.get("cf", 0.0))

    def create_bar_visualization(value):
        """Create a visual bar representation of a value (0.0 to 1.0)."""
        value = max(0.0, min(1.0, float(value)))
        item = int(value * 20)
        return "█" * item + "·" * (20 - item)

    return "\n".join(
        [
            f"Truth: {truth:.2f} |{create_bar_visualization(truth)}|",
            f"Love : {love:.2f} |{create_bar_visualization(love)}|",
            f"Pain : {pain:.2f} |{create_bar_visualization(pain)}|",
            "",
            f"Conscious Frequency (CF): {cf:.3f}",
        ]
    )


def build_rde_section_text(analysis_result):
    """Task 11.1: Safely build RDE section text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "RDE / Sections: No data available"

    rde = (
        analysis_result.get("rde", {})
        if isinstance(analysis_result.get("rde"), dict)
        else {}
    )
    rhythm = rde.get("rhythm", rde.get("resonance", "balanced"))
    dynamics = rde.get("dynamics", rde.get("fracture", "stable"))
    emotion = rde.get("emotion", rde.get("entropy", "neutral"))
    structure = (
        analysis_result.get("structure", {})
        if isinstance(analysis_result.get("structure"), dict)
        else {}
    )
    section_list = structure.get("sections") or []
    headers = structure.get("headers") or []

    # Task 11.1: Safe extraction of fanf and lyrics_sections with defaults
    fanf = (
        analysis_result.get("fanf", {})
        if isinstance(analysis_result.get("fanf"), dict)
        else {}
    )
    lyrics_sections = fanf.get("lyrics_sections") or []
    if not lyrics_sections:
        # Пытаемся получить из другого места
        lyrics_data = (
            analysis_result.get("lyrics", {})
            if isinstance(analysis_result.get("lyrics"), dict)
            else {}
        )
        lyrics_sections = lyrics_data.get("sections", [])

    lines = [
        "RDE (Rhythm / Dynamics / Emotion):",
        f"  Rhythm  : {rhythm}",
        f"  Dynamics: {dynamics}",
        f"  Emotion : {emotion}",
        "",
        f"Detected sections: {len(section_list)}",
    ]

    if section_list:
        for i, sec in enumerate(section_list):
            # Получаем имя секции из headers если доступно
            section_name = "?"
            if i < len(headers) and isinstance(headers[i], dict):
                section_name = (
                    headers[i].get("tag")
                    or headers[i].get("label")
                    or headers[i].get("name")
                    or f"Section {i + 1}"
                )
            else:
                section_name = f"Section {i + 1}"

            # Подсчитываем количество строк в секции
            if isinstance(sec, str):
                line_count = len(sec.split("\n"))
            elif isinstance(sec, dict):
                line_count = sec.get("line_count", len(sec.get("lines", [])))
            else:
                line_count = 0

            # Получаем вокальную технику и эмоцию для секции
            vocal_tech = None
            section_emotion = None
            if i < len(lyrics_sections) and isinstance(lyrics_sections[i], dict):
                vocal_tech = lyrics_sections[i].get("vocal_technique")
                section_emotion = lyrics_sections[i].get("emotion")

            section_info = f"  {i + 1}. {section_name} ({line_count} строк)"
            if vocal_tech and vocal_tech != "adaptive":
                section_info += f" | Vocal: {vocal_tech}"
            if section_emotion and section_emotion != "neutral":
                section_info += f" | Emotion: {section_emotion}"

            lines.append(section_info)
    else:
        lines.append("  (no explicit sections)")

    return "\n".join(lines)


def build_tone_bpm_text(analysis_result):
    """Task 11.1: Safely build tone/bpm text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "Tone / Key / BPM: No data available"

    tone = (
        analysis_result.get("tone", {})
        if isinstance(analysis_result.get("tone"), dict)
        else {}
    )
    style = (
        analysis_result.get("style", {})
        if isinstance(analysis_result.get("style"), dict)
        else {}
    )
    rde = (
        analysis_result.get("rde", {})
        if isinstance(analysis_result.get("rde"), dict)
        else {}
    )
    bpm_val = analysis_result.get("bpm", "auto")
    key_root = tone.get("key_root") or style.get("key_root") or None
    key_mode = tone.get("key_mode") or style.get("mode") or None
    key_full = tone.get("key_full") or style.get("key") or analysis_result.get("key") or None
    
    # Fix Color signature: try color_wave, color_signature, or color_temperature
    color_wave = analysis_result.get("color_wave", [])
    if isinstance(color_wave, list) and color_wave:
        color_sig = ", ".join(color_wave)
    else:
        color_sig = (
            style.get("color_signature")
            or style.get("color_temperature")
            or tone.get("color_signature")
            or style.get("color")
            or None
        )
    
    # Fix Resonance Hz: try rde.resonance_hz, or compute from key
    resonance = rde.get("resonance_hz") or tone.get("resonance_hz")
    if not resonance:
        # Compute from key if available
        key_str = str(key_full or "").upper() if key_full else ""
        if key_str:
            # Extract key root (first letter)
            key_root_char = key_str.split()[0] if key_str else ""
            # Base frequencies for common keys
            key_freq_map = {
                "C": 130.81, "C#": 138.59, "D": 146.83, "D#": 155.56,
                "E": 164.81, "F": 174.61, "F#": 185.00, "G": 196.00,
                "G#": 207.65, "A": 220.00, "A#": 233.08, "B": 246.94,
            }
            base_freq = key_freq_map.get(key_root_char, 130.81)
            # Minor keys typically ~10Hz lower
            if "minor" in key_str.lower():
                base_freq -= 10.0
            resonance = round(base_freq, 2)
        else:
            resonance = "auto"
    
    safe_octaves = (
        tone.get("safe_octaves", [])
        if isinstance(tone.get("safe_octaves"), list)
        else []
    )
    return "\n".join(
        [
            "Tone / Key / BPM:",
            f"  BPM: {bpm_val}",
            f"  Key root: {key_root or 'auto'}",
            f"  Mode: {key_mode or 'auto'}",
            f"  Key full: {key_full or 'auto'}",
            "",
            f"  Color signature: {color_sig or 'adaptive'}",
            f"  Resonance Hz   : {resonance}",
            f"  Safe octaves   : {safe_octaves if safe_octaves else 'auto'}",
        ]
    )


def build_genre_vocal_text(analysis_result):
    """Task 11.1: Safely build genre/vocal text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "Genre Fusion / Vocal Profile: No data available"

    genre = (
        analysis_result.get("genre", {})
        if isinstance(analysis_result.get("genre"), dict)
        else {}
    )
    style = (
        analysis_result.get("style", {})
        if isinstance(analysis_result.get("style"), dict)
        else {}
    )
    vocal = (
        analysis_result.get("vocal", {})
        if isinstance(analysis_result.get("vocal"), dict)
        else {}
    )
    primary = genre.get("primary") or style.get("genre") or None
    secondary = genre.get("secondary") or style.get("secondary") or None
    hybrid = genre.get("hybrid") or None
    
    # Infer Secondary/Hybrid from Primary if empty
    if primary and not secondary:
        primary_lower = str(primary).lower()
        # Genre inference map
        genre_inference = {
            "cinematic": "Ambient / Orchestral",
            "lyrical": "Folk / Acoustic",
            "electronic": "Synth / Ambient",
            "rock": "Alternative / Indie",
            "folk": "Acoustic / Traditional",
            "jazz": "Smooth / Bossa",
            "blues": "Soul / R&B",
            "pop": "Indie / Alternative",
            "metal": "Progressive / Hard",
            "hip-hop": "Trap / R&B",
            "country": "Folk / Americana",
            "classical": "Orchestral / Chamber",
        }
        for key, value in genre_inference.items():
            if key in primary_lower:
                secondary = value
                break
        # If still empty, try to extract from hybrid genre name
        if not secondary and "hybrid" in primary_lower:
            parts = primary_lower.replace(" hybrid", "").split()
            if len(parts) >= 2:
                secondary = parts[1].capitalize()
    
    # If hybrid is empty but primary contains "hybrid", extract it
    if primary and not hybrid and "hybrid" in str(primary).lower():
        hybrid = primary
    
    gender = (
        vocal.get("gender")
        or analysis_result.get("final_gender_preference")
        or None
    )
    form = vocal.get("form") or style.get("vocal_form") or None
    texture = vocal.get("texture") or None
    # Task 11.1: Safe extraction of section_techniques with default
    section_techniques = (
        vocal.get("section_techniques", [])
        if isinstance(vocal.get("section_techniques"), list)
        else []
    )
    techniques_info = ""
    if section_techniques:
        techniques_info = "\n\nVocal Techniques by Section:"
        for idx, tech in enumerate(section_techniques):
            techniques_info += f"\n  Section {idx + 1}: {tech}"
    
    # Build output - don't show "—" for empty fields, show inferred or skip
    genre_lines = ["Genre Fusion:", f"  Primary  : {primary or 'adaptive'}"]
    if secondary:
        genre_lines.append(f"  Secondary: {secondary}")
    if hybrid:
        genre_lines.append(f"  Hybrid   : {hybrid}")
    genre_lines.append("")
    
    return (
        "\n".join(
            genre_lines
            + [
                "Vocal Profile:",
                f"  Gender : {gender or 'auto'}",
                f"  Form   : {form or 'adaptive'}",
                f"  Texture: {texture or 'dynamic'}",
            ]
        )
        + techniques_info
    )


def build_breath_map_text(analysis_result, text=None):
    """Task 11.1: Safely build breath map text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "Breathing / ZeroPulse map: No data available"

    # Try to get breathing data from multiple locations
    breathing = analysis_result.get("breathing") or {}
    zeropulse = analysis_result.get("zeropulse") or {}
    diagnostics = analysis_result.get("diagnostics", {}) or {}
    breath = (
        breathing
        or zeropulse
        or diagnostics.get("breathing")
        or diagnostics.get("zero_pulse")
        or {}
    )
    
    if breath and isinstance(breath, dict):
        lines = ["Breathing / ZeroPulse map:"]
        try:
            for k, v in breath.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)
        except (AttributeError, TypeError):
            pass
    
    # If no breathing data, generate ASCII visualization from text structure
    if text:
        return _generate_breathing_ascii(text)
    
    # Try to extract text from annotated_text_ui or annotated_text_suno
    text_source = (
        analysis_result.get("annotated_text_ui")
        or analysis_result.get("annotated_text_suno")
        or ""
    )
    if text_source:
        # Extract original text (remove annotations)
        import re
        # Remove annotation markers like [INTRO - mood: ...]
        clean_text = re.sub(r'\[.*?\]', '', text_source)
        # Remove BPM/key markers
        clean_text = re.sub(r'\[\d+\s+BPM.*?\]', '', clean_text)
        if clean_text.strip():
            return _generate_breathing_ascii(clean_text)
    
    return "Breathing / ZeroPulse map: No data available"


def _generate_breathing_ascii(text):
    """
    Generate ASCII visualization of breathing pattern from text structure.
    Short lines = (..) (inhale), Long lines = [=====] (exhale).
    """
    if not text:
        return "Breathing / ZeroPulse map: No text available"
    
    lines = text.split('\n')
    breathing_lines = ["Breathing / ZeroPulse map (ASCII visualization):", ""]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_length = len(line)
        # Short lines (<= 30 chars) = inhale (..)
        # Long lines (> 30 chars) = exhale [=====]
        if line_length <= 30:
            breathing_lines.append(f"(..) {line[:50]}")
        else:
            # Create visual bar proportional to line length
            bar_length = min(20, line_length // 3)
            bar = "=" * bar_length
            breathing_lines.append(f"[{bar}] {line[:50]}")
    
    return "\n".join(breathing_lines)


def run_full_analysis(text, gender):
    """
    Run full analysis on input text and return formatted results.

    Args:
        text: Input text to analyze
        gender: Preferred gender for vocal analysis

    Returns:
        Tuple of formatted output strings for UI display
    """
    if not text.strip():
        msg = "⚠️ Введите текст."
        return (
            "",
            "",
            "",
            "",
            "<div style='color:#ffcc33'>Empty input</div>",
            msg,
            "",
            "",
        )
    try:
        analysis_result = engine.analyze(
            text=text,
            preferred_gender=gender if gender != "auto" else None,
        )
    except (AttributeError, TypeError, ValueError, RuntimeError) as e:
        tb = traceback.format_exc()
        err = f"<div style='color:#ff5555'>Exception: {e}</div>"
        return ("", "", "", "", err, tb, "", "")
    style_p, lyrics_p, ui_t, fanf_t, _ = extract_main_outputs(analysis_result)
    pulse_html_output = build_core_pulse_timeline(analysis_result)
    tlp_pulse = build_tlp_pulse_text(analysis_result)
    rde_section = build_rde_section_text(analysis_result)
    tone_bpm = build_tone_bpm_text(analysis_result)
    genre_vocal = build_genre_vocal_text(analysis_result)
    lower_panel_output = "\n\n".join(
        [
            tone_bpm,
            "",
            genre_vocal,
            "",
            build_breath_map_text(analysis_result, text=text),
        ]
    )
    return (
        style_p,
        lyrics_p,
        ui_t,
        fanf_t,
        pulse_html_output,
        tlp_pulse,
        rde_section,
        lower_panel_output,
    )


def run_raw_diagnostics(text):
    """Run raw diagnostics analysis and return full result as JSON."""
    if not text.strip():
        return {"error": "Пустой ввод."}
    try:
        analysis_result = engine.analyze(text=text, preferred_gender=None)
        return (
            analysis_result
            if isinstance(analysis_result, dict)
            else {"raw_result": str(analysis_result)}
        )
    except (AttributeError, TypeError, ValueError, RuntimeError) as e:
        return {"error": str(e), "traceback": traceback.format_exc()}


def _build_theme_kwargs():
    """
    Build theme kwargs safely.
    Some Gradio versions don't support theme parameter for gr.Blocks().
    This function safely checks and only returns theme if supported.
    """
    try:
        # Check Gradio version
        version = gr.__version__
        version_parts = version.split(".")
        major = int(version_parts[0])

        # Theme support check: only for Gradio 4.0+
        if major < 4:
            return {}

        # Try to check if Blocks.__init__ accepts 'theme' parameter
        import inspect  # pylint: disable=import-outside-toplevel
        try:
            blocks_init = gr.Blocks.__init__
            sig = inspect.signature(blocks_init)

            # Check if 'theme' is in the signature
            if 'theme' not in sig.parameters:
                # Theme parameter not supported in this Gradio version
                return {}

            # If we get here, theme is supported, try to create it
            try:
                theme_obj = gr.themes.Soft()
                return {"theme": theme_obj}
            except (AttributeError, TypeError):
                # Themes module not available
                return {}

        except (AttributeError, TypeError, ValueError):
            # Can't inspect signature, play it safe
            return {}

    except (AttributeError, TypeError, ValueError, ImportError):
        # Any error: don't use theme
        return {}


def _safe_textbox_kwargs(**kwargs):
    """
    Safely create Textbox kwargs, removing unsupported parameters.
    This ensures compatibility with older Gradio versions that don't support certain features.
    """
    # Check if show_copy_button is requested
    if kwargs.get('show_copy_button', False):
        try:
            # Try to check if Textbox.__init__ accepts 'show_copy_button'
            import inspect  # pylint: disable=import-outside-toplevel
            sig = inspect.signature(gr.Textbox.__init__)
            if 'show_copy_button' not in sig.parameters:
                # Remove show_copy_button if not supported
                kwargs = {k: v for k, v in kwargs.items() if k != 'show_copy_button'}
        except (AttributeError, TypeError, ValueError):
            # Can't inspect, remove show_copy_button to be safe
            kwargs = {k: v for k, v in kwargs.items() if k != 'show_copy_button'}

    # Check if max_lines is requested
    if 'max_lines' in kwargs:
        try:
            import inspect  # pylint: disable=import-outside-toplevel
            sig = inspect.signature(gr.Textbox.__init__)
            if 'max_lines' not in sig.parameters:
                # Remove max_lines if not supported
                kwargs = {k: v for k, v in kwargs.items() if k != 'max_lines'}
        except (AttributeError, TypeError, ValueError):
            # Can't inspect, remove max_lines to be safe
            kwargs = {k: v for k, v in kwargs.items() if k != 'max_lines'}

    return kwargs


theme_kwargs = _build_theme_kwargs()

with gr.Blocks(
    title="StudioCore IMMORTAL v7 – Impulse Analysis", **theme_kwargs
) as demo:
    gr.Markdown("# StudioCore IMMORTAL v7.0 — Impulse Analysis Engine")

    with gr.Row():
        with gr.Column(scale=3):
            txt_input = gr.Textbox(label="Введите текст", lines=14)
        with gr.Column(scale=1):
            gender_radio = gr.Radio(
                ["auto", "male", "female"], value="auto", label="Пол вокала"
            )
            analyze_btn = gr.Button("Анализировать", variant="primary")
            clear_btn = gr.Button("Очистить", variant="secondary", size="sm")
            core_status_box = gr.Markdown("Готово к анализу.")

    gr.Markdown("## Core Pulse Timeline")
    pulse_html = gr.HTML("<div>Ожидание анализа…</div>")

    gr.Markdown("## Основные результаты")
    with gr.Tab("Style / Lyrics"):
        with gr.Row():
            style_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="Style Prompt",
                    lines=15,
                    max_lines=50,
                    show_copy_button=True,
                    interactive=False,
                )
            )
            lyrics_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="Lyrics Prompt",
                    lines=15,
                    max_lines=50,
                    show_copy_button=True,
                    interactive=False,
                )
            )

    with gr.Tab("Annotated UI / FANF"):
        with gr.Row():
            ui_text_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="Аннотированный текст",
                    lines=20,
                    max_lines=100,
                    show_copy_button=True,
                    interactive=False,
                )
            )
            fanf_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="FANF",
                    lines=20,
                    max_lines=100,
                    show_copy_button=True,
                    interactive=False,
                )
            )

    with gr.Tab("Impulse Panels"):
        with gr.Row():
            tlp_pulse_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="TLP Pulse",
                    lines=12,
                    max_lines=30,
                    show_copy_button=True,
                    interactive=False,
                )
            )
            rde_section_out = gr.Textbox(
                **_safe_textbox_kwargs(
                    label="RDE / Sections",
                    lines=12,
                    max_lines=50,
                    show_copy_button=True,
                    interactive=False,
                )
            )
        lower_panel = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Tone / BPM / Genre / Vocal / Breathing",
                lines=15,
                max_lines=60,
                show_copy_button=True,
                interactive=False,
            )
        )

    with gr.Tab("Diagnostics / JSON"):
        diag_input = gr.Textbox(label="Текст", lines=4)
        diag_btn = gr.Button("Диагностика")
        diag_json_out = gr.JSON(label="JSON")

    def _on_analyze(text, gender):
        style_p, lyrics_p, ui_t, fanf_t, pulse, tlp_txt, rde_txt, lower_txt = (
            run_full_analysis(text, gender)
        )
        return (
            style_p,
            lyrics_p,
            ui_t,
            fanf_t,
            pulse,
            tlp_txt,
            rde_txt,
            lower_txt,
            "Статус: готово.",
        )

    # pylint: disable=no-member
    analyze_btn.click(
        fn=_on_analyze,
        inputs=[txt_input, gender_radio],
        outputs=[
            style_out,
            lyrics_out,
            ui_text_out,
            fanf_out,
            pulse_html,
            tlp_pulse_out,
            rde_section_out,
            lower_panel,
            core_status_box,
        ],
    )

    # pylint: disable=no-member
    diag_btn.click(
        fn=run_raw_diagnostics, inputs=[diag_input], outputs=[diag_json_out]
    )

    # Clear button functionality
    # pylint: disable=no-member
    clear_btn.click(fn=lambda: "", inputs=None, outputs=[txt_input])

if __name__ == "__main__":
    import os
    import sys

    # Handle --test flag
    if "--test" in sys.argv:
        print("=" * 80)
        print("StudioCore App Test Mode")
        print("=" * 80)
        print()

        try:
            # StudioCoreV6 already imported at top level, reuse it
            core = StudioCoreV6()
            print("✅ StudioCoreV6 initialized successfully")
            print()

            # Test analyze with sample text
            sample_input_text = "[Verse 1]\nTest lyrics for app test"
            print("Testing analyze() with sample text...")
            test_result = core.analyze(sample_input_text)

            if isinstance(test_result, dict):
                print("✅ analyze() returned valid dict")
                print(f"   Keys: {list(test_result.keys())[:10]}...")
            else:
                print(
                    f"⚠️  analyze() returned unexpected type: {type(test_result)}"
                )

            print()
            print("=" * 80)
            print("✅ App test completed successfully")
            print("=" * 80)
            sys.exit(0)

        except (AttributeError, TypeError, ValueError, RuntimeError) as e:
            print(f"❌ App test failed: {e}")
            traceback.print_exc()
            sys.exit(1)

    # Конфигурация для деплоя
    port_str = os.getenv("PORT", "7860")
    server_port = int(port_str) if port_str.isdigit() else 7860
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    share = os.getenv("GRADIO_SHARE", "False").lower() == "true"

    demo.launch(server_name=server_name, server_port=server_port, share=share)
