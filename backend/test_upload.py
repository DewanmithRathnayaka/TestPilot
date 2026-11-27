"""
Comprehensive Test Suite for TestPilot Day 6: Secure ZIP Upload and File Handling
Tests normal uploads, structural validation, and security vulnerabilities (Zip Slip, Zip Bombs, Symlinks).
"""
import io
import time
import zipfile
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_in_memory_zip(file_dict: dict, comment: bytes = b"") -> bytes:
    """Helper to generate in-memory ZIP archives."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if comment:
            zf.comment = comment
        for path, content in file_dict.items():
            zf.writestr(path, content)
    return buf.getvalue()


def run_upload_tests():
    print("================ TESTPILOT DAY 6 SECURE ZIP UPLOAD TEST SUITE ================")
    ts = int(time.time() * 1000)

    # 0. Setup: Register and authenticate test users Alice & Bob
    alice_username = f"uploader_alice_{ts}"
    client.post("/api/auth/register", json={
        "username": alice_username,
        "email": f"{alice_username}@university.edu",
        "password": "Password123"
    })
    login_alice = client.post("/api/auth/login", data={"username": alice_username, "password": "Password123"})
    alice_token = login_alice.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    bob_username = f"uploader_bob_{ts}"
    client.post("/api/auth/register", json={
        "username": bob_username,
        "email": f"{bob_username}@university.edu",
        "password": "Password123"
    })
    login_bob = client.post("/api/auth/login", data={"username": bob_username, "password": "Password123"})
    bob_token = login_bob.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # ================= 1. NORMAL UPLOAD TESTS =================

    # Test 1: Upload a valid Python project ZIP
    valid_zip_bytes = create_in_memory_zip({
        "src/calculator.py": "def add(a, b):\n    return a + b\n",
        "tests/test_calculator.py": "from src.calculator import add\ndef test_add():\n    assert add(2, 3) == 5\n",
        "requirements.txt": "pytest>=7.0.0\n",
        "README.md": "# Sample Calculator\n"
    })
    res_valid = client.post(
        "/api/projects/upload",
        files={"file": ("calculator_project.zip", valid_zip_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n1. Valid ZIP upload: Status {res_valid.status_code}")
    print(f"   Project Metadata: {res_valid.json()}")
    assert res_valid.status_code == 201
    alice_project = res_valid.json()
    assert alice_project["name"] == "calculator_project"
    assert alice_project["status"] == "Validated"
    assert alice_project["validation_status"] == "Valid"
    assert alice_project["source_file_count"] == 1
    assert alice_project["test_file_count"] == 1
    assert "storage_path" not in alice_project  # Private storage path must NOT be leaked
    alice_proj_id = alice_project["id"]

    # Test 2: Upload a ZIP containing multiple source and test files
    multi_zip_bytes = create_in_memory_zip({
        "src/main.py": "print('Hello TestPilot')\n",
        "src/utils.py": "def multiply(x, y):\n    return x * y\n",
        "tests/test_main.py": "def test_main(): assert True\n",
        "tests/test_utils.py": "def test_mult(): assert True\n",
        "requirements.txt": "pytest\n"
    })
    res_multi = client.post(
        "/api/projects/upload",
        files={"file": ("multi_module_project.zip", multi_zip_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n2. Multi-module ZIP upload: Status {res_multi.status_code}")
    assert res_multi.status_code == 201
    assert res_multi.json()["source_file_count"] == 2
    assert res_multi.json()["test_file_count"] == 2

    # Test 3: Upload an empty ZIP (0 archive entries)
    empty_zip_bytes = create_in_memory_zip({})
    res_empty_zip = client.post(
        "/api/projects/upload",
        files={"file": ("empty.zip", empty_zip_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n3. Empty ZIP rejection: Status {res_empty_zip.status_code} ({res_empty_zip.json()['detail']})")
    assert res_empty_zip.status_code == 400

    # Test 4: Upload corrupted ZIP bytes
    corrupted_bytes = b"PK\x03\x04ThisIsCorruptedPayloadGarbage12345"
    res_corrupted = client.post(
        "/api/projects/upload",
        files={"file": ("corrupted.zip", corrupted_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n4. Corrupted ZIP rejection: Status {res_corrupted.status_code}")
    assert res_corrupted.status_code == 400

    # Test 5: Upload non-ZIP file (text file with .zip extension, fails magic bytes)
    fake_zip_bytes = b"Hello, this is just a plain text file disguised as a zip."
    res_fake_zip = client.post(
        "/api/projects/upload",
        files={"file": ("fake.zip", fake_zip_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n5. Disguised non-ZIP file rejection: Status {res_fake_zip.status_code}")
    assert res_fake_zip.status_code == 400
    assert "signature mismatch" in res_fake_zip.json()["detail"].lower()

    # Test 6: Upload empty file (0 bytes)
    res_zero_bytes = client.post(
        "/api/projects/upload",
        files={"file": ("zero.zip", b"", "application/zip")},
        headers=alice_headers
    )
    print(f"\n6. Zero-byte file rejection: Status {res_zero_bytes.status_code}")
    assert res_zero_bytes.status_code == 400

    # Test 7: Upload file exceeding 10 MB limit (Stream bounded guard)
    oversized_bytes = b"PK\x03\x04" + (b"A" * (10 * 1024 * 1024 + 100))
    res_oversized = client.post(
        "/api/projects/upload",
        files={"file": ("oversized.zip", oversized_bytes, "application/zip")},
        headers=alice_headers
    )
    print(f"\n7. Oversized upload rejection (> 10MB): Status {res_oversized.status_code}")
    assert res_oversized.status_code == 413

    # Test 8: ZIP with missing src/ directory
    no_src_zip = create_in_memory_zip({
        "tests/test_main.py": "def test_ok(): assert True\n"
    })
    res_no_src = client.post(
        "/api/projects/upload",
        files={"file": ("no_src.zip", no_src_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"\n8. Missing 'src/' directory rejection: Status {res_no_src.status_code}")
    assert res_no_src.status_code == 400
    assert "missing required 'src/'" in res_no_src.json()["detail"].lower()

    # Test 9: ZIP with missing tests/ directory
    no_tests_zip = create_in_memory_zip({
        "src/main.py": "print('No tests')\n"
    })
    res_no_tests = client.post(
        "/api/projects/upload",
        files={"file": ("no_tests.zip", no_tests_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"\n9. Missing 'tests/' directory rejection: Status {res_no_tests.status_code}")
    assert res_no_tests.status_code == 400
    assert "missing required 'tests/'" in res_no_tests.json()["detail"].lower()

    # Test 10: ZIP with empty src/ directory (no Python source files)
    no_py_zip = create_in_memory_zip({
        "src/notes.txt": "just notes\n",
        "tests/test_sample.py": "def test_it(): pass\n"
    })
    res_no_py = client.post(
        "/api/projects/upload",
        files={"file": ("no_py.zip", no_py_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"\n10. Missing Python source files rejection: Status {res_no_py.status_code}")
    assert res_no_py.status_code == 400
    assert "contains no python (.py) source files" in res_no_py.json()["detail"].lower()

    # ================= 2. SECURITY TESTS =================
    print("\n----- Testing Advanced Security Safeguards -----")

    # Security Test 1: Path Traversal (Zip Slip with '../../')
    slip_zip = create_in_memory_zip({
        "../../hacked.txt": "escaped the sandbox!\n",
        "src/main.py": "print('ok')\n",
        "tests/test_main.py": "def test_ok(): pass\n"
    })
    res_slip = client.post(
        "/api/projects/upload",
        files={"file": ("zip_slip.zip", slip_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"11. Zip Slip ('../../') rejection: Status {res_slip.status_code} ({res_slip.json()['detail']})")
    assert res_slip.status_code == 400
    assert "path traversal" in res_slip.json()["detail"].lower()

    # Security Test 2: Absolute Path Traversal ('/etc/passwd')
    abs_zip = create_in_memory_zip({
        "/etc/passwd": "root:x:0:0...\n",
        "src/main.py": "print('ok')\n",
        "tests/test_main.py": "def test_ok(): pass\n"
    })
    res_abs = client.post(
        "/api/projects/upload",
        files={"file": ("abs_path.zip", abs_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"12. Absolute path rejection: Status {res_abs.status_code}")
    assert res_abs.status_code == 400

    # Security Test 3: Windows Drive Path ('C:\\evil.py')
    drive_zip = create_in_memory_zip({
        "C:/evil.py": "print('bad')\n",
        "src/main.py": "print('ok')\n",
        "tests/test_main.py": "def test_ok(): pass\n"
    })
    res_drive = client.post(
        "/api/projects/upload",
        files={"file": ("drive_path.zip", drive_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"13. Windows drive path rejection: Status {res_drive.status_code}")
    assert res_drive.status_code == 400

    # Security Test 4: Symbolic Link entry rejection
    symlink_buf = io.BytesIO()
    with zipfile.ZipFile(symlink_buf, "w") as zf:
        zf.writestr("src/main.py", "print('main')\n")
        zf.writestr("tests/test_main.py", "def test_m(): pass\n")
        zinfo = zipfile.ZipInfo("symlink_target")
        zinfo.create_system = 3  # Unix system
        # Set POSIX file mode for symlink: S_IFLNK (0o120000) | 0o777
        zinfo.external_attr = (0o120777) << 16
        zf.writestr(zinfo, "/etc/shadow")
    symlink_zip = symlink_buf.getvalue()

    res_symlink = client.post(
        "/api/projects/upload",
        files={"file": ("symlink.zip", symlink_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"14. Symbolic link rejection: Status {res_symlink.status_code} ({res_symlink.json()['detail']})")
    assert res_symlink.status_code == 400
    assert "symbolic link" in res_symlink.json()["detail"].lower()

    # Security Test 5: Archive Entry Count Limit (> 500 entries)
    too_many_entries = {f"src/file_{i}.py": f"# file {i}\n" for i in range(505)}
    too_many_entries["tests/test_ok.py"] = "def test(): pass\n"
    bomb_entries_zip = create_in_memory_zip(too_many_entries)
    res_many_entries = client.post(
        "/api/projects/upload",
        files={"file": ("entry_bomb.zip", bomb_entries_zip, "application/zip")},
        headers=alice_headers
    )
    print(f"15. Entry count limit rejection (> 500): Status {res_many_entries.status_code}")
    assert res_many_entries.status_code == 400
    assert "exceeding maximum limit" in res_many_entries.json()["detail"].lower()

    # Security Test 6: Multi-User Project Isolation with Identical Upload Filename
    res_bob_same_name = client.post(
        "/api/projects/upload",
        files={"file": ("calculator_project.zip", valid_zip_bytes, "application/zip")},
        headers=bob_headers
    )
    assert res_bob_same_name.status_code == 201
    bob_project = res_bob_same_name.json()
    assert bob_project["id"] != alice_proj_id  # Unique project records
    print("16. Identical upload filename handled safely across two distinct users.")

    # Bob attempts to access Alice's uploaded project -> 403 Forbidden!
    res_bob_hack = client.get(f"/api/projects/{alice_proj_id}", headers=bob_headers)
    print(f"17. Bob access to Alice's uploaded project: Status {res_bob_hack.status_code} (Forbidden)")
    assert res_bob_hack.status_code == 403

    print("\n================ ALL 17 DAY 6 TESTS PASSED WITH 100% SUCCESS! ================")

if __name__ == "__main__":
    run_upload_tests()
