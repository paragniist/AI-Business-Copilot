from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
import os

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.business_graph import app as business_workflow
from rag.vector_store import add_to_vector_db
from app.services.analyzer import process_query
import shutil

app = FastAPI(
    title="AI Business Copilot API",
    description="API for the AI Business Copilot Agentic RAG system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from utils.llm import ask_gemini
    print("Performing LLM startup validation...")
    response = ask_gemini("hello")
    if "LLM_UNAVAILABLE" in response:
        print(f"WARNING: LLM validation failed gracefully. API will start but LLM features may be unavailable. Details: {response}")
    else:
        print("LLM startup validation successful!")

class AnalyzeRequest(BaseModel):
    query: str = Field(..., description="The business query to analyze", example="Analyze why sales dropped last quarter")

class AnalyzeResponse(BaseModel):
    query: str
    final_output: str
    route: Optional[Dict[str, Any]] = None
    context: Optional[str] = None
    sources: Optional[list] = None
    analysis: Optional[str] = None
    strategy: Optional[str] = None

def run_evaluation_task(query: str, answer: str, context_str: str):
    from evaluation.evaluator import evaluate_single_query, log_evaluation
    context_list = [c.strip() for c in context_str.split("\n\n") if c.strip()]
    if not context_list:
        context_list = ["No context retrieved"]
        
    eval_res = evaluate_single_query(question=query, answer=answer, contexts=context_list)
    log_evaluation(query=query, contexts=context_list, answer=answer, eval_results=eval_res)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_query(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    try:
        # Use adaptive logic: simple queries bypass the graph, complex queries run full graph
        result = process_query(request.query)

        # Hook evaluation after final response generation via a background task
        # This computes metrics (faithfulness, answer_relevance) without slowing down the user response
        background_tasks.add_task(
            run_evaluation_task, 
            request.query, 
            result.get("final_output", ""), 
            result.get("context", "")
        )

        return AnalyzeResponse(
            query=request.query,
            final_output=result.get("final_output", ""),
            route=result.get("route", {}),
            context=result.get("context", ""),
            sources=result.get("sources", []),
            analysis=result.get("analysis", ""),
            strategy=result.get("strategy", "")
        )

    except Exception as e:
        # Proper error handling to return a 500 status code with the error detail
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the workflow: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "AI Business Copilot API is running. Send POST requests to /analyze."}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.post("/upload")
async def upload_file(files: list[UploadFile] = File(...)):
    try:
        os.makedirs("data", exist_ok=True)
        filenames = []
        for file in files:
            file_path = f"data/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            filenames.append(file.filename)
        
        # Add to the RAG vector store
        add_to_vector_db("data")
        
        return {"filenames": filenames, "message": f"Successfully indexed {len(filenames)} files."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload or process document: {str(e)}")

@app.post("/evaluate")
async def evaluate_batch():
    try:
        from evaluation.evaluator import batch_evaluate
        res = batch_evaluate("evaluation/dataset.json")
        return {"status": "success", "results": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")
