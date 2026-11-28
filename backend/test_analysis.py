"""
TestPilot Day 7 Automated Test Suite: Static Project Structure Analysis & AST Validation
Tests all 25 validation, file discovery, AST parsing, test candidate detection,
requirements parsing, API integration, and security isolation requirements.
"""
import ast
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.services.project_analyzer import (
    locate_working_root,
    discover_files,
    check_ast_syntax,
    discover_pytest_candidates,
    inspect_requirements,
    analyze_extracted_project,
    MAX_INSPECT_FILE_SIZE
)

client = TestClient(app)


def get_auth_token(username_prefix: str = "ast_user") -> str:
    """Helper to register and login a fresh test user, returning the JWT token."""
    ts = int(time.time() * 1000)
    user_data = {
        "username": f"{username_prefix}_{ts}",
        "email": f"{username_prefix}_{ts}@testpilot.edu",
        "password": "Password123!"
    }
    r = client.post("/api/auth/register", json=user_data)
    assert r.status_code == 201, f"User registration failed: {r.text}"

    login_res = client.post(
        "/api/auth/login",
        data={"username": user_data["username"], "password": user_data["password"]}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    return login_res.json()["access_token"]


def create_mock_project(base_dir: Path, with_wrapper: bool = False, custom_layout: dict = None) -> Path:
    """
    Creates a temporary project structure on disk for testing.
    custom_layout: dict mapping relative file path strings to text contents.
    """
    root = base_dir / "wrapper_folder" if with_wrapper else base_dir
    root.mkdir(parents=True, exist_ok=True)

    if custom_layout is None:
        # Default valid standard structure
        custom_layout = {
            "src/main.py": "def add(a: int, b: int) -> int:\n    return a + b\n",
            "src/utils.py": "def helper():\n    return 'help'\n",
            "tests/test_main.py": (
                "def test_add_positive():\n    assert 1 + 1 == 2\n\n"
                "def helper_not_test():\n    pass\n\n"
                "class TestMath:\n"
                "    def test_multiplication(self):\n        assert 2 * 3 == 6\n"
                "    def not_a_test_method(self):\n        pass\n"
            ),
            "requirements.txt": "pytest>=7.4.0\nrequests==2.31.0\n# comment\n",
            "README.md": "# Mock Project\nAutomated testing target.\n"
        }

    for rel_path, content in custom_layout.items():
        full_path = root / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            full_path.write_bytes(content)
        else:
            full_path.write_text(content, encoding="utf-8")

    return root


def run_all_tests():
    print("=" * 70)
    print("TESTPILOT DAY 7: STATIC PROJECT ANALYSIS & AST VALIDATION TEST SUITE")
    print("=" * 70)

    passed_count = 0
    total_tests = 25

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        # -------------------------------------------------------------
        # Test 1: Valid Python project structure (src/, tests/)
        # -------------------------------------------------------------
        proj1 = temp_dir / "proj1"
        create_mock_project(proj1)
        res1 = analyze_extracted_project(proj1, 1, "proj1")
        assert res1.structure_valid is True, "Expected structure_valid to be True"
        assert res1.source_file_count == 2, f"Expected 2 src files, got {res1.source_file_count}"
        assert res1.test_file_count == 1, f"Expected 1 test file, got {res1.test_file_count}"
        passed_count += 1
        print("✓ [01/25] Valid Python project structure detected correctly")

        # -------------------------------------------------------------
        # Test 2: Valid project without wrapper folder
        # -------------------------------------------------------------
        proj2 = temp_dir / "proj2"
        create_mock_project(proj2, with_wrapper=False)
        w_root2 = locate_working_root(proj2)
        assert w_root2 == proj2, f"Expected root {proj2}, got {w_root2}"
        passed_count += 1
        print("✓ [02/25] Non-wrapped root recognized without transformation")

        # -------------------------------------------------------------
        # Test 3: Valid project with single wrapper folder unwrapped
        # -------------------------------------------------------------
        proj3 = temp_dir / "proj3"
        create_mock_project(proj3, with_wrapper=True)
        w_root3 = locate_working_root(proj3)
        assert w_root3 == proj3 / "wrapper_folder", f"Expected unwrapped child {proj3 / 'wrapper_folder'}, got {w_root3}"
        res3 = analyze_extracted_project(proj3, 3, "proj3_wrapped")
        assert res3.structure_valid is True
        passed_count += 1
        print("✓ [03/25] Single top-level wrapper folder automatically unwrapped")

        # -------------------------------------------------------------
        # Test 4: Missing src/ directory detection
        # -------------------------------------------------------------
        proj4 = temp_dir / "proj4"
        create_mock_project(proj4, custom_layout={
            "tests/test_one.py": "def test_ok(): pass\n",
            "requirements.txt": "pytest\n"
        })
        res4 = analyze_extracted_project(proj4, 4, "proj4_no_src")
        assert res4.structure_valid is False
        assert any("Missing required 'src/' directory" in w for w in res4.warnings)
        passed_count += 1
        print("✓ [04/25] Missing 'src/' directory flagged with structure_valid=False and warning")

        # -------------------------------------------------------------
        # Test 5: Missing tests/ directory detection
        # -------------------------------------------------------------
        proj5 = temp_dir / "proj5"
        create_mock_project(proj5, custom_layout={
            "src/app.py": "print('hello')\n",
            "requirements.txt": "pytest\n"
        })
        res5 = analyze_extracted_project(proj5, 5, "proj5_no_tests")
        assert res5.structure_valid is False
        assert any("Missing required 'tests/' directory" in w for w in res5.warnings)
        passed_count += 1
        print("✓ [05/25] Missing 'tests/' directory flagged with structure_valid=False and warning")

        # -------------------------------------------------------------
        # Test 6: Empty src/ directory warning
        # -------------------------------------------------------------
        proj6 = temp_dir / "proj6"
        (proj6 / "src").mkdir(parents=True, exist_ok=True)
        (proj6 / "tests").mkdir(parents=True, exist_ok=True)
        (proj6 / "tests" / "test_dummy.py").write_text("def test_d(): pass\n")
        res6 = analyze_extracted_project(proj6, 6, "proj6_empty_src")
        assert res6.source_file_count == 0
        assert any("no Python (.py) source files" in w for w in res6.warnings)
        passed_count += 1
        print("✓ [06/25] Empty 'src/' directory produces actionable advisory warning")

        # -------------------------------------------------------------
        # Test 7: Empty tests/ directory warning
        # -------------------------------------------------------------
        proj7 = temp_dir / "proj7"
        (proj7 / "src").mkdir(parents=True, exist_ok=True)
        (proj7 / "src" / "app.py").write_text("x = 1\n")
        (proj7 / "tests").mkdir(parents=True, exist_ok=True)
        res7 = analyze_extracted_project(proj7, 7, "proj7_empty_tests")
        assert res7.test_file_count == 0
        assert any("no Pytest test files" in w for w in res7.warnings)
        passed_count += 1
        print("✓ [07/25] Empty 'tests/' directory produces actionable advisory warning")

        # -------------------------------------------------------------
        # Test 8: Recursive discovery of nested source files inside packages
        # -------------------------------------------------------------
        proj8 = temp_dir / "proj8"
        create_mock_project(proj8, custom_layout={
            "src/__init__.py": "",
            "src/models/user.py": "class User: pass\n",
            "src/services/auth/crypto.py": "def hash_pw(): pass\n",
            "tests/test_all.py": "def test_ok(): pass\n"
        })
        res8 = analyze_extracted_project(proj8, 8, "proj8_nested_src")
        assert res8.source_file_count == 3, f"Expected 3 nested src files, got {res8.source_file_count}"
        passed_count += 1
        print("✓ [08/25] Discovered all deeply nested source files across subpackages")

        # -------------------------------------------------------------
        # Test 9: Recursive discovery of nested test files
        # -------------------------------------------------------------
        proj9 = temp_dir / "proj9"
        create_mock_project(proj9, custom_layout={
            "src/app.py": "pass\n",
            "tests/unit/test_unit.py": "def test_u(): pass\n",
            "tests/integration/api/test_api.py": "def test_i(): pass\n",
            "tests/suite_test.py": "def test_s(): pass\n"
        })
        res9 = analyze_extracted_project(proj9, 9, "proj9_nested_tests")
        assert res9.test_file_count == 3, f"Expected 3 test files, got {res9.test_file_count}"
        passed_count += 1
        print("✓ [09/25] Discovered nested test files matching test_*.py and *_test.py")

        # -------------------------------------------------------------
        # Test 10: Disregarding non-Python files from Python counts
        # -------------------------------------------------------------
        proj10 = temp_dir / "proj10"
        create_mock_project(proj10, custom_layout={
            "src/app.py": "print('ok')\n",
            "src/data.json": '{"k": 1}',
            "src/notes.txt": 'some notes',
            "tests/test_app.py": "def test_app(): pass\n",
            "tests/test_fixtures.csv": "col1,col2\n1,2\n"
        })
        res10 = analyze_extracted_project(proj10, 10, "proj10_non_py")
        assert res10.source_file_count == 1
        assert res10.test_file_count == 1
        assert res10.python_file_count == 2
        assert res10.total_file_count >= 5
        passed_count += 1
        print("✓ [10/25] Non-Python files (.json, .txt, .csv) excluded from Python metrics")

        # -------------------------------------------------------------
        # Test 11: Disregarding __pycache__ and .pyc files
        # -------------------------------------------------------------
        proj11 = temp_dir / "proj11"
        create_mock_project(proj11, custom_layout={
            "src/app.py": "print('ok')\n",
            "src/__pycache__/app.cpython-312.pyc": b"\x00\x00\x00\x00bytecode",
            "tests/test_app.py": "def test_ok(): pass\n",
            "tests/__pycache__/test_app.cpython-312.pyc": b"\x00\x00\x00\x00bytecode"
        })
        res11 = analyze_extracted_project(proj11, 11, "proj11_pycache")
        assert res11.python_file_count == 2
        assert res11.source_file_count == 1
        assert res11.test_file_count == 1
        passed_count += 1
        print("✓ [11/25] __pycache__ directories and .pyc bytecode cleanly filtered out")

        # -------------------------------------------------------------
        # Test 12: Skipping symbolic links during discovery
        # -------------------------------------------------------------
        proj12 = temp_dir / "proj12"
        create_mock_project(proj12)
        # Attempt symlink creation if OS supports it without privs
        try:
            symlink_target = proj12 / "src" / "main.py"
            symlink_path = proj12 / "src" / "symlink_file.py"
            symlink_path.symlink_to(symlink_target)
            has_symlink = True
        except (OSError, NotImplementedError):
            has_symlink = False

        src_f, test_f, all_py, all_f, _, _, _ = discover_files(proj12)
        if has_symlink:
            assert symlink_path not in src_f, "Symlink was not ignored in discover_files"
            assert symlink_path not in all_py, "Symlink was not ignored in all_py"
        passed_count += 1
        print(f"✓ [12/25] Symbolic links safely skipped (symlinks created: {has_symlink})")

        # -------------------------------------------------------------
        # Test 13: AST parsing of valid Python file
        # -------------------------------------------------------------
        valid_py = temp_dir / "valid.py"
        valid_py.write_text("def greet(name: str) -> str:\n    return f'Hello {name}'\n")
        tree, err = check_ast_syntax(valid_py, temp_dir)
        assert err is None, f"Expected no error, got: {err}"
        assert isinstance(tree, ast.AST), "Expected valid ast.AST object"
        passed_count += 1
        print("✓ [13/25] Valid Python file successfully parsed into Abstract Syntax Tree")

        # -------------------------------------------------------------
        # Test 14: AST syntax error detection
        # -------------------------------------------------------------
        bad_py = temp_dir / "bad.py"
        bad_py.write_text("def broken_func(\n    return 42\n")
        tree, err = check_ast_syntax(bad_py, temp_dir)
        assert tree is None, "Expected tree to be None on syntax error"
        assert err is not None, "Expected SyntaxErrorDetail"
        passed_count += 1
        print("✓ [14/25] SyntaxError successfully trapped via ast.parse without code execution")

        # -------------------------------------------------------------
        # Test 15: AST syntax error line and column reporting
        # -------------------------------------------------------------
        syntax_file = temp_dir / "syntax_err.py"
        syntax_file.write_text("# Line 1\nx = 10\nif x ==\n    print('fail')\n")
        tree, err = check_ast_syntax(syntax_file, temp_dir)
        assert err is not None
        assert err.line == 3, f"Expected error on line 3, got line {err.line}"
        assert err.column is not None and err.column > 0
        assert len(err.message) > 0
        passed_count += 1
        print(f"✓ [15/25] Accurate syntax error diagnostics: line {err.line}, col {err.column}: '{err.message}'")

        # -------------------------------------------------------------
        # Test 16: AST syntax errors on multiple invalid files
        # -------------------------------------------------------------
        proj16 = temp_dir / "proj16"
        create_mock_project(proj16, custom_layout={
            "src/broken1.py": "def bad1(:\n    pass\n",
            "src/broken2.py": "class Bad2\n    pass\n",
            "src/good.py": "def good(): pass\n",
            "tests/test_ok.py": "def test_ok(): pass\n"
        })
        res16 = analyze_extracted_project(proj16, 16, "proj16_multi_err")
        assert res16.syntax_error_count == 2
        assert len(res16.syntax_errors) == 2
        err_files = [e.file for e in res16.syntax_errors]
        assert "src/broken1.py" in err_files
        assert "src/broken2.py" in err_files
        passed_count += 1
        print("✓ [16/25] Multiple syntax error files aggregated into structured response")

        # -------------------------------------------------------------
        # Test 17: Discovery of standalone test_* functions
        # -------------------------------------------------------------
        test_content17 = (
            "def test_first(): pass\n"
            "def test_second_check(): pass\n"
            "async def test_async_endpoint(): pass\n"
            "def regular_function(): pass\n"
        )
        tree17 = ast.parse(test_content17)
        fn_c, cls_c, meth_c = discover_pytest_candidates(tree17)
        assert fn_c == 3, f"Expected 3 test functions, got {fn_c}"
        assert cls_c == 0
        assert meth_c == 0
        passed_count += 1
        print("✓ [17/25] Discovered 3 top-level test functions (including async def)")

        # -------------------------------------------------------------
        # Test 18: Discovery of Test* classes and test_* methods
        # -------------------------------------------------------------
        test_content18 = (
            "class TestAuthentication:\n"
            "    def test_valid_token(self): pass\n"
            "    def test_expired_token(self): pass\n"
            "    def helper_setup(self): pass\n\n"
            "class TestDatabase:\n"
            "    def test_query(self): pass\n"
        )
        tree18 = ast.parse(test_content18)
        fn_c, cls_c, meth_c = discover_pytest_candidates(tree18)
        assert cls_c == 2, f"Expected 2 test classes, got {cls_c}"
        assert meth_c == 3, f"Expected 3 test methods, got {meth_c}"
        passed_count += 1
        print("✓ [18/25] Discovered 2 Test* classes with 3 test_* methods")

        # -------------------------------------------------------------
        # Test 19: Non-test functions ignored
        # -------------------------------------------------------------
        test_content19 = (
            "def setup_module(): pass\n"
            "def teardown_module(): pass\n"
            "def helper(): pass\n"
            "def calculate_total(): pass\n"
        )
        tree19 = ast.parse(test_content19)
        fn_c, _, _ = discover_pytest_candidates(tree19)
        assert fn_c == 0, f"Expected 0 test functions, got {fn_c}"
        passed_count += 1
        print("✓ [19/25] Non-test functions (helper, setup, teardown) correctly ignored")

        # -------------------------------------------------------------
        # Test 20: Non-test classes ignored
        # -------------------------------------------------------------
        test_content20 = (
            "class Calculator:\n"
            "    def test_not_in_test_class(self): pass\n"
            "class MockUser:\n"
            "    pass\n"
        )
        tree20 = ast.parse(test_content20)
        _, cls_c, meth_c = discover_pytest_candidates(tree20)
        assert cls_c == 0, f"Expected 0 test classes, got {cls_c}"
        assert meth_c == 0, f"Expected 0 test methods, got {meth_c}"
        passed_count += 1
        print("✓ [20/25] Non-test classes (Calculator, MockUser) correctly ignored")

        # -------------------------------------------------------------
        # Test 21: Parsing standard requirements.txt with pytest
        # -------------------------------------------------------------
        req_file21 = temp_dir / "req21.txt"
        req_file21.write_text(
            "# Testing dependencies\n"
            "pytest>=7.4.0\n"
            "pytest-cov==4.1.0 # coverage\n"
            "fastapi>=0.100.0\n"
            "pydantic[email]>=2.0.0\n"
        )
        deps, has_pytest, req_warns = inspect_requirements(req_file21)
        assert has_pytest is True, "Expected has_pytest to be True"
        assert len(deps) == 4, f"Expected 4 dependencies, got {len(deps)}"
        assert len(req_warns) == 0
        passed_count += 1
        print("✓ [21/25] requirements.txt parsed: pytest detected, inline comments stripped")

        # -------------------------------------------------------------
        # Test 22: Missing pytest warning in requirements.txt
        # -------------------------------------------------------------
        req_file22 = temp_dir / "req22.txt"
        req_file22.write_text("requests>=2.28.0\nnumpy==1.24.0\n")
        deps22, has_pytest22, _ = inspect_requirements(req_file22)
        assert has_pytest22 is False
        assert len(deps22) == 2
        passed_count += 1
        print("✓ [22/25] requirements.txt missing pytest detected (has_pytest=False)")

        # -------------------------------------------------------------
        # Test 23: Malformed lines in requirements.txt
        # -------------------------------------------------------------
        req_file23 = temp_dir / "req23.txt"
        req_file23.write_text(
            "pytest>=7.0\n"
            "???invalid line!!\n"
            "   \n"
            "requests\n"
        )
        deps23, has_pytest23, warns23 = inspect_requirements(req_file23)
        assert has_pytest23 is True
        assert len(warns23) == 1, f"Expected 1 warning for malformed line, got {len(warns23)}"
        assert "line 2" in warns23[0]
        passed_count += 1
        print("✓ [23/25] Malformed lines in requirements.txt recorded as warnings without crashing")

        # -------------------------------------------------------------
        # Test 24: File exceeding size limit (> 1 MB) handled gracefully
        # -------------------------------------------------------------
        large_file = temp_dir / "huge_file.py"
        # Write 1.1 MB file
        with open(large_file, "wb") as f:
            f.write(b"# huge comment\n" * 80000)
        assert large_file.stat().st_size > MAX_INSPECT_FILE_SIZE
        tree24, err24 = check_ast_syntax(large_file, temp_dir)
        assert tree24 is None
        assert err24 is not None
        assert "exceeds maximum analysis inspection size" in err24.message
        passed_count += 1
        print("✓ [24/25] File exceeding 1 MB limit skipped safely without memory spike")

        # -------------------------------------------------------------
        # Test 25: Isolation verification (Code is NEVER executed)
        # -------------------------------------------------------------
        side_effect_sentinel = temp_dir / "side_effect_detected.txt"
        if side_effect_sentinel.exists():
            side_effect_sentinel.unlink()

        # Malicious Python file designed to execute harmful code if imported or run
        evil_py = temp_dir / "evil.py"
        evil_py.write_text(
            f"import os\n"
            f"open({repr(str(side_effect_sentinel))}, 'w').write('HACKED')\n"
            f"raise RuntimeError('MALICIOUS CODE EXECUTED!')\n"
        )
        # Static AST analysis
        tree25, err25 = check_ast_syntax(evil_py, temp_dir)
        # Verify ast parsed the syntax cleanly without running it
        assert tree25 is not None
        assert err25 is None
        # Verify the side-effect file was NOT created
        assert not side_effect_sentinel.exists(), "CRITICAL FAULT: Python code was executed during analysis!"
        # Verify module was not imported into sys.modules
        assert "evil" not in sys.modules, "Module was imported into sys.modules!"
        passed_count += 1
        print("✓ [25/25] Security Isolation Confirmed: Code was NOT executed, zero side-effects")

    # -------------------------------------------------------------
    # API Integration Tests (Authenticated HTTP Endpoint)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("API INTEGRATION TESTS: POST /api/projects/{id}/analyze")
    print("-" * 70)

    token1 = get_auth_token("ast_api1")
    token2 = get_auth_token("ast_api2")

    # Upload a valid ZIP project for user 1
    import zipfile
    import io

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("src/calc.py", "def multiply(a: int, b: int) -> int:\n    return a * b\n")
        zf.writestr("tests/test_calc.py", "def test_multiply():\n    assert 2 * 3 == 6\n")
        zf.writestr("requirements.txt", "pytest>=7.4.0\n")
        zf.writestr("README.md", "# Calculator API\n")
    zip_bytes = zip_buffer.getvalue()

    upload_res = client.post(
        "/api/projects/upload",
        files={"file": ("calc_proj.zip", zip_bytes, "application/zip")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
    proj_id = upload_res.json()["id"]

    # 1. Unauthenticated request -> 401
    unauth_res = client.post(f"/api/projects/{proj_id}/analyze")
    assert unauth_res.status_code == 401, f"Expected 401 Unauthenticated, got {unauth_res.status_code}"
    print("✓ [API 1/4] Unauthenticated POST /api/projects/{id}/analyze rejected with 401")

    # 2. Unauthorized cross-user access -> 403
    cross_user_res = client.post(
        f"/api/projects/{proj_id}/analyze",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert cross_user_res.status_code == 403, f"Expected 403 Forbidden, got {cross_user_res.status_code}"
    print("✓ [API 2/4] Cross-user unauthorized access rejected with 403")

    # 3. Non-existent project -> 404
    non_exist_res = client.post(
        "/api/projects/999999/analyze",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert non_exist_res.status_code == 404, f"Expected 404 Not Found, got {non_exist_res.status_code}"
    print("✓ [API 3/4] Non-existent project returns 404 Not Found")

    # 4. Authorized analysis -> 200 with complete response
    analyze_res = client.post(
        f"/api/projects/{proj_id}/analyze",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert analyze_res.status_code == 200, f"Analyze failed: {analyze_res.text}"
    data = analyze_res.json()
    assert data["project_id"] == proj_id
    assert data["structure_valid"] is True
    assert data["source_file_count"] == 1
    assert data["test_file_count"] == 1
    assert data["test_function_count"] == 1
    assert data["has_pytest"] is True
    assert data["syntax_error_count"] == 0
    print(f"✓ [API 4/4] Authorized static analysis succeeded for Project #{proj_id}: {data['test_function_count']} test candidates found")

    print("\n" + "=" * 70)
    print(f"ALL {passed_count}/{total_tests} DAY 7 UNIT TESTS + 4 API INTEGRATION TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
