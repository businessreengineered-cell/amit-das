from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import openai
import os

app = FastAPI()

# Mount static folder (for index.html)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Root → serve index.html
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")

    try:
        client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are Jarvis, a helpful futuristic AI assistant."},
                      {"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        reply = f"Error: {str(e)}"

    return JSONResponse({"reply": reply})
