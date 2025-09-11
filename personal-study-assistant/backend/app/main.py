from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .ai_providers import OpenAIProvider, GeminiProvider
from dotenv import load_dotenv
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend on Codespaces (adjust origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://super-duper-trout-x5p4pqr4g7g7hpg7p-3000.app.github.dev"],  # your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
	prompt: str
	mode: str = "chat" # could be `summarize`, `flashcards`, `quiz`, etc.


# configure provider from env
PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
if PROVIDER == "openai":
	provider = OpenAIProvider()
elif PROVIDER in ("gemini", "google"):
	provider = GeminiProvider()
else:
	raise RuntimeError("Unsupported AI_PROVIDER: %s" % PROVIDER)
print(f"Using AI provider: {PROVIDER}")

@app.post("/api/chat")
async def chat(req: ChatRequest):
	try:
		print(f"Received request: {req}")
		resp = provider.generate(req.prompt, mode=req.mode)
		return {"ok": True, "provider": PROVIDER, "response": resp}
	except Exception as e:
		print(f"Error processing request: {e}")
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def landing():
	return {
		"message": "Welcome to the Personal Study Assistant API!",
		"endpoints": [
			{"path": "/api/chat", "method": "POST", "description": "Interact with the AI chat endpoint."}
		]
	}

