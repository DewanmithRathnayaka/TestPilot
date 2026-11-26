"""
Comprehensive Test Suite for TestPilot Day 4: Database & Project CRUD Operations
Tests all database endpoints, error handling, data persistence, and Day 3 regressions.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.project import Project

client = TestClient(app)

def run_database_tests():
    print("================ TESTPILOT DAY 4 DATABASE & CRUD TEST SUITE ================")

    # 1. Test POST /api/projects (Create first project)
    payload_1 = {
        "name": "Calculator App",
        "description": "Basic arithmetic functions with Pytest suite",
        "language": "Python"
    }
    res_create_1 = client.post("/api/projects", json=payload_1)
    print(f"\n1. POST /api/projects (Create 'Calculator App'): Status {res_create_1.status_code}")
    print(f"   Created Project: {res_create_1.json()}")
    assert res_create_1.status_code == 201
    proj_1 = res_create_1.json()
    assert proj_1["name"] == "Calculator App"
    assert proj_1["status"] == "Uploaded"
    assert "id" in proj_1
    proj_1_id = proj_1["id"]

    # 2. Test POST /api/projects (Create second project)
    payload_2 = {
        "name": "Sorting Algorithms",
        "description": "QuickSort and MergeSort benchmarks",
        "language": "Python"
    }
    res_create_2 = client.post("/api/projects", json=payload_2)
    print(f"\n2. POST /api/projects (Create 'Sorting Algorithms'): Status {res_create_2.status_code}")
    assert res_create_2.status_code == 201
    proj_2_id = res_create_2.json()["id"]

    # 3. Test GET /api/projects (Retrieve all projects)
    res_all = client.get("/api/projects")
    print(f"\n3. GET /api/projects (List All): Status {res_all.status_code}")
    all_projects = res_all.json()
    print(f"   Total Projects in Database: {len(all_projects)}")
    assert res_all.status_code == 200
    assert isinstance(all_projects, list)
    assert len(all_projects) >= 2
    assert any(p["id"] == proj_1_id for p in all_projects)
    assert any(p["id"] == proj_2_id for p in all_projects)

    # 4. Test GET /api/projects/{id} (Retrieve single existing project)
    res_single = client.get(f"/api/projects/{proj_1_id}")
    print(f"\n4. GET /api/projects/{proj_1_id} (Retrieve Project 1): Status {res_single.status_code}")
    print(f"   Retrieved Project: {res_single.json()}")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Calculator App"

    # 5. Test GET /api/projects/{id} (Non-existing project -> 404)
    res_not_found = client.get("/api/projects/999999")
    print(f"\n5. GET /api/projects/999999 (Non-existing): Status {res_not_found.status_code}")
    print(f"   Error Detail: {res_not_found.json()}")
    assert res_not_found.status_code == 404
    assert "not found" in res_not_found.json()["detail"].lower()

    # 6. Test PUT /api/projects/{id} (Update existing project)
    update_payload = {
        "name": "Scientific Calculator Pro",
        "status": "Validated"
    }
    res_update = client.put(f"/api/projects/{proj_1_id}", json=update_payload)
    print(f"\n6. PUT /api/projects/{proj_1_id} (Update Name & Status): Status {res_update.status_code}")
    print(f"   Updated Project: {res_update.json()}")
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Scientific Calculator Pro"
    assert res_update.json()["status"] == "Validated"
    # Unchanged fields should remain intact
    assert res_update.json()["language"] == "Python"

    # 7. Test DELETE /api/projects/{id} (Delete project 2)
    res_delete = client.delete(f"/api/projects/{proj_2_id}")
    print(f"\n7. DELETE /api/projects/{proj_2_id} (Delete Project 2): Status {res_delete.status_code}")
    print(f"   Delete Confirmation: {res_delete.json()}")
    assert res_delete.status_code == 200
    assert res_delete.json()["success"] is True

    # Confirm project 2 is now gone
    res_check_deleted = client.get(f"/api/projects/{proj_2_id}")
    print(f"   Verify Deleted Project 2 is now 404: Status {res_check_deleted.status_code}")
    assert res_check_deleted.status_code == 404

    # 8. Test DELETE non-existing project -> 404
    res_del_404 = client.delete("/api/projects/999999")
    print(f"\n8. DELETE /api/projects/999999 (Non-existing): Status {res_del_404.status_code}")
    assert res_del_404.status_code == 404

    # 9. Verify SQLite Persistence across separate database session
    print("\n9. Testing SQLite Disk Persistence:")
    fresh_session = SessionLocal()
    persisted_proj = fresh_session.query(Project).filter(Project.id == proj_1_id).first()
    assert persisted_proj is not None
    assert persisted_proj.name == "Scientific Calculator Pro"
    fresh_session.close()
    print(f"   Persistence Verified! Record {proj_1_id} found in SQLite file on disk.")

    # 10. Regression Check: Day 3 Endpoints Still Pass
    print("\n10. Day 3 Regression Check:")
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/info").status_code == 200
    assert client.get("/api/greeting?name=Student").status_code == 200
    post_check = client.post("/api/test-message", json={"username": "Mentor", "message": "Testing DB compatibility"})
    assert post_check.status_code == 201
    print("   All Day 3 endpoints continue to function with 100% compatibility!")

    print("\n================ ALL 10 TESTS PASSED WITH 100% SUCCESS! ================")

if __name__ == "__main__":
    run_database_tests()
