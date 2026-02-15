"""
Lab 2 — Steps 1 & 2: Environment Setup + First API Call

Step 1: Read through the get_api_token() function — understand why we
        never hardcode tokens.
Step 2: Complete the TODO at the bottom to make your first API call.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_api_token():
    """Retrieve API token with validation."""
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise EnvironmentError(
            "HUGGINGFACE_API_TOKEN not found. "
            "Create a .env file with your token or set the environment variable."
        )
    if not token.startswith("hf_"):
        raise ValueError(
            "Invalid Hugging Face token format. Token should start with 'hf_'."
        )
    return token


# --- Configuration ---
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"
TOKEN = get_api_token()
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


# =====================================================================
# TODO (Step 2): Make your first API call
#
# Use requests.post() to send a request to the Hugging Face Inference API.
#
# Hints:
#   - URL: f"{API_URL}{MODEL_ID}"
#   - Pass `headers=HEADERS`
#   - Pass a JSON body: {"inputs": prompt, "parameters": {...}}
#   - Key parameters: max_new_tokens=150, temperature=0.7, return_full_text=False
#   - Call response.raise_for_status() to catch HTTP errors
#   - Parse with response.json()
#   - The generated text is at result[0]["generated_text"]
# =====================================================================

# prompt = "Explain what a vector database is in one paragraph:"


payload = {
    "model": MODEL_ID,
    "messages": [
        {
            "role": "user",
            "content": "Explain what a vector database is in one paragraph:"
        }
    ],
    "max_tokens": 150,
    "temperature": 0.7
}
response = requests.post(API_URL, headers=headers, json=payload)
response.raise_for_status()

result = response.json()

print("Generated Text:")
print(result["choices"][0]["message"]["content"])

# Your code here:
# response = requests.post(...)
# response.raise_for_status()
# result = response.json()
# print("Generated Text:")
# print(result[0]["generated_text"])
