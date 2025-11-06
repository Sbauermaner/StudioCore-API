from fastapi import FastAPI, Request, Body, Form
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
from pilgrim_layer import PilgrimInterface

app = FastAPI(title="StudioCore API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
pilgrim = PilgrimInterface()

class AnalyzeIn(BaseModel):
    lyrics: str
    prefer_gender: Optional[str] = "auto"
    author_style: Optional[str] = None
    genre_hint: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!doctype html>
<html><head><meta charset="utf-8"><title>StudioCore — Pilgrim</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial;max-width:900px;margin:40px auto;padding:0 16px}
textarea{width:100%;min-height:240px;padding:12px;font-size:16px}
button{padding:10px 16px;font-size:16px;cursor:pointer}
pre{white-space:pre-wrap;background:#0b0b0b;color:#eaeaea;padding:16px;border-radius:8px}
label{display:inline-block;margin:8px 8px 8px 0}
select,input{padding:6px 8px;margin-left:6px}
.small{opacity:.7}
</style></head>
<body>
<h1>StudioCore Pilgrim — Лирика → Скелет + Style Prompt</h1>
<p class="small">Вставь свою лирику в любое формате (со знаками/без) и нажми «Анализировать». Ответ вернётся как чистый текст.</p>

<label>Предпочт. вокал:
<select id="gender">
  <option value="auto" selected>auto</option>
  <option value="male">male</option>
  <option value="female">female</option>
  <option value="duet">duet</option>
  <option value="choir">choir</option>
</select></label>

<label>Подсказка жанра:
<select id="genre">
  <option value="">auto</option>
  <option>rock</option><option>metal</option><option>pop</option>
  <option>folk</option><option>ambient</option><option>classical</option>
  <option>electronic</option><option>orchestral</option>
</select></label>

<textarea id="lyrics" placeholder="Вставь лирику здесь..."></textarea>
<button id="go">Анализировать</button>

<h3>Результат</h3>
<pre id="out">(пусто)</pre>

<script>
const go = document.getElementById('go');
go.onclick = async () => {
  const lyrics = document.getElementById('lyrics').value || "";
  const prefer_gender = document.getElementById('gender').value || "auto";
  const genre_hint = document.getElementById('genre').value || "";
  const resp = await fetch('/analyze_raw?prefer_gender='+encodeURIComponent(prefer_gender)+'&genre_hint='+encodeURIComponent(genre_hint), {
    method: 'POST',
    headers: {'Content-Type':'text/plain;charset=utf-8'},
    body: lyrics
  });
  const text = await resp.text();
  document.getElementById('out').textContent = text || "(пусто)";
};
</script>
</body></html>
    """

@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status":"ok","app":"StudioCore Pilgrim"}

@app.post("/analyze", response_class=JSONResponse)
async def analyze(payload: AnalyzeIn):
    data = pilgrim.analyze_to_objects(
        lyrics=payload.lyrics,
        prefer_gender=payload.prefer_gender or "auto",
        author_style=payload.author_style,
        genre_hint=payload.genre_hint
    )
    return data

@app.post("/analyze_raw", response_class=PlainTextResponse)
async def analyze_raw(request: Request, prefer_gender: Optional[str] = "auto", genre_hint: Optional[str] = None):
    # принимает text/plain ИЛИ форму с полем lyrics
    content_type = request.headers.get("content-type","").lower()
    lyrics = ""
    if "text/plain" in content_type:
        body = await request.body()
        lyrics = body.decode("utf-8", errors="ignore")
    elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        lyrics = form.get("lyrics","")
    else:
        # пробуем как есть
        body = await request.body()
        lyrics = body.decode("utf-8", errors="ignore")

    lyrics = lyrics or ""
    text = pilgrim.analyze_to_text(
        lyrics=lyrics,
        prefer_gender=prefer_gender or "auto",
        author_style=None,
        genre_hint=(genre_hint or None) if genre_hint else None
    )
    return text
