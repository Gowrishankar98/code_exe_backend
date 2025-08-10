from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent import process_prompt, improve_js_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    mode: str  # 'generate' or 'improve'
    prompt: str = None  # used for generation
    code: str = None    # used for improvement
    auto_save: bool = False
    filename: str = "output.js"

@app.post("/code")
async def handle_code(req: CodeRequest):
    if req.mode == "generate":
        if not req.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required for code generation.")
        result = process_prompt(req.prompt, auto_save=req.auto_save, filename=req.filename)
        return result
    elif req.mode == "improve":
        if not req.code:
            raise HTTPException(status_code=400, detail="Code is required for improvement.")
        result = improve_js_code(req.code, auto_save=req.auto_save, filename=req.filename)
        return result
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'generate' or 'improve'.")
