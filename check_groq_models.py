"""
Queries the Groq API to list all currently available models.
Run this to discover which model IDs are active before updating tests/orchestrator.

Usage:
    python check_groq_models.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in environment/.env")
    exit(1)

print("Querying Groq API for available models...\n")

resp = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
    timeout=15
)

if resp.status_code != 200:
    print(f"ERROR {resp.status_code}: {resp.text}")
    exit(1)

data = resp.json()
models = sorted(data["data"], key=lambda x: x["id"])

# Separate chat-capable models from others
chat_keywords = ["llama", "mixtral", "gemma", "qwen", "deepseek", "whisper", "mistral"]

print(f"{'MODEL ID':<50} {'OWNED BY':<20}")
print("-" * 72)
for m in models:
    print(f"{m['id']:<50} {m.get('owned_by', ''):<20}")

print(f"\nTotal: {len(models)} models")

# Print recommended list for copy-paste into test files
print("\n--- Recommended chat models for tests ---")
chat_models = [m["id"] for m in models if any(k in m["id"].lower() for k in chat_keywords)
               and "whisper" not in m["id"].lower() and "guard" not in m["id"].lower()]
for m in chat_models:
    print(f'    "{m}",')
