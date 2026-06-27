from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# List all available models
print("Available models:")
for model in client.models.list():
    print(f"  {model.name}")
