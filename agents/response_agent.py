def response_agent(query, sources, solution):
    return f"""
📌 Business Problem
{query}

📚 Sources
{sources}

{solution}
"""