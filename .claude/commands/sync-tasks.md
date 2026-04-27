______________________________________________________________________

## title: 'Synchronize Tasks with GitHub' read_only: false type: 'command'

# Synchronize Tasks with GitHub

______________________________________________________________________

Complete bi-directional synchronization of task files with GitHub project state including issues, pull requests, actions, security findings, and project activity.

## Process

This command performs comprehensive task-GitHub reconciliation and synchronization:

1. **Run Initial Validation**

   Execute validation script to establish baseline state:

   ```bash
   python scripts/validate_task_docs.py
   ```

   - Capture validation output
   - Document current discrepancies between:
     - Filesystem task counts vs tasks/README.md
     - Filesystem task counts vs tasks/IMPLEMENTATION_SEQUENCE.md
     - README.md vs IMPLEMENTATION_SEQUENCE.md
   - Report initial status:
     - Active task count from filesystem
     - Active task count from README.md
     - Active task count from IMPLEMENTATION_SEQUENCE.md
     - Completed task count from filesystem
     - Completed task count from README.md
   - If validation fails:
     - Log all discrepancies for reconciliation
     - Note which files need updates
     - Continue with sync process
   - If validation passes:
     - Note that files are already consistent
     - Continue with sync process

1. **Analyze GitHub Project State**

   - Fetch all GitHub issues: `gh issue list --state all --limit 1000 --json number,title,state,labels,closedAt,createdAt,updatedAt,body`
   - Fetch all pull requests: `gh pr list --state all --limit 1000 --json number,title,state,labels,closedAt,mergedAt,createdAt,updatedAt,body`
   - Fetch workflow runs: `gh run list --limit 100 --json status,conclusion,name,createdAt`
   - Check security alerts: `gh api repos/{owner}/{repo}/dependabot/alerts`
   - Check CodeQL alerts: `gh api repos/{owner}/{repo}/code-scanning/alerts`
   - Get repository activity: `gh api repos/{owner}/{repo}/activity`
   - Extract task-related metadata:
     - Issue numbers linked to tasks
     - PR numbers linked to tasks
     - Completion timestamps
     - Current status (open, closed, merged)
     - Labels and priorities

1. **Analyze Task File State**

   - Scan all task directories:
     - `tasks/bug-fixes/`
     - `tasks/security/`
     - `tasks/optimization/`
     - `tasks/enhancement/`
     - `tasks/testing/`
     - `tasks/new-features/`
     - `tasks/refactoring/`
     - `tasks/completed/` (all subdirectories)
   - Parse each task file:
     - Extract GitHub issue number from header
     - Extract GitHub PR number from implementation notes
     - Parse priority level
     - Parse estimated effort
     - Check acceptance criteria completion status
     - Check if task has implementation notes
     - Determine task status (planned, in-progress, completed)
   - Build comprehensive task inventory

1. **Identify Discrepancies (Bi-Directional)**

   - **GitHub → Tasks** (GitHub is newer):
     - Closed issues with open/incomplete task files
     - Merged PRs without completed task files
     - Updated issue descriptions not reflected in task files
     - Changed priority labels not reflected in task files
     - Security findings without corresponding tasks
     - Failed CI runs for task-related PRs
   - **Tasks → GitHub** (Tasks are newer):
     - Completed tasks without closed GitHub issues
     - Task files with PRs not merged on GitHub
     - Task files moved to `completed/` but issues still open
     - New task files without GitHub issues
     - Implementation notes added but no PR created
   - **Both Sides**:
     - Mismatched status (task says complete, issue says open)
     - Missing cross-references (task has no issue link)
     - Orphaned issues (no corresponding task file)
     - Orphaned tasks (no corresponding issue)

1. **Determine Sync Direction**

   For each discrepancy, determine which side is authoritative:

   - **Use GitHub as source of truth when**:
     - Issue was closed/merged more recently than task was modified
     - PR was merged (definitive completion signal)
     - Issue was updated by human after task file update
     - Security alert was resolved on GitHub
   - **Use Task as source of truth when**:
     - Task file has newer implementation notes
     - Task was moved to completed/ more recently than issue update
     - Task has detailed completion info not in GitHub
     - Task represents planned work not yet on GitHub
   - **Both need updates when**:
     - Cross-references are missing on both sides
     - Status is inconsistent with timestamps suggesting parallel updates
     - Metadata is incomplete on both sides

1. **Sync GitHub → Tasks**

   For each GitHub-authoritative discrepancy:

   - **Closed/Merged Issue → Complete Task**:
     - Add implementation notes to task file if missing
     - Mark all acceptance criteria complete
     - Extract completion timestamp from GitHub
     - Extract PR number from closing event
     - Extract final effort from PR metadata if available
     - Move task file to `tasks/completed/{category}/`
     - Update cross-references
   - **Updated Issue Description → Update Task**:
     - Sync priority changes
     - Sync description updates
     - Add new requirements to acceptance criteria
     - Update effort estimates if changed
   - **New Security Finding → Create Task**:
     - Create task file in `tasks/security/`
     - Link to security alert
     - Set priority based on severity
     - Generate implementation plan
   - **Failed CI → Add Note to Task**:
     - Add note about CI failure
     - Link to failed run
     - Update testing strategy if needed

1. **Sync Tasks → GitHub**

   For each task-authoritative discrepancy:

   - **Completed Task → Close Issue**:
     - Add completion comment to issue:
       ```
       Completed in PR #{pr-number}

       Implementation: tasks/completed/{category}/{id}-{slug}.md
       Actual effort: {effort}
       Completion date: {date}
       ```
     - Close issue: `gh issue close {issue-number}`
   - **Task with PR → Merge or Update**:
     - Check if PR is mergeable
     - Comment on PR with task completion status
     - Add labels based on task metadata
   - **New Task File → Create Issue**:
     - Create GitHub issue from task file
     - Use task title as issue title
     - Use description and acceptance criteria as body
     - Add appropriate labels
     - Link issue number back to task file
   - **Moved Task → Update Issue Status**:
     - Close issue if task is in completed/
     - Add comment with completion details
     - Update labels to reflect completion

1. **Handle Orphaned Items**

   - **Orphaned GitHub Issues** (no task file):
     - Option 1: Create task file from issue
     - Option 2: Mark issue as "no-task-file" label
     - Option 3: Report for manual review
   - **Orphaned Task Files** (no GitHub issue):
     - Option 1: Create GitHub issue
     - Option 2: Add note to task file about missing issue
     - Option 3: Report for manual review
   - **Report to user** for decision on orphans

1. **Update All Task Files**

   For each task file in all directories:

   - **Normalize Format**:
     - Ensure consistent markdown structure
     - Fix heading levels
     - Normalize list formatting
     - Fix table alignment
   - **Update Metadata**:
     - Current priority (from GitHub labels)
     - Actual effort (from PR metadata)
     - Completion timestamps
     - PR links
     - Issue links
   - **Update Status Indicators**:
     - Mark acceptance criteria checkboxes
     - Update implementation notes
     - Add completion details
     - Update effort estimates vs actuals
   - **Add Missing Sections**:
     - Implementation notes (if completed)
     - Related PRs section
     - Lessons learned (if completed)
   - **Remove Outdated Content**:
     - Stale notes
     - Obsolete references
     - Completed TODOs

1. **Regenerate tasks/README.md**

   Complete reconstruction of the task index:

   - **Header Section**:
     - Project title and description
     - Overview of task tracking system
     - Link to task creation workflow
   - **Summary Statistics**:
     - Total tasks by status (planned, in-progress, completed)
     - Total effort by category
     - Completion percentage
     - Average actual vs estimated effort
   - **Task Index by Category**:
     - Bug Fixes table
     - Security table
     - Optimization table
     - Enhancement table
     - Testing table
     - New Features table
     - Refactoring table
     - Each with columns: ID, Title, Priority, Effort, Status, Issue, PR
   - **Completed Tasks Section**:
     - Grouped by category
     - Include completion date
     - Include PR reference
     - Include actual effort
     - Sort by completion date (newest first)
   - **Recommended Implementation Order**:
     - HIGH and CRITICAL priority tasks
     - Sorted by dependencies
     - Include effort estimates
   - **Total Project Roadmap**:
     - Effort by category
     - Completion percentage
     - Remaining effort
     - Projected completion timeline
   - **Task Categories Explanation**:
     - Description of each category
     - When to use each
     - Priority guidelines
   - **Statistics and Metrics**:
     - Average effort per task
     - Effort variance (estimated vs actual)
     - Completion velocity
     - Most common task types

1. **Regenerate tasks/IMPLEMENTATION_SEQUENCE.md**

   Complete reconstruction of the implementation sequence with optimal ordering:

   - **Header Section**:
     - Generation timestamp
     - Last updated date
     - Total active tasks count
     - Estimated total effort (sum all active tasks)
     - Implementation strategy statement
   - **Recent Changes Section** (if applicable):
     - Document recent work outside task system
     - List major branches/commits
     - Summarize documentation improvements
     - Note any architectural changes
   - **Usage Instructions**:
     - Explain how to use this file
     - Describe ordering criteria (Priority → Dependencies → Strategic Value → Effort)
     - Note that tasks should be executed in order
     - Explain dependency notation
   - **Phase-Based Organization**:
     - Group tasks into logical implementation phases
     - Each phase includes:
       - Phase number and title
       - Total effort for phase
       - Focus/objective statement
       - Dependency requirements
       - List of tasks as `/implement-task` commands
       - Rationale explaining ordering and dependencies
   - **Task Ordering Algorithm**:
     - **Phase 1: CRITICAL Priority**
       - Start with parent/coordinating tasks
       - Then sub-tasks in dependency order
       - Quick wins (< 2h) first within same dependency level
     - **Phase 2: HIGH Priority**
       - Infrastructure before features
       - Bug fixes before enhancements
       - Dependencies before dependents
       - Quick wins first
     - **Phase 3-N: MEDIUM Priority**
       - Group by strategic themes (workflows, testing, features, etc.)
       - Parent tasks before children
       - Foundation before implementation
       - Test infrastructure before specific tests
     - **Final Phases: LOW Priority**
       - Quality-of-life improvements
       - Nice-to-have features
       - Documentation polish
       - Optimization opportunities
   - **Strategic Value Analysis**:
     - **Foundation Tasks** (highest strategic value):
       - Infrastructure setup
       - Framework establishment
       - Core capabilities
       - Required dependencies for other tasks
     - **Feature Tasks** (medium strategic value):
       - User-facing functionality
       - API enhancements
       - CLI improvements
       - Build on foundation tasks
     - **Polish Tasks** (lower strategic value):
       - Developer experience
       - Documentation improvements
       - Performance optimizations
       - Can be deferred if needed
   - **Dependency Tracking**:
     - Mark parent tasks clearly
     - Note which tasks must complete before others
     - Identify tasks that can run in parallel
     - Flag circular dependencies if any exist
   - **Effort Considerations**:
     - Within same priority/dependency level, order by effort:
       - Quick wins (< 2h) first for momentum
       - Medium tasks (2-8h) next
       - Large tasks (> 8h) last
     - Balance quick wins with strategic progress
     - Don't defer all large tasks to end
   - **Format Each Task Entry**:
     ```bash
     # Task Title (Priority, Special Notes)
     /implement-task category/ID-slug.md  # effort, Issue #number, [Dependencies: #ID1, #ID2]
     ```
   - **Include Rationale After Each Phase**:
     - Explain why tasks are in this phase
     - Justify the ordering within phase
     - Note dependencies and blockers
     - Highlight strategic considerations

1. **Validate Changes**

   Before committing, validate all updates:

   - **File Format Validation**:
     - All task files are valid markdown
     - All tables are properly formatted
     - All links are valid
     - No broken references
   - **Data Consistency**:
     - All GitHub issue numbers exist
     - All PR numbers exist
     - All cross-references are bidirectional
     - No duplicate task IDs
     - No orphaned files
   - **Status Consistency**:
     - Completed tasks are in completed/
     - Open tasks are in active directories
     - Issue status matches task status
     - PR status matches task status
   - **Metadata Completeness**:
     - All tasks have priorities
     - All tasks have effort estimates
     - All completed tasks have implementation notes
     - All tasks have GitHub issue links

1. **Run Pre-commit Hooks**

   Execute all quality checks:

   ```bash
   pre-commit run --all-files
   ```

   - If hooks modify files (formatting fixes):
     - Review auto-fixes
     - Stage modified files
     - Proceed to commit
   - If hooks fail with errors:
     - Review failures
     - Fix issues manually
     - Re-run hooks
     - Only proceed when all hooks pass

1. **Run Final Validation**

   Execute validation script to verify synchronization:

   ```bash
   python scripts/validate_task_docs.py
   ```

   - Verify all discrepancies from initial validation are resolved
   - Confirm consistency between:
     - Filesystem task counts == tasks/README.md counts
     - Filesystem task counts == tasks/IMPLEMENTATION_SEQUENCE.md counts
     - README.md counts == IMPLEMENTATION_SEQUENCE.md counts
   - If validation passes:
     - Proceed to commit
     - Note success in commit message
   - If validation fails:
     - Review remaining discrepancies
     - Fix any issues in README.md and/or IMPLEMENTATION_SEQUENCE.md
     - Re-run validation until passes
     - Stage any additional fixes
   - Report final validation status:
     - Initial discrepancies found: {count}
     - Final discrepancies remaining: {count} (should be 0)
     - Files updated to achieve consistency: {list}

1. **Create Commit**

   Commit all synchronized changes:

   ```bash
   git add tasks/
   git commit -m "$(cat <<'EOF'
   chore: Synchronize tasks with GitHub project state

   Bi-directional sync between task files and GitHub:
   - Updated {n} task files from GitHub state
   - Updated {m} GitHub issues from task state
   - Moved {p} completed tasks to completed/
   - Created {q} new task files from GitHub issues
   - Closed {r} GitHub issues from completed tasks

   Changes:
   - {change-1}
   - {change-2}
   - {change-3}

   Documentation:
   - Updated tasks/README.md with current counts
   - Regenerated tasks/IMPLEMENTATION_SEQUENCE.md with optimal ordering
   - Validation: {initial-failures} → {final-failures} discrepancies

   Statistics:
   - Total tasks: {total}
   - Completed: {completed} ({percentage}%)
   - In progress: {in-progress}
   - Planned: {planned}

   Discrepancies resolved: {discrepancy-count}
   EOF
   )"
   ```

1. **Push Changes**

   Push synchronized state to remote:

   ```bash
   git push origin main
   ```

   - Verify push succeeded
   - Check GitHub Actions triggered
   - Monitor CI status
   - Report completion

1. **Generate Sync Report**

   Produce comprehensive report of synchronization:

   ```markdown
   # Task-GitHub Synchronization Report

   **Date**: {timestamp}
   **Branch**: {branch}
   **Commit**: {commit-hash}

   ## Summary

   - **GitHub Issues Analyzed**: {issue-count}
   - **Pull Requests Analyzed**: {pr-count}
   - **Task Files Analyzed**: {task-count}
   - **Discrepancies Found**: {discrepancy-count}
   - **Discrepancies Resolved**: {resolved-count}
   - **Orphaned Items**: {orphan-count}

   ## Changes Applied

   ### GitHub → Tasks ({count})

   - Completed tasks from merged PRs: {count}
   - Updated priorities from labels: {count}
   - Created tasks from security alerts: {count}

   ### Tasks → GitHub ({count})

   - Closed issues from completed tasks: {count}
   - Created issues from new tasks: {count}
   - Updated PR status: {count}

   ### Both Directions ({count})

   - Cross-references added: {count}
   - Metadata synchronized: {count}
   - Status reconciled: {count}

   ## Task Statistics

   ### By Category

   | Category | Total | Completed | In Progress | Planned | % Complete |
   |----------|-------|-----------|-------------|---------|------------|
   | Bug Fixes | {n} | {c} | {i} | {p} | {pct}% |
   | Security | {n} | {c} | {i} | {p} | {pct}% |
   | Optimization | {n} | {c} | {i} | {p} | {pct}% |
   | Enhancement | {n} | {c} | {i} | {p} | {pct}% |
   | Testing | {n} | {c} | {i} | {p} | {pct}% |
   | New Features | {n} | {c} | {i} | {p} | {pct}% |
   | Refactoring | {n} | {c} | {i} | {p} | {pct}% |

   ### By Priority

   | Priority | Count | Completed | % Complete |
   |----------|-------|-----------|------------|
   | CRITICAL | {n} | {c} | {pct}% |
   | HIGH | {n} | {c} | {pct}% |
   | MEDIUM | {n} | {c} | {pct}% |
   | LOW | {n} | {c} | {pct}% |

   ### Effort Analysis

   - **Total Estimated Effort**: {hours}h
   - **Total Actual Effort**: {hours}h
   - **Variance**: {variance}h ({pct}%)
   - **Average Task Effort**: {avg}h
   - **Completed Effort**: {completed}h
   - **Remaining Effort**: {remaining}h

   ## Orphaned Items

   ### Orphaned Issues (no task file)

   {list-of-orphaned-issues}

   ### Orphaned Tasks (no GitHub issue)

   {list-of-orphaned-tasks}

   ## Recommendations

   {recommendations-based-on-analysis}

   ## Next Steps

   {suggested-next-actions}
   ```

## Sync Logic Decision Matrix

### When to Use GitHub as Source of Truth

| Scenario                      | GitHub Timestamp | Task Timestamp | Action                            |
| ----------------------------- | ---------------- | -------------- | --------------------------------- |
| Issue closed, task incomplete | Newer            | Older          | Complete task, move to completed/ |
| PR merged, task in-progress   | Newer            | Older          | Complete task, add PR details     |
| Issue priority changed        | Newer            | Older          | Update task priority              |
| Security alert created        | Newer            | N/A            | Create new task                   |
| Issue description updated     | Newer            | Older          | Update task description           |

### When to Use Task as Source of Truth

| Scenario                             | GitHub Timestamp | Task Timestamp | Action                           |
| ------------------------------------ | ---------------- | -------------- | -------------------------------- |
| Task completed, issue still open     | Older            | Newer          | Close issue with completion note |
| Task has implementation notes, no PR | Older            | Newer          | Create/update PR                 |
| Task moved to completed/, issue open | Older            | Newer          | Close issue                      |
| New task file created, no issue      | N/A              | Newer          | Create GitHub issue              |
| Task acceptance criteria updated     | Older            | Newer          | Update issue description         |

### When Both Need Updates

| Scenario                              | Action                                                     |
| ------------------------------------- | ---------------------------------------------------------- |
| Missing cross-references              | Add issue link to task, add task link to issue             |
| Parallel updates (timestamps similar) | Manual review required, report to user                     |
| Incomplete metadata on both sides     | Combine available data, prompt user for missing info       |
| Conflicting status                    | Use most recent update, add note about conflict resolution |

## GitHub API Commands

### Fetching Data

```bash
# All issues
gh issue list --state all --limit 1000 --json number,title,state,labels,closedAt,createdAt,updatedAt,body,author,assignees

# All PRs
gh pr list --state all --limit 1000 --json number,title,state,labels,closedAt,mergedAt,createdAt,updatedAt,body,author,mergeable,files

# Workflow runs
gh run list --limit 100 --json status,conclusion,name,createdAt,headBranch,event,workflowName

# Dependabot alerts
gh api repos/{owner}/{repo}/dependabot/alerts --paginate --jq '.[] | {number, state, dependency, security_advisory}'

# CodeQL alerts
gh api repos/{owner}/{repo}/code-scanning/alerts --paginate --jq '.[] | {number, state, rule, created_at, dismissed_at}'

# Repository activity
gh api repos/{owner}/{repo}/activity --jq '.[] | {activity_type, ref, timestamp}'

# Specific issue details
gh issue view {number} --json number,title,state,labels,closedAt,body,comments

# PR files changed
gh pr view {number} --json files --jq '.files[].path'

# Issue timeline
gh api repos/{owner}/{repo}/issues/{number}/timeline --jq '.[] | {event, created_at, actor}'
```

### Updating GitHub

```bash
# Close issue with comment
gh issue close {number} --comment "Completed in PR #{pr-number}..."

# Add labels to issue
gh issue edit {number} --add-label "completed,priority:high"

# Create issue
gh issue create --title "{title}" --body "{body}" --label "{labels}"

# Update issue description
gh issue edit {number} --body "{new-body}"

# Add comment to PR
gh pr comment {number} --body "{comment}"

# Merge PR
gh pr merge {number} --squash --delete-branch

# Create PR
gh pr create --title "{title}" --body "{body}" --base main
```

## Task File Parsing

### Extract Issue Number

```python
import re


def extract_issue_number(task_content: str) -> int | None:
    """Extract GitHub issue number from task file header."""
    # Pattern: **GitHub Issue**: #123 - https://...
    pattern = r"\*\*GitHub Issue\*\*:\s*#?(\d+)"
    match = re.search(pattern, task_content)
    return int(match.group(1)) if match else None
```

### Extract PR Number

```python
def extract_pr_number(task_content: str) -> int | None:
    """Extract PR number from implementation notes."""
    # Pattern: **PR**: #123 - https://...
    pattern = r"\*\*PR\*\*:\s*#?(\d+)"
    match = re.search(pattern, task_content)
    return int(match.group(1)) if match else None
```

### Check Completion Status

```python
def is_task_completed(task_content: str) -> bool:
    """Check if task has implementation notes section."""
    return "## Implementation Notes" in task_content
```

### Parse Priority

```python
def extract_priority(task_content: str) -> str | None:
    """Extract priority from task file."""
    # Pattern: **CRITICAL** - Must Do (Immediately)
    pattern = r"\*\*(CRITICAL|HIGH|MEDIUM|LOW)\*\*"
    match = re.search(pattern, task_content)
    return match.group(1) if match else None
```

## Reconciliation Examples

### Example 1: Merged PR, Incomplete Task

**GitHub State:**

- PR #54 merged 2026-04-15
- Issue #52 closed by PR #54
- Files changed: `src/nhl_scrabble/api/nhl_client.py`, tests

**Task State:**

- File: `tasks/bug-fixes/007-api-404-handling.md`
- No implementation notes
- Acceptance criteria unchecked
- Last modified: 2026-04-01

**Action:**

- Extract PR details from GitHub
- Add implementation notes to task file
- Mark acceptance criteria complete
- Extract actual effort from PR timeline
- Move to `tasks/completed/bug-fixes/007-api-404-handling.md`

### Example 2: Completed Task, Open Issue

**Task State:**

- File: `tasks/completed/enhancement/003-sphinx-documentation.md`
- Implementation notes present
- PR #75 referenced
- Completed: 2026-04-14

**GitHub State:**

- Issue #73 still open
- PR #75 merged 2026-04-14
- No closing event

**Action:**

- Add comment to issue #73 with completion details
- Close issue #73
- Link closure to PR #75

### Example 3: Security Alert, No Task

**GitHub State:**

- Dependabot alert #12 (HIGH severity)
- Package: requests 2.31.0 → 2.31.1
- CVE-2024-XXXXX
- Created: 2026-04-16

**Task State:**

- No corresponding task file

**Action:**

- Create `tasks/security/008-dependabot-requests.md`
- Create GitHub issue #85
- Link alert to task and issue
- Set priority to HIGH
- Generate fix plan

### Example 4: Parallel Updates

**GitHub State:**

- Issue #80 updated 2026-04-16 10:00
- Description changed by user
- Priority label added

**Task State:**

- File: `tasks/enhancement/004-automated-api-cli-docs.md`
- Updated 2026-04-16 09:55
- Implementation notes added

**Action:**

- Merge description changes from GitHub to task
- Keep implementation notes from task
- Add priority from GitHub to task
- Report potential conflict to user

## Error Handling

### GitHub API Failures

```python
try:
    issues = fetch_github_issues()
except GitHubAPIError as e:
    if e.status_code == 403:
        # Rate limit exceeded
        wait_time = e.rate_limit_reset - now()
        print(f"Rate limited. Waiting {wait_time}s...")
        time.sleep(wait_time)
        retry()
    elif e.status_code == 404:
        # Repository not found
        print("Error: Repository not found. Check permissions.")
        exit(1)
    else:
        # Other error
        print(f"GitHub API error: {e}")
        exit(1)
```

### Invalid Task Files

```python
try:
    task = parse_task_file(path)
except TaskParseError as e:
    print(f"Warning: Could not parse {path}: {e}")
    # Add to invalid_files list
    # Report to user for manual review
    invalid_files.append((path, str(e)))
    continue
```

### Conflicting Updates

```python
if github_timestamp > task_timestamp + threshold:
    # GitHub is definitively newer
    sync_github_to_task(issue, task)
elif task_timestamp > github_timestamp + threshold:
    # Task is definitively newer
    sync_task_to_github(task, issue)
else:
    # Timestamps too close, manual review needed
    conflicts.append(
        {
            "task": task,
            "issue": issue,
            "github_time": github_timestamp,
            "task_time": task_timestamp,
        }
    )
    # Report to user
```

## Safety Considerations

**Before Syncing:**

- ✅ Create backup branch with current state
- ✅ Verify GitHub authentication and permissions
- ✅ Check rate limits
- ✅ Validate task file structure
- ✅ Dry run option available

**During Syncing:**

- ✅ Validate all API responses
- ✅ Check for conflicts before overwriting
- ✅ Preserve manual edits where possible
- ✅ Log all changes for review
- ✅ Prompt for confirmation on destructive actions

**After Syncing:**

- ✅ Verify all cross-references are valid
- ✅ Check no data loss occurred
- ✅ Validate markdown formatting
- ✅ Run pre-commit hooks
- ✅ Review commit diff before pushing

## Configuration

### Environment Variables

```bash
# GitHub API token (required for API access)
GITHUB_TOKEN=ghp_xxxxx

# Sync behavior
SYNC_TASKS_DRY_RUN=true          # Preview changes without applying
SYNC_TASKS_AUTO_CLOSE=true       # Auto-close completed issues
SYNC_TASKS_AUTO_CREATE=true      # Auto-create tasks from alerts
SYNC_TASKS_BACKUP=true           # Create backup branch before sync

# Conflict resolution
SYNC_TASKS_TIME_THRESHOLD=300    # 5 minutes threshold for conflict detection
SYNC_TASKS_PREFER_GITHUB=false   # Prefer GitHub in conflicts (default: newer)
SYNC_TASKS_PREFER_TASKS=false    # Prefer tasks in conflicts (default: newer)

# Reporting
SYNC_TASKS_VERBOSE=true          # Detailed sync reporting
SYNC_TASKS_REPORT_FILE=sync-report.md  # Save report to file
```

### Sync Options

```bash
# Full sync (default)
/sync-tasks

# Dry run (preview only)
/sync-tasks --dry-run

# Specific categories only
/sync-tasks --categories bug-fixes,security

# GitHub to tasks only (one direction)
/sync-tasks --direction github-to-tasks

# Tasks to GitHub only
/sync-tasks --direction tasks-to-github

# Skip orphan handling
/sync-tasks --skip-orphans

# Force sync (ignore conflicts)
/sync-tasks --force

# Backup branch name
/sync-tasks --backup-branch sync-backup-$(date +%Y%m%d)
```

## Usage

```bash
# Standard sync
/sync-tasks

# Dry run to preview changes
/sync-tasks --dry-run

# Sync specific category
/sync-tasks --categories security

# Verbose output
/sync-tasks --verbose

# Auto-confirm all prompts
/sync-tasks --yes
```

## Output

```
🔄 Synchronizing Tasks with GitHub

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Running Initial Validation...
  ✓ Executed scripts/validate_task_docs.py
  → Filesystem: 60 active, 79 completed
  → README.md: 58 active, 79 completed
  → IMPLEMENTATION_SEQUENCE.md: 58 active
  ⚠ Found 2 discrepancies:
    • README.md missing 2 active tasks
    • IMPLEMENTATION_SEQUENCE.md missing 2 active tasks

Step 2: Analyzing GitHub Project State...
  ✓ Fetched 52 issues
  ✓ Fetched 48 pull requests
  ✓ Fetched 25 workflow runs
  ✓ Fetched 3 Dependabot alerts
  ✓ Fetched 0 CodeQL alerts

Step 3: Analyzing Task File State...
  ✓ Scanned 7 task directories
  ✓ Found 60 task files
  ✓ Found 79 completed tasks

Step 4: Identifying Discrepancies...
  → Found 8 discrepancies requiring sync

  GitHub → Tasks (5):
    • Issue #52 closed, task 007 incomplete
    • PR #75 merged, task 003 missing notes
    • Issue #80 priority changed (MEDIUM → HIGH)
    • Security alert #12 has no task
    • Issue #81 description updated

  Tasks → GitHub (3):
    • Task 002 completed, issue #74 still open
    • Task 005 has new PR #78, not linked in issue
    • New task 006 has no GitHub issue

Step 5: Determining Sync Direction...
  ✓ 5 use GitHub as source of truth
  ✓ 3 use tasks as source of truth
  ✓ 0 conflicts requiring manual review

Step 6: Syncing GitHub → Tasks...
  ✓ Completed task 007 from issue #52
  ✓ Added notes to task 003 from PR #75
  ✓ Updated task 004 priority to HIGH
  ✓ Created task 008 from security alert #12
  ✓ Updated task 004 description from issue #81

Step 7: Syncing Tasks → GitHub...
  ✓ Closed issue #74 from completed task 002
  ✓ Linked PR #78 in issue #79
  ✓ Created issue #86 for task 006

Step 8: Updating All Task Files...
  ✓ Normalized 60 task files
  ✓ Updated metadata in 8 files
  ✓ Added missing sections to 3 files
  ✓ Fixed formatting in 12 files

Step 9: Regenerating tasks/README.md...
  ✓ Updated summary statistics (60 active, 79 completed)
  ✓ Rebuilt task index (7 categories)
  ✓ Added completed tasks section
  ✓ Updated roadmap and metrics

Step 10: Regenerating tasks/IMPLEMENTATION_SEQUENCE.md...
  ✓ Analyzed task priorities and dependencies
  ✓ Grouped 60 tasks into 12 implementation phases
  ✓ Ordered by: Priority → Dependencies → Strategic Value → Effort
  ✓ Updated total effort calculation: 522 hours
  ✓ Added phase rationales and dependency notes

Step 11: Running Pre-commit Hooks...
  ✓ All 67 hooks passed

Step 12: Running Final Validation...
  ✓ Executed scripts/validate_task_docs.py
  ✓ Filesystem: 60 active, 79 completed
  ✓ README.md: 60 active, 79 completed
  ✓ IMPLEMENTATION_SEQUENCE.md: 60 active
  ✓ All validation checks passed!
  → Discrepancies resolved: 2 → 0

Step 13: Creating Commit...
  ✓ Commit: abc123d

Step 14: Pushing Changes...
  ✓ Pushed to origin/main

Step 15: Generating Sync Report...
  ✓ Report saved to sync-report.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Synchronization Complete!

Summary:
  • GitHub-Task discrepancies resolved: 8
  • Documentation validation: 2 → 0 discrepancies
  • Task files updated: 60
  • GitHub issues updated: 3
  • Files moved to completed/: 2
  • New tasks created: 1
  • New issues created: 1

Documentation:
  • tasks/README.md: Updated and validated
  • tasks/IMPLEMENTATION_SEQUENCE.md: Regenerated with optimal ordering
  • Validation: ✅ All checks passed

Statistics:
  • Total tasks: 139 (60 active, 79 completed)
  • Active effort: 522 hours
  • Completion rate: 57%
  • In progress: 3 tasks
  • Planned: 57 tasks

Next Steps:
  • Review sync report: sync-report.md
  • Review IMPLEMENTATION_SEQUENCE.md for task order
  • Check GitHub Actions: gh run watch
  • Monitor for issues: gh issue list
```

## Related Commands

- `/create-task` - Create new task files
- `/implement-task` - Implement existing tasks
- `/fix-security-finding` - Fix security findings
- `/git:commit` - Commit changes
- `/git:push` - Push to remote

## Notes

- Run this command regularly (weekly/monthly) to keep tasks and GitHub in sync
- Always review the sync report before pushing changes
- Use `--dry-run` first to preview changes
- Create backup branch automatically before major syncs
- Orphaned items require manual review and decision
- Conflicts with similar timestamps need human judgment
- GitHub API rate limits: 5000 requests/hour for authenticated users

## Best Practices

1. **Run sync before sprint planning** to ensure accurate task list
1. **Run sync after completing tasks** to update GitHub
1. **Use dry-run first** for large syncs
1. **Review orphaned items** to decide on action
1. **Keep task files updated** during development
1. **Use conventional commits** for sync commits
1. **Monitor GitHub Actions** after pushing
1. **Archive old completed tasks** periodically
