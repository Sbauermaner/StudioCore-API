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


def visualize_breathing_ascii(breathing_data):
    """Converts breathing points into a visual timeline string."""
    if not breathing_data or not isinstance(breathing_data, dict):
        return "No breathing data available."
    
    if 'breathing_points' not in breathing_data:
        return "No breathing data available."
    
    points = breathing_data.get('breathing_points', [])
    if not isinstance(points, list) or not points:
        return "No breathing data available."
    
    # Sort points by position
    try:
        points = sorted(points, key=lambda x: x.get('position', 0) if isinstance(x, dict) else 0)
    except (TypeError, AttributeError):
        return "No breathing data available."
    
    timeline = []
    for i, pt in enumerate(points):
        if not isinstance(pt, dict):
            continue
        
        # Calculate gap since last point (scaled down)
        prev = points[i-1].get('position', 0) if i > 0 and isinstance(points[i-1], dict) else 0
        gap = pt.get('position', 0) - prev
        
        # Draw flow line
        flow = "_" * min(int(gap / 15), 5)
        if gap > 50:
            flow = "~~~~" + flow
        timeline.append(flow)
        
        # Draw breath marker
        if pt.get('type') == 'long':
            timeline.append(" [💨 DEEP] ")
        else:
            timeline.append(" (•) ")
    
    result = "".join(timeline)
    # Truncate for UI
    if len(result) > 120:
        result = result[:120] + "..."
    return result if result else "No breathing data available."


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

    # BRIDGE LOGIC: Use pre-cooked Suno prompt from monolith (if available)
    # Otherwise, construct from Matrix Architecture data
    style = (
        analysis_result.get("style", {})
        if isinstance(analysis_result.get("style"), dict)
        else {}
    )
    
    # ============================================================
    # 🥇 ИЕРАРХИЯ ПРИОРИТЕТОВ ДЛЯ STYLE OUTPUT (ЗОЛОТОЙ СТАНДАРТ ПЕРВЫМ)
    # ============================================================
    # 1. 🥇 ЗОЛОТОЙ СТАНДАРТ: FusionEngine.suno_style_prompt
    #    - Объединяет все источники (emotion, bpm, tonality, color, instrumentation, vocal)
    #    - Самый точный и полный промпт
    # 2. 🥈 ВЫСОКИЙ: build_suno_prompt (legacy bridge)
    #    - Профессиональный форматтер с Matrix Architecture данными
    #    - Формат: [GENRE: ...] [MOOD: ...] [INSTRUMENTATION: ...] и т.д.
    # 3. 🥉 СРЕДНИЙ: style.suno_style_prompt_fusion (альтернативный fusion)
    #    - Альтернативный промпт от FusionEngine (если основной недоступен)
    # 4. 📊 ДОПОЛНИТЕЛЬНЫЙ: style.suno_style_prompt_alt (SunoPromptEngine)
    #    - Альтернативный формат от SunoPromptEngine.get_style_prompt()
    # 5. 🗺️ МАППИНГ: style.suno_style_from_routing (GenreRoutingEngine)
    #    - Suno стиль из GenreRoutingEngine.SUNO_STYLE маппинга
    # 6. 🔧 FALLBACK: Ручная конструкция из Matrix данных
    # ============================================================
    
    fusion = analysis_result.get("fusion", {})
    suno_style_output = (
        fusion.get("suno_style_prompt", "")  # 🥇 ЗОЛОТОЙ СТАНДАРТ: FusionEngine (объединяет все источники)
        or style.get("suno_ready_prompt", "")  # 🥈 ВЫСОКИЙ: Legacy bridge (профессиональный форматтер)
        or style.get("suno_style_prompt_fusion", "")  # 🥉 СРЕДНИЙ: Альтернативный fusion промпт
        or style.get("suno_style_prompt_alt", "")  # 📊 ДОПОЛНИТЕЛЬНЫЙ: SunoPromptEngine альтернатива
        or style.get("suno_style_from_routing", "")  # 🗺️ МАППИНГ: GenreRoutingEngine маппинг
        or ""
    )
    
    # If not available or contains error, construct it manually (fallback)
    # 🔧 ИСПРАВЛЕНИЕ: Безопасная конструкция fallback промпта
    if not suno_style_output or (isinstance(suno_style_output, str) and "Error" in suno_style_output):
        genre = style.get("genre") or style.get("style") or "Unknown"
        if not isinstance(genre, str):
            genre = str(genre) if genre else "Unknown"
        
        # Get instruments from style (Matrix Architecture)
        instruments_list = style.get("instruments", [])
        if isinstance(instruments_list, list) and len(instruments_list) > 0:
            try:
                instruments_str = ", ".join(str(instr) for instr in instruments_list)
            except (TypeError, AttributeError):
                instruments_str = "None"
        else:
            instruments_str = "None"
        
    # Extract BPM
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение BPM
    bpm = analysis_result.get("bpm")
    if isinstance(bpm, dict):
        bpm_val = bpm.get("estimate") or bpm.get("target_bpm") or bpm.get("bpm") or "Auto"
    elif isinstance(bpm, (int, float)):
        bpm_val = int(bpm)
    else:
        bpm_val = str(bpm) if bpm else "Auto"
        
    # Extract Key
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение Key
    key = analysis_result.get("key")
    if isinstance(key, dict):
        key_val = key.get("key") or key.get("key_root") or key.get("key_full") or "Auto"
    elif isinstance(key, str):
        key_val = key
    else:
        key_val = str(key) if key else "Auto"
        
        # Get Mood (Dominant Emotion)
        # 🔧 ИСПРАВЛЕНИЕ: Безопасное получение mood из emotions
        emotions = analysis_result.get("emotions", {})
        if isinstance(emotions, dict) and len(emotions) > 0:
            # Get the dominant emotion (highest value) - безопасно
            try:
                mood = max(emotions, key=emotions.get)
            except (ValueError, TypeError):
                mood = list(emotions.keys())[0] if emotions else "neutral"
        else:
            # Fallback to style mood
            mood = (
                style.get("mood")
                or style.get("atmosphere")
                or "neutral"
            )
        
        # BRIDGE: Combine New Brain + Old Format (fallback)
        # Format: "Genre | Instruments | Mood | BPM BPM | Key"
        suno_style_output = f"{genre} | {instruments_str} | {mood} | {bpm_val} BPM | {key_val}"
    
    # Use the retrieved or constructed prompt
    style_prompt = suno_style_output
    
    # Add Matrix Architecture metadata to style_prompt (additional info)
    # These are added as metadata below the main Suno format string
    source = style.get("genre_source", "Legacy")
    
    # Add emotion-driven style if available (from EmotionDrivenSunoAdapter)
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение emotion_driven
    emotion_driven = analysis_result.get("emotion_driven_annotations", {})
    if isinstance(emotion_driven, dict) and emotion_driven.get("style") and "🎭 Emotion Style:" not in style_prompt:
        style_prompt += f"\n🎭 Emotion Style: {emotion_driven.get('style')}"
    
    # Add hybrid genre info if available
    # 🔧 ИСПРАВЛЕНИЕ: Безопасная проверка hybrid genre
    if isinstance(style, dict) and style.get("is_hybrid") and style.get("secondary_genre"):
        if "🎶 Hybrid:" not in style_prompt:
            style_prompt += f"\n🎶 Hybrid Genre: {style.get('secondary_genre')}"
    
    if "⚙️ Engine:" not in style_prompt:
        style_prompt += f"\n⚙️ Engine: {source}"
    
    # Get breathing visualization - always add as metadata
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение breathing_data
    breathing_data = analysis_result.get("breathing", {})
    if not isinstance(breathing_data, dict):
        breathing_data = {}
    breath_vis = visualize_breathing_ascii(breathing_data)
    if breath_vis and isinstance(breath_vis, str) and breath_vis != "No breathing data available.":
        if "🫁 Breathing Map:" not in style_prompt:
            style_prompt += f"\n🫁 Breathing Map: {breath_vis}"

    # ============================================================
    # 🥇 ИЕРАРХИЯ ПРИОРИТЕТОВ ДЛЯ LYRICS OUTPUT (ЗОЛОТОЙ СТАНДАРТ ПЕРВЫМ)
    # ============================================================
    # 1. 🥇 ЗОЛОТОЙ СТАНДАРТ: FusionEngine.suno_lyrics_prompt
    #    - Эмоциональное ядро с TLP данными
    #    - Формат: (mood: ...) (dominant_emotion: ...) (TLP: ...)
    # 2. 🥈 ВЫСОКИЙ: suno_safe_annotations (SunoAnnotationEngine)
    #    - Безопасные аннотации с BPM, Key, Genre, Mood, Energy, Arrangement
    #    - Формат: [Section Tag] (BPM:xxx) (Key:x) (Genre:x) (Mood:x, Energy:x, Arrangement:x)
    # 3. 🥉 СРЕДНИЙ: annotated_text_suno (улучшен SunoPromptEngine)
    #    - Стандартный аннотированный текст с расширенными тегами
    #    - Использует construct_section, experimental_stack для улучшения
    # 4. 📊 ДОПОЛНИТЕЛЬНЫЙ: style.suno_lyrics_prompt_fusion
    #    - Альтернативный lyrics промпт от FusionEngine
    # 5. 🔧 FALLBACK: annotated_text_ui или другие источники
    # ============================================================
    
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение suno_safe_annotations
    suno_safe_annotations = analysis_result.get("suno_safe_annotations", [])
    if not isinstance(suno_safe_annotations, list):
        suno_safe_annotations = []
    
    # Безопасное объединение аннотаций
    safe_annotations_str = ""
    if suno_safe_annotations:
        try:
            safe_annotations_str = "\n".join(str(ann) for ann in suno_safe_annotations)
        except (TypeError, AttributeError):
            safe_annotations_str = ""
    
    suno_lyrics_output = (
        fusion.get("suno_lyrics_prompt", "") if isinstance(fusion, dict) else ""  # 🥇 ЗОЛОТОЙ СТАНДАРТ: FusionEngine (эмоциональное ядро + TLP)
        or safe_annotations_str  # 🥈 ВЫСОКИЙ: Safe annotations (BPM, Key, Genre, Mood)
        or (analysis_result.get("annotated_text_suno", "") if isinstance(analysis_result.get("annotated_text_suno"), str) else "")  # 🥉 СРЕДНИЙ: Улучшенный аннотированный текст
        or (style.get("suno_lyrics_prompt_fusion", "") if isinstance(style, dict) else "")  # 📊 ДОПОЛНИТЕЛЬНЫЙ: Альтернативный fusion lyrics
        or ""
    )
    
    # If it's empty, fallback to annotated_text_ui
    # 🔧 ИСПРАВЛЕНИЕ: Безопасный fallback с проверками типов
    if not suno_lyrics_output:
        fallback_fanf = analysis_result.get("fanf", {})
        if not isinstance(fallback_fanf, dict):
            fallback_fanf = {}
        
        suno_lyrics_output = (
            (fanf.get("lyrics_prompt") if isinstance(fanf.get("lyrics_prompt"), str) else None)
            or (fanf.get("suno_lyrics_prompt") if isinstance(fanf.get("suno_lyrics_prompt"), str) else None)
            or (analysis_result.get("lyrics_prompt") if isinstance(analysis_result.get("lyrics_prompt"), str) else None)
            or (analysis_result.get("suno_lyrics_prompt") if isinstance(analysis_result.get("suno_lyrics_prompt"), str) else None)
            or (fallback_fanf.get("suno_lyrics_prompt", "") if isinstance(fallback_fanf.get("suno_lyrics_prompt"), str) else None)
            or (analysis_result.get("annotated_text_ui", "") if isinstance(analysis_result.get("annotated_text_ui"), str) else "")
            or ""
        )
    
    # Use the retrieved lyrics
    lyrics_prompt = suno_lyrics_output

    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение ui_text и fanf_text с проверками типов
    ui_text = (
        (fanf.get("ui_text") if isinstance(fanf.get("ui_text"), str) else None)
        or (analysis_result.get("annotated_text") if isinstance(analysis_result.get("annotated_text"), str) else None)
        or (analysis_result.get("annotated_text_ui") if isinstance(analysis_result.get("annotated_text_ui"), str) else None)
        or ""
    )
    fanf_text = (
        (fanf.get("full") if isinstance(fanf.get("full"), str) else None)
        or (fanf.get("summary") if isinstance(fanf.get("summary"), str) else None)
        or (fanf.get("annotated_text_fanf") if isinstance(fanf.get("annotated_text_fanf"), str) else None)
        or (ui_text if isinstance(ui_text, str) else "")
        or ""
    )
    # 🔧 ИСПРАВЛЕНИЕ: Улучшенная обработка JSON сериализации
    try:
        summary_json = json.dumps(analysis_result, ensure_ascii=False, indent=2, default=str)
    except (TypeError, ValueError) as e:
        # Log the error but continue with fallback
        summary_json = str(analysis_result) if analysis_result else "{}"
        logging.getLogger(__name__).warning(
            "Failed to serialize result to JSON: %s", e
        )
    except Exception as e:
        # Catch-all для неожиданных ошибок
        logging.getLogger(__name__).error(
            "Unexpected error serializing result to JSON: %s", e, exc_info=True
        )
        summary_json = "{}"
    return style_prompt, lyrics_prompt, ui_text, fanf_text, summary_json


def build_core_pulse_timeline(analysis_result):
    """Build HTML timeline visualization for core pulse stages."""
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение diagnostics
    if not isinstance(analysis_result, dict):
        return "<div style='color:#ff5555'>No data available</div>"
    
    diagnostics = analysis_result.get("diagnostics", {}) or {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    
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
        # 🔧 ИСПРАВЛЕНИЕ: Безопасная обработка status
        if status is None:
            return "#555555"
        try:
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
        except (AttributeError, TypeError):
            return "#777777"

    html = [
        "<div style='display:flex;gap:8px;align-items:center;font-family:monospace;'>"
    ]
    for label, key in stages:
        status = None
        # Task 15.1: Use .get() with defaults to prevent KeyErrors
        # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение engine_data
        engine_data = engines.get(key) if isinstance(engines, dict) else None
        if isinstance(engine_data, dict):
            status = engine_data.get("status")
        elif isinstance(engine_data, str):
            status = engine_data
        elif engine_data is not None:
            # Fallback для других типов
            try:
                status = str(engine_data)
            except (TypeError, AttributeError):
                status = None
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
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение TLP значений с проверкой типов
    truth = float(tlp.get("truth", 0.0)) if isinstance(tlp.get("truth"), (int, float)) else 0.0
    love = float(tlp.get("love", 0.0)) if isinstance(tlp.get("love"), (int, float)) else 0.0
    pain = float(tlp.get("pain", 0.0)) if isinstance(tlp.get("pain"), (int, float)) else 0.0
    cf_raw = tlp.get("conscious_frequency") or tlp.get("cf", 0.0)
    cf = float(cf_raw) if isinstance(cf_raw, (int, float)) else 0.0

    def create_bar_visualization(value):
        """Create a visual bar representation of a value (0.0 to 1.0)."""
        # 🔧 ИСПРАВЛЕНИЕ: Безопасное преобразование value
        try:
            value = max(0.0, min(1.0, float(value)))
            item = int(value * 20)
            return "█" * item + "·" * (20 - item)
        except (TypeError, ValueError, OverflowError):
            return "·" * 20  # Fallback для невалидных значений

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
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение RDE значений
    rhythm = rde.get("rhythm") or rde.get("resonance") or "balanced"
    if not isinstance(rhythm, str):
        rhythm = str(rhythm) if rhythm else "balanced"
    
    dynamics = rde.get("dynamics") or rde.get("fracture") or "stable"
    if not isinstance(dynamics, str):
        dynamics = str(dynamics) if dynamics else "stable"
    
    emotion = rde.get("emotion") or rde.get("entropy") or "neutral"
    if not isinstance(emotion, str):
        emotion = str(emotion) if emotion else "neutral"
    structure = (
        analysis_result.get("structure", {})
        if isinstance(analysis_result.get("structure"), dict)
        else {}
    )
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение sections и headers
    section_list = structure.get("sections", [])
    if not isinstance(section_list, list):
        section_list = []
    
    headers = structure.get("headers", [])
    if not isinstance(headers, list):
        headers = []

    # Task 11.1: Safe extraction of fanf and lyrics_sections with defaults
    fanf = (
        analysis_result.get("fanf", {})
        if isinstance(analysis_result.get("fanf"), dict)
        else {}
    )
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение lyrics_sections
    lyrics_sections = fanf.get("lyrics_sections", [])
    if not isinstance(lyrics_sections, list):
        lyrics_sections = []
    
    if not lyrics_sections:
        # Пытаемся получить из другого места
        lyrics_data = (
            analysis_result.get("lyrics", {})
            if isinstance(analysis_result.get("lyrics"), dict)
            else {}
        )
        lyrics_sections_raw = lyrics_data.get("sections", [])
        lyrics_sections = lyrics_sections_raw if isinstance(lyrics_sections_raw, list) else []

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
            # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение section_name
            section_name = f"Section {i + 1}"
            if i < len(headers) and isinstance(headers[i], dict):
                header_dict = headers[i]
                section_name = (
                    header_dict.get("tag")
                    or header_dict.get("label")
                    or header_dict.get("name")
                    or section_name
                )
                if not isinstance(section_name, str):
                    section_name = f"Section {i + 1}"

            # Подсчитываем количество строк в секции
            # 🔧 ИСПРАВЛЕНИЕ: Безопасный подсчет строк
            line_count = 0
            if isinstance(sec, str):
                line_count = len(sec.split("\n"))
            elif isinstance(sec, dict):
                line_count_raw = sec.get("line_count")
                if isinstance(line_count_raw, int):
                    line_count = line_count_raw
                else:
                    lines_list = sec.get("lines", [])
                    line_count = len(lines_list) if isinstance(lines_list, list) else 0

            # Получаем вокальную технику и эмоцию для секции
            # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение vocal_tech и section_emotion
            vocal_tech = None
            section_emotion = None
            if i < len(lyrics_sections) and isinstance(lyrics_sections[i], dict):
                section_dict = lyrics_sections[i]
                vocal_tech = section_dict.get("vocal_technique")
                section_emotion = section_dict.get("emotion")
                # Проверка типов
                if vocal_tech and not isinstance(vocal_tech, str):
                    vocal_tech = str(vocal_tech) if vocal_tech else None
                if section_emotion and not isinstance(section_emotion, str):
                    section_emotion = str(section_emotion) if section_emotion else None

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
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение BPM и Key
    bpm_raw = analysis_result.get("bpm", "auto")
    if isinstance(bpm_raw, dict):
        bpm_val = bpm_raw.get("estimate") or bpm_raw.get("target_bpm") or bpm_raw.get("bpm") or "auto"
    elif isinstance(bpm_raw, (int, float)):
        bpm_val = int(bpm_raw)
    else:
        bpm_val = str(bpm_raw) if bpm_raw else "auto"
    
    key_root = tone.get("key_root") or style.get("key_root") or None
    if key_root and not isinstance(key_root, str):
        key_root = str(key_root) if key_root else None
    
    key_mode = tone.get("key_mode") or style.get("mode") or None
    if key_mode and not isinstance(key_mode, str):
        key_mode = str(key_mode) if key_mode else None
    
    key_full = tone.get("key_full") or style.get("key") or analysis_result.get("key") or None
    if key_full and not isinstance(key_full, str):
        key_full = str(key_full) if key_full else None
    
    # Fix Color signature: try color_wave, color_signature, or color_temperature
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение color_wave
    color_wave = analysis_result.get("color_wave", [])
    if isinstance(color_wave, list) and len(color_wave) > 0:
        try:
            color_sig = ", ".join(str(c) for c in color_wave)
        except (TypeError, AttributeError):
            color_sig = None
    else:
        color_sig = (
            style.get("color_signature")
            or style.get("color_temperature")
            or tone.get("color_signature")
            or style.get("color")
            or None
        )
        if color_sig and not isinstance(color_sig, str):
            color_sig = str(color_sig) if color_sig else None
    
    # Fix Resonance Hz: try rde.resonance_hz, or compute from key
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение и вычисление resonance
    resonance = rde.get("resonance_hz") or tone.get("resonance_hz")
    if not resonance:
        # Compute from key if available
        try:
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
        except (TypeError, AttributeError, ValueError):
            resonance = "auto"
    elif not isinstance(resonance, (int, float, str)):
        resonance = "auto"
    
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение safe_octaves
    safe_octaves = (
        tone.get("safe_octaves", [])
        if isinstance(tone.get("safe_octaves"), list)
        else []
    )
    
    # Extract instruments from style (Matrix Architecture)
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение instruments
    instruments = style.get("instruments", [])
    if isinstance(instruments, list) and len(instruments) > 0:
        try:
            instruments_str = ", ".join(str(instr) for instr in instruments)
        except (TypeError, AttributeError):
            instruments_str = "auto"
    else:
        instruments_str = "auto"
    
    # Extract genre source (Matrix Architecture indicator)
    genre_source = style.get("genre_source", "Legacy")
    engine_indicator = "⚙️ Engine: " + genre_source
    
    lines = [
        "Tone / Key / BPM:",
        f"  BPM: {bpm_val}",
        f"  Key root: {key_root or 'auto'}",
        f"  Mode: {key_mode or 'auto'}",
        f"  Key full: {key_full or 'auto'}",
        "",
        f"  Color signature: {color_sig or 'adaptive'}",
        f"  Resonance Hz   : {resonance}",
        f"  Safe octaves   : {safe_octaves if safe_octaves else 'auto'}",
        "",
        f"🎹 Instruments: {instruments_str}",
        f"{engine_indicator}",
    ]
    
    return "\n".join(lines)


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
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение genre данных
    primary = genre.get("primary") or style.get("genre") or None
    if primary and not isinstance(primary, str):
        primary = str(primary) if primary else None
    
    secondary = genre.get("secondary") or style.get("secondary") or None
    if secondary and not isinstance(secondary, str):
        secondary = str(secondary) if secondary else None
    
    hybrid = genre.get("hybrid") or None
    if hybrid and not isinstance(hybrid, str):
        hybrid = str(hybrid) if hybrid else None
    
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
    
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение vocal данных
    gender = (
        vocal.get("gender")
        or analysis_result.get("final_gender_preference")
        or None
    )
    if gender and not isinstance(gender, str):
        gender = str(gender) if gender else None
    
    form = vocal.get("form") or style.get("vocal_form") or None
    if form and not isinstance(form, str):
        form = str(form) if form else None
    
    texture = vocal.get("texture") or None
    if texture and not isinstance(texture, str):
        texture = str(texture) if texture else None
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
    # Display genre prominently (Matrix Architecture)
    genre_lines = [
        "🎵 Genre Fusion:",
        f"  🎼 Primary  : {primary or 'adaptive'}",
    ]
    if secondary:
        genre_lines.append(f"  🎵 Secondary: {secondary}")
    if hybrid:
        genre_lines.append(f"  🎶 Hybrid   : {hybrid}")
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


def build_matrix_architecture_text(analysis_result):
    """Форматирует данные Matrix Architecture для отображения."""
    if not isinstance(analysis_result, dict):
        return "Matrix Architecture: No data available"
    
    style = analysis_result.get("style", {})
    if not isinstance(style, dict):
        style = {}
    
    matrix_arch = analysis_result.get("matrix_architecture", {})
    if not isinstance(matrix_arch, dict):
        matrix_arch = {}
    
    lines = ["=== Matrix Architecture ==="]
    
    # Matrix Architecture Status
    enabled = matrix_arch.get("enabled", False)
    lines.append(f"🔷 Matrix Architecture: {'✅ Enabled' if enabled else '❌ Disabled (Legacy Mode)'}")
    lines.append("")
    
    # Genre и Confidence
    genre = style.get("genre", "Unknown")
    confidence = style.get("confidence")
    if confidence is not None:
        lines.append(f"🎵 Genre: {genre}")
        lines.append(f"   Confidence: {confidence:.2%} ({confidence:.3f})")
    else:
        lines.append(f"🎵 Genre: {genre}")
        lines.append(f"   Confidence: N/A")
    
    # Genre Source
    source = style.get("genre_source", "Legacy")
    lines.append(f"⚙️ Engine: {source}")
    
    # Matrix Mode
    matrix_mode = style.get("matrix_mode", False)
    lines.append(f"🔷 Matrix Mode: {'✅ Enabled' if matrix_mode else '❌ Disabled'}")
    
    # Subgenre (если есть)
    subgenre = style.get("subgenre")
    if subgenre:
        lines.append(f"🎵 Subgenre: {subgenre}")
    
    # Instruments - ПОЛНЫЙ ВЫВОД
    instruments = style.get("instruments", [])
    if instruments:
        instruments_str = ", ".join(str(instr) for instr in instruments)
        lines.append(f"🎹 Instruments ({len(instruments)}): {instruments_str}")
    else:
        lines.append("🎹 Instruments: None")
    
    # Engines Status - ПОЛНЫЙ ВЫВОД
    engines = matrix_arch.get("engines", {})
    if engines:
        lines.append("")
        lines.append("🔧 Engines Status:")
        enabled_count = sum(1 for v in engines.values() if v)
        total_count = len(engines)
        lines.append(f"   Active: {enabled_count}/{total_count}")
        lines.append("")
        for engine_name, status in engines.items():
            status_icon = "✅" if status else "❌"
            engine_display = engine_name.replace('_', ' ').title()
            lines.append(f"   {status_icon} {engine_display}")
    else:
        lines.append("")
        lines.append("🔧 Engines Status: No data available")
    
    # Дополнительные Matrix данные
    if matrix_mode:
        lines.append("")
        lines.append("📊 Additional Matrix Data:")
        # BPM Suggested (если есть в semantic_layers)
        semantic_layers = analysis_result.get("semantic_layers", {})
        if isinstance(semantic_layers, dict):
            bpm_suggested = semantic_layers.get("bpm_suggested")
            if bpm_suggested:
                lines.append(f"   BPM Suggested: {bpm_suggested}")
        
        # Top Genres (если есть альтернативные варианты) - ВЫВОДИТСЯ
        top_genres = style.get("top_genres", [])
        if top_genres and isinstance(top_genres, list):
            lines.append("")
            lines.append("🎵 Top Genres (Alternatives):")
            for i, genre_item in enumerate(top_genres[:5], 1):
                if isinstance(genre_item, (list, tuple)) and len(genre_item) >= 2:
                    alt_genre, alt_confidence = genre_item[0], genre_item[1]
                    if isinstance(alt_genre, str) and isinstance(alt_confidence, (int, float)):
                        lines.append(f"   {i}. {alt_genre:20} {alt_confidence:.2%}")
                elif isinstance(genre_item, str):
                    lines.append(f"   {i}. {genre_item}")
        
        # Hybrid Genre Info
        if style.get("is_hybrid"):
            secondary = style.get("secondary_genre") or style.get("secondary")
            if secondary:
                lines.append("")
                lines.append(f"🎶 Hybrid Genre: {genre} + {secondary}")
        
        # Quantum Jitter - ВЫВОДИТСЯ в Matrix Architecture
        quantum_jitter = analysis_result.get("quantum_jitter", {})
        if isinstance(quantum_jitter, dict) and quantum_jitter:
            lines.append("")
            lines.append("⚛️ Quantum Jitter (Matrix Mode):")
            for param, values in quantum_jitter.items():
                if isinstance(values, dict):
                    original = values.get("original")
                    jittered = values.get("jittered")
                    if original is not None and jittered is not None:
                        diff = jittered - original
                        diff_sign = "+" if diff >= 0 else ""
                        lines.append(f"   {param}: {original:.3f} → {jittered:.3f} ({diff_sign}{diff:.3f})")
        
        # Serendipity - ВЫВОДИТСЯ в Matrix Architecture
        serendipity = analysis_result.get("serendipity", {})
        if isinstance(serendipity, dict) and serendipity:
            applied = serendipity.get("applied", False)
            original_genre = serendipity.get("original_genre")
            final_genre = serendipity.get("final_genre")
            lines.append("")
            lines.append("🎲 Serendipity (Matrix Mode):")
            lines.append(f"   Applied: {'✅ Yes' if applied else '❌ No'}")
            if original_genre and final_genre and original_genre != final_genre:
                lines.append(f"   Genre Changed: {original_genre} → {final_genre}")
    
    # Genre Selection Process (если доступно) - ВЫВОДИТСЯ
    genre_selection = analysis_result.get("genre_selection", {})
    if isinstance(genre_selection, dict) and genre_selection:
        lines.append("")
        lines.append("🔍 Genre Selection Process (Summary):")
        
        # Emotion Clusters - ВЫВОДИТСЯ
        clusters = genre_selection.get("clusters", {})
        if clusters:
            lines.append("   Emotion Clusters (Top-3):")
            sorted_clusters = sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:3]
            for cluster_name, cluster_value in sorted_clusters:
                if isinstance(cluster_value, (int, float)) and cluster_value > 0:
                    lines.append(f"     {cluster_name}: {cluster_value:.3f}")
        
        # Genre Scores - ВЫВОДИТСЯ
        genre_scores = genre_selection.get("genre_scores", {})
        if genre_scores:
            lines.append("   Genre Scores (Top-3):")
            sorted_scores = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            for genre_name, score in sorted_scores:
                if isinstance(score, (int, float)) and score > 0:
                    lines.append(f"     {genre_name:20} {score:.3f}")
    
    return "\n".join(lines)


def build_genre_selection_process_text(analysis_result):
    """Форматирует детальный процесс выбора жанра для отображения."""
    if not isinstance(analysis_result, dict):
        return "Genre Selection Process: No data available"
    
    lines = ["=== Genre Selection Process ==="]
    
    style = analysis_result.get("style", {})
    if not isinstance(style, dict):
        style = {}
    
    # Genre Selection Process
    genre_selection = analysis_result.get("genre_selection", {})
    if isinstance(genre_selection, dict) and genre_selection:
        # Emotion Clusters
        clusters = genre_selection.get("clusters", {})
        if clusters:
            lines.append("")
            lines.append("🎭 Emotion Clusters (Top-5):")
            sorted_clusters = sorted(clusters.items(), key=lambda x: x[1], reverse=True)[:5]
            for cluster_name, cluster_value in sorted_clusters:
                if isinstance(cluster_value, (int, float)) and cluster_value > 0:
                    bar = "█" * int(cluster_value * 20) + "·" * (20 - int(cluster_value * 20))
                    lines.append(f"  {cluster_name:20} {cluster_value:.3f} |{bar}|")
        
        # Genre Scores
        genre_scores = genre_selection.get("genre_scores", {})
        if genre_scores:
            lines.append("")
            lines.append("🎵 Genre Scores (Top-5):")
            sorted_scores = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            for genre_name, score in sorted_scores:
                if isinstance(score, (int, float)) and score > 0:
                    bar = "█" * int(score * 20) + "·" * (20 - int(score * 20))
                    lines.append(f"  {genre_name:20} {score:.3f} |{bar}|")
    else:
        lines.append("")
        lines.append("⚠️ Genre Selection Process: No detailed data available")
    
    # Genre Routing Info
    genre_routing = analysis_result.get("genre_routing", {})
    if isinstance(genre_routing, dict) and genre_routing:
        lines.append("")
        lines.append("🗺️ Genre Routing:")
        emotion_group = genre_routing.get("emotion_group")
        main_genre = genre_routing.get("genre")
        subgenre = genre_routing.get("subgenre")
        suno_style = genre_routing.get("suno_style")
        
        if emotion_group:
            lines.append(f"  Emotion Group: {emotion_group}")
        if main_genre:
            lines.append(f"  Main Genre: {main_genre}")
        if subgenre:
            lines.append(f"  Subgenre: {subgenre}")
        if suno_style:
            lines.append(f"  Suno Style: {suno_style}")
    
    # Matrix Mode Details
    matrix_mode = style.get("matrix_mode", False)
    if matrix_mode:
        lines.append("")
        lines.append("🔷 Matrix Mode Details:")
        
        # Quantum Jitter
        quantum_jitter = analysis_result.get("quantum_jitter", {})
        if isinstance(quantum_jitter, dict) and quantum_jitter:
            lines.append("  Quantum Jitter:")
            for param, values in quantum_jitter.items():
                if isinstance(values, dict):
                    original = values.get("original")
                    jittered = values.get("jittered")
                    if original is not None and jittered is not None:
                        diff = jittered - original
                        diff_sign = "+" if diff >= 0 else ""
                        lines.append(f"    {param}: {original:.3f} → {jittered:.3f} ({diff_sign}{diff:.3f})")
        
        # Serendipity
        serendipity = analysis_result.get("serendipity", {})
        if isinstance(serendipity, dict) and serendipity:
            applied = serendipity.get("applied", False)
            original_genre = serendipity.get("original_genre")
            final_genre = serendipity.get("final_genre")
            lines.append("  Serendipity:")
            lines.append(f"    Applied: {'✅ Yes' if applied else '❌ No'}")
            if original_genre and final_genre and original_genre != final_genre:
                lines.append(f"    Genre Changed: {original_genre} → {final_genre}")
        
        # Fibonacci Rotation
        fibonacci = analysis_result.get("fibonacci_rotation", {})
        if isinstance(fibonacci, dict) and fibonacci:
            counter = fibonacci.get("counter")
            if counter is not None:
                lines.append(f"  Fibonacci Counter: {counter}")
    
    # Top Genres (Alternatives)
    top_genres = style.get("top_genres", [])
    if top_genres and isinstance(top_genres, list):
        lines.append("")
        lines.append("🎵 Top Genres (Alternatives):")
        for i, genre_item in enumerate(top_genres[:5], 1):
            if isinstance(genre_item, (list, tuple)) and len(genre_item) >= 2:
                alt_genre, alt_confidence = genre_item[0], genre_item[1]
                if isinstance(alt_genre, str) and isinstance(alt_confidence, (int, float)):
                    lines.append(f"  {i}. {alt_genre:20} {alt_confidence:.2%}")
            elif isinstance(genre_item, str):
                lines.append(f"  {i}. {genre_item}")
    
    return "\n".join(lines)


def build_unique_values_text(analysis_result):
    """Извлекает и форматирует уникальные/индивидуальные значения из всех секций."""
    if not isinstance(analysis_result, dict):
        return "Unique Values: No data available"
    
    lines = ["=== Unique Individual Values ==="]
    lines.append("(Values that appear only once and don't duplicate across sections)")
    lines.append("")
    
    # Собираем все значения из разных секций
    all_sections = {
        "emotions": analysis_result.get("emotions", {}),
        "tlp": analysis_result.get("tlp", {}),
        "style": analysis_result.get("style", {}),
        "rde": analysis_result.get("rde", {}),
        "vocal": analysis_result.get("vocal", {}),
        "structure": analysis_result.get("structure", {}),
        "integrity": analysis_result.get("integrity", {}),
        "semantic_layers": analysis_result.get("semantic_layers", {}),
        "genre_selection": analysis_result.get("genre_selection", {}),
        "genre_routing": analysis_result.get("genre_routing", {}),
        "quantum_jitter": analysis_result.get("quantum_jitter", {}),
        "serendipity": analysis_result.get("serendipity", {}),
        "fibonacci_rotation": analysis_result.get("fibonacci_rotation", {}),
        "genre_bias": analysis_result.get("genre_bias", {}),
        "matrix_architecture": analysis_result.get("matrix_architecture", {}),
    }
    
    # Собираем все ключи и их значения
    all_keys_values = {}
    for section_name, section_data in all_sections.items():
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                full_key = f"{section_name}.{key}"
                if full_key not in all_keys_values:
                    all_keys_values[full_key] = []
                all_keys_values[full_key].append((section_name, value))
    
    # Находим уникальные значения (которые встречаются только в одной секции)
    unique_values = []
    for full_key, occurrences in all_keys_values.items():
        if len(occurrences) == 1:
            section_name, value = occurrences[0]
            # Пропускаем пустые значения и None
            if value is not None and value != "" and value != {} and value != []:
                unique_values.append((full_key, section_name, value))
    
    # Группируем по секциям
    grouped = {}
    for full_key, section_name, value in unique_values:
        if section_name not in grouped:
            grouped[section_name] = []
        grouped[section_name].append((full_key, value))
    
    # Выводим сгруппированные уникальные значения
    if grouped:
        for section_name, items in sorted(grouped.items()):
            lines.append(f"📦 {section_name.replace('_', ' ').title()}:")
            for full_key, value in items[:10]:  # Ограничиваем до 10 на секцию
                key_name = full_key.split('.', 1)[1] if '.' in full_key else full_key
                if isinstance(value, (int, float)):
                    lines.append(f"  {key_name}: {value:.3f}" if isinstance(value, float) else f"  {key_name}: {value}")
                elif isinstance(value, str):
                    if len(value) <= 50:
                        lines.append(f"  {key_name}: {value}")
                    else:
                        lines.append(f"  {key_name}: {value[:47]}...")
                elif isinstance(value, (list, dict)):
                    lines.append(f"  {key_name}: {type(value).__name__} ({len(value)} items)")
                else:
                    lines.append(f"  {key_name}: {value}")
            if len(items) > 10:
                lines.append(f"  ... and {len(items) - 10} more")
            lines.append("")
    else:
        lines.append("⚠️ No unique individual values found")
        lines.append("(All values appear in multiple sections or are empty)")
    
    return "\n".join(lines)


def build_vector_analysis_text(analysis_result):
    """Форматирует векторный анализ (Emotion Vector, 7-axis, TLP) для отображения."""
    if not isinstance(analysis_result, dict):
        return "Vector Analysis: No data available"
    
    lines = ["=== Vector Analysis ==="]
    
    # RDE Emotion Vector (Valence/Arousal)
    rde = analysis_result.get("rde", {})
    if isinstance(rde, dict):
        emotion_vector = rde.get("emotion_vector", {})
        if isinstance(emotion_vector, dict):
            valence = emotion_vector.get("valence")
            arousal = emotion_vector.get("arousal")
            if valence is not None and arousal is not None:
                lines.append("")
                lines.append("📊 Emotion Vector (Valence/Arousal):")
                lines.append(f"  Valence: {valence:.3f} (Love - Pain, range: [-1.0, 1.0])")
                lines.append(f"  Arousal: {arousal:.3f} (Intensity, range: [0.0, 1.0])")
                
                # Визуализация
                valence_bar = "█" * int((valence + 1.0) * 10) + "·" * (20 - int((valence + 1.0) * 10))
                arousal_bar = "█" * int(arousal * 20) + "·" * (20 - int(arousal * 20))
                lines.append(f"  Valence: |{valence_bar}|")
                lines.append(f"  Arousal: |{arousal_bar}|")
    
    # 7-axis Emotion Profile
    emotion_profile_7axis = analysis_result.get("emotion_profile_7axis", {})
    if isinstance(emotion_profile_7axis, dict) and emotion_profile_7axis:
        lines.append("")
        lines.append("📈 7-Axis Emotion Profile:")
        for axis, value in emotion_profile_7axis.items():
            if isinstance(value, (int, float)):
                bar = "█" * int(value * 20) + "·" * (20 - int(value * 20))
                lines.append(f"  {axis.capitalize():12} {value:.3f} |{bar}|")
        
        # Genre Bias Influence (если доступно) - ВЫВОДИТСЯ
        genre_bias = analysis_result.get("genre_bias", {})
        if isinstance(genre_bias, dict) and genre_bias:
            lines.append("")
            lines.append("🎵 Genre Bias Influence (from 7-axis emotions):")
            lines.append("   (How emotions affect genre selection)")
            sorted_bias = sorted(genre_bias.items(), key=lambda x: x[1], reverse=True)[:5]
            for genre_name, bias_value in sorted_bias:
                if isinstance(bias_value, (int, float)):
                    # Bias values start from 1.0, so we normalize for visualization
                    normalized_bias = max(0.0, min(1.0, (bias_value - 1.0) / 0.5))  # Normalize to [0, 1]
                    bar = "█" * int(normalized_bias * 20) + "·" * (20 - int(normalized_bias * 20))
                    lines.append(f"  {genre_name:20} {bias_value:.3f} |{bar}|")
    
    # TLP Vector
    tlp = analysis_result.get("tlp", {})
    if isinstance(tlp, dict):
        truth = tlp.get("truth", 0.0)
        love = tlp.get("love", 0.0)
        pain = tlp.get("pain", 0.0)
        cf = tlp.get("conscious_frequency", 0.0)
        
        lines.append("")
        lines.append("🎯 TLP Vector (Truth/Love/Pain):")
        lines.append(f"  Truth:  {truth:.3f}")
        lines.append(f"  Love:   {love:.3f}")
        lines.append(f"  Pain:   {pain:.3f}")
        lines.append(f"  CF:     {cf:.3f} (Conscious Frequency)")
        
        # Дополнительные метрики TLP
        dominant_axis = tlp.get("dominant_axis")
        balance = tlp.get("balance")
        if dominant_axis:
            lines.append(f"  Dominant Axis: {dominant_axis}")
        if balance is not None:
            lines.append(f"  Balance: {balance:.3f}")
    
    # RDE Metrics
    if isinstance(rde, dict):
        resonance = rde.get("resonance")
        fracture = rde.get("fracture")
        entropy = rde.get("entropy")
        
        if resonance is not None or fracture is not None or entropy is not None:
            lines.append("")
            lines.append("🌀 RDE Metrics:")
            if resonance is not None:
                lines.append(f"  Resonance: {resonance:.3f}")
            if fracture is not None:
                lines.append(f"  Fracture:  {fracture:.3f}")
            if entropy is not None:
                lines.append(f"  Entropy:    {entropy:.3f}")
    
    return "\n".join(lines)


def build_advanced_analysis_text(analysis_result):
    """Форматирует расширенные данные анализа (semantic_layers, integrity, runtime) для отображения."""
    if not isinstance(analysis_result, dict):
        return "Advanced Analysis: No data available"
    
    lines = ["=== Advanced Analysis ==="]
    
    # Semantic Layers - ПОЛНЫЙ ВЫВОД
    semantic_layers = analysis_result.get("semantic_layers", {})
    if isinstance(semantic_layers, dict):
        layers = semantic_layers.get("layers", {})
        if isinstance(layers, dict):
            sections = layers.get("sections", [])
            if sections:
                lines.append("")
                lines.append("📚 Semantic Layers:")
                lines.append(f"  Total Sections: {len(sections)}")
                for i, section in enumerate(sections):  # Показываем ВСЕ секции
                    if isinstance(section, dict):
                        tag = section.get("tag", f"Section {i+1}")
                        mood = section.get("mood", "unknown")
                        energy = section.get("energy", "unknown")
                        bpm = section.get("bpm", "N/A")
                        key = section.get("key", "N/A")
                        arrangement = section.get("arrangement", "N/A")
                        focus = section.get("focus", "N/A")
                        lines.append(f"  [{i+1}] {tag}:")
                        lines.append(f"      Mood: {mood} | Energy: {energy} | BPM: {bpm}")
                        lines.append(f"      Key: {key} | Arrangement: {arrangement} | Focus: {focus}")
                # Дополнительные метрики semantic_layers
                depth = layers.get("depth")
                warmth = layers.get("warmth")
                clarity = layers.get("clarity")
                if depth is not None or warmth is not None or clarity is not None:
                    lines.append("")
                    lines.append("  Layer Metrics:")
                    if depth is not None:
                        lines.append(f"    Depth: {depth:.3f}")
                    if warmth is not None:
                        lines.append(f"    Warmth: {warmth:.3f}")
                    if clarity is not None:
                        lines.append(f"    Clarity: {clarity:.3f}")
            else:
                lines.append("")
                lines.append("📚 Semantic Layers: No sections available")
    
    # Integrity - ПОЛНЫЙ ВЫВОД
    integrity = analysis_result.get("integrity", {})
    if isinstance(integrity, dict) and integrity:
        lines.append("")
        lines.append("🔍 Integrity Scan:")
        word_count = integrity.get("word_count")
        sentence_count = integrity.get("sentence_count")
        char_count = integrity.get("char_count")
        paragraph_count = integrity.get("paragraph_count")
        
        if word_count is not None:
            lines.append(f"  Words: {word_count}")
        if sentence_count is not None:
            lines.append(f"  Sentences: {sentence_count}")
        if char_count is not None:
            lines.append(f"  Characters: {char_count}")
        if paragraph_count is not None:
            lines.append(f"  Paragraphs: {paragraph_count}")
        
        # Дополнительные метрики integrity
        other_metrics = {k: v for k, v in integrity.items() 
                        if k not in ["word_count", "sentence_count", "char_count", "paragraph_count"] 
                        and v is not None}
        if other_metrics:
            lines.append("")
            lines.append("  Additional Metrics:")
            for key, value in other_metrics.items():
                lines.append(f"    {key}: {value}")
    else:
        lines.append("")
        lines.append("🔍 Integrity Scan: No data available")
    
    # Runtime Metrics - ПОЛНЫЙ ВЫВОД
    runtime_ms = analysis_result.get("runtime_ms")
    if runtime_ms is not None:
        lines.append("")
        lines.append("⏱️ Performance:")
        lines.append(f"  Runtime: {runtime_ms} ms ({runtime_ms/1000:.2f} s)")
        if runtime_ms < 1000:
            lines.append(f"  Status: ⚡ Very Fast (< 1s)")
        elif runtime_ms < 3000:
            lines.append(f"  Status: ✅ Fast (< 3s)")
        elif runtime_ms < 5000:
            lines.append(f"  Status: ⚠️ Moderate (< 5s)")
        else:
            lines.append(f"  Status: 🐌 Slow (>= 5s)")
    else:
        lines.append("")
        lines.append("⏱️ Performance: No runtime data available")
    
    # Integrations Status - ПОЛНЫЙ ВЫВОД
    integrations = analysis_result.get("integrations", {})
    if isinstance(integrations, dict) and integrations:
        lines.append("")
        lines.append("🔌 Active Integrations:")
        enabled_count = sum(1 for v in integrations.values() if v)
        total_count = len(integrations)
        lines.append(f"  Status: {enabled_count}/{total_count} enabled")
        lines.append("")
        for integration, enabled in integrations.items():
            status_icon = "✅" if enabled else "❌"
            integration_name = integration.replace('_', ' ').title()
            lines.append(f"  {status_icon} {integration_name}")
    else:
        lines.append("")
        lines.append("🔌 Active Integrations: No data available")
    
    # Matrix Architecture Status - ПОЛНЫЙ ВЫВОД
    matrix_arch = analysis_result.get("matrix_architecture", {})
    if isinstance(matrix_arch, dict):
        enabled = matrix_arch.get("enabled", False)
        lines.append("")
        lines.append(f"🔷 Matrix Architecture: {'✅ Enabled' if enabled else '❌ Disabled'}")
        if enabled:
            engines = matrix_arch.get("engines", {})
            if engines:
                lines.append("  Engines:")
                for engine_name, status in engines.items():
                    status_icon = "✅" if status else "❌"
                    lines.append(f"    {status_icon} {engine_name.capitalize()}")
    else:
        lines.append("")
        lines.append("🔷 Matrix Architecture: No data available")
    
    return "\n".join(lines)


def build_breath_map_text(analysis_result, text=None):
    """Task 11.1: Safely build breath map text with defaults for missing fields."""
    if not isinstance(analysis_result, dict):
        return "Breathing / ZeroPulse map: No data available"

    # Try to get breathing data from multiple locations
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение breathing данных
    breathing = analysis_result.get("breathing", {})
    if not isinstance(breathing, dict):
        breathing = {}
    
    zeropulse = analysis_result.get("zeropulse", {})
    if not isinstance(zeropulse, dict):
        zeropulse = {}
    
    diagnostics = analysis_result.get("diagnostics", {}) or {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    
    breath = breathing if breathing else (zeropulse if zeropulse else {})
    if not breath:
        breath = diagnostics.get("breathing") or diagnostics.get("zero_pulse") or {}
        if not isinstance(breath, dict):
            breath = {}
    
    if breath and isinstance(breath, dict):
        # Use new visualization function for breathing data
        breathing_visual = visualize_breathing_ascii(breath)
        if breathing_visual and breathing_visual != "No breathing data.":
            lines = ["Breathing / ZeroPulse map:"]
            lines.append("")
            lines.append("Visualization:")
            lines.append(f"  {breathing_visual}")
            lines.append("")
            # Also show raw data for reference
            # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение breathing points
            try:
                points = breath.get('breathing_points', [])
                if isinstance(points, list) and points:
                    inhale_points = breath.get('inhale_points', [])
                    exhale_points = breath.get('exhale_points', [])
                    lines.append(f"Total points: {len(points)}")
                    lines.append(f"Inhale points: {len(inhale_points) if isinstance(inhale_points, list) else 0}")
                    lines.append(f"Exhale points: {len(exhale_points) if isinstance(exhale_points, list) else 0}")
            except (AttributeError, TypeError, KeyError):
                pass
            return "\n".join(lines)
        # Fallback to old format if visualization fails
        # 🔧 ИСПРАВЛЕНИЕ: Безопасная итерация по breath.items()
        lines = ["Breathing / ZeroPulse map:"]
        try:
            if isinstance(breath, dict):
                for k, v in breath.items():
                    if k != 'breathing_points':  # Skip raw points, we show visualization
                        try:
                            lines.append(f"  {k}: {v}")
                        except (TypeError, AttributeError):
                            lines.append(f"  {k}: <unable to display>")
            return "\n".join(lines)
        except (AttributeError, TypeError, KeyError):
            pass
    
    # If no breathing data, generate ASCII visualization from text structure
    if text:
        return _generate_breathing_ascii(text)
    
    # Try to extract text from annotated_text_ui or annotated_text_suno
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение text_source
    text_source = (
        analysis_result.get("annotated_text_ui")
        or analysis_result.get("annotated_text_suno")
        or ""
    )
    if text_source and isinstance(text_source, str):
        # Extract original text (remove annotations)
        import re
        try:
            # Remove annotation markers like [INTRO - mood: ...]
            clean_text = re.sub(r'\[.*?\]', '', text_source)
            # Remove BPM/key markers
            clean_text = re.sub(r'\[\d+\s+BPM.*?\]', '', clean_text)
            if clean_text.strip():
                return _generate_breathing_ascii(clean_text)
        except (TypeError, AttributeError, re.error):
            pass
    
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
        # 🚑 ПАТЧ 8: Не показываем traceback пользователю (утечка информации)
        tb = traceback.format_exc()
        err = "<div style='color:#ff5555'>Internal Server Error. Please try again.</div>"
        logging.getLogger(__name__).error(f"Error in run_full_analysis: {e}\n{tb}", exc_info=True)
        return ("", "", "", "", err, "", "", "")
    except Exception as e:
        # Catch-all для неожиданных ошибок
        # 🚑 ПАТЧ 8: Не показываем traceback пользователю (утечка информации)
        tb = traceback.format_exc()
        err = "<div style='color:#ff5555'>Internal Server Error. Please try again.</div>"
        logging.getLogger(__name__).critical(f"Unexpected error in run_full_analysis: {e}\n{tb}", exc_info=True)
        return ("", "", "", "", err, "", "", "")
    # 🔧 ИСПРАВЛЕНИЕ: Безопасный вызов всех функций с обработкой ошибок
    try:
        style_p, lyrics_p, ui_t, fanf_t, _ = extract_main_outputs(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in extract_main_outputs: {e}")
        style_p, lyrics_p, ui_t, fanf_t = "", "", "", ""
    
    try:
        pulse_html_output = build_core_pulse_timeline(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_core_pulse_timeline: {e}")
        pulse_html_output = "<div style='color:#ff5555'>Error building timeline</div>"
    
    try:
        tlp_pulse = build_tlp_pulse_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_tlp_pulse_text: {e}")
        tlp_pulse = "TLP Pulse: Error"
    
    try:
        rde_section = build_rde_section_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_rde_section_text: {e}")
        rde_section = "RDE / Sections: Error"
    
    try:
        tone_bpm = build_tone_bpm_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_tone_bpm_text: {e}")
        tone_bpm = "Tone / BPM: Error"
    
    try:
        genre_vocal = build_genre_vocal_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_genre_vocal_text: {e}")
        genre_vocal = "Genre / Vocal: Error"
    
    # Add Matrix Architecture data to lower panel
    style = analysis_result.get("style", {}) if isinstance(analysis_result.get("style"), dict) else {}
    
    # Extract instruments
    inst_list = style.get("instruments", [])
    instruments_str = ", ".join(str(instr) for instr in inst_list) if inst_list else "None"
    
    # Extract genre source
    source = style.get("genre_source", "Legacy")
    
    # Extract breathing visualization
    # 🔧 ИСПРАВЛЕНИЕ: Безопасное извлечение breathing_data
    breathing_data = analysis_result.get("breathing", {})
    if not isinstance(breathing_data, dict):
        breathing_data = {}
    breath_vis = visualize_breathing_ascii(breathing_data)
    
    # Build Matrix Architecture info section
    matrix_info = [
        "",
        "=== Matrix Architecture Data ===",
        f"🎹 Instruments: {instruments_str}",
        f"⚙️ Engine: {source}",
        f"🫁 Breathing Map: {breath_vis}",
    ]
    
    lower_panel_output = "\n\n".join(
        [
            tone_bpm,
            "",
            genre_vocal,
            "",
            build_breath_map_text(analysis_result, text=text),
            "\n".join(matrix_info),
        ]
    )
    
    # Новые секции для расширенного вывода
    try:
        matrix_arch_text = build_matrix_architecture_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_matrix_architecture_text: {e}")
        matrix_arch_text = "Matrix Architecture: Error"
    
    try:
        vector_analysis_text = build_vector_analysis_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_vector_analysis_text: {e}")
        vector_analysis_text = "Vector Analysis: Error"
    
    try:
        advanced_analysis_text = build_advanced_analysis_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_advanced_analysis_text: {e}")
        advanced_analysis_text = "Advanced Analysis: Error"
    
    try:
        genre_selection_text = build_genre_selection_process_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_genre_selection_process_text: {e}")
        genre_selection_text = "Genre Selection Process: Error"
    
    try:
        unique_values_text = build_unique_values_text(analysis_result)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error in build_unique_values_text: {e}")
        unique_values_text = "Unique Values: Error"
    
    return (
        style_p,
        lyrics_p,
        ui_t,
        fanf_t,
        pulse_html_output,
        tlp_pulse,
        rde_section,
        lower_panel_output,
        matrix_arch_text,
        vector_analysis_text,
        advanced_analysis_text,
        genre_selection_text,
        unique_values_text,
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
        logging.getLogger(__name__).error(f"Error in run_raw_diagnostics: {e}", exc_info=True)
        return {"error": str(e), "traceback": traceback.format_exc()}
    except Exception as e:
        # Catch-all для неожиданных ошибок
        logging.getLogger(__name__).critical(f"Unexpected error in run_raw_diagnostics: {e}", exc_info=True)
        return {"error": "Unexpected error occurred", "traceback": traceback.format_exc()}


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

    with gr.Tab("Matrix Architecture"):
        matrix_arch_out = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Matrix Architecture Details",
                lines=25,
                max_lines=80,
                show_copy_button=True,
                interactive=False,
            )
        )
    
    with gr.Tab("Vector Analysis"):
        vector_analysis_out = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Vector Analysis (Emotion Vector, 7-axis, TLP, RDE)",
                lines=30,
                max_lines=100,
                show_copy_button=True,
                interactive=False,
            )
        )
    
    with gr.Tab("Advanced Analysis"):
        advanced_analysis_out = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Advanced Analysis (Semantic Layers, Integrity, Runtime, Integrations)",
                lines=30,
                max_lines=100,
                show_copy_button=True,
                interactive=False,
            )
        )
    
    with gr.Tab("Genre Selection Process"):
        genre_selection_out = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Genre Selection Process (Clusters, Scores, Routing, Matrix Details)",
                lines=30,
                max_lines=100,
                show_copy_button=True,
                interactive=False,
            )
        )
    
    with gr.Tab("Unique Values"):
        unique_values_out = gr.Textbox(
            **_safe_textbox_kwargs(
                label="Unique Individual Values (Non-duplicated across sections)",
                lines=30,
                max_lines=100,
                show_copy_button=True,
                interactive=False,
            )
        )

    with gr.Tab("Diagnostics / JSON"):
        diag_input = gr.Textbox(label="Текст", lines=4)
        diag_btn = gr.Button("Диагностика")
        diag_json_out = gr.JSON(label="JSON")

    def _on_analyze(text, gender):
        style_p, lyrics_p, ui_t, fanf_t, pulse, tlp_txt, rde_txt, lower_txt, matrix_arch, vector_anal, advanced_anal, genre_sel, unique_vals = (
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
            matrix_arch,
            vector_anal,
            advanced_anal,
            genre_sel,
            unique_vals,
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
            matrix_arch_out,
            vector_analysis_out,
            advanced_analysis_out,
            genre_selection_out,
            unique_values_out,
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
        except Exception as e:
            print(f"❌ App test failed with unexpected error: {e}")
            traceback.print_exc()
            sys.exit(1)

    # Конфигурация для деплоя
    port_str = os.getenv("PORT", "7860")
    server_port = int(port_str) if port_str.isdigit() else 7860
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    share = os.getenv("GRADIO_SHARE", "False").lower() == "true"

    demo.launch(server_name=server_name, server_port=server_port, share=share)
