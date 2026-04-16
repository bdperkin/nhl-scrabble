# Wait for CI

______________________________________________________________________

## title: 'Wait for CI/CD Checks' read_only: false type: 'command'

Monitor and wait for GitHub Actions CI/CD checks to complete on a pull request.

## Process

This command monitors PR checks until all pass, fail, or timeout:

1. **Validate PR Number**

   - Verify PR exists
   - Check PR is not already merged
   - Get current check status

1. **Monitor Checks**

   - Poll `gh pr checks` at regular intervals
   - Count passed, pending, and failed checks
   - Detect when all checks complete
   - Display progress updates

1. **Determine Outcome**

   - **All Pass**: Exit success (0)
   - **Any Fail**: Exit failure (1) with details
   - **Timeout**: Exit timeout (2) with status

1. **Report Results**

   - Show final status
   - List any failed checks
   - Show total duration
   - Provide next steps

## Detection Logic

**Check Status Values** (from `gh pr checks`):

- `pass` - Check passed successfully
- `fail` or `failure` - Check failed
- `pending` - Check still running
- `skipped` - Check was skipped
- `neutral` - Check completed but neutral status

**Completion Detection**:

```bash
# Count checks by status
PASSED=$(gh pr checks <pr> 2>&1 | grep -c "pass")
FAILED=$(gh pr checks <pr> 2>&1 | grep -cE "fail|failure")
PENDING=$(gh pr checks <pr> 2>&1 | grep -c "pending")

# All complete when no pending checks
if [ $PENDING -eq 0 ]; then
  if [ $FAILED -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
  else
    echo "❌ $FAILED check(s) failed"
    exit 1
  fi
fi
```

## Usage

```bash
# Wait for PR checks (default: 30 min timeout, 30s interval)
/wait-for-ci 53

# Custom timeout (seconds)
/wait-for-ci 53 --timeout 3600

# Custom poll interval (seconds)
/wait-for-ci 53 --interval 15

# Quiet mode (minimal output)
/wait-for-ci 53 --quiet

# Verbose mode (show all check details)
/wait-for-ci 53 --verbose
```

## Examples

### Basic Usage

```bash
# Monitor PR #53
/wait-for-ci 53

# Output:
# ⏳ Waiting for CI checks on PR #53...
# [1/60] Still running... (12/35 passed, 23 pending)
# [2/60] Still running... (28/35 passed, 7 pending)
# [3/60] Still running... (34/35 passed, 1 pending)
# ✅ All 35 checks passed! (Duration: 1m 45s)
```

### With Failure

```bash
# Monitor PR with failing check
/wait-for-ci 54

# Output:
# ⏳ Waiting for CI checks on PR #54...
# [1/60] Still running... (15/35 passed, 20 pending)
# [2/60] Still running... (33/35 passed, 2 pending)
# ❌ 2 check(s) failed:
#   - Test on Python 3.12: https://github.com/.../actions/runs/...
#   - Tox tests with UV (mypy): https://github.com/.../actions/runs/...
```

### Timeout

```bash
# Monitor with 5 minute timeout
/wait-for-ci 53 --timeout 300

# Output:
# ⏳ Waiting for CI checks on PR #53...
# [1/10] Still running... (12/35 passed, 23 pending)
# ...
# ⏱️  Timeout after 5 minutes
# Status: 30/35 passed, 5 pending
# Pending checks:
#   - Tox tests with UV (coverage)
#   - Tox tests with UV (mypy)
#   ...
```

## Script Implementation

**Location**: `.github/scripts/wait-for-ci.sh`

```bash
#!/usr/bin/env bash
# Wait for GitHub Actions CI/CD checks to complete

set -e

# Configuration
PR_NUMBER="$1"
TIMEOUT="${2:-1800}"  # Default: 30 minutes
INTERVAL="${3:-30}"   # Default: 30 seconds
QUIET="${QUIET:-false}"
VERBOSE="${VERBOSE:-false}"

# Validate PR number
if [ -z "$PR_NUMBER" ]; then
  echo "❌ Error: PR number required"
  echo "Usage: $0 <pr-number> [timeout] [interval]"
  exit 1
fi

# Check PR exists
if ! gh pr view "$PR_NUMBER" &>/dev/null; then
  echo "❌ Error: PR #$PR_NUMBER not found"
  exit 1
fi

# Start monitoring
START_TIME=$(date +%s)
MAX_ITERATIONS=$((TIMEOUT / INTERVAL))
ITERATION=0

echo "⏳ Waiting for CI checks on PR #$PR_NUMBER..."
echo "   Timeout: ${TIMEOUT}s, Interval: ${INTERVAL}s"
echo ""

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
  ITERATION=$((ITERATION + 1))

  # Get check status
  STATUS=$(gh pr checks "$PR_NUMBER" 2>&1)

  # Count by status (FIX: use "pass" not "success")
  PASSED=$(echo "$STATUS" | grep -c "pass" || true)
  FAILED=$(echo "$STATUS" | grep -cE "fail|failure" || true)
  PENDING=$(echo "$STATUS" | grep -c "pending" || true)
  TOTAL=$((PASSED + FAILED + PENDING))

  # Check for completion
  if [ "$PENDING" -eq 0 ]; then
    ELAPSED=$(($(date +%s) - START_TIME))
    DURATION=$(printf "%dm %ds" $((ELAPSED / 60)) $((ELAPSED % 60)))

    if [ "$FAILED" -eq 0 ]; then
      echo ""
      echo "✅ All $PASSED checks passed! (Duration: $DURATION)"
      echo ""

      if [ "$VERBOSE" = "true" ]; then
        echo "Passed checks:"
        echo "$STATUS" | grep "pass" | head -10
        echo ""
      fi

      exit 0
    else
      echo ""
      echo "❌ $FAILED check(s) failed:"
      echo "$STATUS" | grep -E "fail|failure"
      echo ""
      echo "Duration: $DURATION"
      exit 1
    fi
  fi

  # Progress update
  if [ "$QUIET" != "true" ]; then
    echo "[$ITERATION/$MAX_ITERATIONS] Still running... ($PASSED/$TOTAL passed, $PENDING pending)"
  fi

  # Show verbose details
  if [ "$VERBOSE" = "true" ]; then
    echo "  Pending:"
    echo "$STATUS" | grep "pending" | head -5
    echo ""
  fi

  sleep "$INTERVAL"
done

# Timeout
ELAPSED=$(($(date +%s) - START_TIME))
DURATION=$(printf "%dm %ds" $((ELAPSED / 60)) $((ELAPSED % 60)))

echo ""
echo "⏱️  Timeout after $DURATION"
echo "Status: $PASSED/$TOTAL passed, $PENDING pending"
echo ""
echo "Pending checks:"
echo "$STATUS" | grep "pending"
echo ""
echo "Re-run: gh run watch \$(gh run list --branch <branch> --limit 1 --json databaseId -q '.[0].databaseId')"

exit 2
```

## Configuration

### Environment Variables

```bash
# Quiet mode (minimal output)
export QUIET=true

# Verbose mode (detailed check info)
export VERBOSE=true

# Custom timeout (seconds)
export CI_WAIT_TIMEOUT=3600

# Custom poll interval (seconds)
export CI_POLL_INTERVAL=15
```

### Per-Repository Settings

Add to `.github/ci-wait.conf`:

```ini
# Default timeout (seconds)
TIMEOUT=1800

# Poll interval (seconds)
INTERVAL=30

# Show progress (true/false)
SHOW_PROGRESS=true

# Exit on first failure (true/false)
FAIL_FAST=false
```

## Integration

### With PR Creation

```bash
# Create PR and wait for CI
gh pr create --fill
PR_NUMBER=$(gh pr view --json number -q '.number')
/wait-for-ci "$PR_NUMBER"
```

### With Merge Workflow

```bash
# Wait for CI, then merge
/wait-for-ci 53 && gh pr merge 53 --squash
```

### In Scripts

```bash
#!/bin/bash

# Create PR
gh pr create --title "Fix bug" --body "Details..."
PR_NUM=$(gh pr view --json number -q '.number')

# Wait for CI (custom timeout)
if .github/scripts/wait-for-ci.sh "$PR_NUM" 600 15; then
  echo "CI passed, merging..."
  gh pr merge "$PR_NUM" --squash
else
  echo "CI failed, please review"
  exit 1
fi
```

## Error Handling

### PR Not Found

```
❌ Error: PR #999 not found

Verify:
- PR number is correct
- PR exists in repository
- You have access to repository
```

### Check Failures

```
❌ 2 check(s) failed:
  - Test on Python 3.12: https://...
  - Tox tests with UV (mypy): https://...

Next steps:
1. Review failure logs: gh run view <run-id> --log-failed
2. Fix issues locally
3. Push fixes: git push
4. Re-run: /wait-for-ci 53
```

### Timeout

```
⏱️  Timeout after 30m 0s
Status: 32/35 passed, 3 pending

Pending checks:
  - Tox tests with UV (coverage)
  - Tox tests with UV (interrogate)
  - Tox tests with UV (mypy)

Options:
1. Continue waiting: /wait-for-ci 53 --timeout 3600
2. Check status manually: gh pr checks 53
3. Cancel run: gh run cancel <run-id>
```

## Best Practices

1. **Set reasonable timeouts**

   - Most CI: 5-15 minutes
   - Heavy tests: 30 minutes
   - Integration tests: 60 minutes

1. **Use appropriate intervals**

   - Fast CI: 15 seconds
   - Normal CI: 30 seconds
   - Slow CI: 60 seconds

1. **Monitor in background**

   - For long-running CI, use background monitoring
   - Continue other work while waiting
   - Get notified on completion

1. **Handle failures gracefully**

   - Don't auto-merge on CI failure
   - Review failure logs
   - Fix and re-run

1. **Check before merging**

   - Always verify CI passed
   - Check for required approvals
   - Verify no merge conflicts

## Troubleshooting

### Script exits immediately

```bash
# Check PR exists
gh pr view 53

# Check checks are running
gh pr checks 53

# Verbose mode for debugging
VERBOSE=true /wait-for-ci 53
```

### Wrong check count

```bash
# View raw output
gh pr checks 53

# Count manually
gh pr checks 53 | grep -c "pass"
gh pr checks 53 | grep -c "pending"
```

### Checks stuck pending

```bash
# View workflow runs
gh run list --branch feature/branch

# Check specific run
gh run view <run-id>

# Re-run failed jobs
gh run rerun <run-id>
```

## Related Commands

- `/gh:create-pr` - Create pull request
- `/gh:merge-pr` - Merge pull request
- `/gh:pr-status` - Check PR status
- `/implement-task` - Uses this for CI monitoring

## Notes

- **Critical fix**: Use `grep "pass"` not `grep "success"`
- GitHub Actions uses "pass" for successful checks
- Exit codes: 0 = success, 1 = failure, 2 = timeout
- Background monitoring available via `run_in_background`
- Integrates with implement-task workflow
- Can be used standalone or in scripts
