# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

# === OpenAI client ===
# Requires env var: OPENAI_API_KEY
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
except Exception as e:  # library not installed yet, or no key
    _client = None

app = FastAPI(title="Jarvis Voice Assistant")

# Serve /static and index.html
STATIC_DIR = "app/static"
INDEX_FILE = f"{STATIC_DIR}/index.html"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    # Serves the voice UI
    return FileResponse(INDEX_FILE)


class ChatRequest(BaseModel):
    client_id: str
    message: str
    history: Optional[List[Dict[str, Any]]] = None  # optional: client can send its own memory


# very small, in-memory cache (ephemeral; resets on restart)
MEMORY: Dict[str, List[Dict[str, str]]] = {}


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Accepts text, keeps short-term memory, returns assistant reply.
    """
    if _client is None or not os.getenv("OPENAI_API_KEY"):
        return JSONResponse(
            {"error": "Server missing OPENAI_API_KEY or openai package."},
            status_code=500,
        )

    # Retrieve/merge memory
    hist = MEMORY.get(req.client_id, [])
    if req.history:
        hist = req.history  # allow client to drive memory if it wants

    # Clamp memory size (keep it lean for a free Render service)
    hist = hist[-18:]  # keep last 18; we’ll add 2 more messages below

    system_prompt = os.getenv(
        "SYSTEM_PROMPT",
        "You are Jarvis, a proactive, mobile-first voice assistant. "
        "Keep answers brief and helpful. If asked to perform actions you can’t do, "
        "explain simple next steps. Use plain language.",
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    messages = [{"role": "system", "content": system_prompt}] + hist + [
        {"role": "user", "content": req.message}
    ]

    try:
        completion = _client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # Update memory and return
    hist.append({"role": "user", "content": req.message})
    hist.append({"role": "assistant", "content": reply})
    MEMORY[req.client_id] = hist[-20:]  # keep last 20 turns

    return {"reply": reply, "memory_len": len(MEMORY[req.client_id])}
