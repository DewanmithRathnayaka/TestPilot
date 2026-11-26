"""
Comprehensive Test Suite for TestPilot Day 5: Authentication & Multi-Tenant Authorization
Tests registration, password hashing, JWT generation, login, protected routes, and project isolation.
"""
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_auth_tests():
    print("================ TESTPILOT DAY 5 AUTH & AUTHORIZATION TEST SUITE ================")
    ts = int(time.time() * 1000)
    alice_username = f"alice_{ts}"
    alice_email = f"alice_{ts}@university.edu"
    bob_username = f"bob_{ts}"
    bob_email = f"bob_{ts}@university.edu"

    # 1. Registration: Valid user Alice
    alice_reg_payload = {
        "username": alice_username,
        "email": alice_email,
        "password": "StrongPassword123"
    }
    res_reg_alice = client.post("/api/auth/register", json=alice_reg_payload)
    print(f"\n1. POST /api/auth/register (Alice): Status {res_reg_alice.status_code}")
    print(f"   Registered Profile: {res_reg_alice.json()}")
    assert res_reg_alice.status_code == 201
    alice_profile = res_reg_alice.json()
    assert alice_profile["username"] == alice_username
    assert "password" not in alice_profile
    assert "hashed_password" not in alice_profile

    # 2. Registration: Duplicate username rejection
    res_dup_user = client.post("/api/auth/register", json={
        "username": alice_username,
        "email": f"another_{ts}@university.edu",
        "password": "AnotherPassword123"
    })
    print(f"\n2. POST /api/auth/register (Duplicate Username): Status {res_dup_user.status_code}")
    assert res_dup_user.status_code == 400
    assert "already exists" in res_dup_user.json()["detail"].lower()

    # 3. Registration: Duplicate email rejection
    res_dup_email = client.post("/api/auth/register", json={
        "username": f"different_{ts}",
        "email": alice_email,
        "password": "AnotherPassword123"
    })
    print(f"\n3. POST /api/auth/register (Duplicate Email): Status {res_dup_email.status_code}")
    assert res_dup_email.status_code == 400
    assert "already exists" in res_dup_email.json()["detail"].lower()

    # 4. Registration: Invalid data validation (password too short < 6)
    res_invalid = client.post("/api/auth/register", json={
        "username": f"valid_{ts}",
        "email": f"valid_{ts}@email.com",
        "password": "123"  # Too short
    })
    print(f"\n4. POST /api/auth/register (Short Password): Status {res_invalid.status_code}")
    assert res_invalid.status_code == 422

    # 5. Login: Alice login with correct credentials
    login_alice_data = {
        "username": alice_username,
        "password": "StrongPassword123"
    }
    res_login_alice = client.post("/api/auth/login", data=login_alice_data)
    print(f"\n5. POST /api/auth/login (Alice Valid): Status {res_login_alice.status_code}")
    assert res_login_alice.status_code == 200
    alice_token = res_login_alice.json()["access_token"]
    assert res_login_alice.json()["token_type"] == "bearer"
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    print("   Issued JWT Token successfully!")

    # 6. Login: Alice login with incorrect password
    res_bad_pw = client.post("/api/auth/login", data={
        "username": alice_username,
        "password": "WrongPassword999"
    })
    print(f"\n6. POST /api/auth/login (Wrong Password): Status {res_bad_pw.status_code}")
    assert res_bad_pw.status_code == 401
    assert "incorrect" in res_bad_pw.json()["detail"].lower()

    # 7. Login: Non-existing user
    res_no_user = client.post("/api/auth/login", data={
        "username": f"ghost_{ts}",
        "password": "Password123"
    })
    print(f"\n7. POST /api/auth/login (Non-existing User): Status {res_no_user.status_code}")
    assert res_no_user.status_code == 401

    # 8. Protected Endpoint: GET /api/auth/me without token -> 401
    res_me_no_token = client.get("/api/auth/me")
    print(f"\n8. GET /api/auth/me (No Token): Status {res_me_no_token.status_code}")
    assert res_me_no_token.status_code == 401

    # 9. Protected Endpoint: GET /api/auth/me with invalid token -> 401
    res_me_bad_token = client.get("/api/auth/me", headers={"Authorization": "Bearer bad.token.value"})
    print(f"\n9. GET /api/auth/me (Invalid Token): Status {res_me_bad_token.status_code}")
    assert res_me_bad_token.status_code == 401

    # 10. Protected Endpoint: GET /api/auth/me with Alice's valid token -> 200
    res_me_alice = client.get("/api/auth/me", headers=alice_headers)
    print(f"\n10. GET /api/auth/me (Alice Valid Token): Status {res_me_alice.status_code}")
    print(f"    Profile: {res_me_alice.json()}")
    assert res_me_alice.status_code == 200
    assert res_me_alice.json()["username"] == alice_username

    # ================= AUTHORIZATION & PROJECT ISOLATION =================
    print("\n----- Testing Multi-Tenant Project Authorization -----")

    # 11. Register User Bob
    bob_reg = client.post("/api/auth/register", json={
        "username": bob_username,
        "email": bob_email,
        "password": "BobSecretPassword123"
    })
    assert bob_reg.status_code == 201
    bob_login = client.post("/api/auth/login", data={"username": bob_username, "password": "BobSecretPassword123"})
    bob_headers = {"Authorization": f"Bearer {bob_login.json()['access_token']}"}

    # 12. Alice creates a private project
    res_alice_proj = client.post("/api/projects", json={
        "name": f"Alice Project {ts}",
        "description": "Confidential grading project",
        "language": "Python"
    }, headers=alice_headers)
    print(f"\n12. POST /api/projects (Alice creates project): Status {res_alice_proj.status_code}")
    assert res_alice_proj.status_code == 201
    alice_proj_id = res_alice_proj.json()["id"]

    # 13. Alice retrieves her project list -> includes Alice Project
    res_alice_list = client.get("/api/projects", headers=alice_headers)
    assert any(p["id"] == alice_proj_id for p in res_alice_list.json())
    print("13. Alice can see her own project in her list.")

    # 14. Bob retrieves his project list -> Alice Project is NOT visible to Bob!
    res_bob_list = client.get("/api/projects", headers=bob_headers)
    assert not any(p["id"] == alice_proj_id for p in res_bob_list.json())
    print("14. Isolation Verified: Bob CANNOT see Alice's project in his list.")

    # 15. Bob attempts to access Alice's project by ID -> 403 Forbidden!
    res_bob_hack_get = client.get(f"/api/projects/{alice_proj_id}", headers=bob_headers)
    print(f"15. Bob attempts GET /api/projects/{alice_proj_id}: Status {res_bob_hack_get.status_code}")
    assert res_bob_hack_get.status_code == 403

    # 16. Bob attempts to update Alice's project -> 403 Forbidden!
    res_bob_hack_put = client.put(f"/api/projects/{alice_proj_id}", json={"name": "Hacked Title"}, headers=bob_headers)
    print(f"16. Bob attempts PUT /api/projects/{alice_proj_id}: Status {res_bob_hack_put.status_code}")
    assert res_bob_hack_put.status_code == 403

    # 17. Bob attempts to delete Alice's project -> 403 Forbidden!
    res_bob_hack_del = client.delete(f"/api/projects/{alice_proj_id}", headers=bob_headers)
    print(f"17. Bob attempts DELETE /api/projects/{alice_proj_id}: Status {res_bob_hack_del.status_code}")
    assert res_bob_hack_del.status_code == 403

    # 18. Alice deletes her own project -> 200 OK
    res_alice_del = client.delete(f"/api/projects/{alice_proj_id}", headers=alice_headers)
    assert res_alice_del.status_code == 200
    print("18. Alice successfully deletes her own project.")

    # 19. Day 3 Regression Check
    assert client.get("/api/health").status_code == 200
    print("19. Regression Check: Day 3 endpoints continue to function.")

    print("\n================ ALL 19 TESTS PASSED WITH 100% SUCCESS! ================")

if __name__ == "__main__":
    run_auth_tests()
