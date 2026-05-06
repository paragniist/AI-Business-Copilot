from utils.llm import ask_gemini

def analyst_agent(context, query):
    prompt = f"""
You are a Business Analysis Agent working with retrieved document context.
Your job is to synthesize insights, identify key drivers, and provide recommendations based ONLY on the data provided.

STRICT CONTEXT GROUNDING:
- Answer ONLY from the provided Data context.
- Do NOT use outside knowledge or hallucinate.
- If the context is completely empty or completely unrelated to the query, output exactly: {{"problem_analysis": "Insufficient data", "key_drivers": [], "recommendations": []}}
- CONFIDENCE LOGIC: If you can identify at least 2 relevant business signals (e.g., sales drops, delays, pricing issues) from the context, you MUST generate the analysis and DO NOT output "Insufficient data".

Business Question:
{query}

Data:
{context}

Return ONLY a JSON object in this exact format, with no markdown formatting or extra text:
{{
  "problem_analysis": "Concise paragraph synthesizing the core problem based on evidence.",
  "key_drivers": [
    "Specific driver 1 (e.g., aggressive competitor pricing)",
    "Specific driver 2 (e.g., checkout friction)"
  ],
  "recommendations": [
    "Actionable recommendation 1 derived from drivers",
    "Actionable recommendation 2 derived from drivers"
  ],
  "compressed_sources": [
    {{
      "file": "source_filename.pdf",
      "excerpt": "Concise executive-friendly evidence (max 20-25 words) capturing the most relevant sentence without repetition."
    }}
  ]
}}

Ensure all recommendations and drivers are directly supported by the retrieved Data.
"""
    return ask_gemini(prompt)