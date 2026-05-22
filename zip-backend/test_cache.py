import requests
import time

url = "http://127.0.0.1:8000/api/v1/search"
data = {"name": "Elon Musk", "description": "CEO Tesla SpaceX"}

def wait_for_job(job_id):
    while True:
        resp = requests.get(f"{url}/status/{job_id}").json()
        if resp["status"] in ("complete", "failed"):
            return resp
        time.sleep(0.5)

print("--- First Search ---")
start = time.time()
r1 = requests.post(url, data=data).json()
res1 = wait_for_job(r1["job_id"])
print(f"Finished in {time.time() - start:.2f}s")

print("\n--- Second Search ---")
start = time.time()
r2 = requests.post(url, data=data).json()
res2 = wait_for_job(r2["job_id"])
print(f"Finished in {time.time() - start:.2f}s")
