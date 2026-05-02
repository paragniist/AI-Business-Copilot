from utils.llm import ask_gemini

def strategy_agent(analysis):
    prompt = f"""
You are a management consultant.

Based on this analysis:

{analysis}

Give practical business recommendations .
"""
    return ask_gemini(prompt)