"""
Lab 2 — Step 5: Cached Client

Extends HuggingFaceClient with local caching to minimize API calls.
Essential for development on free tier.

The cache directory setup and key generation are complete.
Complete the three TODOs in the query() method.
"""

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Import the client you built in Step 3-4
from hf_client import HuggingFaceClient, get_api_token


class CachedHFClient(HuggingFaceClient):
    """
    Extends HuggingFaceClient with local caching to minimize API calls.
    """

    def __init__(self, token: str, cache_dir: str = ".cache/hf_responses"):
        super().__init__(token)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, model_id: str, payload: dict) -> str:
        """Generate a unique cache key from the request."""
        content = json.dumps({"model": model_id, "payload": payload}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def query(self, model_id: str, payload: dict, use_cache: bool = True) -> dict:
        """Query with optional local caching."""
        cache_key = self._cache_key(model_id, payload)
        cache_file = self.cache_dir / f"{cache_key}.json"

        # =================================================================
        # TODO 1: Check cache — return cached response if available
        #
        # If use_cache is True AND cache_file.exists():
        #   - Print "[Cache HIT] Using cached response"
        #   - Read the file: cache_file.read_text(encoding="utf-8")
        #   - Parse JSON and return it
        # =================================================================

        if use_cache and cache_file.exists():
            print("[Cache HIT] Using cached response")
            cached_data = cache_file.read_text(encoding="utf-8")
            return json.loads(cached_data)

        # =================================================================
        # TODO 2: Make the API call (cache miss)
        #
        # - Print "[Cache MISS] Calling API..."
        # - Call the parent's query method: super().query(model_id, payload)
        # - Store the result in a variable
        # =================================================================

        print("[Cache MISS] Calling API...")
        result = super().query(model_id, payload)  # Replace with: super().query(model_id, payload)

        # =================================================================
        # TODO 3: Write result to cache
        #
        # - Convert result to JSON string: json.dumps(result, ensure_ascii=False)
        # - Write to cache_file: cache_file.write_text(..., encoding="utf-8")
        # =================================================================  
        if result:
            result_json = json.dumps(result, ensure_ascii=False, indent=4)
            cache_file.write_text(result_json, encoding="utf-8")

        return result


# --- Main: demonstrate cache behavior ---
if __name__ == "__main__":
    client = CachedHFClient(token=get_api_token())
    MODEL_ID = "Qwen/Qwen2.5-72B-Instruct" 
    prompt_payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user", 
                "content": "What is retrieval-augmented generation in one sentence?"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    print("--- First call (should be Cache MISS) ---")
    result1 = client.query(MODEL_ID, prompt_payload)  
    if result1:
        print(result1["choices"][0]["message"]["content"])

    print("\n--- Second call (should be Cache HIT) ---")
    result2 = client.query(MODEL_ID, prompt_payload)
    if result2:
        print(result1["choices"][0]["message"]["content"])
