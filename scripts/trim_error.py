#!/usr/bin/env python3
"""
fuse error trimmer:
Parses raw terminal/compiler/test output and extracts strictly:
1. Root Exception & Message
2. Immediate Local Application Frame (filtering out stdlib & site-packages)
3. Actionable failing statement

Outputs <= 3 lines, discarding all multi-page noise.
"""
import sys
import re

def is_internal_frame(filepath: str) -> bool:
    internal_keywords = [
        "site-packages",
        "dist-packages",
        "lib/python",
        "Frameworks/Python",
        "node_modules",
        "node:internal",
        "node:",
        "pytest/",
        "_pytest/",
        "pluggy/",
        "/usr/",
        "/opt/homebrew/Cellar",
        "go/src/runtime",
    ]
    return any(k in filepath for k in internal_keywords)

def trim_error_text(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return "No error output detected."

    # 1. Check for Python Traceback
    if "Traceback (most recent call last):" in text or any(l.startswith("  File ") for l in lines):
        root_error = ""
        app_frame = ""
        failing_code = ""

        # Bottom-most line is usually the Exception: message
        for l in reversed(lines):
            if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception|Exit|Interrupt|Fault|Warning):", l) or "AssertionError" in l:
                root_error = l.strip()
                break
        if not root_error and lines:
            root_error = lines[-1].strip()

        # Find candidate frames
        file_pattern = re.compile(r'^\s*File "([^"]+)", line (\d+)(?:, in (.+))?')
        candidate_frames = []
        for i, l in enumerate(lines):
            m = file_pattern.match(l)
            if m:
                filepath, lineno, func = m.group(1), m.group(2), m.group(3) or "module"
                code_line = lines[i+1].strip() if i+1 < len(lines) and not lines[i+1].startswith("  File ") else ""
                candidate_frames.append((filepath, lineno, func, code_line))

        user_frames = [f for f in candidate_frames if not is_internal_frame(f[0])]
        chosen_frame = user_frames[-1] if user_frames else (candidate_frames[-1] if candidate_frames else None)

        if chosen_frame:
            fp, ln, fn, code = chosen_frame
            app_frame = f"{fp}:{ln} (in {fn})"
            failing_code = code

        result = [f"[Root Error]: {root_error}"]
        if app_frame:
            result.append(f"[Culprit Frame]: {app_frame}")
        if failing_code and failing_code != root_error:
            result.append(f"[Failing Code]: {failing_code}")
        return "\n".join(result)

    # 2. Check for Pytest Failure format (e.g. E       AssertionError: assert ...)
    pytest_errors = [l for l in lines if l.startswith("E   ")]
    if pytest_errors:
        clean_errors = [l.replace("E   ", "").strip() for l in pytest_errors]
        # Look for the primary assertion line
        primary_assert = next((e for e in clean_errors if "AssertionError" in e or "assert " in e), clean_errors[0])
        details = [e for e in clean_errors if e != primary_assert]
        res = [f"[Pytest Failure]: {primary_assert}"]
        if details:
            res.append(f"[Details]: {' '.join(details)}")
        return "\n".join(res)

    # 3. Check for Node.js / JavaScript Error
    node_err_match = None
    node_frames = []
    for l in lines:
        if re.match(r"^[A-Za-z]*Error: ", l) and not node_err_match:
            node_err_match = l.strip()
        elif "at " in l:
            node_frames.append(l.strip())

    if node_err_match:
        user_node_frames = [f for f in node_frames if not is_internal_frame(f)]
        chosen_frame = user_node_frames[0] if user_node_frames else (node_frames[0] if node_frames else None)
        res = [f"[Root Error]: {node_err_match}"]
        if chosen_frame:
            res.append(f"[Culprit Frame]: {chosen_frame.replace('at ', '')}")
        return "\n".join(res)

    # 4. Check for Permission Denied / EACCES / OS Error
    for l in lines:
        if any(err_kw in l.lower() for err_kw in ["permission denied", "eacces", "operation not permitted", "connection refused", "503 service unavailable"]):
            return f"[Infra/Env Error]: {l.strip()}"

    # 5. Fallback: Last 3 lines
    tail = lines[-3:] if len(lines) > 3 else lines
    return "[Trimmed Output]:\n" + "\n".join(f"  {l}" for l in tail)

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    print(trim_error_text(content))

if __name__ == "__main__":
    main()
