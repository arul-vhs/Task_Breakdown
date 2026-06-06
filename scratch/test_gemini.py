import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API Key starts with:", api_key[:10] if api_key else "None")

genai.configure(api_key=api_key)

print("\n--- Listing available models ---")
try:
    for m in genai.list_models():
        print(f"Name: {m.name}, Supported Actions: {m.supported_generation_methods}")
except Exception as e:
    print("Failed to list models:", e)

print("\n--- Trying gemini-1.5-flash ---")
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Hello")
    print("gemini-1.5-flash success! Response:", response.text)
except Exception as e:
    print("gemini-1.5-flash failed:", e)

print("\n--- Trying gemma-4-31b-it ---")
try:
    model = genai.GenerativeModel("gemma-4-31b-it")
    response = model.generate_content("Hello")
    print("gemma-4-31b-it success! Response:", response.text)
except Exception as e:
    print("gemma-4-31b-it failed:", e)

print("\n--- Trying models/gemma-4-31b-it ---")
try:
    model = genai.GenerativeModel("models/gemma-4-31b-it")
    response = model.generate_content("Hello")
    print("models/gemma-4-31b-it success! Response:", response.text)
except Exception as e:
    print("models/gemma-4-31b-it failed:", e)
