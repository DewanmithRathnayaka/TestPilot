"""
Automated Test Verification Script for TestPilot Day 2 & Day 3 Endpoints
Uses FastAPI TestClient (backed by httpx) to test all routes synchronously.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("================ TESTPILOT API TEST SUITE ================")
    
    # 1. Health check
    res_health = client.get("/api/health")
    print(f"\n1. GET /api/health: Status {res_health.status_code}")
    print(f"   Response: {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    assert res_health.json()["application"] == "TestPilot"

    # 2. Application Info
    res_info = client.get("/api/info")
    print(f"\n2. GET /api/info: Status {res_info.status_code}")
    print(f"   Response: {res_info.json()}")
    assert res_info.status_code == 200
    assert res_info.json()["name"] == "TestPilot"
    assert res_info.json()["version"] == "0.1.0"

    # 3. Welcome endpoint
    res_welcome = client.get("/api/")
    print(f"\n3. GET /api/: Status {res_welcome.status_code}")
    print(f"   Response: {res_welcome.json()}")
    assert res_welcome.status_code == 200
    assert "TestPilot" in res_welcome.json()["message"]

    # 4. Valid POST /api/test-message
    valid_payload = {
        "username": "Student",
        "message": "Testing my first API"
    }
    res_post_valid = client.post("/api/test-message", json=valid_payload)
    print(f"\n4. POST /api/test-message (Valid): Status {res_post_valid.status_code}")
    print(f"   Response: {res_post_valid.json()}")
    assert res_post_valid.status_code == 201
    assert res_post_valid.json()["success"] is True
    assert res_post_valid.json()["echo"]["username"] == "Student"

    # 5. Invalid POST /api/test-message (Pydantic validation failure)
    invalid_payload = {
        "username": "S",  # Too short (min 2)
        "message": ""     # Too short (min 3)
    }
    res_post_invalid = client.post("/api/test-message", json=invalid_payload)
    print(f"\n5. POST /api/test-message (Invalid): Status {res_post_invalid.status_code}")
    print(f"   Validation Error: {res_post_invalid.json()}")
    assert res_post_invalid.status_code == 422  # Unprocessable Entity

    # 6. Query parameter: GET /api/greeting?name=Alice
    res_greeting = client.get("/api/greeting?name=Alice")
    print(f"\n6. GET /api/greeting?name=Alice: Status {res_greeting.status_code}")
    print(f"   Response: {res_greeting.json()}")
    assert res_greeting.status_code == 200
    assert "Alice" in res_greeting.json()["greeting"]

    # 7. Error handling: GET /api/items/150 (HTTPException 404)
    res_404 = client.get("/api/items/150")
    print(f"\n7. GET /api/items/150 (Expected 404): Status {res_404.status_code}")
    print(f"   Response: {res_404.json()}")
    assert res_404.status_code == 404
    assert "was not found" in res_404.json()["detail"]

    # 8. OpenAPI JSON schema generated automatically
    res_openapi = client.get("/openapi.json")
    print(f"\n8. GET /openapi.json (Swagger schema): Status {res_openapi.status_code}")
    assert res_openapi.status_code == 200
    assert res_openapi.json()["info"]["title"] == "TestPilot"

    print("\n================ ALL 8 TESTS PASSED SUCCESSFULLY! ================")

if __name__ == "__main__":
    run_tests()
