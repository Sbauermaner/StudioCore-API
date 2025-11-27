# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
FusionEngine v6.4

Задача:
- взять разрозненные куски анализа (emotion, bpm, tonality, style, color, genre_route)
- уважить legacy - настройки пользователя (bpm / key / genre / mood)
- собрать единый "fusion_summary" с:
    * final_bpm
    * final_key
    * final_genre + subgenre
    * mood_label
    * color_signature
    * suno_style_prompt
    * suno_lyrics_prompt
    * diagnostics
"""

from typing import Any, Dict


class FusionEngineV64:
    """Объединяющий слой StudioCore v6.4.

    Ожидаемый входной payload (из core_v6):
    - legacy: dict (старый движок: emotions / tlp / style / bpm / инструменты)
    - emotion: dict (profile, dominant, curve)
    - bpm: dict (estimate, locks, manual_override)
    - tonality: dict (section_keys, mode)
    - color: dict (profile / wave)
    - instrumentation: dict (selection, emotion, color)
    - genre_route: dict (genre, subgenre, suno_style)
    """

    def _get_dominant_emotion(self, emotion: Dict[str, Any]) -> str:
        profile = emotion.get("profile") or {}
        if not profile:
            return emotion.get("dominant") or "neutral"
        # максимум по значению
        return max(profile.items(), key=lambda kv: kv[1])[0]

    def _resolve_bpm(self, legacy: Dict[str, Any], bpm: Dict[str, Any]) -> float:
        # 1) если legacy явно задали bpm — уважаем его
        legacy_bpm = legacy.get("bpm")
        if isinstance(legacy_bpm, (int, float)) and legacy_bpm > 0:
            return float(legacy_bpm)

        locks = bpm.get("locks") or {}
        manual = bpm.get("manual_override") or {}
        manual_bpm = manual.get("bpm")

        # 2) если есть ручная блокировка — берем её
        if locks.get("user_lock") and isinstance(manual_bpm, (int, float)):
            return float(manual_bpm)

        # 3) иначе — оценка движка / target_bpm
        estimate = bpm.get("estimate")
        if isinstance(estimate, (int, float)) and estimate > 0:
            return float(estimate)

        emotion_map = bpm.get("emotion_map") or {}
        target = emotion_map.get("target_bpm")
        if isinstance(target, (int, float)) and target > 0:
            return float(target)

        # 4) запасной вариант
        fallback = locks.get("fallback_bpm", 120)
        return float(fallback)

    def _resolve_key(self, legacy: Dict[str, Any], tonality: Dict[str, Any]) -> str:
        # 1) пробуем legacy.style.key
        style = legacy.get("style") or {}
        key = style.get("key")
        if isinstance(key, str) and key.strip():
            return key.strip()

        # 2) берем первую секционную тональность
        section_keys = tonality.get("section_keys") or []
        if section_keys:
            return str(section_keys[0])

        # 3) используем fallback_key
        fallback = tonality.get("fallback_key")
        if isinstance(fallback, str) and fallback.strip():
            return fallback.strip()

        # 4) дефолт
        return "C (C minor)"

    def _resolve_genre(
        self, legacy: Dict[str, Any], genre_route: Dict[str, Any]
    ) -> Dict[str, str]:
        style = legacy.get("style") or {}
        legacy_genre = style.get("genre")
        # если пользователь явно прописал жанр — уважаем
        if (
            isinstance(legacy_genre, str)
            and legacy_genre.strip()
            and legacy_genre not in ("auto", "adaptive")
        ):
            main = legacy_genre.strip()
            sub = genre_route.get("subgenre") or main
            return {
                "genre": main,
                "subgenre": sub,
                "source": "legacy",
            }

        # иначе — берем маршрут из GenreRoutingEngineV64
        main = genre_route.get("genre") or "cinematic_neutral"
        sub = genre_route.get("subgenre") or main
        return {
            "genre": str(main),
            "subgenre": str(sub),
            "source": "routed",
        }

    def _resolve_mood(self, legacy: Dict[str, Any], emotion: Dict[str, Any]) -> str:
        style = legacy.get("style") or {}
        mood = style.get("mood")
        if isinstance(mood, str) and mood.strip():
            return mood.strip()
        dominant = self._get_dominant_emotion(emotion)
        return f"{dominant}_driven"

    def _resolve_instrumentation(
        self, legacy: Dict[str, Any], instrumentation: Dict[str, Any]
    ) -> str:
        # 1) если legacy.instruments есть — собираем их
        legacy_instr = legacy.get("instruments") or []
        if isinstance(legacy_instr, list) and legacy_instr:
            return ", ".join(str(x) for x in legacy_instr)

        # 2) берем selection.selected из нового движка
        selection = instrumentation.get("selection") or {}
        selected = selection.get("selected") or []
        if isinstance(selected, list) and selected:
            return ", ".join(str(x) for x in selected)

        # 3) fallback: вся палитра
        palette = instrumentation.get("palette") or []
        if palette:
            return ", ".join(str(x) for x in palette[:5])

        return "piano, strings, bass, pads"

    def _resolve_vocal_profile(
        self, legacy: Dict[str, Any], vocal: Dict[str, Any]
    ) -> str:
        # 1) legacy.vocals + vocal_form
        vocals = legacy.get("vocals") or []
        vocal_form = legacy.get("vocal_form") or ""
        if vocals:
            profile = ", ".join(str(v) for v in vocals)
            if vocal_form:
                return f"{vocal_form}: {profile}"
            return profile

        # 2) новый vocal - профиль
        tone = vocal.get("tone") or "neutral"
        style = vocal.get("style") or "standard"
        gender = vocal.get("gender") or "neutral"
        return f"{gender} vocal, {tone}, {style}"

    def _resolve_visuals(self, legacy: Dict[str, Any], color: Dict[str, Any]) -> str:
        style = legacy.get("style") or {}
        visual = style.get("visual")
        if isinstance(visual, str) and visual.strip():
            return visual.strip()

        profile = color.get("profile") or {}
        primary = profile.get("primary_color") or "soft light"
        accent = profile.get("accent_color") or "shadows"
        return f"{primary} with {accent}"

    def _build_suno_style_prompt(
        self,
        genre_info: Dict[str, str],
        mood: str,
        instruments: str,
        vocal_profile: str,
        visuals: str,
        bpm: float,
        key: str,
    ) -> str:
        # итоговый блок для Suno "Style of Music"
        return (
            f"[GENRE: {genre_info['genre']} / {genre_info['subgenre']}]\n"
            f"[MOOD: {mood}]\n"
            f"[INSTRUMENTATION: {instruments}]\n"
            f"[VOCAL: {vocal_profile}]\n"
            f"[PRODUCTION: {visuals}]\n"
            f"[BPM: {int(round(bpm))}]\n"
            f"[KEY: {key}]"
        )

    def _build_suno_lyrics_prompt(
        self,
        mood: str,
        dominant_emotion: str,
        tlp: Dict[str, float],
    ) -> str:
        # компактный подсказчик для "Lyrics" — чтобы Suno понимал эмоциональное
        # ядро
        truth = tlp.get("truth", 0.0)
        love = tlp.get("love", 0.0)
        pain = tlp.get("pain", 0.0)
        return (
            f"(mood: {mood}) "
            f"(dominant_emotion: {dominant_emotion}) "
            f"(TLP: truth={truth:.2f}, love={love:.2f}, pain={pain:.2f})"
        )

    def fuse(
        self, payload: Dict[str, Any], *, genre_route: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Главный метод.

        Принимает:
            payload: огромный результат core.analyze(...)
            genre_route: результат GenreRoutingEngineV64.route(...)

        Возвращает:
            fusion_summary: dict с финальными параметрами
        """
        legacy = (
            payload.get("legacy") or payload.get("symbiosis", {}).get("legacy") or {}
        )
        emotion = (
            payload.get("emotion") or payload.get("symbiosis", {}).get("emotion") or {}
        )
        bpm = payload.get("bpm") or payload.get("symbiosis", {}).get("bpm") or {}
        tonality = (
            payload.get("tonality")
            or payload.get("symbiosis", {}).get("tonality")
            or {}
        )
        color = payload.get("color") or payload.get("symbiosis", {}).get("color") or {}
        instrumentation = (
            payload.get("instrumentation")
            or payload.get("symbiosis", {}).get("instrumentation")
            or {}
        )
        vocal = payload.get("vocal") or payload.get("symbiosis", {}).get("vocal") or {}
        tlp = (
            legacy.get("tlp")
            or payload.get("tlp")
            or payload.get("symbiosis", {}).get("tlp")
            or {}
        )

        dominant = self._get_dominant_emotion(emotion)
        final_bpm = self._resolve_bpm(legacy, bpm)
        final_key = self._resolve_key(legacy, tonality)
        genre_info = self._resolve_genre(legacy, genre_route)
        mood_label = self._resolve_mood(legacy, emotion)
        instruments = self._resolve_instrumentation(legacy, instrumentation)
        vocal_profile = self._resolve_vocal_profile(legacy, vocal)
        visuals = self._resolve_visuals(legacy, color)

        suno_style_prompt = self._build_suno_style_prompt(
            genre_info=genre_info,
            mood=mood_label,
            instruments=instruments,
            vocal_profile=vocal_profile,
            visuals=visuals,
            bpm=final_bpm,
            key=final_key,
        )

        suno_lyrics_prompt = self._build_suno_lyrics_prompt(
            mood=mood_label,
            dominant_emotion=dominant,
            tlp=tlp,
        )

        fusion_summary = {
            "final_bpm": final_bpm,
            "final_key": final_key,
            "final_genre": genre_info["genre"],
            "final_subgenre": genre_info["subgenre"],
            "mood": mood_label,
            "dominant_emotion": dominant,
            "visuals": visuals,
            "instruments": instruments,
            "vocal_profile": vocal_profile,
            "suno_style_prompt": suno_style_prompt,
            "suno_lyrics_prompt": suno_lyrics_prompt,
            "source": {
                "genre_source": genre_info["source"],
            },
        }

        return fusion_summary


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
