# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5 — Expressive Adaptive Engine
Truth × Love × Pain = Conscious Frequency
"""

import os
import gradio as gr
import traceback
import importlib, subprocess, sys, threading, json, time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from studiocore import StudioCore, STUDIOCORE_VERSION

# === 🔄 Автоматическая синхронизация OpenAPI ===
try:
    if os.path.exists("auto_sync_openapi.py"):
        print("🔄 Синхронизирую OpenAPI (JSON → YAML)...")
        subprocess.call([sys.executable, "auto_sync_openapi.py"])
    else:
        print("ℹ️ auto_sync_openapi.py не найден, пропускаю синхронизацию.")
except Exception as e:
    print("⚠️ Ошибка при автосинхронизации OpenAPI:", e)

# === Проверка и установка requests (для self-check) ===
if importlib.util.find_spec("requests") is None:
    try:
        print("⚙️ Устанавливаю 'requests' для self-check...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    except Exception:
        pass

try:
    import requests  # type: ignore
except Exception:
    requests = None

# === Инициализация ядра ===
core = StudioCore()
app = FastAPI(title="StudioCore API")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SELF-CHECK ===
def auto_core_check():
    if os.environ.get("DISABLE_SELF_CHECK") == "1":
        print("🧪 Self-check отключён (DISABLE_SELF_CHECK=1).")
        return
    if requests is None:
        print("ℹ️ requests недоступен — пропускаю HTTP self-check. Используй /compat-check.")
        return

    time.sleep(5)
    api_url = "http://0.0.0.0:7860/api/predict"
    test_text = "Вся моя жизнь — как быль или небыль, Вся моя жизнь — по краю скользить..."
    print("\n🧠 [StudioCore Self-Check] Запуск теста совместимости...\n")
    try:
        r = requests.post(api_url, json={"text": test_text}, timeout=25)
        if r.status_code != 200:
            print(f"❌ [Self-Check] API вернул {r.status_code}")
            return
        data = r.json()
        summary = data.get("summary", "")
        annotated = data.get("annotated_text", "")
        tlp_ok = any(tag in summary for tag in ["Truth", "Love", "Pain"])
        tonesync_ok = "ToneSync" in data.get("prompt_suno", "")
        ann_ok = "[" in annotated
        status = (
            "✅ StudioCore v5 совместимо и активно."
            if all([tlp_ok, tonesync_ok, ann_ok])
            else "⚠️ Обнаружено несовпадение с монолитом."
        )
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "engine_version": STUDIOCORE_VERSION,
            "status": status,
            "summary_preview": summary[:300],
            "annotated_preview": "\n".join(annotated.splitlines()[:6]),
        }
        print(status)
        with open("startup_selfcheck_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("❌ [Self-Check] Ошибка:", e)

threading.Thread(target=auto_core_check, daemon=True).start()

# === Основной анализ ===
def analyze_text(text: str):
    if not text.strip():
        return "⚠️ Введите текст для анализа.", "", "", ""
    try:
        result = core.analyze(text)
        if "error" in result:
            return f"❌ Ошибка: {result['error']}", "", "", ""

        summary = (
            f"✅ Анализ завершён успешно.\n"
            f"Жанр: {result['style'].get('genre', '—')}\n"
            f"Стиль: {result['style'].get('style', '—')}\n"
            f"Вокальная форма: {result['style'].get('vocal_form', '—')}\n"
            f"Темп: {result.get('bpm', '—')} BPM\n"
            f"Философия: {result.get('philosophy', '—')}\n"
            f"Версия ядра: {result.get('version', '—')}"
        )

        annotated_text = result.get("annotated_text") or core.annotate_text(
            text,
            result.get("overlay", {}),
            result.get("style", {}),
            result.get("vocals", []),
            result.get("bpm") or core.rhythm.bpm_from_density(text) or 120,
            result.get("emotions", {}),
            result.get("tlp", {}),
        )

        tlp = result.get("tlp", {})
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        annotated_lines = []

        def tone(idx, total):
            if idx < total * 0.25:
                return "(soft whisper)", "fragile"
            elif idx < total * 0.6:
                return "(warm mid-voice)", "balanced"
            elif love > pain and cf > 0.6:
                return "(gentle falsetto)", "open"
            else:
                return "(strong release)", "bright"

        for i, line in enumerate(lines):
            desc, tag = tone(i, len(lines))
            if i == 0:
                header = f"[Verse 1 – {desc}]"
            elif i == len(lines) - 1:
                header = f"[Outro – {desc}]"
            elif "люб" in line.lower() or "you" in line.lower():
                header = f"[Chorus – {desc}]"
            else:
                header = f"[Verse – {desc}]"
            annotated_lines += [
                header,
                line,
                f"(tone: {tag}, Truth={truth:.2f}, Love={love:.2f}, Pain={pain:.2f}, CF={cf:.2f})",
                "",
            ]

        annotated_text = (
            "🎙️ **Core Annotation + Vocal Layer**\n\n"
            + annotated_text + "\n\n" + "\n".join(annotated_lines)
        )
        return (
            summary,
            result.get("prompt_full", "⚠️ Нет данных"),
            result.get("prompt_suno", "⚠️ Нет данных"),
            annotated_text,
        )
    except Exception as e:
        print("❌ Ошибка при анализе:\n", traceback.format_exc())
        return f"❌ Исключение: {str(e)}", "", "", ""

# === PUBLIC UI ===
with gr.Blocks(title="🎧 StudioCore v5 — Public Interface") as iface_public:
    gr.Markdown("### StudioCore (Public)\nПубличная версия без кнопки Flag и логов.")
    gr.Interface(
        fn=analyze_text,
        inputs=gr.Textbox(label="Введите текст песни", lines=10),
        outputs=[
            gr.Textbox(label="📊 Результат анализа", lines=6),
            gr.Textbox(label="🎼 Полный промт", lines=8),
            gr.Textbox(label="🎧 Suno-промт", lines=8),
            gr.Textbox(label="🎙️ Аннотация (Vocal Layer)", lines=20),
        ],
        flagging_mode="never",
        title=None,
        description=None,
    )

# === ADMIN UI ===
def password_gate(password):
    if password == "Timofej151106":
        return gr.update(visible=False), gr.update(visible=True), ""
    return gr.update(visible=True), gr.update(visible=False), "❌ Неверный пароль"

with gr.Blocks(title="🎧 StudioCore Admin Access") as iface_admin:
    gr.Markdown("## 🔐 Вход в административную панель StudioCore")
    pwd = gr.Textbox(label="Пароль", type="password", placeholder="••••••••")
    err = gr.Markdown("")
    btn = gr.Button("Войти")
    admin_panel = gr.Group(visible=False)
    with admin_panel:
        gr.Markdown("### 🎛 Панель администратора")
        gr.Interface(
            fn=analyze_text,
            inputs=gr.Textbox(label="Введите текст", lines=10),
            outputs=[
                gr.Textbox(label="📊 Результат анализа", lines=6),
                gr.Textbox(label="🎼 Полный промт", lines=8),
                gr.Textbox(label="🎧 Suno-промт", lines=8),
                gr.Textbox(label="🎙️ Вокальная аннотация", lines=20),
            ],
            flagging_mode="manual",
            title=None,
            description="Админская версия с диагностикой.",
        )
    btn.click(password_gate, inputs=pwd, outputs=[pwd, admin_panel, err])

# === API ===
@app.get("/status")
async def status():
    return JSONResponse(
        content={"status": "ok", "engine": "StudioCore", "ready": True, "version": STUDIOCORE_VERSION}
    )

@app.get("/version")
async def version_info():
    return JSONResponse(
        content={
            "status": "ok",
            "engine": "StudioCore",
            "version": STUDIOCORE_VERSION,
            "signature": core.__class__.__name__,
        }
    )

@app.get("/compat/core")
async def compat_core():
    """Сравнивает openapi_main.yaml и openapi_studiocore.yaml"""
    try:
        from compat_check_core import run_check as run_core
        report = run_core()
        return JSONResponse(content=report)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/compat/remote")
async def compat_remote():
    """Проверяет удалённый API /api/predict"""
    try:
        from compat_check_remote import run_check as run_remote
        run_remote()
        if os.path.exists("remote_compatibility_full_report.json"):
            with open("remote_compatibility_full_report.json", "r", encoding="utf-8") as f:
                return JSONResponse(content=json.load(f))
        return JSONResponse(content={"status": "no_report"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/compat-check")
async def compat_check():
    """Проверка совместимости ядра без HTTP-запроса"""
    text = (
        "Вся моя жизнь — как быль или небыль,\n"
        "Вся моя жизнь — по краю скользить.\n"
        "Но я молю открыть в сердце двери,\n"
        "Я так хочу твоей женщиной быть…"
    )
    try:
        res = core.analyze(text)
        ok = {
            "has_tlp": isinstance(res.get("tlp"), dict) and all(k in res["tlp"] for k in ("truth", "love", "pain")),
            "has_tonesync": isinstance(res.get("tonesync"), dict) and "primary_color" in res["tonesync"],
            "has_overlay": isinstance(res.get("overlay"), dict) and "sections" in res["overlay"],
            "has_prompts": bool(res.get("prompt_full")) and bool(res.get("prompt_suno")),
            "has_annotation": bool(res.get("annotated_text")),
        }
        status = "ok" if all(ok.values()) else "partial"
        return JSONResponse(
            content={
                "status": status,
                "engine_version": STUDIOCORE_VERSION,
                "checks": ok,
                "bpm": res.get("bpm"),
                "style_key": res.get("style", {}).get("key"),
                "vocal_form": res.get("style", {}).get("vocal_form"),
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

@app.post("/api/predict")
async def predict_api(request: Request):
    try:
        payload = await request.json()
        text = payload.get("text", "")
        summary, full, suno, annotated = analyze_text(text)
        return JSONResponse(
            content={
                "summary": summary,
                "prompt_full": full,
                "prompt_suno": suno,
                "annotated_text": annotated,
                "engine_version": STUDIOCORE_VERSION,
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# === MOUNT ===
iface_public.queue()
iface_admin.queue()
app = gr.mount_gradio_app(app, iface_public, path="/")
app = gr.mount_gradio_app(app, iface_admin, path="/admin")

# === RUN ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
