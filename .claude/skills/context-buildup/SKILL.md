---
name: context-buildup
description: Bootstrap session context by reading recent session learnings and project status. Accepts optional argument for number of sessions (default 3).
allowed-tools: Bash, Read, Glob, Grep
---

Build up context from recent session learnings so you understand the current state of the project without the user having to explain it.

## Arguments

- Optional: number of sessions to load (default: 3). Example: `/context-buildup 5`

## Steps

1. **Read project status** for current project state:
   ```
   Read .claude/project-status.md
   ```

2. **List session learning files** sorted by sequential number (descending):
   ```bash
   ls -1r claude_session_learnings/*.md 2>/dev/null | head -n <N>
   ```
   Where `<N>` is the argument passed (default 3). If no files exist, report that there are no session learnings yet and skip to step 5.

3. **Read each session file** — read all N files in parallel using the Read tool.

4. **Read MEMORY.md** to know what has already been promoted:
   ```
   Read .claude/projects/-Users-rahul-PycharmProjects-portfolio/memory/MEMORY.md
   ```

5. **Synthesize a smart summary** and print it directly to the conversation. Do NOT write any files. Use this exact output format:

```
## Context Briefing (Last N Sessions)

### Project Status
<Summarize current project state from project-status.md in 3-5 sentences>

### Recent Work
<Merged summary of what was accomplished across all loaded sessions. Deduplicate overlapping work. List as bullet points, most recent first. Include which session each item came from.>

### Active Decisions
<Decisions from recent sessions that are still relevant. Skip any that were superseded by later decisions. Show as a table:>
| Decision | Rationale | Session |
|----------|-----------|---------|

### Cumulative Unfinished Work
<Merge all unfinished work / TODOs from loaded sessions. Deduplicate. If a TODO from an earlier session was completed in a later session, mark it as done and note which session completed it.>
- [ ] Incomplete item (from session NNN)
- [x] ~~Completed item~~ (from session NNN, completed in session MMM)

### Active Learnings
<Merge learnings and mistake-prevention insights across sessions. Deduplicate. Focus on actionable patterns and conventions.>
- Learning or pattern to follow
- Mistake to avoid and why

### Unpromoted Memory Candidates
<Collect all Memory Promotion Candidates from loaded sessions. Cross-reference with MEMORY.md — only show items that have NOT already been added. If all candidates have been promoted, say so.>
> The following insights from recent sessions have not been added to MEMORY.md yet:
- Candidate item (from session NNN)
- Another candidate (from session MMM)
```

## Guidelines

- This skill is **read-only** — do NOT modify any files
- Be concise — the goal is to give useful context, not dump raw content
- When deduplicating, prefer the most recent/complete version of an item
- For unfinished work, actively check if later sessions resolved earlier TODOs
- If fewer than N session files exist, load whatever is available and note it
- If no session learning files exist at all, just print the project status section and note that no session learnings are available yet
- The summary should be useful as a starting point — after printing, ask the user what they want to work on this session
