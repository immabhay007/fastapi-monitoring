import httpx
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(path, method="GET", headers=None):
    url = f"{BASE_URL}{path}"
    try:
        start = time.time()
        response = httpx.request(method, url, headers=headers, timeout=10)
        duration = time.time() - start
        print(f"{method} {path} -> {response.status_code} ({duration:.2f}s)")
        return response
    except Exception as e:
        print(f"{method} {path} -> ERROR: {e}")
        return None

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_endpoint("/health")
    test_endpoint("/users")
    test_endpoint("/products")
    test_endpoint("/simulate-error")
    test_endpoint("/simulate-timeout")
    test_endpoint("/simulate-rate-limit")
    test_endpoint("/secure")  # without API key -> 401
    test_endpoint("/secure", headers={"X-API-Key": "secret-api-key-123"})  # with correct key
    test_endpoint("/secure", headers={"X-API-Key": "wrong-key"})  # wrong key -> 401