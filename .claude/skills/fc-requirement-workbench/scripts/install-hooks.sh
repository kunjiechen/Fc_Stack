#!/usr/bin/env bash
# Install git hooks for fc-requirement-workbench regression checks.
#
# Usage:
#   bash .claude/skills/fc-requirement-workbench/scripts/install-hooks.sh
#
# This creates symlinks in .git/hooks/ pointing to the hook scripts in this directory.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SKILL_SCRIPTS="$REPO_ROOT/.claude/skills/fc-requirement-workbench/scripts"

echo "Installing fc-requirement-workbench hooks..."

# pre-push: run regression pack before pushing
ln -sf "../../.claude/skills/fc-requirement-workbench/scripts/pre-push-hook.sh" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

echo "Installed: pre-push -> pre-push-hook.sh"
echo "Done. Hooks will run automatically on the next push."
