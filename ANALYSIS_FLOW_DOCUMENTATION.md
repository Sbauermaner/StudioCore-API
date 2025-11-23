# 📊 Полная последовательность анализов StudioCore V6

## 🎯 Общая архитектура

```
analyze(text) 
  → Подготовка текста
  → _backend_analyze() 
  → Параллельные анализы движков
  → Сборка результатов
  → Финальная обработка
  → Возврат результата
```

---

## 📋 Детальная последовательность

### **ЭТАП 1: Инициализация и валидация** (строки 563-612)

```python
def analyze(self, text: str, **kwargs):
    # 1.1 Создание движков (stateless - новые для каждого запроса)
    engines = self._build_engine_bundle()
    self._engine_bundle = engines
    
    # 1.2 Валидация входных данных
    if not isinstance(text, str):
        return error_payload
    if not text.strip():
        return error_payload
    
    # 1.3 Получение движков из bundle
    text_engine = engines["text_engine"]
    emotion_engine = engines["emotion_engine"]
    bpm_engine = engines["bpm_engine"]
    # ... и т.д.
    
    # 1.4 Сброс состояния движков
    text_engine.reset()
    
    # 1.5 Обрезка текста (если превышает MAX_INPUT_LENGTH)
    if len(incoming_text) > max_len:
        incoming_text = incoming_text[:max_len]
```

**Результат этапа**: Подготовленный текст и инициализированные движки

---

### **ЭТАП 2: Предобработка текста** (строки 613-636)

```python
    # 2.1 Парсинг пользовательских параметров
    params = self._merge_user_params(dict(kwargs))
    override_manager = engines["user_override_manager_cls"](overrides)
    
    # 2.2 Извлечение команд и тегов из текста
    cleaned_text, command_bundle, preserved_tags = extract_commands_and_tags(incoming_text)
    commands = list(command_bundle.get("detected", []))
    
    # 2.3 Определение языка
    language_info = detect_language(cleaned_text)
    
    # 2.4 Перевод (если нужно)
    translated_text, was_translated = translate_text_for_analysis(
        cleaned_text, language_info["language"]
    )
    
    # 2.5 Построение контекста структуры
    structure_context = self._build_structure_context(
        translated_text,
        params.get("semantic_hints"),
        commands=commands,
        preserved_tags=preserved_tags,
        language_info=language_info,
    )
    
    # 2.6 Применение пользовательских переопределений
    structure_context = self._apply_overrides_to_context(
        structure_context,
        override_manager,
        text=translated_text,
    )
```

**Результат этапа**: Очищенный, переведенный текст + структурированный контекст

---

### **ЭТАП 3: Основной анализ (_backend_analyze)** (строки 998-1890)

#### **3.1 Разрешение секций** (строки 1012-1014)
```python
    base_sections = list(structure_context.get("sections", []))
    hinted_sections = semantic_hints.get("sections")
    sections = self._resolve_sections_from_hints(text, hinted_sections, fallback_sections=base_sections)
```

#### **3.2 Анализ эмоций** (строки 1022-1028)
```python
    # Базовый профиль эмоций
    emotion_profile = self.emotion_engine.emotion_detection(text)
    
    # Кривая интенсивности эмоций
    emotion_curve = self.emotion_engine.emotion_intensity_curve(text)
    
    # Динамический профиль (7 осей)
    dynamic_emotion_profile = self.dynamic_emotion_engine.emotion_profile(text)
    
    # Сброс phrase packets перед анализом
    self._emotion_engine.reset_phrase_packets()
    
    # Интеллектуальный анализ секций
    section_intel_payload = self.section_intelligence.analyze(
        text, sections, emotion_curve, emotion_engine=self._emotion_engine
    )
    
    # Глобальная кривая эмоций
    section_emotions = list(section_intel_payload.get("section_emotions", []))
    global_emotion_curve = build_global_emotion_curve(section_emotions)
    curve_dict = global_emotion_curve.to_dict()
```

#### **3.3 Обновление semantic_hints** (строки 1042-1050)
```python
    semantic_hints = self._merge_semantic_hints(
        semantic_hints,
        {
            "dominant_emotion": max(emotion_profile, key=emotion_profile.get),
            "emotion_curve_max": max(emotion_curve),
            "section_intelligence": section_intel_payload,
            "emotion_profile_axes7": dynamic_emotion_profile,
        },
    )
```

#### **3.4 Вызов Legacy Core** (строки 1062-1080)
```python
    # Параллельный анализ через legacy core для совместимости
    legacy_core = self._legacy_core_cls()
    legacy_result = legacy_core.analyze(
        original_text or text,
        preferred_gender=preferred_gender,
        version=version,
        semantic_hints=copy.deepcopy(semantic_hints),  # Глубокая копия!
    )
    
    # Проверка на ошибки legacy
    if legacy_error_detected:
        legacy_result = {"error": legacy_result["error"]}  # Защита от утечки данных
```

#### **3.5 Структурный анализ** (строки 1082-1103)
```python
    structure = {
        "sections": sections,
        "intro": self.text_engine.detect_intro(text, sections=sections),
        "verse": self.text_engine.detect_verse(text, sections=sections),
        "prechorus": self.text_engine.detect_prechorus(text, sections=sections),
        "chorus": self.text_engine.detect_chorus(text, sections=sections),
        "bridge": self.text_engine.detect_bridge(text, sections=sections),
        "outro": self.text_engine.detect_outro(text, sections=sections),
        "meta_pause": self.text_engine.detect_meta_pause(text, sections=sections),
        "intelligence": section_intel_payload,
    }
```

#### **3.6 TLP (Truth, Love, Pain) анализ** (строки 1110-1129)
```python
    tlp_profile = {
        "truth": float(min(1, max(0, self.tlp_engine.truth_score(text)))),
        "love": float(min(1, max(0, self.tlp_engine.love_score(text)))),
        "pain": float(min(1, max(0, self.tlp_engine.pain_score(text)))),
    }
    tlp_profile["conscious_frequency"] = round(
        (tlp_profile["truth"] + tlp_profile["love"] + tlp_profile["pain"]) / 3, 4
    )
```

#### **3.7 Эмоциональный payload** (строки 1130-1138)
```python
    emotion_payload = {
        "profile": emotion_profile,
        "dynamic_profile": dynamic_emotion_profile,
        "curve": emotion_curve,
        "pivots": self.emotion_engine.emotion_pivot_points(text, intensity_curve=emotion_curve),
        "secondary": self.emotion_engine.secondary_emotion_detection(emotion_profile),
        "conflict": self.emotion_engine.emotion_conflict_map(emotion_profile),
    }
    emotion_payload = self._merge_semantic_hints(emotion_payload, semantic_hints.get("emotion", {}))
```

#### **3.8 Цветовой профиль** (строки 1143-1146)
```python
    color_profile = self.color_engine.assign_color_by_emotion(emotion_profile)
    color_wave = self.color_engine.generate_color_wave(emotion_profile)
    color_transitions = self.color_engine.color_transition_map(emotion_profile)
```

#### **3.9 Вокальный анализ** (строки 1148-1165)
```python
    voice_gender = self.vocal_engine.detect_voice_gender(text)
    voice_type = self.vocal_engine.detect_voice_type(text)
    voice_emotion_vector = self.emotion_engine.export_emotion_vector(text)
    voice_tone = self.vocal_engine.detect_voice_tone(text, emotion=voice_emotion_vector)
    voice_style = self.vocal_engine.detect_vocal_style(text, voice_type=voice_type, voice_tone=voice_tone)
    vocal_dynamics = self.vocal_engine.vocal_dynamics_map(sections)
    vocal_curve = self.vocal_engine.vocal_intensity_curve(vocal_dynamics)
    
    vocal_payload = {
        "gender": voice_gender,
        "type": voice_type,
        "tone": voice_tone,
        "style": voice_style,
        "dynamics": vocal_dynamics,
        "intensity_curve": vocal_curve,
        "average_intensity": round(sum(vocal_curve) / max(len(vocal_curve), 1), 3),
    }
```

#### **3.10 Дыхательный анализ** (строки 1171-1180)
```python
    breathing_profile = {
        "inhale_points": self.breathing_engine.detect_inhale_points(text),
        "short_breath": self.breathing_engine.detect_short_breath(text),
        "broken_breath": self.breathing_engine.detect_broken_breath(text),
        "spasms": self.breathing_engine.detect_spasms(text),
    }
    breathing_profile.update(self.breathing_engine.detect_emotional_breathing(text, emotion_profile))
    breath_sync = self.breathing_engine.breath_to_emotion_sync(text, emotion_profile)
```

#### **3.11 BPM анализ** (строки 1182-1231)
```python
    # Получение BPM из legacy (если доступно)
    legacy_bpm = legacy_result.get("bpm") or legacy_result.get("style", {}).get("bpm")
    
    # Оценка BPM из текста
    bpm_estimate = self.bpm_engine.text_bpm_estimation(text)
    
    # Приоритет: user_hint > legacy_bpm > semantic_suggested > text_estimation
    if isinstance(user_bpm_hint, (int, float)):
        bpm_estimate = float(user_bpm_hint)
    elif legacy_bpm is not None:
        bpm_estimate = float(legacy_bpm)
    
    # Применение override
    bpm_estimate = self.override_engine.resolve_bpm(override_manager, bpm_estimate)
    
    # Кривая BPM по секциям
    bpm_curve = self.bpm_engine.meaning_bpm_curve(sections, base_bpm=bpm_estimate)
    
    # Ограничение вариаций BPM
    bpm_estimate, bpm_curve, bpm_locks = self._enforce_bpm_limits(
        bpm_estimate, bpm_curve, override_manager.overrides, len(sections)
    )
    
    # Маппинг эмоций на BPM
    bpm_mapping = self.bpm_engine.emotion_bpm_mapping(emotion_profile, base_bpm=bpm_estimate)
    
    # Интеграция дыхания с BPM
    bpm_breath = self.bpm_engine.breathing_bpm_integration(breathing_profile, bpm_estimate)
    
    # Полиритмия
    bpm_poly = self.bpm_engine.poly_rhythm_detection(bpm_curve)
    
    bpm_payload = {
        "estimate": bpm_estimate,
        "emotion_map": bpm_mapping,
        "curve": bpm_curve,
        "breathing": bpm_breath,
        "poly_rhythm": bpm_poly,
        "locks": bpm_locks,
    }
```

#### **3.12 Анализ смысла (Meaning Velocity)** (строки 1233-1243)
```python
    meaning_curve = self.meaning_engine.meaning_curve_generation(sections)
    meaning_shifts = self.meaning_engine.semantic_shift_detection(sections)
    meaning_accel = self.meaning_engine.meaning_acceleration(meaning_curve)
    meaning_fractures = self.meaning_engine.meaning_fracture_detection(meaning_shifts.get("shifts", []))
    
    meaning_payload = {
        "curve": meaning_curve,
        "shifts": meaning_shifts,
        "acceleration": meaning_accel,
        "fractures": meaning_fractures,
    }
```

#### **3.13 Тональность (Tonality)** (строки 1245-1295)
```python
    # Определение лада
    mode_result = self.tonality_engine.mode_detection(emotion_profile, tlp_profile)
    mode = self.tonality_engine.major_minor_classifier(sections, mode_result.get("mode", "major"))
    
    # Ключи для секций
    section_keys = self.tonality_engine.section_key_selection(sections, mode)
    modal_shifts = self.tonality_engine.modal_shift_detection(section_keys)
    
    # Выравнивание ключей с override
    section_keys, mode, anchor_key = self._align_section_keys(
        section_keys, override_manager.overrides, sections, mode
    )
    
    tonality_payload = {
        "mode": mode,
        "confidence": mode_result.get("confidence"),
        "section_keys": section_keys,
        "modal_shifts": modal_shifts,
        "key_curve": self.tonality_engine.key_transition_curve(section_keys),
        "fallback_key": anchor_key,
    }
    
    # Применение legacy key (если доступен)
    if legacy_key and not override_manager.overrides.key:
        tonality_payload["mode"] = "minor" if "minor" in str(legacy_key).lower() else "major"
        tonality_payload["section_keys"] = [legacy_key] * len(sections)
    
    # Эмоциональная модуляция тональности
    tone_result = self.tone_engine.detect_key(text)
    for ev in smoothed_vectors:
        mod = self.tone_engine.apply_emotion_modulation(
            {"key": tone_result.get("key"), "mode": mode},
            ev,
        )
        local_tone_mod.append(mod)
    
    # Применение финальной модуляции
    if local_tone_mod and (final_mod := local_tone_mod[-1]):
        if final_mod.get("key") and tonality_payload.get("key") in (None, "auto"):
            tonality_payload["key"] = final_mod["key"]
            tonality_payload["source"] = "emotional_tone_modulation"
```

#### **3.14 Частотный профиль (Frequency)** (строки 1297-1306)
```python
    freq_profile = self.frequency_engine.resonance_profile(tlp_profile)
    freq_profile["recommended_octaves"] = self.rns_safety.clamp_octaves(
        freq_profile.get("recommended_octaves", [])
    )
    freq_profile["safe_band_hz"] = self.rns_safety.clamp_band(freq_profile.get("safe_band_hz", 0.0))
```

#### **3.15 Инструментация** (строки 1308-1345)
```python
    # Выбор инструментов на основе жанра
    instrument_selection = self.instrumentation_engine.instrument_selection(
        genre=legacy_result.get("style", {}).get("genre"),
        energy=semantic_hints.get("target_energy", bpm_mapping.get("target_energy")),
        mood=semantic_hints.get("target_mood"),
        reference_palette=semantic_hints.get("instrument_palette"),
    )
    
    # Инструменты на основе эмоций
    instrument_emotion = self.instrumentation_engine.instrument_based_on_emotion(
        emotion_profile,
        base_palette=instrument_selection.get("palette"),
    )
    
    # Инструменты на основе вокала
    instrument_voice = self.instrumentation_engine.instrument_based_on_voice(
        vocal_for_instrumentation.get("style"),
        target_energy=bpm_mapping.get("target_energy"),
    )
    
    # Инструменты на основе цвета
    instrument_color = self.instrumentation_engine.instrument_color_sync(
        color_profile,
        base_palette=instrument_emotion.get("palette"),
    )
    
    # Инструменты на основе ритма
    instrument_rhythm = self.instrumentation_engine.instrument_rhythm_sync(
        bpm_estimate,
        rhythm_profile=bpm_curve,
    )
    
    instrumentation_payload = {
        "selection": instrument_selection,
        "emotion": instrument_emotion,
        "voice": instrument_voice,
        "color": instrument_color,
        "rhythm": instrument_rhythm,
        "palette": instrument_color.get("palette") or instrument_emotion.get("palette") or instrument_selection.get("palette"),
    }
```

#### **3.16 Команды** (строки 1347-1361)
```python
    command_payload = {
        "detected": commands,
        "bpm": self.command_interpreter.execute_bpm_commands(commands, base_bpm=bpm_estimate),
        "key": self.command_interpreter.execute_key_commands(commands, default_key=section_keys[0]),
        "rhythm": self.command_interpreter.execute_rhythm_commands(commands),
        "emotion": self.command_interpreter.execute_emotion_commands(commands),
        "style": self.command_interpreter.execute_style_commands(commands),
    }
```

#### **3.17 REM синхронизация** (строки 1363-1375)
```python
    rem_conflicts = self.rem_engine.detect_layer_conflicts(structure, bpm_curve, instrument_selection)
    rem_resolution = self.rem_engine.resolve_layer_conflicts(rem_conflicts)
    rem_dominant = self.rem_engine.assign_dominant_layer(structure=structure, emotion=emotion_payload)
    rem_alignment = self.rem_engine.align_layers_for_final_output(
        structure, instrument_selection, tonality_payload
    )
    
    rem_payload = {
        "conflicts": rem_conflicts,
        "resolution": rem_resolution,
        "dominant_layer": rem_dominant,
        "alignment": rem_alignment,
    }
```

#### **3.18 Zero Pulse** (строки 1377-1384)
```python
    zero_pulse_payload = {
        "structure_hint": zero_hint,
        "analysis": self.zero_pulse_engine.detect_zero_pulse(text),
        "vacuum": self.zero_pulse_engine.vacuum_beat_state(text),
        "emotion": self.zero_pulse_engine.silence_as_emotion(text, emotion_profile),
        "transition": self.zero_pulse_engine.silence_as_transition(text),
    }
```

#### **3.19 Динамика инструментов** (строки 1386-1392)
```python
    instrument_dynamics_payload = self.instrument_dynamics.map_instruments_to_structure(
        sections,
        instrumentation_payload.get("palette"),
        bpm_payload,
        emotion_payload,
        zero_pulse_payload,
    )
```

#### **3.20 Построение feature map для жанра** (строки 1394-1656)
```python
    # Вычисление множества признаков для определения жанра
    semantic_aggression = _clamp(conflict_value + emotion_profile.get("anger", 0.0) * 0.4)
    power_vector = _clamp((bpm_value / 180.0) + avg_intensity * 0.3)
    rhythm_density = _clamp(density / max(bpm_value or 120.0, 1.0))
    edge_factor = emotion_profile.get("anger", 0.0) * 0.6
    narrative_pressure = _clamp(accel_value + fractures * 0.1)
    emotional_gradient = _clamp(amplitude / gradient_max)
    # ... и еще ~20 признаков
    
    genre_feature_inputs = {
        "semantic_aggression": semantic_aggression,
        "power_vector": power_vector,
        "rhythm_density": rhythm_density,
        # ... все признаки
    }
    
    feature_map = self.build_feature_map(genre_feature_inputs)
    domain_genre = self.genre_matrix.evaluate(feature_map)
```

#### **3.21 Стиль (Style)** (строки 1689-1755)
```python
    # Выбор жанра
    style_genre = (
        style_commands.get("genre")
        or semantic_hints.get("style", {}).get("genre")
        or domain_genre
        or self.style_engine.genre_selection(emotion_profile, tlp_profile)
    )
    
    # Выбор настроения
    style_mood = (
        style_commands.get("mood")
        or semantic_hints.get("style", {}).get("mood")
        or self.style_engine.mood_selection(emotion_profile, tlp_profile)
    )
    
    # Построение финального промпта стиля
    style_prompt = self.style_engine.final_style_prompt_build(
        genre=style_genre,
        mood=style_mood,
        tone=self.style_engine.tone_style({
            "mode": tonality_payload.get("mode"),
            "section_keys": tonality_payload.get("section_keys", []),
        }),
        instrumentation=style_instrumentation,
        vocal=style_vocal,
        visual=style_visual,
    )
```

#### **3.22 Роутинг жанра** (строки 1761-1790)
```python
    router_input = {
        **result,
        "bpm": bpm_payload,
        "tlp": tlp_profile,
        "integrity": integrity_block,
        "emotion": {**emotion_payload, "label": emotion_label},
        "style": {**style_payload},
    }
    macro_genre, genre_reason = self.genre_router.route(router_input)
    
    # Обновление style_payload с финальным жанром
    if "genre" not in style_block or str(style_block.get("genre")).lower() in ("auto", "unknown", ""):
        style_block["genre"] = macro_genre
```

#### **3.23 Финальная эмоциональная профилировка** (строки 1792-1828)
```python
    emotion_profile_v1 = self._emotion_engine.build_emotion_profile(
        text,
        legacy_context={
            "style": style_payload,
            "bpm": bpm_payload,
            "tone": tonality_payload,
            "commands": command_payload,
        },
    )
    
    # Финальный выбор жанра
    final_genre = self._emotion_engine.pick_final_genre(
        emotion_profile_v1.get("genre_scores", {}),
        legacy_genre=legacy_genre,
    )
    
    # Финальный BPM
    final_bpm = legacy_bpm or emotion_profile_v1.get("bpm")
    
    # Финальный ключ
    final_key = legacy_key or (emotion_profile_v1.get("key") or {}).get("scale")
    
    # Применение финальных значений (если нет override)
    if "bpm" not in overrides_block:
        bpm_payload["estimate"] = final_bpm
    if "genre" not in overrides_block:
        style_payload.setdefault("genre", final_genre)
    if "key" not in overrides_block:
        tonality_payload.setdefault("key", final_key)
```

#### **3.24 RDE Summary** (строки 1832-1836)
```python
    rde_summary = {
        "resonance": self.rde_engine.calc_resonance(text),
        "fracture": self.rde_engine.calc_fracture(text),
        "entropy": self.rde_engine.calc_entropy(text),
    }
```

#### **3.25 Integrity проверка** (строки 1838-1839)
```python
    integrity_report = self.integrity_engine.analyze(text)
```

#### **3.26 Аннотации** (строки 1841-1850)
```python
    annotations = {
        "vocal": self.annotation_engine.add_vocal_annotations(sections, vocal_payload),
        "breath": self.annotation_engine.add_breath_annotations(sections, breathing_profile),
        "tonality": self.annotation_engine.add_tonal_annotations(sections, tonality_payload),
        "emotion": self.annotation_engine.add_emotional_annotations(sections, emotion_payload),
        "rhythm": self.annotation_engine.add_rhythm_annotations(sections, bpm_curve),
    }
```

#### **3.27 Сборка результата** (строки 1852-1890)
```python
    result.update({
        "legacy": legacy_result,
        "structure": structure,
        "emotion": emotion_payload,
        "color": {
            "profile": color_profile,
            "wave": color_wave,
            "transitions": color_transitions,
        },
        "vocal": vocal_payload,
        "breathing": {**breathing_profile, "sync": breath_sync},
        "bpm": bpm_payload,
        "meaning": meaning_payload,
        "tonality": tonality_payload,
        "instrumentation": instrumentation_payload,
        "rem": rem_payload,
        "zero_pulse": zero_pulse_payload,
        "tlp": dict(tlp_profile),
        "style": style_payload,
        "freq_profile": freq_profile,
        "rns_safety": {...},
        "integrity": integrity_report,
        "commands": command_payload,
        "annotations": annotations,
        "phrase_packets": section_intel_payload.get("phrase_packets", []),
        "section_emotions": section_intel_payload.get("section_emotions", []),
        "semantic_hints": semantic_hints,
        "auto_context": structure_context,
        "emotion_curve": curve_dict,
        "instrument_dynamics": instrument_dynamics_payload,
        "override_debug": override_manager.debug_summary(),
        "rde_summary": rde_summary,
        "genre_analysis": genre_analysis,
    })
```

#### **3.28 Emotion Matrix** (строки 1894-1906)
```python
    matrix = self.emotion_matrix.build_matrix(
        phrase_emotions=phrase_emotions,
        section_emotions=section_emotions,
        global_curve=curve_dict,
        tlp_profile=tlp_profile,
        dynamic_bias=dynamic_bias,
        genre_hint=result["style"].get("genre"),
        bpm_hint=result.get("bpm", {}).get("estimate"),
        key_hint=key_hint,
        suno_annotation=result.get("suno_annotation", {}),
    )
    emotion_matrix = matrix if isinstance(matrix, dict) else {}
```

#### **3.29 FANF аннотации** (строки 2016-2045)
```python
    fanf_analysis_payload = {
        "emotion": {"profile": emotion_profile, "curve": emotion_curve},
        "bpm": bpm_payload,
        "tonality": tonality_payload,
        "style": style_payload,
        "tlp": tlp_profile,
        "zero_pulse": zero_pulse_payload,
        "color": {"wave": color_wave, "profile": color_profile},
        "instrumentation": instrumentation_payload,
        "rde": rde_summary,
    }
    
    fanf_annotation = self.fanf_engine.build_annotations(
        text,
        sections,
        fanf_analysis_payload,
    )
    
    result["fanf"] = {
        "annotated_text_fanf": fanf_annotation.annotated_text_fanf,
        "annotated_text_ui": fanf_annotation.annotated_text_ui,
        "annotated_text_suno": fanf_annotation.annotated_text_suno,
        "choir_active": fanf_annotation.choir_active,
        "cinematic_header": fanf_annotation.cinematic_header,
        "resonance_header": fanf_annotation.resonance_header,
    }
```

**Результат этапа**: Полный `result` словарь со всеми анализами

---

### **ЭТАП 4: Постобработка в analyze()** (строки 644-872)

#### **4.1 Инъекция нормализованного текста** (строка 657)
```python
    backend_payload = self._inject_normalized_snapshot(normalized_text, backend_payload)
```

#### **4.2 Fusion и Suno** (строка 658)
```python
    backend_payload = self._apply_fusion_and_suno(backend_payload)
```

#### **4.3 Дополнительные анализы V2** (строки 660-703)
```python
    # Emotion Matrix V2
    emotion_matrix = emotion_engine_v2.analyze(incoming_text)
    
    # TLP вектор
    tlp = tlp_engine.tlp_vector(incoming_text, emotion_matrix)
    
    # BPM V2
    bpm_v2 = bpm_engine.compute_bpm_v2(incoming_text.splitlines())
    
    # RDE (Resonance, Dynamics, Emotion)
    rde = {
        "resonance": resonance_engine.calc_resonance(incoming_text),
        "fracture": resonance_engine.calc_fracture(incoming_text),
        "entropy": resonance_engine.calc_entropy(incoming_text),
    }
    
    # Tone Profile
    tone_profile = tse.build_profile(
        key=backend_payload.get("style", {}).get("key"),
        tlp=tlp,
        emotions=emotion_matrix,
    )
    
    # Добавление в payload
    backend_payload["emotion_matrix"] = emotion_matrix
    backend_payload["tlp"] = tlp
    backend_payload["rde"] = rde
    backend_payload["bpm"] = {**(bpm_block or {}), "flow_estimate": bpm_v2, "estimate": bpm_v2}
    backend_payload["tone_profile"] = tone_profile
```

#### **4.4 Применение Fusion результатов** (строки 705-727)
```python
    fusion_summary = backend_payload.get("fusion_summary")
    if fusion_summary:
        # Применение финального BPM из fusion
        final_bpm = fusion_summary.get("final_bpm")
        if final_bpm is not None:
            bpm_block["estimate"] = final_bpm
        
        # Применение финального ключа из fusion
        final_key = fusion_summary.get("final_key")
        if final_key is not None:
            backend_payload.setdefault("tonality", {})["key"] = final_key
        
        # Применение финального жанра из fusion
        final_genre = fusion_summary.get("final_genre")
        if final_genre:
            style_block["genre"] = final_genre
```

#### **4.5 Диагностика** (строки 736-805)
```python
    # Объединение диагностики
    diagnostics = {**diagnostics_block, **diagnostics}
    
    # Genre Universe
    genre_info = genre_universe.detect_domain(str(style_block.get("genre")))
    
    # Color диагностика
    color_diag = {"color_wave": color_wave}
    
    # TLP блок
    diagnostics["tlp_block"] = f"[TLP: {truth:.2f}/{love:.2f}/{pain:.2f} | CF {cf:.2f}]"
    
    # RDE блок
    diagnostics["rde_block"] = f"[RDE: resonance={resonance}, fracture={fracture}, entropy={entropy}]"
    
    # Genre блок
    diagnostics["genre_block"] = f"[Genre: {macro_genre}]"
    
    # ZeroPulse блок
    diagnostics["zeropulse_block"] = f"[ZeroPulse: {status}]"
    
    # Consistency Layer v8
    consistency_block = ConsistencyLayerV8(diagnostics).build()
    
    # Diagnostics Builder v8
    structured_diagnostics = DiagnosticsBuilderV8(
        base=diagnostics,
        payload=payload,
    ).build()
```

#### **4.6 FANF Output** (строки 837-853)
```python
    fanf_payload = self.build_fanf_output(
        text=normalized_text,
        style=style or {},
        lyrics={"sections": lyrics_sections},
        diagnostics=structured_diagnostics,
    )
    
    ui_text = _extract_ui_text(fanf_payload.get("lyrics_prompt", ""))
    
    fanf_block: dict[str, Any] = {}
    fanf_block.update(payload.get("fanf", {}))
    fanf_block.update(fanf_payload)
    fanf_block.setdefault("ui_text", ui_text)
    
    payload["summary"] = fanf_block.get("summary", summary_block)
    payload["fanf"] = fanf_block
```

#### **4.7 Финальная обработка** (строки 855-872)
```python
    final_result = self._finalize_result(payload)
    final_result["engine"] = "StudioCoreV6"
    final_result.setdefault("ok", True)
    final_result["diagnostics"] = structured_diagnostics
    final_result.setdefault("fanf", fanf_block)
    
    # Runtime logging
    write_runtime_log({
        "text_preview": text[:200],
        "diagnostics": final_result.get("diagnostics"),
        "fanf": final_result.get("fanf"),
    })
    
    return final_result
```

#### **4.8 Очистка состояния** (строки 873-874)
```python
    finally:
        self._reset_state()  # Гарантированная очистка
```

---

## 🔄 Схема потока данных

```
INPUT TEXT
    ↓
[Валидация]
    ↓
[Очистка + Перевод]
    ↓
[Извлечение команд]
    ↓
[Определение языка]
    ↓
┌─────────────────────────────────────┐
│     _backend_analyze()               │
│                                     │
│  ┌──────────────────────────────┐   │
│  │ 1. Эмоции                    │   │
│  │ 2. Структура                │   │
│  │ 3. TLP                      │   │
│  │ 4. Цвета                    │   │
│  │ 5. Вокал                    │   │
│  │ 6. Дыхание                  │   │
│  │ 7. BPM                      │   │
│  │ 8. Смысл                    │   │
│  │ 9. Тональность              │   │
│  │ 10. Частоты                 │   │
│  │ 11. Инструментация          │   │
│  │ 12. Команды                 │   │
│  │ 13. REM                     │   │
│  │ 14. Zero Pulse              │   │
│  │ 15. Жанр                    │   │
│  │ 16. Стиль                   │   │
│  │ 17. FANF                    │   │
│  └──────────────────────────────┘   │
│                                     │
│  [Legacy Core] ← параллельно        │
│                                     │
└─────────────────────────────────────┘
    ↓
[Fusion + Suno]
    ↓
[V2 Анализы]
    ↓
[Диагностика]
    ↓
[FANF Output]
    ↓
[_finalize_result()]
    ↓
OUTPUT RESULT
```

---

## 🔑 Ключевые моменты архитектуры

### 1. **Stateless дизайн**
- Каждый `analyze()` создает новые экземпляры движков
- `_reset_state()` гарантирует очистку после каждого запроса
- Нет shared mutable state между запросами

### 2. **Приоритеты данных**
- **User Overrides** > **Semantic Hints** > **Legacy Results** > **Auto Detection**
- Всегда проверяется наличие override перед применением автоматических значений

### 3. **Параллельные анализы**
- Legacy Core работает параллельно с основным анализом
- V2 движки (emotion_matrix, tlp, bpm_v2) работают после основного анализа

### 4. **Защита от утечек**
- `copy.deepcopy()` для semantic_hints при передаче в legacy
- Проверка ошибок legacy перед использованием данных
- Локальные переменные для всех временных данных

### 5. **Модульность**
- Каждый движок независим и может быть заменен
- Четкое разделение ответственности
- Легко тестировать отдельные компоненты

---

## 📝 Заключение

Весь процесс анализа состоит из **~30 этапов**, которые последовательно обрабатывают текст и собирают информацию о:
- Эмоциях и их динамике
- Структуре и секциях
- Ритме и BPM
- Тональности и гармонии
- Стиле и жанре
- Вокале и инструментации
- Дыхании и паузах
- И многом другом...

Все это объединяется в единый результат через `_finalize_result()` и возвращается пользователю.

---

## 📤 Структура финального вывода

После прохождения всех анализов метод `analyze()` возвращает словарь с полной структурой данных.

**📄 Подробная документация структуры вывода:** см. [OUTPUT_STRUCTURE.md](./OUTPUT_STRUCTURE.md)

### Основные блоки результата:

- **`structure`** - Структура текста и секций
- **`emotion`** - Эмоциональный профиль (базовый, динамический, кривая)
- **`style`** - Стиль, жанр, настроение, промпт
- **`bpm`** - Ритм, BPM, кривая по секциям
- **`tonality`** - Тональность, ключи, лад
- **`vocal`** - Вокальные характеристики
- **`instrumentation`** - Инструментация и палитра
- **`color`** - Цветовой профиль и волна
- **`breathing`** - Дыхательные паттерны
- **`tlp`** - Truth, Love, Pain профиль
- **`meaning`** - Семантический анализ
- **`rem`** - REM синхронизация слоев
- **`zero_pulse`** - Zero Pulse анализ
- **`fanf`** - FANF аннотации (style_prompt, lyrics_prompt, ui_text, summary)
- **`annotations`** - Аннотации текста
- **`diagnostics`** - Полная диагностическая информация
- **`emotion_matrix`** - Матрица эмоций V2
- **`legacy`** - Результаты legacy core

### Ключевые поля для использования:

**Для UI:**
- `fanf.ui_text` - очищенный текст
- `fanf.style_prompt` - промпт стиля
- `fanf.lyrics_prompt` - промпт текста
- `fanf.summary` - резюме

**Для музыкальной генерации:**
- `style.genre`, `style.mood`
- `bpm.estimate`
- `tonality.key`, `tonality.mode`
- `instrumentation.palette`
- `vocal.style`

