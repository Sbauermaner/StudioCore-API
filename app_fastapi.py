from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ---------- FastAPI ----------
app = FastAPI(title="StudioCore Pilgrim API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---------- I/O схемы ----------
class AuthorSection(BaseModel):
    tag: str
    hint: Optional[str] = ""

class BuildIn(BaseModel):
    lyrics: str = Field(..., description="Raw lyrics text")
    author_structure: Optional[List[AuthorSection]] = Field(default=None)
    author_style: Optional[str] = Field(default=None, description="Optional style words by author")
    mode: Optional[str] = Field(default="auto", description="auto | author | healing | dramatic | epic | minimal")

class AnalyzeIn(BaseModel):
    lyrics: str

class BuildOut(BaseModel):
    genre: str
    bpm: int
    tonality: str
    vocals: List[str]
    instruments: List[str]
    tlp: Dict[str, float]
    emotions: Dict[str, float]
    resonance: Dict[str, Any]
    integrity: Dict[str, Any]
    tonesync: Dict[str, Any]
    prompt: str
    structured_lyrics: str

# ---------- Импорт ядра ----------
# Ожидается, что файл StudioCore_Complete_v4.py лежит рядом
from StudioCore_Complete_v4 import StudioCore, PipelineResult

core = StudioCore()

# ---------- Вспомогательное: наложение авторской структуры ----------
def apply_author_structure(text: str, author_sections: Optional[List[AuthorSection]]) -> str:
    if not author_sections:
        return text
    # Простая сборка: берем текст по строкам и проставляем теги секций.
    lines = [l for l in text.splitlines()]
    out = []
    i = 0
    for sec in author_sections:
        tag = sec.tag.strip()
        hint = (sec.hint or "").strip()
        header = f"[{tag}]"
        if hint:
            header += f" ({hint})"
        out.append(header)
        # Выделяем до 4 строк на секцию, чтобы не «съедать» весь текст (можно усложнить при желании)
        chunk = lines[i:i+4] if i < len(lines) else []
        if not chunk:
            out.append("...")
        else:
            out.extend(chunk)
            i += len(chunk)
        out.append("")  # пустая строка между секциями
    # добросыпаем хвост, если остался
    if i < len(lines):
        out.append("[Extra]")
        out.extend(lines[i:])
    return "\n".join(out).strip()

# ---------- Эндпоинты ----------
@app.get("/", response_class=HTMLResponse)
def home(_: Request):
    # Встроенный Pilgrim UI
    return HTMLResponse(f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>StudioCore Pilgrim • v4</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0a0a0b;
    --panel: #121214;
    --ink: #e9e6d8;
    --muted: #a8a091;
    --gold: #d4af37;
    --accent: #7f6a2b;
    --ok: #36c98e;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    margin: 0; background: radial-gradient(1000px 600px at 20% -10%, #1a1a1e 0%, #0a0a0b 60%), var(--bg);
    color: var(--ink); font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 60px; }}
  .hdr {{
    display:flex; align-items:center; justify-content:space-between; margin-bottom: 18px;
  }}
  .brand {{ display:flex; gap:14px; align-items:center; }}
  .rune {{
    width:42px; height:42px; border-radius:12px;
    background: linear-gradient(145deg, #2a2312, #0e0b06);
    box-shadow: 0 0 0 1px #3b3318 inset, 0 1px 14px rgba(212,175,55,0.15);
    display:grid; place-items:center; color:var(--gold); font-weight:700; font-family: Cinzel, serif; letter-spacing:1px;
  }}
  h1 {{ font-family: Cinzel, serif; font-weight:700; font-size:22px; margin:0; letter-spacing:0.5px; }}
  .muted {{ color: var(--muted); font-size: 12px; }}
  .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:18px; }}
  .card {{
    background: linear-gradient(180deg, #121214, #0f0f11);
    border: 1px solid #1e1b12; border-radius:18px; padding:16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
  }}
  .card h2 {{ margin: 0 0 10px 0; font-size:14px; letter-spacing:0.4px; color:var(--gold); font-family: Cinzel, serif; }}
  textarea, select, input {{
    width:100%; background:#0b0b0d; color:var(--ink); border:1px solid #232017; border-radius:12px; padding:10px 12px; font: inherit;
  }}
  textarea {{ min-height: 180px; resize: vertical; }}
  .small {{ font-size:12px; color:var(--muted); margin-top:6px; }}
  .row {{ display:flex; gap:10px; }}
  .row > * {{ flex:1; }}
  button {{
    background: linear-gradient(180deg, #2c2411, #1a160a);
    color: var(--gold); border: 1px solid #3b3318; border-radius: 12px; padding: 10px 14px;
    font-weight: 600; cursor: pointer; letter-spacing: 0.4px;
  }}
  button:hover {{ filter: brightness(1.08); }}
  .out pre {{
    background:#0b0b0d; border:1px solid #232017; border-radius: 12px; padding: 12px; white-space: pre-wrap; word-wrap: break-word;
  }}
  .kv {{ display:grid; grid-template-columns: 120px 1fr; gap:6px; margin-bottom:10px; }}
  .pill {{ font-size: 11px; color:#0f1712; background: linear-gradient(180deg, #c8b06a, #b49533); padding: 2px 8px; border-radius: 999px; display:inline-block; }}
  .ok {{ color: var(--ok); font-weight: 600; }}
  .copy {{ margin-left: 8px; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <div class="brand">
        <div class="rune">ᚠ</div>
        <div>
          <h1>StudioCore Pilgrim</h1>
          <div class="muted">Truth • Love • Pain — Conscious Resonance Engine</div>
        </div>
      </div>
      <div class="pill">v4</div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Lyrics</h2>
        <textarea id="lyrics" placeholder="[Вставь лирику]"></textarea>
        <div class="small">Текст — это «атмосфера». На её основе ядро подбирает жанр, BPM, тональность и строит структуру.</div>
        <div class="row" style="margin-top:10px;">
          <div>
            <label class="small">Mode</label>
            <select id="mode">
              <option value="auto" selected>auto</option>
              <option value="author">author (строго по разметке автора)</option>
              <option value="healing">healing (умиротворяющий)</option>
              <option value="dramatic">dramatic</option>
              <option value="epic">epic</option>
              <option value="minimal">minimal</option>
            </select>
          </div>
          <div>
            <label class="small">Author style (optional)</label>
            <input id="authorStyle" placeholder="например: throat singing + war drums + choir" />
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Author structure</h2>
        <textarea id="authorStruct" placeholder="[Verse 1] | Throat singing + war drums
[Chorus]  | Choir + strings + cinematic percussion
[Verse 2] | Tagelharpa + low chant"></textarea>
        <div class="small">Каждая строка: <code>[TAG] | hint</code>. Если пусто — ядро само разметит.</div>
        <div style="margin-top:10px;">
          <button id="run">Build</button>
          <span id="status" class="small"></span>
        </div>
      </div>
    </div>

    <div class="grid" style="margin-top:18px;">
      <div class="card out">
        <h2>Structured lyrics</h2>
        <div class="row" style="margin-bottom:8px;">
          <button class="copy" onclick="copyText('outLyrics')">Copy</button>
        </div>
        <pre id="outLyrics">—</pre>
      </div>
      <div class="card out">
        <h2>Prompt</h2>
        <div class="row" style="margin-bottom:8px;">
          <button class="copy" onclick="copyText('outPrompt')">Copy</button>
        </div>
        <pre id="outPrompt">—</pre>
      </div>
    </div>

    <div class="grid" style="margin-top:18px;">
      <div class="card">
        <h2>Analysis</h2>
        <div id="anKVs" class="kv">
          <!-- заполняется скриптом -->
        </div>
      </div>
      <div class="card">
        <h2>Status</h2>
        <div class="small">API: <span id="apiStatus">checking…</span></div>
      </div>
    </div>
  </div>

<script>
async function checkStatus(){{
  try {{
    const r = await fetch('/status');
    const j = await r.json();
    document.getElementById('apiStatus').innerText = j.status ? 'OK' : 'unknown';
  }} catch(e) {{
    document.getElementById('apiStatus').innerText = 'unavailable';
  }}
}}
checkStatus();

function parseAuthorStruct(txt){{
  const lines = (txt || '').split(/\\n+/).map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const line of lines) {{
    // "[Tag] | hint"
    const m = line.match(/^\\s*\\[([^\\]]+)\\]\\s*(?:\\|\\s*(.+))?\\s*$/);
    if (m) {{
      out.push({{ tag: m[1], hint: m[2] || '' }});
    }}
  }}
  return out.length ? out : null;
}}

function setKV(targetId, kv) {{
  const root = document.getElementById(targetId);
  root.innerHTML = '';
  for (const [k,v] of Object.entries(kv)) {{
    const key = document.createElement('div');
    key.innerText = k;
    key.style.color = '#a8a091';
    const val = document.createElement('div');
    val.innerText = typeof v === 'object' ? JSON.stringify(v) : String(v);
    root.appendChild(key); root.appendChild(val);
  }}
}}

function copyText(id){{
  const el = document.getElementById(id);
  if (!el) return;
  const txt = el.innerText || el.textContent || '';
  navigator.clipboard.writeText(txt);
}}

document.getElementById('run').addEventListener('click', async () => {{
  const status = document.getElementById('status');
  status.innerText = 'building…';
  const lyrics = document.getElementById('lyrics').value;
  const mode = document.getElementById('mode').value;
  const authorStyle = document.getElementById('authorStyle').value;
  const authorStructTxt = document.getElementById('authorStruct').value;
  const author_structure = parseAuthorStruct(authorStructTxt);

  const body = {{
    lyrics,
    mode,
    author_style: authorStyle || null,
    author_structure
  }};

  try {{
    const r = await fetch('/build', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(body)
    }});
    if (!r.ok) {{
      const t = await r.text();
      status.innerText = 'error';
      alert('Build error\\n' + t);
      return;
    }}
    const j = await r.json();
    document.getElementById('outPrompt').innerText = j.prompt || '—';
    document.getElementById('outLyrics').innerText = j.structured_lyrics || '—';

    const kv = {{
      'Genre': j.genre,
      'BPM': j.bpm,
      'Tonality': j.tonality,
      'Vocals': (j.vocals || []).join(', '),
      'Instruments': (j.instruments || []).join(', ')
    }};
    setKV('anKVs', kv);
    status.innerHTML = '<span class="ok">done</span>';
  }} catch (e) {{
    status.innerText = 'error';
    alert('Network/JS error: ' + e.message);
  }}
});
</script>
</body>
</html>
    """)

@app.get("/status")
def status():
    return {"status": "StudioCore FastAPI running"}

@app.post("/analyze")
def analyze(inp: AnalyzeIn):
    res: PipelineResult = core.analyze(inp.lyrics)
    return {
        "genre": res.genre,
        "bpm": res.bpm,
        "tonality": res.tonality,
        "vocals": res.vocals,
        "instruments": res.instruments,
        "tlp": res.tlp,
        "emotions": res.emotions,
        "resonance": res.resonance,
        "integrity": res.integrity,
        "tonesync": res.tonesync,
        "prompt": res.prompt
    }

@app.post("/build", response_model=BuildOut)
def build(inp: BuildIn):
    res: PipelineResult = core.analyze(inp.lyrics)
    # режимы можно тонко влиять на prompt здесь при необходимости
    if inp.author_style:
        # подмешиваем стиль автора в prompt
        res.prompt = res.prompt.replace("Style:", f"Style: {inp.author_style}; base=")

    structured = apply_author_structure(inp.lyrics, inp.author_structure)
    return BuildOut(
        genre=res.genre, bpm=res.bpm, tonality=res.tonality,
        vocals=res.vocals, instruments=res.instruments, tlp=res.tlp,
        emotions=res.emotions, resonance=res.resonance, integrity=res.integrity,
        tonesync=res.tonesync, prompt=res.prompt, structured_lyrics=structured
    )