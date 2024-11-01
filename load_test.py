import requests
from concurrent.futures import ThreadPoolExecutor
import time

# API endpoint and sample data
URL = "http://127.0.0.1:5000/your_endpoint"
HEADERS = {"Authorization": "Bearer <your_token>"}
DATA = {"key": "value"}  # Adjust with necessary payload


# Function to send a single request
def send_request():
    response = requests.post(URL, headers=HEADERS, json=DATA)
    return response.status_code, response.elapsed.total_seconds()


# Load testing function
def load_test(num_requests, concurrent_users):
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        start_time = time.time()
        results = list(executor.map(lambda _: send_request(), range(num_requests)))
        end_time = time.time()

    # Calculate and print results
    total_time = end_time - start_time
    successful_requests = sum(1 for status, _ in results if status == 200)
    avg_response_time = sum(time for _, time in results) / num_requests

    print(f"Total requests: {num_requests}")
    print(f"Concurrent users: {concurrent_users}")
    print(f"Successful requests: {successful_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average response time: {avg_response_time:.2f} seconds")


# Run the load test
load_test(num_requests=100, concurrent_users=10)
