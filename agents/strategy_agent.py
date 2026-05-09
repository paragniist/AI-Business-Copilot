from utils.llm import ask_gemini

def strategy_agent(context):
    if not context or context in ["Insufficient data", "Skipped"]:
        return "No specific recommendations can be generated due to insufficient data context."

    prompt = f"""
You are a Senior Strategy Consultant. 
Your goal is to provide 3 high-impact, actionable strategic recommendations based on the provided business analysis and context.

STRICT CONTEXT GROUNDING:
- Base your recommendations ONLY on the evidence provided in the Context below.
- Do NOT use outside market knowledge or general business advice not tied to the data.

Context:
{context}

Output Format:
Return ONLY 3 bullet points, each starting with "• ". 
Use professional, executive-ready language.
Keep each recommendation to one concise sentence.

Example:
• Implement a dynamic pricing tier to counter competitor discounting in Region Y.
• Reallocate 15% of the underperforming social budget to high-intent search ads.
• Launch a customer loyalty pilot program to reduce churn in the enterprise segment.
"""
    return ask_gemini(prompt)