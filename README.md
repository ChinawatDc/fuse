# fuse

[![skills.sh](https://skills.sh/b/ChinawatDc/fuse)](https://skills.sh/ChinawatDc/fuse)

**Circuit breaker for AI coding agents. Trips before tokens burn.**

When coding assistants hit a failing test or compilation error, they often enter a destructive trial-and-error thrash—blindly editing files, stacking broken patches, and burning tens of thousands of tokens without progress.

`fuse` acts as a hard circuit breaker with **error-tiered thresholds**. If attempts hit the tier limit, the circuit trips: the agent halts, records why previous attempts failed in a Negative Knowledge Ledger, and escalates to the human developer with structured strategic options.

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
                                 Stop Edits & Rollback    Present 2 Strategic Forks
                                                          & Await Human Direction
```

### 1. Zero-Overhead Dormant Mode
During normal development and passing tests, `fuse` stays dormant with ~0% prompt overhead. Full ledgering and escalation protocols activate only when commands fail (`exit code != 0` or stack trace detected).

### 2. Error-Tiered Attempt Thresholds
Different classes of errors warrant different tolerances:
* **Tier A (Syntax / Typing):** Up to **3 attempts** for shallow compiler issues and missing imports.
* **Tier B (Logic & Assertions):** Strictly **2 attempts** for test failures and contract drift.
* **Tier C (Environment & Infra):** **1 attempt (Instant Trip)** for connection refusals, 503s, missing environment variables, or OS permission limits—preventing futile code edits when the environment is the blocker.

### 3. Negative Knowledge Ledger
Instead of circular trial-and-error, `fuse` requires the agent to document:
* **Hypothesis:** What was assumed to be the cause.
* **Intervention:** What patch was applied.
* **Failure Evidence:** The exact failure message that disproved the hypothesis.
* **Exclusion:** Marks that approach as permanently exhausted.

### 4. Clean Rollback Discipline
Never stack new speculative code on top of failed experiments. If an attempt fails, clean up the diff to prevent cascading corruption across the codebase.

### 5. Structured Escalation
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
