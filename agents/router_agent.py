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

    if "why" in query or "decline" in query or "problem" in query:
        route["analysis"] = True

    if "fix" in query or "recommend" in query or "improve" in query or "strategy" in query:
        route["strategy"] = True

    if route["analysis"] is False and route["strategy"] is False:
        route["analysis"] = True

    return route