# Changelog

All notable changes to `fuse` will be documented in this file.

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
