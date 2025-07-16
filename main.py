from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent import ask_gemini  # Refactor your logic into this function
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class CodeRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_code(req: CodeRequest):
    code = ask_gemini(req.prompt)
    print(code,'code')
    return {"code": code}
