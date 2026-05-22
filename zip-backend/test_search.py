import time
import requests

def test_search():
    print("Starting search...")
    resp = requests.post(
        "http://127.0.0.1:8000/api/v1/search",
        data={"name": "Elon Musk", "description": "CEO Tesla SpaceX"}
    )
    if resp.status_code != 200:
        print("Failed to start search:", resp.text)
        return
        
    data = resp.json()
    job_id = data["job_id"]
    print(f"Job started. ID: {job_id}")
    
    while True:
        status_resp = requests.get(f"http://127.0.0.1:8000/api/v1/search/status/{job_id}")
        if status_resp.status_code != 200:
            print("Failed to get status:", status_resp.text)
            break
            
        status_data = status_resp.json()
        
        if status_data["status"] in ("complete", "failed"):
            print("Job finished!")
            break
            
        time.sleep(1)

if __name__ == "__main__":
    test_search()
