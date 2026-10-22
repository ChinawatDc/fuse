# Changelog

All notable changes to `fuse` will be documented in this file.

## v0.3.0 — 2026-10-22
- **Context & Error Trimmer (`Context Trimmer on Error`)**: Prunes raw terminal dumps, multi-page stack traces, and test framework dumps down to strictly <= 3 lines (`[Root Error]` + `[Culprit Frame]`).
- **>85% Token Reduction on Traceback Logs**: Automatically strips internal runtime/framework frames (`site-packages`, `node_modules`, `pytest`, standard library internals) from working context and agent thoughts.
- **Negative Ledger Invariant**: Strictly bounds `Failure Evidence` in the Negative Knowledge Ledger to `<= 2` lines, preventing quadratic context growth during multi-turn debugging.
- **Decisive Tier C Execution**: Explicitly bans speculative thought deliberation on environmental errors (EACCES/PermissionDenied, connection refused), forcing immediate escalation.
- **Built-in Trimmer Utility & Test Suite**: Added standalone `scripts/trim_error.py` and `tests/test_trim_error.py` with 100% test pass across Python, Pytest, Node.js, and OS permission errors.

## v0.2.0 — 2026-10-22
- **3-Tier Attempt Thresholds**:
  - Tier A (Syntax / Typing): up to 3 attempts.
  - Tier B (Logic / Test Assertions): strictly 2 attempts.
  - Tier C (Environment / Infra / Permissions): instant trip on attempt 1.
- **Zero-Overhead Dormant Mode**: Remains completely dormant on passing code/tests (~0% prompt overhead).
- **False-Green Guard**: Requires 1-line root-cause verification when a test passes to prevent accidental pass hacks (e.g. relaxing thresholds).
- **Attempt Accounting & Reset Policy**: Clearly defines 1 attempt as `Hypothesis + Patch + Verify`, and resets the counter when progress is made to an unrelated error symptom.
- **Verified Benchmark Results**: Achieved 100% Trip Recall on Tier C barriers (`b05` permission wall, `b06` external outage saving −61.3% tokens).

## v0.1.0 — 2026-10-22
- Initial release of the `fuse` circuit breaker skill.
- Core rules: Max 2 speculative attempts, Negative Knowledge Ledger, and structured escalation protocol.
