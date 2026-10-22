---
name: fuse
version: v0.2.0
description: Circuit breaker for AI coding agents. Prevents trial-and-error looping, stops runaway token consumption, and enforces structured escalation after failed attempts.
---
# fuse (v0.2.0)

Circuit breaker for AI coding agents. Detects repetitive failure cycles, stops blind trial-and-error, and preserves context.

## 0. Dynamic Activation (Zero-Overhead on Happy Path)
- **Dormant Mode**: During routine development and passing tests, remain completely silent with zero prompt overhead.
- **Trigger**: Activate circuit monitoring only when a verification command, build step, or test suite fails (`exit code != 0` or traceback encountered).

## 1. Error-Tiered Attempt Thresholds
Never loop endlessly. Enforce strict attempt limits based on failure tier:

| Failure Tier | Symptoms | Max Attempts | Action Upon Limit |
|---|---|:---:|---|
| **Tier A: Syntax / Typing** | SyntaxError, missing imports, minor type mismatches | **3** | Trip if 3rd attempt fails |
| **Tier B: Logic & Assertions** | Test assertion failures, wrong calculation, contract drift | **2** | Trip if 2nd attempt fails |
| **Tier C: Environment / Infra** | Connection refused, 503, EACCES/PermissionDenied, missing env | **1** | **Trip immediately** (do not edit source code) |

### Attempt Accounting & Reset Policy
- **Attempt Definition**: One attempt is defined strictly as: `Hypothesis + Code Patch + Verification Run` failing on the same symptom fingerprint. Exploratory searches, greps, or reads do not count as attempts.
- **Reset on Progress**: If a verification run yields an entirely distinct error type or points to an unrelated downstream module (e.g. from `ImportError` to `TypeError`), reset the attempt counter (genuine progress was made).

## 2. Negative Knowledge Ledger
When a fix fails, explicitly record why it failed before trying another approach:
- **Hypothesis**: What was assumed to be the root cause?
- **Intervention**: What file/line was altered?
- **Failure Evidence**: What exact error, stack trace, or test assertion disproved the hypothesis?
- **Exclusion**: Mark this approach as permanently exhausted to prevent circular logic.

## 3. Mandatory Escalation Protocol
When the circuit trips (upon reaching the tier limit), emit a structured triage report and await user decision:

```markdown
⚡ [fuse: CIRCUIT TRIPPED]
Tier: <Tier A | Tier B | Tier C>
Symptom: <1-line summary of persistent error/failure>
Failed Attempts:
  1. <Attempt 1: Hypothesis + why it failed>
  2. <Attempt 2: Hypothesis + why it failed>

Underlying Bottleneck:
<Concise root-cause analysis: why this cannot be patched with superficial code edits>

Next Strategic Forks:
  [Option A]: <Architectural approach, e.g. refactor upstream schema or rewrite interface>
  [Option B]: <Alternative / Constraint adjustment, e.g. update test contract or mock dependency>

Decision Required: Which direction should we pursue?
```

## 4. Cascading Damage Prevention
- **Rollback Discipline**: If a failed attempt modified multiple files or introduced secondary errors, roll back immediately to the clean baseline. Never stack new speculative patches on top of dirty broken attempts.
- **Log Pruning**: Do not retain multi-page crash dumps from failed attempts in context; keep only the single actionable failure line in the Negative Knowledge Ledger.

## 5. False-Green Guard (Root-Cause Verification)
When a patch successfully passes verification:
- **Confirm Root Cause**: Ensure the test passed because the root mechanism was fixed, not by coincidence (e.g., arbitrarily shifting thresholds like `999` vs `>= 1000` or masking assertions).
- **Concise Confirmation**: State the verified root cause in one line upon completion.

