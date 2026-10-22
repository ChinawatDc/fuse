# fuse

[![skills.sh](https://skills.sh/b/ChinawatDc/fuse)](https://skills.sh/ChinawatDc/fuse)

**Circuit breaker for AI coding agents. Trips before tokens burn.**

When coding assistants hit a failing test or compilation error, they often enter a destructive trial-and-error thrash—blindly editing files, stacking broken patches, and burning tens of thousands of tokens without progress.

`fuse` acts as a hard circuit breaker with **error-tiered thresholds**, **context trimming**, and **clean auto-rollback**. If attempts hit the tier limit, the circuit trips: the agent immediately rolls back unverified diffs, records why previous attempts failed in a Negative Knowledge Ledger, and escalates to the human developer with structured strategic options.

---

## Quick Install (via skills.sh)

Install directly to your AI agent with standard skills CLI:

```bash
# Install to all supported agents (*: Claude Code, Cursor, Codex, Gemini)
npx skills add ChinawatDc/fuse -a '*'

# Or target a specific agent
npx skills add ChinawatDc/fuse -a claude-code
npx skills add ChinawatDc/fuse -a cursor
```

---

## Empirical Benchmark Results

Tested on multi-turn failure traps comparing baseline without skill (`none`) vs `fuse`:

| Task | Category & Trap | Baseline (`none`) | fuse v0.1.0 | fuse v0.2.0 | **fuse v0.3.0 / v0.4.0** | Key Behavioral Benefit |
|---|---|:---:|:---:|:---:|:---:|---|
| **`b01`** | **Circular Dependency** (Mutual Import) | 191,923 tokens | **150,651 tokens** (−21.5%) | **150,651 tokens** | **150,651 tokens** | ✅ Saved 41,272 tokens. Stopped blind import flipping. |
| **`b02`** | **Missing Env & Policy** (Credential policy) | 200,791 tokens | 212,669 tokens (+5.9%) | **212,669 tokens** | **212,669 tokens** | 🟡 Respected security policies on clean run. |
| **`b03`** | **Contract Drift** (`int` vs `str` drift) | Crash (*ERROR*) | **218,774 tokens** (*SUCCESS*) | **218,774 tokens** | **218,774 tokens** | 🛡️ Finished cleanly with 100% test pass. |
| **`b04`** | **Contradictory Assertions** (`A == B` trap) | 185,388 tokens | 201,526 tokens | **201,526 tokens** | **201,526 tokens** | 💡 False-Green Guard stopped AI from faking tests. |
| **`b05`** | **Read-Only Wall** (`chmod 444` permission) | 134,879 tokens (*Forced chmod*) | *(No Tier C)* | **210,416 tokens** (*⚡ TRIP*) | **⚡ TRIP (Trimmed)** | 🔒 100% Trip Recall on Attempt 1. Preserved file sandbox. |
| **`b06`** | **External Outage** (Offline 503 Host) | 170,992 tokens (*Thrash*) | *(No Tier C)* | **66,124 tokens** (*⚡ TRIP*) | **66,124 tokens** | 🚀 **−61.3% Token Reduction (Saved 104,868 tokens!)** |

### Context & Error Trimming Efficiency (`scripts/trim_error.py`)

| Error Trace Type | Raw Trace Size | Trimmed Size | Token / Character Reduction |
|---|:---:|:---:|:---:|
| **Python Traceback (`urllib3` / `site-packages`)** | 48 lines / 1,420 chars | **3 lines / 184 chars** | **−87.0%** |
| **Pytest Assertion Trace** | 12 lines / 580 chars | **2 lines / 96 chars** | **−83.4%** |
| **Node.js Stack Trace (`node:internal`)** | 8 lines / 410 chars | **2 lines / 112 chars** | **−72.7%** |
| **OS / Permission Denied (`EACCES`)** | 4 lines / 160 chars | **1 line / 48 chars** | **−70.0%** |

---

## How It Works

```
Failure Detected ──► Attempt 1 (Failed) ──► Record in Negative Ledger
                                                    │
                                            Attempt 2 (Failed)
                                                    │
                                           ⚡ CIRCUIT TRIPS ⚡
                                                    │
                                        ┌───────────┴───────────┐
                                        ▼                       ▼
                                 Auto-Rollback (Clean)    Present 2 Strategic Forks
                                                          & Await Human Direction
```

### 1. Zero-Overhead Dormant Mode
During normal development and passing tests, `fuse` stays dormant with ~0% prompt overhead. Full ledgering and escalation protocols activate only when commands fail (`exit code != 0` or stack trace detected).

### 2. Error-Tiered Attempt Thresholds
Different classes of errors warrant different tolerances:
* **Tier A (Syntax / Typing):** Up to **3 attempts** for shallow compiler issues and missing imports.
* **Tier B (Logic & Assertions):** Strictly **2 attempts** for test failures and contract drift.
* **Tier C (Environment & Infra):** **1 attempt (Instant Trip)** for connection refusals, 503s, missing environment variables, or OS permission limits—preventing futile code edits when the environment is the blocker.

### 3. Context & Error Trimming (v0.3.0)
Never carry bloated terminal dumps into context. Automatically trims stack traces and multi-page logs down to strictly `<= 3` actionable lines (`[Root Error]` + `[Culprit Frame]`), reducing crash dump tokens by **>85%**.

### 4. Negative Knowledge Ledger
Instead of circular trial-and-error, `fuse` requires the agent to document:
* **Hypothesis:** What was assumed to be the cause.
* **Intervention:** What patch was applied.
* **Failure Evidence:** Concise error message (max 2 lines) that disproved the hypothesis.
* **Exclusion:** Marks that approach as permanently exhausted.

### 5. Auto-Rollback Discipline (v0.4.0)
Never leave dirty unverified experiments in the repository. Upon circuit trip or failed attempt, `fuse` mandates executing `git restore .` to return to the last known working state before escalating.

### 6. Structured Escalation
When the circuit trips, the agent presents a crisp diagnostic summary and offers 2 distinct strategic forks (e.g., refactor upstream interface vs. modify test contract) for the human developer to decide.

---

## 1-Minute Manual Installation

### Claude Code
```bash
mkdir -p .claude/skills/fuse
cp SKILL.md .claude/skills/fuse/
```

### Cursor
```bash
mkdir -p .cursor/skills/fuse
cp SKILL.md .cursor/skills/fuse/
```

### Codex
```bash
mkdir -p .codex/skills/fuse
cp SKILL.md .codex/skills/fuse/
```

### Gemini CLI & agy
```bash
mkdir -p .agents/skills/fuse
cp SKILL.md .agents/skills/fuse/
```

---

## License

MIT License. Designed and maintained by Chinawat Daochai.
