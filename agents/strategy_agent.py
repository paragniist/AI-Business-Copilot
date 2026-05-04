from utils.llm import ask_gemini

def strategy_agent(context):
    prompt = f"""
You are a strategy consultant.

STRICT CONTEXT GROUNDING:
- Answer ONLY from the provided context.
- Do NOT use outside knowledge.
- If the answer is not found in the context, output exactly: "Answer not found in the document".

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