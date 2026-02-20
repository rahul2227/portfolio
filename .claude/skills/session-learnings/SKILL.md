---
name: session-learnings
description: Capture session insights, decisions, learnings, and subagent analysis into a structured markdown file. Run at end of session or anytime.
allowed-tools: Bash, Read, Glob, Grep, Write
---

Capture and save learnings from the current working session.

## Steps

1. **Detect file changes** — run these commands to understand what changed:
   ```bash
   git status --short
   git diff --stat HEAD
   ```

2. **Determine the next sequential number** — count existing files:
   ```bash
   ls claude_session_learnings/*.md 2>/dev/null | wc -l
   ```
   The next number is count + 1, zero-padded to 3 digits (e.g., `001`, `012`).

3. **Generate the filename** using format: `NNN_YYYY-MM-DD_HHMM_short-slug.md`
   - `NNN`: zero-padded sequential number
   - `YYYY-MM-DD`: today's date
   - `HHMM`: current time (24h)
   - `short-slug`: 2-4 word kebab-case summary of the session's primary work

   Get current date and time:
   ```bash
   date +"%Y-%m-%d_%H%M"
   ```

4. **Review the full conversation context** and extract insights across these categories:
   - What was accomplished (summary)
   - Files changed and why
   - Decisions made and alternatives that were considered
   - Learnings and discoveries
   - Subagent usage — which agents, what tasks, outcomes, and reasoning
   - Mistakes made and how they were corrected
   - Remaining unfinished work
   - Insights worth promoting to MEMORY.md

5. **Write the session file** to `claude_session_learnings/NNN_YYYY-MM-DD_HHMM_slug.md` using this exact template:

```markdown
# Session: YYYY-MM-DD — <Session Title>

## Summary
Brief 2-3 sentence overview of what was accomplished in this session.

## Files Changed
- `path/to/file.py` — What changed and why
- `path/to/other.ts` — What changed and why

## Decisions & Rationale
| Decision | Alternatives Considered | Why Chosen |
|----------|------------------------|------------|
| Choice made | Other options explored | Reasoning |

## Learnings
- Insight discovered during this session
- Another learning

## Subagent Analysis
| Agent | Task | Outcome | Notes |
|-------|------|---------|-------|
| agent-type | What it was asked to do | Success/Failed/Partial | Why this agent was chosen, what happened |

## Mistakes & Corrections
- **Mistake**: What went wrong
  - **Fix**: How it was corrected
  - **Prevention**: How to avoid this next time

## Unfinished Work
- [ ] Remaining TODO item
- [ ] Another item to pick up next session

## Memory Promotion Candidates
> These insights may be worth adding to MEMORY.md:
- Insight that should persist across sessions
- Pattern or convention discovered
```

6. **Report results** — print:
   - The file path that was created
   - The memory promotion candidates (so the user can decide whether to promote them)
   - If the session was trivial (no meaningful changes or learnings), say so and skip file creation

## Guidelines

- Be thorough in the subagent analysis — capture WHY each agent was chosen, not just what it did
- For decisions, always include at least one alternative that was considered (even if it was briefly dismissed)
- Only include sections that have content — skip empty sections rather than writing "None"
- The summary should be useful to someone reading it weeks later with no context
- For mistakes, focus on the prevention angle — what to do differently next time
- Memory promotion candidates should be things that are broadly applicable, not session-specific details
