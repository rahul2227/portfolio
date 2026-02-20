#!/bin/bash
# Block dangerous bash commands before they execute.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block destructive database commands
if echo "$COMMAND" | grep -qiE 'DROP (TABLE|DATABASE)|TRUNCATE'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive database commands are blocked. Use the /seed-db reset skill instead."
    }
  }'
  exit 0
fi

# Block force-push to main
if echo "$COMMAND" | grep -qE 'git push.*--force.*main|git push.*main.*--force'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Force-pushing to main is not allowed."
    }
  }'
  exit 0
fi

exit 0
