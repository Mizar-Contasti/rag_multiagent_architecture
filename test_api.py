import requests
import uuid
import os

BASE_URL = "http://localhost:8000"
SESSION_ID = f"test-session-{uuid.uuid4().hex[:8]}"

def test_flow():
    # 0. Test Simple Chat (No docs)
    print("\nSTEP 0: Testing simple chat (No documents)...")
    simple_session = f"simple-{uuid.uuid4().hex[:6]}"
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={
            "message": "Hola, ¿quién eres?",
            "thread_id": simple_session,
            "model": "llama-3.1-8b-instant"
        }, timeout=120)
        resp.raise_for_status()
        print(f"Simple chat OK. Reply: {resp.json().get('reply')[:50]}...")
    except Exception as e:
        print(f"Simple chat FAILED: {e}")

    # 1. Create Session for RAG
    print(f"\nSTEP 1: Creating RAG session {SESSION_ID}...")
    try:
        resp = requests.post(f"{BASE_URL}/sessions", json={
            "id": SESSION_ID,
            "title": "RAG Test",
            "selectedModel": "llama-3.3-70b-versatile"
        })
        resp.raise_for_status()
        print("Session created.")
    except Exception as e:
        print(f"Error creating session: {e}")
        return

    # 2. Upload Document
    pdf_path = "data/uploads/contrato-arrendamiento.pdf"
    if os.path.exists(pdf_path):
        print(f"STEP 2: Uploading {pdf_path}...")
        try:
            with open(pdf_path, "rb") as f:
                resp = requests.post(f"{BASE_URL}/upload", 
                                     files={"file": (os.path.basename(pdf_path), f, "application/pdf")},
                                     data={"session_id": SESSION_ID})
            resp.raise_for_status()
            print("Document uploaded.")
        except Exception as e:
            print(f"Error uploading document: {e}")
            return
    else:
        print(f"Document {pdf_path} not found.")

    # 3. Chat with RAG
    message = "Busca en el documento y dime: ¿Cuál es el objeto del contrato?"
    print(f"STEP 3: Sending RAG chat message: '{message}'...")
    try:
        resp = requests.post(f"{BASE_URL}/chat", json={
            "message": message,
            "thread_id": SESSION_ID,
            "model": "llama-3.1-8b-instant"
        }, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        print(f"\nREPLY from Agent ({result.get('agent')}):")
        print("-" * 40)
        print(result.get("reply"))
        print("-" * 40)
    except Exception as e:
        print(f"Error in RAG chat: {e}")

if __name__ == "__main__":
    test_flow()
