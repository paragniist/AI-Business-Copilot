from utils.llm import ask_gemini

def strategy_agent(context):
    prompt = f"""
You are a strategy consultant.

Based on this:

{context}

Return ONLY:

💡 Recommended Actions
• point
• point
• point

Max 3 bullets.
Short business language.
"""
    return ask_gemini(prompt)