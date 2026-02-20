#!/bin/bash
# Auto-lint files after Claude edits them.
# Feeds lint errors back as a system message so Claude can fix them.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Python files: run ruff
if [[ "$FILE_PATH" == *.py ]]; then
  RESULT=$(cd backend && uv run ruff check "$FILE_PATH" 2>&1)
  if [[ $? -ne 0 ]]; then
    echo "{\"systemMessage\": \"Ruff lint errors in $FILE_PATH:\\n$RESULT\"}"
  fi
  exit 0
fi

# TypeScript/JSX files: run eslint
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx ]]; then
  RESULT=$(cd frontend && npx eslint "$FILE_PATH" 2>&1)
  if [[ $? -ne 0 ]]; then
    echo "{\"systemMessage\": \"ESLint errors in $FILE_PATH:\\n$RESULT\"}"
  fi
  exit 0
fi

exit 0
