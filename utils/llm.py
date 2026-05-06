from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize the new google-genai client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Use a currently supported, non-deprecated model
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Primary model {PRIMARY_MODEL} failed: {e}. Trying fallback...")
        try:
            response = client.models.generate_content(
                model=FALLBACK_MODEL,
                contents=prompt
            )
            return response.text
        except Exception as fallback_e:
            print(f"Gemini API Error (Fallback failed): {fallback_e}")
            error_response = {
                "error": "LLM_UNAVAILABLE",
                "details": str(fallback_e)
            }
            return json.dumps(error_response)