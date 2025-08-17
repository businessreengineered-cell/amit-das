# app/main.py
from pathlib import Path
from typing import List, Literal, Optional
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---- OpenAI (server-side fallback for text or speech-to-text if you ever add it)
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="Jarvis Voice Assistant")

# CORS so you can open from your phone freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API models
Role = Literal["system", "user", "assistant"]

class ChatMessage(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o-mini"        # small/fast by default
    temperature: Optional[float] = 0.5

class ChatResponse(BaseModel):
    role: Role = "assistant"
    content: str

# ---------- Health & root
@app.get("/")
def root():
    return {"message": "Hello, Jarvis is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------- Core chat endpoint (server-side LLM)
@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest):
    """
    Mobile client posts the running conversation (messages).
    We return the assistant reply text.
    """
    if not client:
        # No server key? Return a friendly message so UI can still talk using client-side speech.
        return ChatResponse(content="Server is up, but no OPENAI_API_KEY is set. Add it to Render to enable AI replies.")

    # Ensure a system prompt so it feels like a “next-gen” assistant
    system_msg = {
        "role": "system",
        "content": (
            "You are Jarvis, a friendly, proactive mobile voice assistant. "
            "Be concise, helpful, and anticipate the user's next step. "
            "If asked to remember facts, reflect them back explicitly."
        ),
    }
    messages = [system_msg] + [m.model_dump() for m in req.messages]

    chat = client.chat.completions.create(
        model=req.model or "gpt-4o-mini",
        messages=messages,
        temperature=req.temperature or 0.5,
    )
    text = chat.choices[0].message.content.strip()
    return ChatResponse(content=text)

# ---------- Static/PWA (serve the web app)
ROOT = Path(__file__).resolve().parent.parent  # repo root
WEB_DIR = ROOT / "web"

# Make sure the web folder exists in the image (it will after you add the files below)
if WEB_DIR.exists():
    app.mount("/",
              StaticFiles(directory=str(WEB_DIR), html=True),
              name="web")
