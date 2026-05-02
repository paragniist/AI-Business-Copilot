def response_agent(query, sources, solution):
    return f"""
📌 PROBLEM ASKED
{query}

📚 SOURCES USED
{sources}

💡 SOLUTION
{solution}

📝 SUMMARY
The system analyzed internal business documents, identified the likely causes behind the issue, and generated practical actions to improve performance and decision-making.
"""