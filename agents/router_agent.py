## Our Router Agent dynamically selects which downstream agents to activate 
# based on user intent. This reduces unnecessary LLM calls 
# and mimics autonomous task delegation.


def router_agent(query):
    query = query.lower()

    route = {
        "research": True,
        "analysis": False,
        "strategy": False
    }

    # If it's a "why" question or indicates a problem, it needs analysis
    if any(word in query for word in ["why", "decline", "problem", "analyze", "causes"]):
        route["analysis"] = True

    # If it asks for solutions or strategies
    if any(word in query for word in ["fix", "recommend", "improve", "strategy", "solutions"]):
        route["strategy"] = True

    # Default to analysis if nothing specific matched
    if not route["analysis"] and not route["strategy"]:
        route["analysis"] = True

    # LINKING: If analysis is active, strategy should usually follow to provide value
    if route["analysis"]:
        route["strategy"] = True

    return route