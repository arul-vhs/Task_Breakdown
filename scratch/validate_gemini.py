import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables from backend/.env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "models/gemma-4-31b-it")

print(f"API Key: {api_key[:10]}... if set else None")
print(f"Model: {model_name}")

if not api_key:
    print("Error: GEMINI_API_KEY not set in .env")
    exit(1)

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, respond in 5 words.")
    print("Gemini response:")
    print(response.text)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
