import json
from utils.llm import ask_gemini
from rag.retriever import search_docs
from workflows.business_graph import app as business_workflow

def classify_query(query: str) -> str:
    """
    Classify a business query into SIMPLE or COMPLEX.
    Uses LLM for classification to minimize tokens and routing overhead.
    """
    prompt = f"""
Classify the following business query as either 'SIMPLE' or 'COMPLEX'.

SIMPLE queries include: 
- "what is the name of the company?"
- "who is the CEO?"
- "summarize the report"
- "what is this about?"

COMPLEX queries include:
- "why did sales decline?"
- "what strategy should we follow?"
- "analyze the business performance"
- "identify key problems and solutions"

Return ONLY a JSON object with the key 'classification'. Example: {{"classification": "SIMPLE"}}

Query: "{query}"
"""
    try:
        response_text = ask_gemini(prompt)
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return data.get("classification", "COMPLEX").upper()
    except Exception as e:
        print(f"Classification failed, defaulting to COMPLEX: {e}")
        return "COMPLEX"

def process_query(query: str) -> dict:
    """
    Adaptive response logic based on query complexity.
    """
    classification = classify_query(query)
    
    if classification == "SIMPLE":
        # Fast path for simple queries - minimal token usage, skip multi-agent graph
        try:
            search_res = search_docs(query)
            context_text = search_res.get("text", "")
            chunks = search_res.get("chunks", [])
        except Exception as e:
            print(f"Retriever failed: {e}")
            context_text = "No context found."
            chunks = []
            
        prompt = f"""
Answer the following business query very concisely (1-2 lines maximum).

STRICT CONTEXT GROUNDING:
- Answer ONLY from the provided context.
- Do NOT use outside knowledge.
- If the answer is not found in the context, output exactly: "Answer not found in the document".

Context: 
{context_text}

Query: {query}
"""
        short_answer = ask_gemini(prompt)
        return {
            "query": query,
            "final_output": short_answer,
            "route": {"classification": "SIMPLE", "path": "direct_llm_bypass"},
            "context": context_text,
            "sources": chunks,
            "analysis": "Skipped (Simple Query - No deep analysis needed)",
            "strategy": "Skipped (Simple Query - No strategy needed)"
        }
    else:
        # Complex path - full LangGraph workflow
        result = business_workflow.invoke({
            "query": query,
            "route": {},
            "context": "",
            "sources": [],
            "analysis": "",
            "strategy": "",
            "final_output": ""
        })
        
        # Inject the classification type into the route for UI/debugging visibility
        if "route" not in result or not result["route"]:
            result["route"] = {}
        result["route"]["classification"] = "COMPLEX"
        
        return result
