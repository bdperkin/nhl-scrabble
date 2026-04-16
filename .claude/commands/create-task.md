# Create Task

______________________________________________________________________

## title: 'Create Implementation Task' read_only: false type: 'command'

Create a comprehensive implementation task with documentation, categorization, prioritization, and GitHub issue tracking.

## Process

This command automates the complete task creation workflow:

1. **Analyze Task Description**

   - Read and interpret the task description provided
   - Identify the problem or enhancement being addressed
   - Determine technical requirements and scope
   - Identify affected components and files

1. **Categorize Task**

   - **bug-fixes** - Bug fixes and corrections
   - **security** - Security improvements
   - **optimization** - Performance optimizations
   - **enhancement** - Feature enhancements
   - **testing** - Test coverage improvements
   - **new-features** - Major new features
   - **refactoring** - Code refactoring

1. **Prioritize Task**

   - **CRITICAL** - Must Do (Immediately) - Security issues, data loss, crashes
   - **HIGH** - Must Do (Next Sprint) - Important bugs, key features
   - **MEDIUM** - Should Do (Next Month) - Enhancements, optimizations
   - **LOW** - Nice to Have (Next Quarter) - Minor improvements, cleanup

1. **Estimate Effort**

   - Analyze complexity and scope
   - Consider testing requirements
   - Account for documentation updates
   - Provide realistic time range (e.g., "2-4h", "8-12h")

1. **Create Implementation Plan**

   - Define current state (what exists now)
   - Propose detailed solution with code examples
   - Outline testing strategy
   - List acceptance criteria
   - Identify related files and dependencies

1. **Determine Task ID**

   - Read existing tasks in the category directory
   - Find highest numbered task file (e.g., 001, 002, 003)
   - Assign next sequential number

1. **Create Task File**

   - Use the Task Template from tasks/README.md
   - Write to `tasks/{category}/{id}-{slug}.md`
   - Include all analysis and planning details
   - Follow markdown formatting standards

1. **Update tasks/README.md**

   - **Task Index**: Add entry to appropriate category table
   - **Total Project Roadmap**: Update task counts and effort totals
   - **Recommended Implementation Order**: Add if HIGH or CRITICAL priority
   - Maintain proper markdown formatting and alignment

1. **Create GitHub Issue**

   - Follow process from `.claude/commands/gh/create-issue.md`
   - Use task title as issue title
   - Use task description and acceptance criteria as issue body
   - Add appropriate labels based on category and priority
   - Create issue using `gh issue create`

1. **Document GitHub Issue**

   - Add GitHub issue URL to task file header
   - Add GitHub issue reference to tasks/README.md Task Index
   - Link task file in GitHub issue body

## Task Template Structure

```markdown
# Task Title

**GitHub Issue**: #{issue-number} - {issue-url}

## Priority

**PRIORITY_LEVEL** - Time Frame

## Estimated Effort

X-Y hours

## Description

Brief description of the problem/enhancement

## Current State

Current implementation with code examples showing what exists

## Proposed Solution

Detailed solution with:
- Architecture changes
- Code examples
- Configuration changes
- Database changes (if applicable)

## Implementation Steps

1. Step one
2. Step two
3. Step three

## Testing Strategy

How to test the implementation:
- Unit tests
- Integration tests
- Manual testing steps

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `path/to/file1.py` - Description
- `path/to/file2.py` - Description

## Dependencies

- Other tasks that must be completed first
- Required packages or tools
- External dependencies

## Additional Notes

Any extra context, trade-offs, or considerations:
- Performance implications
- Security considerations
- Breaking changes
- Migration requirements

## Implementation Notes

*To be filled during implementation:*
- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
```

## Priority Guidelines

**CRITICAL** - Must Do (Immediately):

- Security vulnerabilities
- Data loss or corruption issues
- Application crashes
- Critical functionality broken
- Production blockers

**HIGH** - Must Do (Next Sprint):

- Important bugs affecting users
- Key feature requests
- Significant performance issues
- Required for upcoming release

**MEDIUM** - Should Do (Next Month):

- Minor bugs
- Nice-to-have features
- Code quality improvements
- Moderate optimizations

**LOW** - Nice to Have (Next Quarter):

- Cosmetic improvements
- Minor refactoring
- Nice-to-have features
- Long-term improvements

## Category Guidelines

**bug-fixes**:

- Incorrect behavior
- Error handling issues
- Edge case failures
- Regression fixes

**security**:

- Vulnerability fixes
- Authentication/authorization
- Input validation
- Secret management
- Security policies

**optimization**:

- Performance improvements
- Memory usage reduction
- API call optimization
- Caching strategies

**enhancement**:

- Existing feature improvements
- UI/UX enhancements
- Better error messages
- Configuration options

**testing**:

- Test coverage increase
- Test infrastructure
- Test utilities
- Integration tests

**new-features**:

- Completely new functionality
- New commands/options
- New output formats
- New integrations

**refactoring**:

- Code organization
- Design pattern improvements
- Dependency management
- Type safety improvements

## Examples

### Example: Bug Fix Task

```bash
# Input description:
"The NHL API client doesn't properly handle 404 errors when a team
doesn't exist. It should raise NHLApiNotFoundError but currently
just logs a warning."

# Claude will:
1. Analyze: This is a bug in error handling
2. Categorize: bug-fixes
3. Prioritize: HIGH (incorrect error handling)
4. Estimate: 1-2h (simple fix, add tests)
5. Create plan with code examples
6. Assign ID: 007 (next in bug-fixes/)
7. Create: tasks/bug-fixes/007-api-404-handling.md
8. Update: tasks/README.md
9. Create: GitHub issue with "bug" label
10. Link: Issue number in task file and README
```

### Example: New Feature Task

```bash
# Input description:
"Add REST API server to allow web applications to query NHL Scrabble
scores programmatically. Should use FastAPI, support JSON responses,
include OpenAPI docs, and handle authentication."

# Claude will:
1. Analyze: Major new feature requiring API design
2. Categorize: new-features
3. Prioritize: LOW (nice to have, not core)
4. Estimate: 16-24h (complex, many components)
5. Create detailed plan with FastAPI examples
6. Assign ID: 002 (next in new-features/)
7. Create: tasks/new-features/002-rest-api-server.md
8. Update: tasks/README.md
9. Create: GitHub issue with "enhancement" label
10. Link: Issue number in task file and README
```

## Usage

```bash
# Provide task description
claude> /create-task "Add caching to API responses to improve performance"

# Or more detailed
claude> /create-task "The playoff calculator doesn't handle ties correctly.
When two teams have the same total score, it should use tiebreaker rules
but currently just uses alphabetical order. Need to implement proper
NHL tiebreaker logic."

# Or from a GitHub issue
claude> /create-task "Implement the functionality described in issue #42"
```

## Output

The command will:

1. ✅ Create task file in appropriate directory
1. ✅ Update tasks/README.md with new task
1. ✅ Create GitHub issue
1. ✅ Link GitHub issue in documentation
1. 📋 Display task summary and next steps

Example output:

```
✅ Task Created Successfully!

Category: bug-fixes
Priority: HIGH
Effort: 1-2h
ID: 007

Task File: tasks/bug-fixes/007-api-404-handling.md
GitHub Issue: #52 - https://github.com/user/repo/issues/52

Task Summary:
- Fix NHL API 404 error handling
- Raise NHLApiNotFoundError instead of logging warning
- Add tests for 404 scenarios

Next Steps:
1. Review task file: tasks/bug-fixes/007-api-404-handling.md
2. Create branch: git checkout -b bug-fixes/007-api-404-handling
3. Implement solution following the task specification
4. Create PR referencing task file and issue #52
```

## Error Handling

The command will validate:

- ✅ Task description is not empty
- ✅ tasks/ directory structure exists
- ✅ tasks/README.md exists and is readable
- ✅ GitHub CLI (`gh`) is available for issue creation
- ✅ Task files use sequential numbering

If errors occur:

- 🔴 Missing task description → Prompt user
- 🔴 Cannot determine category → Ask user to clarify
- 🔴 Directory doesn't exist → Create it
- 🔴 GitHub CLI fails → Still create task file, note manual issue creation needed

## Best Practices

**When creating tasks:**

1. **Be specific**: Clear, actionable descriptions
1. **Provide context**: Why is this needed?
1. **Include examples**: Show what you mean
1. **Think testing**: How will we verify it works?
1. **Consider dependencies**: What else is needed?

**Task descriptions should include:**

- What the problem/enhancement is
- Why it matters
- Any relevant technical details
- Expected behavior or outcome
- Files/components affected

**Good task descriptions:**

```
✅ "Add input validation to CLI arguments to prevent SQL injection
   through the --output parameter. Currently accepts any path without
   sanitization."

✅ "Implement caching for NHL API responses using Redis. API calls
   are slow (3-5s) and rate-limited. Cache should expire after 1 hour
   and handle cache misses gracefully."

✅ "Refactor report generators to use a common base class. Currently
   5 report classes duplicate pagination, formatting, and header logic."
```

**Poor task descriptions:**

```
❌ "Fix the bug" - Not specific
❌ "Make it faster" - No details
❌ "Add tests" - Too vague
❌ "Improve code" - Not actionable
```

## Tips

- Use this command for ANY new task, no matter how small
- Tasks create a historical record of work
- Well-documented tasks help future contributors
- GitHub issues enable community participation
- Task files are great for knowledge transfer
- Effort estimates improve over time with feedback

## Related Commands

- `/gh:create-issue` - Create GitHub issues
- `/gh:view-issue` - View issue details
- `/git:commit` - Commit task files
- `/git:push` - Push to GitHub

## Notes

- Task numbering is per-category (bug-fixes/001, security/001, etc.)
- Tasks are never deleted, only marked complete
- Completed tasks can be moved to tasks/completed/
- Update tasks/README.md when completing tasks
- Link PRs in task files when implemented
