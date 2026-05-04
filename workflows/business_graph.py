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
    analysis: str
    strategy: str
    final_output: str


# Node 1: Router
def router_node(state):
    route = router_agent(state["query"])
    return {"route": route}


# Node 2: Research
def research_node(state):
    context = research_agent(state["query"])
    return {"context": context}


# Node 3: Analysis
def analysis_node(state):
    if state["route"].get("analysis"):
        result = analyst_agent(state["context"], state["query"])
        return {"analysis": result}
    return {"analysis": ""}


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