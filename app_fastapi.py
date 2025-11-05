from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from studiocore_pilgrim import StudioCore, load_config

app = FastAPI(title="StudioCore Pilgrim API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

core = StudioCore(load_config())

class Section(BaseModel):
    tag: str = Field(..., examples=["Verse 1","Chorus","Bridge"])
    hint: Optional[str] = Field(None, examples=["Tagelharpa + throat singing"])

class AnalyzeRequest(BaseModel):
    lyrics: str
    prefer_gender: Optional[str] = "auto"
    modes: Optional[Dict[str,bool]] = None
    author_style: Optional[str] = None
    author_structure: Optional[List[Section]] = None

class AnalyzeResponse(BaseModel):
    genre:str; bpm:int; tonality:str
    vocals:List[str]; instruments:List[str]
    tlp:Dict[str,float]; emotions:Dict[str,float]
    resonance:Dict[str,Any]; integrity:Dict[str,Any]
    tonesync:Dict[str,Any]; prompt:str
    structured_lyrics:str

@app.get("/", tags=["health"])
def root():
    return {"status":"StudioCore Pilgrim running"}

@app.post("/analyze", response_model=AnalyzeResponse, tags=["core"])
def analyze(req: AnalyzeRequest):
    result = core.analyze(
        lyrics=req.lyrics,
        prefer_gender=req.prefer_gender or "auto",
        modes=req.modes or {},
        author_style=req.author_style,
        author_structure=[s.dict() for s in (req.author_structure or [])] or None
    )
    return AnalyzeResponse(
        genre=result.genre, bpm=result.bpm, tonality=result.tonality,
        vocals=result.vocals, instruments=result.instruments,
        tlp=result.tlp, emotions=result.emotions,
        resonance=result.resonance, integrity=result.integrity,
        tonesync=result.tonesync, prompt=result.prompt,
        structured_lyrics=result.structured_lyrics
    )

class BuildRequest(BaseModel):
    lyrics: str
    author_style: Optional[str] = None
    modes: Optional[Dict[str,bool]] = None
    prefer_gender: Optional[str] = "auto"

class BuildResponse(BaseModel):
    prompt: str
    genre: str
    bpm: int
    tonality: str

@app.post("/build", response_model=BuildResponse, tags=["core"])
def build(req: BuildRequest):
    r = core.analyze(
        lyrics=req.lyrics,
        prefer_gender=req.prefer_gender or "auto",
        modes=req.modes or {},
        author_style=req.author_style
    )
    return BuildResponse(prompt=r.prompt, genre=r.genre, bpm=r.bpm, tonality=r.tonality)