# Session: 2026-02-20 — Build Claude Code Skills & Hooks Tooling

## Summary
Designed and built three Claude Code skills for session workflow management: `/session-learnings` (captures session insights), `/context-buildup` (bootstraps new sessions from recent learnings), and updated `/deploy` (environment-aware deployment for Pi and local MacBook). Also configured hooks for session start/stop reminders.

## Files Changed
- `.claude/skills/session-learnings/SKILL.md` — New skill that extracts session insights (decisions, learnings, subagent analysis, mistakes) into structured markdown files in `claude_session_learnings/`
- `.claude/skills/context-buildup/SKILL.md` — New skill that reads the last N session learning files + project-status.md, synthesizes a smart summary, and prints it to bootstrap a new session's context
- `.claude/skills/deploy/SKILL.md` — Rewrote deploy skill to support three modes: `/deploy pi` (production on Raspberry Pi), `/deploy local` (dev servers with HMR), `/deploy local prod` (production-like local build)
- `.claude/settings.json` — Added `SessionStart` hook (reminder to run `/context-buildup`) and `Stop` hook (reminder to run `/session-learnings`)
- `claude_session_learnings/.gitkeep` — Created output directory for session learning files (git-tracked)

## Decisions & Rationale
| Decision | Alternatives Considered | Why Chosen |
|----------|------------------------|------------|
| Single file per session for learnings | Split by category files, or both combined | Easier to browse chronologically, keeps related context together |
| Print context-buildup to conversation (not file) | Write to temp file, update project-status.md | Immediate absorption by Claude, no file clutter, read-only is safer |
| Smart summary for context-buildup (not raw dump) | Full verbatim content, key sections only | Deduplicates across sessions, more concise, highlights what's still relevant |
| Always require target argument for deploy | Auto-detect via hostname/uname/systemd | User explicitly chose "always ask" — avoids misdetection since both Pi and Mac are ARM |
| Foreground with interleaved logs for local deploy | Background + health check, background + print URLs | User can see all service output, Ctrl+C cleanly kills everything via trap |
| Delegate Pi deploy to existing deploy.sh | Inline all steps in SKILL.md | deploy.sh is already well-structured with colors, retries, and error handling |
| Session learnings are git-tracked | Gitignored (local only), separate branch | Creates a searchable knowledge base that persists with the repo |

## Learnings
- Claude Code skills use SKILL.md files in `.claude/skills/<name>/` with YAML frontmatter for metadata
- Hook events available: `SessionStart`, `Stop`, `PreToolUse`, `PostToolUse` — Stop fires when Claude finishes responding
- Settings.json validates against a strict JSON schema — escaped characters like `\n` in echo commands cause JSON parse failures
- The `disable-model-invocation: true` frontmatter option exists for skills that are pure bash scripts (no LLM reasoning needed)
- Write tool fails validation on settings.json edits if the resulting JSON is malformed — acts as a safety net

## Subagent Analysis
| Agent | Task | Outcome | Notes |
|-------|------|---------|-------|
| N/A — no subagents used | — | — | All work was done in the main conversation. Skills are prompt files, not code — no need for specialized agents. The brainstorming/Q&A flow with AskUserQuestion was more appropriate than delegating to subagents. |

## Mistakes & Corrections
- **Mistake**: First attempt to edit settings.json with a `Stop` hook used `\n` in the echo command string, which broke JSON parsing
  - **Fix**: Used plain single-quoted string without escape characters
  - **Prevention**: Avoid escape sequences in JSON string values for hook commands — use simple strings or move complex logic to a shell script
- **Mistake**: Edit tool's `old_string` matched ambiguously (the closing `}` appeared multiple times in the JSON)
  - **Fix**: Used Write tool to rewrite the entire file with the new hook added
  - **Prevention**: For JSON config files with repetitive structure, prefer Write over Edit when adding new sections to avoid ambiguous matches

## Unfinished Work
- [ ] Test `/session-learnings` skill end-to-end (this is the first real run)
- [ ] Test `/context-buildup` skill in a fresh session
- [ ] Test `/deploy local` and `/deploy local prod` on MacBook
- [ ] Add new demos to the local deploy modes as they are created (EEG, Chatbot, Bomberman)
- [ ] Consider whether memory promotion candidates should auto-diff against MEMORY.md to avoid suggesting already-promoted items

## Memory Promotion Candidates
> These insights may be worth adding to MEMORY.md:
- Claude Code skills live in `.claude/skills/<name>/SKILL.md` with YAML frontmatter (name, description, allowed-tools)
- Hook events: SessionStart, Stop, PreToolUse, PostToolUse — configured in `.claude/settings.json` under `hooks`
- Avoid escape sequences in JSON hook command strings — use simple quotes or delegate to shell scripts
- When editing JSON config files with repetitive structure, prefer Write over Edit to avoid ambiguous old_string matches
