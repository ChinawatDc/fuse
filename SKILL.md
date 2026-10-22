---
name: fuse
version: v0.4.0
description: Circuit breaker for AI coding agents. Prevents trial-and-error looping, stops runaway token consumption, trims error dumps to root causes, and enforces clean auto-rollback and structured escalation after failed attempts.
---
# fuse (v0.4.0)

Circuit breaker for AI coding agents. Detects repetitive failure cycles, stops blind trial-and-error, prunes error context to root causes, enforces clean auto-rollback, and preserves context.

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
- **Failure Evidence**: What exact error, stack trace, or test assertion disproved the hypothesis? (Bounded strictly to `<= 2` lines; never paste multi-page logs).
- **Exclusion**: Mark this approach as permanently exhausted to prevent circular logic.

## 3. Context & Error Trimming (Root Extraction Only)
Never carry, quote, or reflect raw terminal dumps, multi-page stack traces, or verbose test diffs in working memory or thoughts.
- **Root Extraction Rule**: Strip all runtime/framework internal frames (`site-packages`, `node_modules`, standard library internals). Retain strictly:
  1. Root Exception & Message (`<ErrorClass>: <Message>`)
  2. Local Origin Frame (`<file>:<line>`)
- **Zero-Deliberation on Tier C**: When the root cause is environmental (EACCES/PermissionDenied, connection refused, offline service), immediately halt and trip. Do not deliberate bypassing permissions, chmodding files, or mocking unmockable resources.
- **Helper Utility**: When processing raw logs, you may pipe through or invoke `scripts/trim_error.py` to extract concise root causes.

## 4. Mandatory Escalation Protocol
When the circuit trips (upon reaching the tier limit), emit a structured triage report and await user decision:

```markdown
⚡ [fuse: CIRCUIT TRIPPED]
Tier: <Tier A | Tier B | Tier C>
Symptom: <1-line summary of persistent error/failure>
Failed Attempts:
  1. <Attempt 1: Hypothesis + root failure evidence (max 1 line)>
  2. <Attempt 2: Hypothesis + root failure evidence (max 1 line)>

Underlying Bottleneck:
<Concise root-cause analysis (max 3 lines): why code edits cannot fix this>

Next Strategic Forks:
  [Option A]: <Architectural / environment direction>
  [Option B]: <Alternative / contract direction>

Decision Required: Which direction should we pursue?
```

## 5. Auto-Rollback Discipline & Cascading Damage Prevention
- **Auto-Rollback on Trip**: When the circuit trips, the agent MUST immediately discard unverified speculative changes (`git restore .` or restoring touched files) before emitting the escalation report. Leaving half-baked patches in working tree is prohibited.
- **Attempt Cleanliness**: If a failed attempt modified files or caused secondary failures, roll back immediately to the clean baseline before attempting hypothesis 2. Never stack speculative patches on broken state.
- **Log Pruning**: Drop all verbose terminal logs from failed runs; carry only the compact Negative Knowledge Ledger.

## 6. False-Green Guard (Root-Cause Verification)
When a patch successfully passes verification:
- **Confirm Root Cause**: Ensure the test passed because the root mechanism was fixed, not by coincidence (e.g., arbitrarily shifting thresholds like `999` vs `>= 1000` or masking assertions).
- **Concise Confirmation**: State the verified root cause in one line upon completion.
