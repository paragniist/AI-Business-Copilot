from utils.llm import ask_gemini

def analyst_agent(context, query):
    prompt = f"""
You are a business analyst.

User Question:
{query}

Business Context:
{context}

Find:
1. Root causes
2. Key insights
3. Important patterns
"""
    return ask_gemini(prompt)