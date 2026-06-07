import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env file
load_dotenv(dotenv_path="backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded key: {api_key}")

genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")

try:
    print("Testing models/gemma-4-31b-it...")
    model = genai.GenerativeModel('models/gemma-4-31b-it')
    response = model.generate_content("Hello")
    print(f"Gemma Response: {response.text}")
except Exception as e:
    print(f"Gemma Error: {e}")
