from utils.llm import ask_gemini

def response_agent(query, sources, solution):
    prompt = f"""
You are a senior executive. Write a very short Executive Summary (maximum 2-3 lines) based on this business analysis.
Do NOT repeat the full analysis. Only summarize the final conclusion.

Analysis:
{solution}
"""
    return ask_gemini(prompt)