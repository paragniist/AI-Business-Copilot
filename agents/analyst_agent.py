from utils.llm import ask_gemini

def analyst_agent(context, query):
    prompt = f"""
You are a top-tier management consultant.

Business Question:
{query}

Data:
{context}

Return ONLY in this format:

📊 Key Drivers
• point
• point
• point

Keep max 3 bullets.
Short sharp lines only.
"""
    return ask_gemini(prompt)