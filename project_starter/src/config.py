import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("GEMINI_API_TOKEN")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini/gemini-1.5-pro")
    # Add other configuration as needed
