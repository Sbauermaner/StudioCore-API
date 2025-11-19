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
    """Проверка того, что ядро можно создать и запустить минимальный анализ."""

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
        global CORE_RELOAD_REQUIRED
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
    """
    Основная функция анализа текста через StudioCore для UI Gradio.
    v8: Возвращает 3 строки: Summary, Suno Prompt, Annotated Text
    """
    log.debug(f"Gradio analyze_text: получено {len(text)} символов, gender={gender}")

    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", ""

    is_valid, validation_error = _validate_input_length(text)
    if not is_valid:
        return validation_error, "", ""

    try:
        core = create_core_instance()
    except Exception as exc:
        log.error("Gradio analyze_text: не удалось создать ядро: %s", exc)
        return f"❌ Ядро не загружено: {exc}", "", ""

    try:
        # --- Проверка пользовательских описаний вокала ---
        semantic_hints = {}
        voice_hint_keywords = [
            "вокал", "voice", "growl", "scream", "raspy", "мужск", "женск",
            "пескляв", "soft", "airy", "shout", "grit", "фальцет", "whisper"
        ]
        
        # v8: Улучшенная логика: ищем хинт только в ПОСЛЕДНЕЙ строке, 
        # если она в скобках или начинается с "под"
        last_line = text.strip().splitlines()[-1].strip().lower()
        if (last_line.startswith("(") and last_line.endswith(")")) or \
           last_line.startswith("под "):
            if any(k in last_line for k in voice_hint_keywords):
                semantic_hints["voice_profile_hint"] = last_line
                log.info(f"🎙️ [UI] Обнаружено описание вокала: {semantic_hints['voice_profile_hint']}")
        
        log.debug("Gradio -> core.analyze...")
        result = core.analyze(text, preferred_gender=gender, semantic_hints=semantic_hints or None)

        if isinstance(result, dict) and "error" in result:
            log.error(f"Gradio: Ядро вернуло ошибку: {result['error']}")
            return f"❌ Ошибка: {result['error']}", "", ""

        # --- 1. Summary ---
        style = result.get("style", {})
        vocal_form = style.get("vocal_form", "auto")
        
        summary = (
            f"✅ StudioCore {STUDIOCORE_VERSION}\n"
            f"🎭 {style.get('genre', '—')} | "
            f"🎵 {style.get('style', '—')} | "
            f"🎙 {vocal_form} ({result.get('final_gender_preference', 'auto')}) | "
            f"⏱ {result.get('bpm', '—')} BPM | "
            f"🔑 {style.get('key', 'auto')}"
        )

        # --- 2. Suno Prompt (v8) ---
        # (Объединяет Style и Lyrics)
        suno_prompt = (
            f"[STYLE PROMPT - КОПИРОВАТЬ В SUNO 'Style of Music']\n"
            f"{result.get('prompt_suno_style', 'Ошибка: prompt_suno_style не найден')}\n\n"
            f"[LYRICS PROMPT - КОПИРОВАТЬ В SUNO 'Lyrics']\n"
            f"{result.get('annotated_text_suno', 'Ошибка: annotated_text_suno не найден')}"
        )
        
        # --- 3. Аннотированный текст (для UI) ---
        annotated_text_ui = result.get("annotated_text_ui", "Ошибка: annotated_text_ui не найден")

        return (
            summary,
            suno_prompt,
            annotated_text_ui,
        )

    except Exception as e:
        log.critical(f"❌ КРИТИЧЕСКАЯ ОШИБКА в analyze_text (Gradio): {traceback.format_exc()}")
        # v10: Возвращаем traceback в UI для легкой отладки
        return f"❌ Внутреннее исключение: {e}\n\n{traceback.format_exc()}", "", ""

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

        # --- v8: Единый блок Suno Prompt ---
        suno_box = gr.Textbox(
            label="[StudioCore] Suno Prompt (Style + Lyrics)", 
            lines=16, 
            show_copy_button=True,
            info="Скопируйте [STYLE PROMPT] в 'Style of Music' и [LYRICS PROMPT] в 'Lyrics' в Suno."
        )

        with gr.Accordion("Показать расширенный анализ (Summary и Аннотация)", open=False):
            # v8: Кнопки копирования возвращены
            result_box = gr.Textbox(label="📊 Результат (Summary)", lines=6, show_copy_button=True)
            annotated_box = gr.Textbox(label="🎙️ Аннотированный текст (UI)", lines=24, show_copy_button=True)

        analyze_button.click(
            fn=analyze_text,
            inputs=[text_input, gender_input],
            outputs=[result_box, suno_box, annotated_box],
        )

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