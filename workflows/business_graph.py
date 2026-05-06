from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.router_agent import router_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.strategy_agent import strategy_agent
from agents.response_agent import response_agent


# Shared State
class BusinessState(TypedDict):
    query: str
    route: dict
    context: str
    sources: list
    analysis: str
    strategy: str
    final_output: str


# Node 1: Router
def router_node(state):
    route = router_agent(state["query"])
    return {"route": route}


# Node 2: Research
def research_node(state):
    search_res = research_agent(state["query"])
    return {
        "context": search_res.get("text", ""),
        "sources": search_res.get("chunks", [])
    }


# Node 3: Analysis
def analysis_node(state):
    import json
    if state["route"].get("analysis"):
        result_str = analyst_agent(state["context"], state["query"])
        if result_str.startswith("LLM_FAILURE:"):
            return {"analysis": f"API Error: {result_str}", "sources": state.get("sources", [])}
        try:
            clean_str = result_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_str)
            
            if "error" in data:
                # Surface LLM API errors (like 429 Quota Exceeded) directly to the UI
                analysis_text = f"LLM API Error: {data['error']} - {data.get('details', 'No details provided.')}"
                new_sources = state.get("sources", [])
            elif "problem_analysis" in data:
                # Format the new structure into the analysis state string
                parts = []
                if data.get("problem_analysis") and data["problem_analysis"] != "Insufficient data":
                    parts.append(f"Problem Analysis:\n{data['problem_analysis']}")
                    
                    if data.get("key_drivers"):
                        drivers = "\\n".join([f"• {d}" for d in data['key_drivers']])
                        parts.append(f"Key Drivers:\n{drivers}")
                        
                    if data.get("recommendations"):
                        recs = "\\n".join([f"• {r}" for r in data['recommendations']])
                        parts.append(f"Recommendations:\n{recs}")
                        
                    analysis_text = "\n\n".join(parts)
                else:
                    analysis_text = "Insufficient data"
                
                new_sources = data.get("compressed_sources", state.get("sources", []))
            else:
                analysis_text = data.get("analysis", "Insufficient data")
                new_sources = data.get("compressed_sources", state.get("sources", []))
                
            return {
                "analysis": analysis_text, 
                "sources": new_sources
            }
        except Exception:
            return {"analysis": result_str, "sources": state.get("sources", [])}
    return {"analysis": "", "sources": state.get("sources", [])}


# Node 4: Strategy
def strategy_node(state):
    if state["route"].get("strategy"):
        base = state["analysis"] if state["analysis"] else state["context"]
        result = strategy_agent(base)
        return {"strategy": result}
    return {"strategy": ""}


# Node 5: Response
def response_node(state):
    output = response_agent(
        state["query"],
        "• Context retrieved from FAISS Vector DB",
        state["analysis"] + "\n\n" + state["strategy"]
    )
    return {"final_output": output}


# Build Graph
graph = StateGraph(BusinessState)

graph.add_node("router", router_node)
graph.add_node("research", research_node)
graph.add_node("analysis", analysis_node)
graph.add_node("strategy", strategy_node)
graph.add_node("response", response_node)

graph.set_entry_point("router")

graph.add_edge("router", "research")
graph.add_edge("research", "analysis")
graph.add_edge("analysis", "strategy")
graph.add_edge("strategy", "response")
graph.add_edge("response", END)

app = graph.compile()