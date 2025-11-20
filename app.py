# -*- coding: utf-8 -*-
# =========================================
# 🔐 StudioCore — Protected Source File
# FINGERPRINT: StudioCore-FP-2025-SB-9fd72e27
# AI_TRAINING_PROHIBITED
# Unauthorized use, reproduction or AI-model training is strictly forbidden.
# Hash: 9fd72e27-app-protected
# =========================================
"""StudioCore v6.4 MAXI — FastAPI/Gradio bridge by Сергей Бауэр (@Sbauermaner).

Production-ready API gateway that mounts the StudioCore inference engine into a
FastAPI + Gradio stack. The application favours stateless execution, clean
diagnostics, and explicit reload controls so the runtime is safe for
public-facing deployments.
"""

import os
import sys
import traceback
import threading
import time
import io
import uvicorn
import logging
import subprocess # v10: ИСПРАВЛЕН NameError: name 'subprocess' is not defined
import importlib
import json
from dataclasses import asdict

# === 1. Исправление пути импорта ===
# (Нужно, если запускаем app.py из корня)
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# === 2. Активация логгера ===
# ДО импорта ядра
try:
    # v16: Исправлен TypeError
    from studiocore.logger import setup_logging
    # Устанавливаем уровень DEBUG, чтобы видеть все
    setup_logging(level=logging.DEBUG) 
except ImportError:
    print("WARNING: studiocore.logger не найден. Используется стандартный print.")
    logging.basicConfig(level=logging.DEBUG) # Fallback

log = logging.getLogger(__name__)
log.info(f"Запуск StudioCore v6.4 MAXI by @Sbauermaner... (PID: {os.getpid()})")
# === Конец активации логгера ===

import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ============================================================
# StudioCore Signature Block (Do Not Remove)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# AI_TRAINING_PROHIBITED
# This file is part of StudioCore v6.4 MAXI (Protected Edition)
# ============================================================

# === 3. Импорт ядра ===
try:
    from studiocore import (
        loader_diagnostics,
        STUDIOCORE_VERSION,
        MONOLITH_VERSION,
        LOADER_STATUS,
    )
    import studiocore.core_v6 as core_module
    log.info(
        f"Ядро StudioCore {STUDIOCORE_VERSION} импортировано (stateless режим)."
    )
except Exception as e:
    log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить модуль ядра: {e}")
    log.critical(traceback.format_exc())
    core_module = None

CORE_LOCK = threading.Lock()
CORE_RELOAD_REQUIRED = False
LAST_CORE_ERROR: str | None = None
CORE_SUCCESSFUL_INITS = 0
MAX_INPUT_LENGTH = 60000


def _ensure_core_module(force_reload: bool = False):
    global core_module, CORE_RELOAD_REQUIRED
    if core_module is None:
        raise RuntimeError("StudioCore модуль недоступен")
    if force_reload or CORE_RELOAD_REQUIRED:
        log.warning("Перезагрузка модуля StudioCoreV6 (force_reload=%s)", force_reload)
        core_module = importlib.reload(core_module)
        CORE_RELOAD_REQUIRED = False
    return core_module


def create_core_instance(force_reload: bool = False):
    global LAST_CORE_ERROR, CORE_SUCCESSFUL_INITS, CORE_RELOAD_REQUIRED
    module = _ensure_core_module(force_reload=force_reload or CORE_RELOAD_REQUIRED)
    with CORE_LOCK:
        try:
            instance = module.StudioCoreV6()
            CORE_SUCCESSFUL_INITS += 1
            LAST_CORE_ERROR = None
            return instance
        except Exception as exc:  # pragma: no cover - defensive guard
            LAST_CORE_ERROR = str(exc)
            CORE_RELOAD_REQUIRED = True
            log.error("Не удалось создать StudioCoreV6: %s", exc)
            raise


def _validate_input_length(text: str | None) -> tuple[bool, str | None]:
    payload = text or ""
    if len(payload) > MAX_INPUT_LENGTH:
        return (
            False,
            f"⚠️ Текст слишком длинный (>{MAX_INPUT_LENGTH} символов). Сократите ввод для обработки.",
        )
    return True, None

# === 4. Инициализация FastAPI ===
log.debug("Инициализация FastAPI...")
app = FastAPI(
    title="StudioCore v6.4 MAXI by @Sbauermaner",
    version=STUDIOCORE_VERSION,
    description=(
        "StudioCore v6.4 MAXI — FastAPI/Gradio bridge by Сергей Бауэр (@Sbauermaner)."
        " Stateless, безопасный и готовый к продакшену интерфейс."
    ),
    contact={"name": "Serhiy Bauer", "url": "https://github.com/Sbauermaner"},
    license_info={
        "name": "MIT License (with additional usage restrictions)",
        "url": "https://github.com/Sbauermaner/StudioCore/blob/main/LICENSE",
    },
)

# ===============================================
# NEW: /status endpoint
# ===============================================
@app.get("/status")
async def status():
    diag = loader_diagnostics()
    return {
        "status": "ok" if LAST_CORE_ERROR is None else "degraded",
        "loader": LOADER_STATUS,
        "core_version": STUDIOCORE_VERSION,
        "monolith_version": MONOLITH_VERSION,
        "core_inits": CORE_SUCCESSFUL_INITS,
        "reload_required": CORE_RELOAD_REQUIRED,
        "last_error": LAST_CORE_ERROR,
        "diagnostics": asdict(diag),
    }

# ===============================================
# NEW: stable JSON debug endpoint
# ===============================================


class DebugRequest(BaseModel):
    text: str


@app.post("/debug_json")
async def debug_json(req: DebugRequest):
    """
    Возвращает полный JSON-payload, минуя Gradio и консоль.
    Используется для диагностики: prompt_suno_style, annotated_text_suno,
    annotations, жанры, BPM, эмоции, структура, симбиоз.
    """

    core = create_core_instance(force_reload=False)
    result = core.analyze(req.text, preferred_gender="auto")
    return {"debug": True, "payload": result}


# ===============================================
# NEW: /version endpoint
# ===============================================
@app.get("/version")
async def version():
    return {
        "version": STUDIOCORE_VERSION,
        "monolith": MONOLITH_VERSION,
        "loader": LOADER_STATUS,
        "diagnostics": asdict(loader_diagnostics()),
    }


# ===============================================
# NEW: /diagnostics endpoint
# ===============================================
@app.get("/diagnostics")
async def diagnostics():
    diag = loader_diagnostics()
    return {
        "requested_order": list(diag.engine_order),
        "attempted": list(diag.attempted),
        "errors": list(diag.errors),
        "active": diag.active,
        "monolith_module": diag.monolith_module,
        "monolith_version": diag.monolith_version,
    }


@app.get("/health")
async def health(force_reload: bool = False):
    """
    Проверка того, что ядро можно создать и выполнить минимальный анализ.
    Здесь исправлена ошибка: global CORE_RELOAD_REQUIRED должен объявляться
    до любого использования внутри функции.
    """

    global CORE_RELOAD_REQUIRED

    try:
        core = create_core_instance(force_reload=force_reload)
        probe = core.analyze("healthcheck ping", preferred_gender="auto")
        status = "ok" if isinstance(probe, dict) and "error" not in probe else "degraded"
        
        return {
            "status": status,
            "core_inits": CORE_SUCCESSFUL_INITS,
            "reload_required": CORE_RELOAD_REQUIRED,
            "last_error": LAST_CORE_ERROR,
        }

    except Exception as exc:  # pragma: no cover - defensive guard
        CORE_RELOAD_REQUIRED = True
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(exc),
                "core_inits": CORE_SUCCESSFUL_INITS,
                "reload_required": CORE_RELOAD_REQUIRED,
                "last_error": LAST_CORE_ERROR,
            },
        )


@app.post("/healthcheck")
async def healthcheck(force_reload: bool = False):
    try:
        create_core_instance(force_reload=force_reload)
        return {
            "status": "ok",
            "core_inits": CORE_SUCCESSFUL_INITS,
            "reload_required": CORE_RELOAD_REQUIRED,
            "last_error": LAST_CORE_ERROR,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(exc),
                "reload_required": CORE_RELOAD_REQUIRED,
                "last_error": LAST_CORE_ERROR,
            },
        )

# === 5. CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 6. 🎧 PUBLIC API ENDPOINT ===
# (Исправляет HTTP 404 в тестах)

class PredictRequest(BaseModel):
    """ Модель запроса для API """
    text: str
    gender: str = "auto"
    tlp: Optional[dict] = None
    semantic_hints: Optional[dict] = None

@app.post("/api/predict")
async def api_predict(request_data: PredictRequest):
    """
    Эндпоинт, который ищут 'test_all.py' и 'auto_core_check'.
    Он принимает JSON и возвращает JSON.
    """
    log.debug(f"Входящий запрос /api/predict: {request_data.text[:50]}...")
    
    is_valid, validation_error = _validate_input_length(request_data.text)
    if not is_valid:
        return JSONResponse(content={"error": validation_error}, status_code=400)

    try:
        core = create_core_instance()
    except Exception as exc:
        log.error("API /api/predict: не удалось создать ядро: %s", exc)
        return JSONResponse(
            content={"error": f"Ядро недоступно: {exc}"},
            status_code=500,
        )

    try:
        result = core.analyze(
            request_data.text,
            preferred_gender=request_data.gender,
            semantic_hints=request_data.semantic_hints,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        global CORE_RELOAD_REQUIRED
        CORE_RELOAD_REQUIRED = True
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в /api/predict: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(exc)}, status_code=500)

    if isinstance(result, dict) and "error" in result:
        log.warning(f"API /api/predict: Ядро вернуло ошибку: {result['error']}")
        return JSONResponse(content=result, status_code=400)

    log.debug("API /api/predict: Анализ успешен.")
    return JSONResponse(content=result, status_code=200)

# === 7. SELF-CHECK ===
def auto_core_check():
    """ 
    Фоновая проверка API-эндпоинта (v7 - таймаут 20с).
    Дает серверу 5 секунд на запуск, затем пингует /api/predict.
    """
    log.debug("[Self-Check] Поток запущен, ожидание 5с...")
    time.sleep(5) 
    
    if os.environ.get("DISABLE_SELF_CHECK") == "1":
        log.info("[Self-Check] Проверка отключена (DISABLE_SELF_CHECK=1).")
        return
        
    try:
        import requests
    except ImportError:
        log.warning("[Self-Check] 'requests' не найден. Не могу выполнить самопроверку.")
        return

    log.debug("[Self-Check] Запуск самопроверки эндпоинта /api/predict...")
    api_url = "http://127.0.0.1:7860/api/predict"
    payload = {"text": "self-check test"}
    
    try:
        # v7: Таймаут 20с (для "Плана C" - быстрые словари)
        r = requests.post(api_url, json=payload, timeout=20) 
        log.info(f"[Self-Check] → Статус: {r.status_code}")
        if r.status_code != 200:
             log.warning(f"[Self-Check] → Ответ: {r.text[:200]}...")
    except Exception as e:
        log.error(f"❌ Self-Check ошибка: {e}")

# Запускаем проверку в отдельном потоке
threading.Thread(target=auto_core_check, daemon=True).start()


# === 8. АНАЛИЗ ТЕКСТА (Gradio) ===

def analyze_text(text: str, gender: str = "auto"):
    """Основная функция анализа текста через StudioCore для UI Gradio."""

    def _empty_payload(message: str = ""):
        return {
            prompt_suno_style: gr.update(value=""),
            annotated_text_suno: gr.update(value=""),
            annotated_text_ui: gr.update(value=""),
            annotated_text_fanf: gr.update(value=""),
            summary_box: gr.update(value=message or ""),
        }

    log.debug(f"Gradio analyze_text: получено {len(text)} символов, gender={gender}")

    if not text.strip():
        return _empty_payload("⚠️ Введите текст для анализа.")

    is_valid, validation_error = _validate_input_length(text)
    if not is_valid:
        return _empty_payload(validation_error)

    try:
        core = create_core_instance()
    except Exception as exc:
        log.error("Gradio analyze_text: не удалось создать ядро: %s", exc)
        return _empty_payload(f"❌ Ядро не загружено: {exc}")

    try:
        semantic_hints: Dict[str, Any] = {}
        voice_hint_keywords = [
            "вокал",
            "voice",
            "growl",
            "scream",
            "raspy",
            "мужск",
            "женск",
            "пескляв",
            "soft",
            "airy",
            "shout",
            "grit",
            "фальцет",
            "whisper",
        ]

        last_line = text.strip().splitlines()[-1].strip().lower()
        if (last_line.startswith("(") and last_line.endswith(")")) or last_line.startswith("под "):
            if any(k in last_line for k in voice_hint_keywords):
                semantic_hints["voice_profile_hint"] = last_line
                log.info(f"🎙️ [UI] Обнаружено описание вокала: {semantic_hints['voice_profile_hint']}")

        log.debug("Gradio -> core.analyze...")
        result = core.analyze(text, preferred_gender=gender, semantic_hints=semantic_hints or None)

        if isinstance(result, dict) and "error" in result:
            log.error(f"Gradio: Ядро вернуло ошибку: {result['error']}")
            return _empty_payload(f"❌ Ошибка: {result['error']}")

        if not isinstance(result, dict):
            log.warning("Gradio: unexpected result type, coercing to empty dict")
            result = {}

        legacy = result.get("legacy", {}) if isinstance(result.get("legacy"), dict) else {}
        fanf_block = result.get("fanf", {}) if isinstance(result.get("fanf"), dict) else {}
        style = result.get("style", {}) if isinstance(result.get("style"), dict) else {}
        bpm = result.get("bpm", {}) if isinstance(result.get("bpm"), dict) else {}
        tonality = result.get("tonality", {}) if isinstance(result.get("tonality"), dict) else {}
        tlp = result.get("tlp", {}) if isinstance(result.get("tlp"), dict) else {}
        zero = result.get("zero_pulse", {}) if isinstance(result.get("zero_pulse"), dict) else {}
        color_wave = result.get("color", {}).get("wave") if isinstance(result.get("color"), dict) else None
        rde = result.get("rde_summary", {}) if isinstance(result.get("rde_summary"), dict) else {}

        def _coalesce(*values: Any, fallback: str = "—") -> str:
            for val in values:
                if val is None:
                    continue
                if isinstance(val, (int, float)):
                    return str(val)
                if isinstance(val, str) and val.strip():
                    return val
                if val:
                    return str(val)
            return fallback

        style_prompt_value = _coalesce(
            result.get("style_prompt"),
            legacy.get("prompt_suno_style") if isinstance(legacy, dict) else None,
            fanf_block.get("cinematic_header"),
            fallback="Ошибка: style_prompt отсутствует",
        )

        annotated_text_suno_value = _coalesce(
            fanf_block.get("annotated_text_suno"),
            legacy.get("annotated_text_suno") if isinstance(legacy, dict) else None,
            "",
            fallback="Ошибка: annotated_text_suno отсутствует",
        )

        annotated_text_ui_value = _coalesce(
            fanf_block.get("annotated_text_ui"),
            legacy.get("annotated_text_ui") if isinstance(legacy, dict) else None,
            result.get("annotations", {}).get("vocal") if isinstance(result.get("annotations"), dict) else None,
            fallback="Ошибка: annotated_text_ui отсутствует",
        )

        annotated_text_fanf_value = _coalesce(
            fanf_block.get("annotated_text_fanf"),
            result.get("annotations", {}).get("vocal") if isinstance(result.get("annotations"), dict) else None,
            fallback="Ошибка: FANF аннотация отсутствует",
        )

        summary_payload = {
            "genre": _coalesce(style.get("genre"), style.get("domain_genre")),
            "style": _coalesce(style.get("tone"), style.get("mood")),
            "bpm": _coalesce(bpm.get("estimate"), bpm.get("emotion_map", {}).get("target_bpm") if isinstance(bpm.get("emotion_map"), dict) else None),
            "key": _coalesce(style.get("key"), _coalesce(*tonality.get("section_keys", []), fallback="auto")),
            "tlp": tlp or {},
            "rde": rde,
            "zero_pulse_count": len(zero.get("analysis", [])) if isinstance(zero.get("analysis"), list) else 0,
            "color_wave": color_wave or "adaptive",
            "choir": bool(fanf_block.get("choir_active", False)),
            "mode_shifts": tonality.get("modal_shifts", []),
            "resonance_layers": tonality.get("key_curve", []),
        }

        summary_box_value = json.dumps(summary_payload, ensure_ascii=False, indent=2)

        return {
            prompt_suno_style: gr.update(value=style_prompt_value),
            annotated_text_suno: gr.update(value=annotated_text_suno_value),
            annotated_text_ui: gr.update(value=annotated_text_ui_value),
            annotated_text_fanf: gr.update(value=annotated_text_fanf_value),
            summary_box: gr.update(value=summary_box_value),
        }

    except Exception as e:
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в analyze_text (Gradio): {traceback.format_exc()}")
        return _empty_payload(f"❌ Внутреннее исключение: {e}\n\n{traceback.format_exc()}")

# === 9. INLINE TEST RUNNER ===
def run_inline_tests():
    """Выполняет тесты и возвращает stdout прямо в интерфейс."""
    log.info("=" * 30)
    log.info("🚀 ЗАПУСК ВСТРОЕННЫХ ТЕСТОВ...")
    log.info("=" * 30)
    
    buffer = io.StringIO()
    buffer.write(f"🧩 StudioCore {STUDIOCORE_VERSION} — Inline Test Session\n")
    buffer.write(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    tests_path = os.path.join(ROOT, "tests")
    pytest_missing = False

    try:
        import pytest  # type: ignore
    except Exception:
        pytest_missing = True

    if pytest_missing:
        message = (
            "⚠️ Pytest не установлен. Установите pytest для запуска тестов "
            "(pip install pytest) либо запустите их вручную."
        )
        log.warning(message)
        buffer.write(message + "\n")
        return buffer.getvalue()

    if not os.path.isdir(tests_path):
        log.warning(f"Каталог тестов не найден: {tests_path}")
        buffer.write("ℹ️ Каталог tests/ отсутствует, тесты не запускались.\n")
        return buffer.getvalue()

    try:
        log.info(f"🚀 Running pytest in {tests_path}")
        buffer.write(f"🚀 Running pytest in {tests_path}\n\n")

        process = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", tests_path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=300,
        )

        if process.stdout:
            buffer.write(process.stdout)

        if process.stderr:
            buffer.write("\n--- STDERR ---\n")
            buffer.write(process.stderr)

    except subprocess.TimeoutExpired:
        log.error("Test runner: ТЕСТЫ ПРЕВЫСИЛИ ТАЙМАУТ (300с)!")
        buffer.write(
            "\n❌ КРИТИЧЕСКАЯ ОШИБКА: Тесты заняли слишком много времени (Timeout 300s).\n"
        )
    except Exception as e:
        log.error(f"Test runner: КРИТИЧЕСКАЯ ОШИБКА: {e}")
        buffer.write(f"❌ ОШИБКА ПРИ ЗАПУСКЕ ТЕСТОВ: {e}\n{traceback.format_exc()}\n")

    log.info("🏁 ...Встроенные тесты завершены.")
    buffer.write("\n✅ Inline test session complete.\n")
    return buffer.getvalue()


# === 10. PUBLIC UI (Gradio) ===
log.debug("Инициализация Gradio UI...")
with gr.Blocks(
    title=f"🎧 StudioCore v6.4 MAXI — Public Interface by @Sbauermaner"
) as iface_public:
    gr.Markdown(
        f"## 🎧 StudioCore {STUDIOCORE_VERSION} — Public Interface by @Sbauermaner\n"
        "Адаптивный движок с тестами и логами.\n"
    )

    with gr.Tab("🎙️ Анализ текста"):
        with gr.Row():
            text_input = gr.Textbox(
                label="Введите текст песни",
                lines=12,
                placeholder="Вставьте лирику здесь…\n\n(Подсказка: чтобы задать вокал, напишите в ПОСЛЕДНЕЙ строке, например: (под хриплый мужской вокал) или (soft female whisper))"
            )
            gender_input = gr.Radio(["auto", "male", "female"], value="auto", label="Принудительный Пол (UI)")

        analyze_button = gr.Button("🔍 Анализировать")

        prompt_suno_style = gr.Code(
            label="[STYLE PROMPT - КОПИРОВАТЬ В SUNO 'Style of Music']",
            language="markdown",
            interactive=False,
            show_copy_button=True,
        )

        annotated_text_suno = gr.Code(
            label="[LYRICS PROMPT - КОПИРОВАТЬ В SUNO 'Lyrics']",
            language="markdown",
            interactive=False,
            show_copy_button=True,
        )

        annotated_text_ui = gr.Code(
            label="Аннотированный текст (UI)",
            language="markdown",
            interactive=False,
            show_copy_button=True,
        )

        with gr.Accordion("🎞 FANF Cinematic Annotation", open=False):
            annotated_text_fanf = gr.Code(
                label="FANF Cinematic", language="markdown", interactive=False, show_copy_button=True
            )

        with gr.Accordion("Показать расширенный анализ (Summary и Аннотация)", open=False):
            summary_box = gr.Code(label="📊 Результат (Summary)", language="json", interactive=False)

        analyze_button.click(
            fn=analyze_text,
            inputs=[text_input, gender_input],
            outputs=[prompt_suno_style, annotated_text_suno, annotated_text_ui, annotated_text_fanf, summary_box],
        )

        # === JSON DEBUG SECTION ===
        with gr.Row():
            debug_input = gr.Textbox(
                label="Текст для JSON-диагностики",
                placeholder="Вставь сюда любой текст, команды, BPM, теги...",
            )
            debug_button = gr.Button("Показать JSON")
            debug_output = gr.JSON(label="Полный JSON от StudioCore")

        def on_debug_json(text):
            import requests

            try:
                r = requests.post("http://localhost:7860/debug_json", json={"text": text})
                return r.json()
            except Exception as e:  # pragma: no cover - UI helper
                return {"error": str(e)}

        debug_button.click(on_debug_json, inputs=debug_input, outputs=debug_output)

    with gr.Tab("🧩 Логи и тесты"):
        gr.Markdown("### Автоматическая проверка ядра StudioCore")
        run_btn = gr.Button("🚀 Запустить тесты")
        output_box = gr.Textbox(
            label="Результаты тестов (stdout/stderr)", 
            lines=30, 
            show_copy_button=True
        )
        run_btn.click(fn=run_inline_tests, inputs=None, outputs=output_box)

# === 11. MOUNT ===
log.debug("Монтирование Gradio App в FastAPI (path='/')...")
iface_public.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")

# === 12. RUN ===
if __name__ == "__main__":
    log.info(
        f"🚀 Запуск StudioCore v6.4 MAXI by @Sbauermaner (API + Gradio)..."
    )
    uvicorn.run(app, host="0.0.0.0", port=7860)