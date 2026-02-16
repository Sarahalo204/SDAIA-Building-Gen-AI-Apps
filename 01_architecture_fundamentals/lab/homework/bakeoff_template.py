"""
The Great Model Bake-off — Homework Template

Send the same prompts to multiple models and compare quality + latency.
Uses the HuggingFaceClient pattern from Lab 2.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()


def get_api_token():
    """Retrieve API token with validation."""
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise EnvironmentError(
            "HUGGINGFACE_API_TOKEN not found. "
            "Create a .env file with your token or set the environment variable."
        )
    return token


def query_model(model_id: str, prompt: str, token: str, max_retries: int = 3) -> dict:
    """Query a Hugging Face model with retry logic. Returns response + timing."""
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "return_full_text": False,
        },
    }

    start_time = time.time()

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                elapsed = time.time() - start_time
                result = response.json()
                text = result[0].get("generated_text", str(result))
                return {"text": text, "latency_s": round(elapsed, 2), "status": "ok"}
            if response.status_code == 503:
                wait = response.json().get("estimated_time", 30)
                print(f"  Model loading... waiting {wait:.0f}s")
                time.sleep(min(wait, 60))
                continue
            if response.status_code == 429:
                time.sleep(5 * (2 ** attempt))
                continue
            response.raise_for_status()
        except Exception as e:
            if attempt == max_retries - 1:
                elapsed = time.time() - start_time
                return {"text": f"ERROR: {e}", "latency_s": round(elapsed, 2), "status": "error"}
            time.sleep(5)

    elapsed = time.time() - start_time
    return {"text": "Failed after retries", "latency_s": round(elapsed, 2), "status": "error"}


# =====================================================================
# CONFIGURE YOUR BAKE-OFF BELOW
# =====================================================================

MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/flan-t5-large",
]

# TODO: Replace these with your own prompts
PROMPTS = [
    "Explain the difference between TCP and UDP in 3 sentences.",
    "Write a short poem about machine learning.",
    "A company has 100 employees. 60% use Python, 40% use Java, and 20% use both. How many use at least one language?",
]


def main():
    token = get_api_token()
    results = []

    print("=" * 70)
    print("  THE GREAT MODEL BAKE-OFF")
    print("=" * 70)

    for i, prompt in enumerate(PROMPTS, 1):
        print(f"\n--- Prompt {i}: {prompt[:60]}... ---")
        for model in MODELS:
            model_short = model.split("/")[-1]
            print(f"\n  [{model_short}] Querying...")
            result = query_model(model, prompt, token)
            print(f"  [{model_short}] Latency: {result['latency_s']}s")
            print(f"  [{model_short}] Response: {result['text'][:150]}...")

            results.append({
                "prompt_num": i,
                "prompt": prompt,
                "model": model,
                "response": result["text"],
                "latency_s": result["latency_s"],
                "status": result["status"],
            })

    # --- Summary Table ---
    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n{'Prompt':<8} {'Model':<35} {'Latency':>10} {'Status':>8}")
    print("-" * 65)
    for r in results:
        model_short = r["model"].split("/")[-1]
        print(f"  #{r['prompt_num']:<5} {model_short:<35} {r['latency_s']:>8.1f}s {r['status']:>8}")

    # --- Rate quality (manual step) ---
    print("\n" + "=" * 70)
    print("  QUALITY RATINGS")
    print("=" * 70)
    print("\nReview the responses above and add your quality ratings (1-5) to")
    print("report_template.md. Consider: accuracy, completeness, clarity, relevance.")


if __name__ == "__main__":
    main()
