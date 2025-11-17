import base64
from io import BytesIO
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

from analyzer import generate_ai_summary, CodeAnalyzer, build_graph_model, create_logic_flowchart, ast

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Backend is running on Render 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# 🔥 FIXED CORS CONFIGURATION
# ---------------------------
FRONTEND_URL = os.environ.get("FRONTEND_URL", "")

origins = [
    FRONTEND_URL,  # Your Vercel deployment
    "http://localhost:5173",  # Local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # No "*", needs explicit domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# API Models
# ---------------------------

class CodePayload(BaseModel):
    code: str

class AnalysisResult(BaseModel):
    summary: str
    flowchart_base64: str | None
    error: str | None

# ---------------------------
# Analyze Endpoint
# ---------------------------

@app.post("/analyze", response_model=AnalysisResult)
def analyze_code_endpoint(payload: CodePayload):
    try:
        # Summary
        summary = generate_ai_summary(payload.code)

        # Flowchart generation
        tree = ast.parse(payload.code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        code_structure = analyzer.structure

        graph_model = build_graph_model(code_structure)
        dot_obj = create_logic_flowchart(graph_model)

        if dot_obj is None:
            raise ValueError("Flowchart generation failed.")

        png_data = dot_obj.pipe(format="png")
        if not png_data:
            raise RuntimeError("Graphviz returned empty output.")

        img_base64 = base64.b64encode(png_data).decode("utf-8")

        return AnalysisResult(
            summary=summary,
            flowchart_base64=img_base64,
            error=None
        )

    except Exception as e:
        return AnalysisResult(
            summary="",
            flowchart_base64=None,
            error=f"Error: {e}"
        )
