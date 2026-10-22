import unittest
from scripts.trim_error import trim_error_text

class TestTrimError(unittest.TestCase):
    def test_python_traceback_with_site_packages(self):
        raw = """Traceback (most recent call last):
  File "/opt/homebrew/lib/python3.11/site-packages/urllib3/connectionpool.py", line 714, in urlopen
    httplib_response = self._make_request(conn, method, url, ...)
  File "/workspace/payment_gateway.py", line 14, in charge
    response = urllib.request.urlopen(req)
  File "/opt/homebrew/Cellar/python@3.11/3.11.8/Frameworks/Python.framework/Versions/3.11/lib/python3.11/urllib/request.py", line 216, in urlopen
    return opener.open(url, data, timeout)
urllib.error.URLError: <urlopen error [Errno 61] Connection refused>
"""
        trimmed = trim_error_text(raw)
        self.assertIn("[Root Error]: urllib.error.URLError: <urlopen error [Errno 61] Connection refused>", trimmed)
        self.assertIn("/workspace/payment_gateway.py:14 (in charge)", trimmed)
        self.assertNotIn("connectionpool.py", trimmed)
        self.assertLessEqual(len(trimmed.splitlines()), 3)

    def test_pytest_assertion(self):
        raw = """________________________________ test_discount _________________________________
    def test_discount():
>       assert calculate_discount(1000) == 950.0
E       AssertionError: assert 1000 == 950.0
E       +  where 1000 = calculate_discount(1000)
test_app.py:8: AssertionError
=========================== short test summary info ============================
FAILED test_app.py::test_discount - AssertionError: assert 1000 == 950.0
============================== 1 failed in 0.05s ===============================
"""
        trimmed = trim_error_text(raw)
        self.assertIn("[Pytest Failure]: AssertionError: assert 1000 == 950.0", trimmed)
        self.assertLessEqual(len(trimmed.splitlines()), 3)

    def test_node_stack_trace(self):
        raw = """Error: connect ECONNREFUSED 127.0.0.1:5432
    at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1607:16)
    at /Users/dev/app/src/db.ts:42:15
"""
        trimmed = trim_error_text(raw)
        self.assertIn("[Root Error]: Error: connect ECONNREFUSED 127.0.0.1:5432", trimmed)
        self.assertIn("/Users/dev/app/src/db.ts:42:15", trimmed)
        self.assertLessEqual(len(trimmed.splitlines()), 3)

    def test_permission_denied(self):
        raw = """bash: line 1: ./config.json: Permission denied"""
        trimmed = trim_error_text(raw)
        self.assertIn("Permission denied", trimmed)
        self.assertLessEqual(len(trimmed.splitlines()), 2)

    def test_go_build_failure(self):
        raw = """# myapp/pkg/auth
pkg/auth/jwt.go:28:12: undefined: GenerateToken
pkg/auth/jwt.go:35:5: cannot use token (variable of type string) as type []byte
"""
        trimmed = trim_error_text(raw)
        self.assertIn("[Trimmed Output]:", trimmed)
        self.assertIn("cannot use token", trimmed)
        self.assertLessEqual(len(trimmed.splitlines()), 4)

    def test_token_efficiency_reduction(self):
        # Measure token reduction on a real 50-line traceback
        huge_trace = "Traceback (most recent call last):\n" + "\n".join(
            f'  File "/site-packages/lib{i}.py", line {i*10}, in run\n    do_internal_work()' for i in range(25)
        ) + '\n  File "app.py", line 99, in main\n    crash()\nValueError: invalid literal'
        
        trimmed = trim_error_text(huge_trace)
        self.assertIn("[Root Error]: ValueError: invalid literal", trimmed)
        self.assertIn("app.py:99", trimmed)
        # Reduction ratio must be at least 80%
        raw_char_count = len(huge_trace)
        trimmed_char_count = len(trimmed)
        reduction_pct = (raw_char_count - trimmed_char_count) / raw_char_count * 100
        self.assertGreater(reduction_pct, 85.0)

if __name__ == "__main__":
    unittest.main()
