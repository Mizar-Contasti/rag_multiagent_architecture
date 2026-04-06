import requests
import time
import os
import uuid
import sys

API_BASE = "http://localhost:8000"
UPLOADS_DIR = "data/uploads"

def test_file(filename):
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found")
        return False

    session_id = f"stress-{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 Testing file: {filename} (Session: {session_id})")
    
    # 1. Create Session
    requests.post(f"{API_BASE}/sessions", json={"id": session_id, "title": f"Test {filename}"})
    
    # 2. Upload
    print(f"   Uploading...")
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/upload", 
            files={"file": (filename, f)}, 
            data={"session_id": session_id}
        )
    
    if resp.status_code != 200:
        print(f"   ❌ Upload FAILED: {resp.text}")
        return False
    
    print(f"   Upload OK. Monitoring progress...")

    # 3. Poll
    start_time = time.time()
    last_prog = -1
    
    while True:
        try:
            status_resp = requests.get(f"{API_BASE}/sessions/{session_id}/status")
            data = status_resp.json()
            status = data.get("status")
            progress = data.get("progress", 0)
            
            if progress != last_prog:
                print(f"   📈 Progress: {progress}% (Status: {status})")
                last_prog = progress
            
            if status == "completed":
                duration = time.time() - start_time
                print(f"   ✅ SUCCESS! Time: {duration:.1f}s")
                return True
            
            if status == "failed":
                print(f"   ❌ FAILED in background task.")
                return False
                
        except Exception as e:
            print(f"   ⚠️ Polling error: {e}")
        
        # Max timeout protection (10 minutes for the huge book)
        if time.time() - start_time > 600:
            print(f"   ⏳ TIMEOUT after 10 minutes.")
            return False
            
        time.sleep(5)

def main():
    files = [
        "contrato-arrendamiento.pdf",
    ]
    
    results = {}
    for f in files:
        success = test_file(f)
        results[f] = "PASS" if success else "FAIL"

    print("\n" + "="*40)
    print("      FINAL STRESS TEST REPORT")
    print("="*40)
    for f, res in results.items():
        print(f"{f:<50} | {res}")
    print("="*40)

if __name__ == "__main__":
    main()
