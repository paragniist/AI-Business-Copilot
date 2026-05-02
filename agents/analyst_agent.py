from utils.llm import ask_gemini

def analyst_agent(context, query):
    prompt = f"""
You are a business consultant.

Question:
{query}

Context:
{context}

Give only concise practical solution points.
Use bullet points.
No introduction.
No repetition.
"""
    return ask_gemini(prompt)