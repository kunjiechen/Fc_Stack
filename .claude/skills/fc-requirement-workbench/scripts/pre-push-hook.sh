#!/usr/bin/env bash
# Pre-push hook: run fc-requirement-workbench regression pack + drift check.
#
# Install:
#   ln -sf ../../.claude/skills/fc-requirement-workbench/scripts/pre-push-hook.sh .git/hooks/pre-push
#
# Or use the install script:
#   bash .claude/skills/fc-requirement-workbench/scripts/install-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SKILL_ROOT="$REPO_ROOT/.claude/skills/fc-requirement-workbench"
REGRESSION_SCRIPT="$SKILL_ROOT/scripts/run_regression_pack.py"
DRIFT_CHECKER="$SKILL_ROOT/scripts/check_requirement_markdown.py"
GATE_CHECKER="$SKILL_ROOT/scripts/check_gate_regression.py"

echo "=== fc-requirement-workbench pre-push checks ==="

# Check if any requirement-workbench source files changed vs the remote tracking branch
REMOTE_BRANCH="$(git rev-parse --abbrev-ref --symbolic-full-name @{push} 2>/dev/null || echo 'origin/main')"
CHANGED_FILES="$(git diff --name-only "HEAD...$REMOTE_BRANCH" 2>/dev/null || git diff --name-only HEAD~1..HEAD)"

if [ -n "$CHANGED_FILES" ]; then
    RELEVANT=$(echo "$CHANGED_FILES" | grep -c '.claude/skills/fc-requirement-workbench/' || true)
    if [ "$RELEVANT" -eq 0 ]; then
        echo "No requirement-workbench files changed. Skipping checks."
        exit 0
    fi
fi

PYTHON=""
for candidate in python3.11 python3.10 python3.9 python3; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "WARNING: No Python found. Skipping regression checks."
    exit 0
fi

FAILURES=0

# 1. Gate regression (classification rules)
echo ""
echo "[1/3] Gate classification regression..."
if [ -f "$GATE_CHECKER" ]; then
    if "$PYTHON" "$GATE_CHECKER"; then
        echo "  PASS"
    else
        echo "  FAIL"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo "  SKIP (no gate checker)"
fi

# 2. Full regression pack (CI mode: expectations only, no byte-exact comparison)
echo ""
echo "[2/3] Regression pack (CI mode)..."
if "$PYTHON" "$REGRESSION_SCRIPT" --ci; then
    echo "  PASS"
else
    echo "  FAIL"
    FAILURES=$((FAILURES + 1))
fi

# 3. Drift check: verify SRS markdown matches requirement bundle
echo ""
echo "[3/3] Bundle↔SRS drift check..."
DRIFT_FAILURES=0
for bundle in "$REPO_ROOT"/artifacts/gp_*_requirement_bundle.yaml; do
    if [ ! -f "$bundle" ]; then
        continue
    fi
    base="$(basename "$bundle" _requirement_bundle.yaml)"
    # Derive SRS path from bundle name (module name in bundle)
    srs_candidate="$REPO_ROOT/artifacts/srs_${base}.md"
    if [ -f "$srs_candidate" ]; then
        if "$PYTHON" "$DRIFT_CHECKER" --bundle "$bundle" --srs "$srs_candidate" >/dev/null 2>&1; then
            echo "  PASS $srs_candidate"
        else
            echo "  FAIL $srs_candidate"
            DRIFT_FAILURES=$((DRIFT_FAILURES + 1))
        fi
    fi
done
if [ "$DRIFT_FAILURES" -gt 0 ]; then
    FAILURES=$((FAILURES + 1))
fi
if [ "$DRIFT_FAILURES" -eq 0 ]; then
    echo "  (no SRS markdown files to check)"
fi

echo ""
if [ "$FAILURES" -gt 0 ]; then
    echo "=== $FAILURES check(s) failed. Push aborted. ==="
    echo "Run manually for details:"
    echo "  $PYTHON $REGRESSION_SCRIPT"
    echo "  $PYTHON $DRIFT_CHECKER --bundle <bundle> --srs <srs>"
    exit 1
fi

echo "=== All checks passed ==="
exit 0
