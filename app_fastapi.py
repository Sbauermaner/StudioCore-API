import uvicorn
from fastapi import FastAPI, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pilgrim_layer import PilgrimInterface

app = FastAPI(title="StudioCore Pilgrim API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
pilgrim = PilgrimInterface()

@app.get("/")
def root():
    return {"status":"StudioCore Pilgrim running","version":"1.0.0"}

# 1) Чистый текст -> JSON
@app.post("/analyze", summary="Paste raw lyrics in body (text/plain or JSON)")
async def analyze(request: Request,
                  prefer_gender: Optional[str] = None,
                  author_style: Optional[str] = None):
    ct = request.headers.get("content-type","").lower()
    if "application/json" in ct:
        data = await request.json()
        lyrics = data.get("lyrics","")
        prefer = data.get("prefer_gender", prefer_gender or "auto")
        astyle = data.get("author_style", author_style)
    else:
        # text/plain (или что-то ещё) — читаем как сырой текст
        lyrics = (await request.body()).decode("utf-8",errors="ignore")
        prefer = prefer_gender or "auto"
        astyle = author_style

    res = pilgrim.analyze_text(lyrics, prefer_gender=prefer, author_style=astyle)
    return {
        "genre": res.genre,
        "bpm": res.bpm,
        "tonality": res.tonality,
        "vocals": res.vocals,
        "instruments": res.instruments,
        "tlp": res.tlp,
        "emotions": res.emotions,
        "resonance": res.resonance,
        "mode": res.mode,
        "prompt": res.prompt,
        "skeleton": res.skeleton,
    }

# 2) Чистый текст -> Чистый текст (готовый результат)
@app.post("/build", summary="Paste raw lyrics in body (text/plain). Returns clean text with skeleton + prompt")
async def build(request: Request,
                prefer_gender: Optional[str] = None,
                author_style: Optional[str] = None):
    body = (await request.body()).decode("utf-8",errors="ignore")
    res = pilgrim.analyze_text(body, prefer_gender=prefer_gender or "auto", author_style=author_style)
    txt = pilgrim.format_text(res)
    return Response(content=txt, media_type="text/plain; charset=utf-8")

# Простейшая форма для ручной проверки в браузере
@app.get("/ui")
def ui():
    return Response(content="""
<!doctype html><meta charset="utf-8"/>
<h2>StudioCore Pilgrim — quick UI</h2>
<form onsubmit="send(); return false;">
  <textarea id="t" rows="12" cols="100" placeholder="Вставьте лирику..."></textarea><br/>
  <label>prefer_gender: </label><input id="g" value="auto"/>
  <button>Analyze (JSON)</button>
  <button type="button" onclick="build()">Build (text)</button>
</form>
<pre id="out"></pre>
<script>
async function send(){
  const t=document.getElementById('t').value, g=document.getElementById('g').value||'auto';
  const r=await fetch('/analyze?prefer_gender='+encodeURIComponent(g),{method:'POST',headers:{'Content-Type':'text/plain'},body:t});
  document.getElementById('out').textContent = await r.text();
}
async function build(){
  const t=document.getElementById('t').value, g=document.getElementById('g').value||'auto';
  const r=await fetch('/build?prefer_gender='+encodeURIComponent(g),{method:'POST',headers:{'Content-Type':'text/plain'},body:t});
  document.getElementById('out').textContent = await r.text();
}
</script>
""", media_type="text/html; charset=utf-8")

if __name__ == "__main__":
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=7860, reload=False)
