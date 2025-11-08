from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from StudioCore_Complete_v4 import StudioCore, load_config
from pilgrim_layer import PilgrimInterface
import json

app = FastAPI(title="StudioCore Pilgrim API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация ядра
config = load_config()
core = StudioCore(config)
pilgrim = PilgrimInterface(core)

# ------------------------------------------------------------
# 🧠 Основные маршруты API
# ------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "StudioCore Pilgrim running", "version": "1.0", "endpoints": ["/analyze", "/build", "/ui"]}


@app.post("/analyze")
async def analyze(request: Request, prefer_gender: str = "auto"):
    """
    Анализ лирики → возвращает JSON со всеми параметрами (жанр, bpm, эмоции, тональность, инструменты и т.д.)
    """
    raw_text = await request.body()
    text = raw_text.decode("utf-8", errors="ignore").strip()
    if not text:
        return Response(content=json.dumps({"error": "Пустой текст"}), media_type="application/json")
    result = core.analyze(text, prefer_gender=prefer_gender)
    return Response(content=json.dumps(result.__dict__, ensure_ascii=False, indent=2), media_type="application/json")


@app.post("/build")
async def build(request: Request, prefer_gender: str = "auto"):
    """
    Строит текст с разметкой + выдает готовый style prompt
    """
    raw_text = await request.body()
    text = raw_text.decode("utf-8", errors="ignore").strip()
    if not text:
        return Response(content="⚠️ Пустой текст.", media_type="text/plain; charset=utf-8")
    built_text = pilgrim.build_from_text(text, prefer_gender=prefer_gender)
    return Response(content=built_text, media_type="text/plain; charset=utf-8")


# ------------------------------------------------------------
# 🌐 Встроенный минималистичный UI (/ui)
# ------------------------------------------------------------

@app.get("/ui", summary="Web UI для проверки StudioCore Pilgrim")
def ui():
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>StudioCore Pilgrim UI</title>
<style>
body { font-family: system-ui, sans-serif; background: #0b0b15; color: #e6e6e6; text-align:center; margin: 30px;}
textarea { width: 90%; height: 280px; background: #111; color: #0f0; font-family: monospace; border: 1px solid #444; border-radius: 6px; padding: 10px;}
button { margin: 10px; padding: 8px 18px; background: #444; color: #fff; border: none; border-radius: 6px; cursor:pointer;}
button:hover { background:#666; }
pre { background: #111; text-align:left; color:#0ff; padding: 12px; border-radius:8px; overflow:auto; white-space:pre-wrap; width:90%; margin:auto;}
input, select { padding:4px; border-radius:4px; border:1px solid #333; background:#222; color:#ccc;}
</style>
</head>
<body>
<h2>🎛 StudioCore Pilgrim — тестовая форма</h2>
<p>Вставь сюда свою лирику (русский / английский / смешанный текст)</p>
<textarea id="lyrics" placeholder="Вставь текст лирики..."></textarea><br>
<label>prefer_gender:</label>
<select id="gender">
  <option value="auto">auto</option>
  <option value="male">male</option>
  <option value="female">female</option>
  <option value="duet">duet</option>
  <option value="choir">choir</option>
</select>
<button onclick="analyze()">🧠 Analyze (JSON)</button>
<button onclick="build()">🪶 Build (text)</button>
<pre id="out"></pre>
<script>
async function analyze() {
  const text = document.getElementById("lyrics").value;
  const gender = document.getElementById("gender").value;
  const r = await fetch(`/analyze?prefer_gender=${gender}`, {
    method: 'POST',
    headers: {'Content-Type': 'text/plain'},
    body: text
  });
  document.getElementById("out").textContent = await r.text();
}
async function build() {
  const text = document.getElementById("lyrics").value;
  const gender = document.getElementById("gender").value;
  const r = await fetch(`/build?prefer_gender=${gender}`, {
    method: 'POST',
    headers: {'Content-Type': 'text/plain'},
    body: text
  });
  document.getElementById("out").textContent = await r.text();
}
</script>
</body>
</html>
"""
    return Response(content=html, media_type="text/html; charset=utf-8")

