import requests
import uuid
import time

API_BASE = "http://localhost:8000"

def test_model_chat(model_id):
    session_id = f"val-{uuid.uuid4().hex[:8]}"
    print(f"\n🔍 Testing Model Chat: {model_id} (Session: {session_id})")
    
    # 1. Create Session
    requests.post(f"{API_BASE}/sessions", json={"id": session_id, "title": f"Val Chat {model_id}"})
    
    # 2. Chat
    payload = {
        "message": "Hola, ¿cómo estás? Responde brevemente.",
        "thread_id": session_id,
        "model": model_id
    }
    
    try:
        resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ [CHAT OK] Reply from {data.get('agent', 'unknown')}: {data.get('reply', '')[:60]}...")
            return True
        else:
            print(f"   ❌ [CHAT FAILED] Error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"   ⚠️ [CHAT ERROR]: {e}")
        return False

def test_rag_query(model_id, filename="contrato-arrendamiento.pdf"):
    session_id = f"val-rag-{uuid.uuid4().hex[:8]}"
    print(f"\n📚 Testing RAG with Model: {model_id} (Session: {session_id})")
    
    # 1. Create Session
    requests.post(f"{API_BASE}/sessions", json={"id": session_id, "title": f"Val RAG {model_id}"})
    
    # 2. Sync Upload (simulated)
    import os
    file_path = os.path.join("data/uploads", filename)
    if not os.path.exists(file_path):
        # We need a file, let's look for one
        print(f"   ⚠️ File {filename} not found in uploads. Skipping RAG test.")
        return False

    with open(file_path, "rb") as f:
        requests.post(f"{API_BASE}/upload", files={"file": (filename, f)}, data={"session_id": session_id})
    
    print(f"   Waiting for vectorization...")
    # Poll until completed (timeout 60s for small file)
    start = time.time()
    while time.time() - start < 60:
        st = requests.get(f"{API_BASE}/sessions/{session_id}/status").json()
        if st.get("status") == "completed":
            break
        time.sleep(3)

    # 3. Ask a specific question about the document
    payload = {
        "message": "¿Quién es el arrendador en este contrato?",
        "thread_id": session_id,
        "model": model_id
    }
    
    try:
        resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ [RAG OK] Source-based reply: {data.get('reply', '')[:100]}...")
            return True
        else:
            print(f"   ❌ [RAG FAILED] Error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"   ⚠️ [RAG ERROR]: {e}")
        return False

def main():
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
    ]
    
    print("="*50)
    print("      MULTI-MODEL VALIDATION RUN")
    print("="*50)
    
    results = {}
    for m in models:
        success = test_model_chat(m)
        results[f"{m}_chat"] = "PASS" if success else "FAIL"
        
    # Test RAG with the best quota model
    rag_res = test_rag_query("llama-3.1-8b-instant")
    results["RAG_TEST"] = "PASS" if rag_res else "FAIL"

    print("\n" + "="*50)
    print("      FINAL VALIDATION REPORT")
    print("="*50)
    for k, v in results.items():
        print(f"{k:<30} | {v}")
    print("="*50)

if __name__ == "__main__":
    main()
