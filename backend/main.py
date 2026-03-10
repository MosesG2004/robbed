from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from interpreter import EnglishInterpreter, _AI_AVAILABLE
from executor import SafeExecutor

# ── App setup ──────────────────────────────────────────────────────────

app = FastAPI(
    title="Proteus",
    description="Hacker-style educational tool — translate English into Python.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interpreter = EnglishInterpreter()
executor = SafeExecutor(timeout=2)

# ── Request / response models ─────────────────────────────────────────


class CodeInput(BaseModel):
    code: str


class Instruction(BaseModel):
    line: int
    text: str
    type: str


class ParseResponse(BaseModel):
    instructions: List[Instruction]


class Translation(BaseModel):
    english: str
    python: str
    line: int


class TranslateResponse(BaseModel):
    translations: List[Translation]
    full_code: str


class VariableSnapshot(BaseModel):
    step: int
    variables: Dict


class RunResponse(BaseModel):
    python_code: str
    output: str
    variables: List[VariableSnapshot]
    error: Optional[str]


# ── Routes ─────────────────────────────────────────────────────────────


@app.get("/status")
def status():
    """Check if AI fallback is available."""
    return {"ai_enabled": _AI_AVAILABLE}


@app.post("/parse", response_model=ParseResponse)
def parse_code(body: CodeInput):
    """Classify each English instruction by type."""
    instructions = interpreter.classify(body.code)
    return ParseResponse(instructions=instructions)


@app.post("/translate", response_model=TranslateResponse)
def translate_code(body: CodeInput):
    """Translate English instructions into Python source code."""
    translations, full_code = interpreter.translate(body.code)
    return TranslateResponse(translations=translations, full_code=full_code)


@app.post("/run", response_model=RunResponse)
def run_code(body: CodeInput):
    """Translate and execute the English instructions."""
    translations, full_code = interpreter.translate(body.code)
    result = executor.run(full_code)
    return RunResponse(
        python_code=full_code,
        output=result["output"],
        variables=result["variables"],
        error=result["error"],
    )
