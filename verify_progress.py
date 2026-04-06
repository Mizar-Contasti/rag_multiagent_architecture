import requests
import time

BASE_URL = "http://localhost:8000"
import uuid
SESSION_ID = f"test-prog-{uuid.uuid4().hex[:8]}"

def test_flow():
    print(f"1. Creating session {SESSION_ID}...")
    resp = requests.post(f"{BASE_URL}/sessions", json={"id": SESSION_ID, "title": "Verification Session"})
    print(f"   Response: {resp.status_code} {resp.json()}")

    print("2. Uploading small PDF...")
    # Usamos el contrato que ya existe en el repo
    pdf_path = "data/uploads/contrato-arrendamiento.pdf"
    with open(pdf_path, "rb") as f:
        resp = requests.post(f"{BASE_URL}/upload", 
                             files={"file": (pdf_path, f, "application/pdf")},
                             data={"session_id": SESSION_ID})
    print(f"   Response: {resp.status_code} {resp.json()}")

    print("3. Polling status...")
    for _ in range(10):
        resp = requests.get(f"{BASE_URL}/sessions/{SESSION_ID}/status")
        status_data = resp.json()
        print(f"   Status: {status_data}")
        if status_data.get("status") == "completed":
            print("   SUCCESS: Vectorization completed!")
            return
        time.sleep(2)
    print("   TIMEOUT: Vectorization took too long or failed.")

if __name__ == "__main__":
    test_flow()
