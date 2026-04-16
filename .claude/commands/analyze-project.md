# Analyze Project

______________________________________________________________________

## title: 'Analyze Project and Generate Tasks' read_only: false type: 'command'

Comprehensively analyze the entire project and generate prioritized implementation tasks for all identified improvements.

## Process

This command performs a complete project analysis and creates tasks for all identified improvements:

1. **Comprehensive Project Analysis**

   - Scan entire repository structure and architecture
   - Analyze all Python code (quality, patterns, complexity)
   - Review configuration files and build system
   - Examine CI/CD pipelines and automation
   - Inspect test suite (coverage, quality, gaps)
   - Review documentation completeness
   - Analyze dependencies and security
   - Check performance and optimization opportunities
   - Identify technical debt and refactoring needs

1. **Identify Bug Fixes**

   - **Error Handling Issues**:
     - Uncaught exceptions
     - Missing error handling
     - Incorrect exception types
     - Silent failures
   - **Logic Errors**:
     - Edge case failures
     - Incorrect algorithms
     - Data validation gaps
     - Type mismatches
   - **API Integration Issues**:
     - Rate limiting problems
     - Retry logic gaps
     - Timeout handling
     - Response validation
   - **Configuration Bugs**:
     - Invalid defaults
     - Missing validation
     - Environment issues

1. **Identify Optimizations**

   - **Performance Improvements**:
     - Slow algorithms (O(n²) → O(n log n))
     - Unnecessary computations
     - Missing caching opportunities
     - Inefficient data structures
   - **API Optimizations**:
     - Parallel requests
     - Response caching
     - Connection pooling
     - Batch operations
   - **Memory Optimizations**:
     - Large object retention
     - Memory leaks
     - Unnecessary copies
     - Generator opportunities
   - **Build/CI Optimizations**:
     - Slow CI pipelines
     - Missing caching
     - Redundant steps

1. **Identify Enhancements**

   - **User Experience**:
     - Better error messages
     - Progress indicators
     - Interactive modes
     - Color/formatting improvements
   - **Output Formats**:
     - HTML reports
     - CSV/Excel export
     - PDF generation
     - Custom formats
   - **Configuration**:
     - More options
     - Better defaults
     - Config file support
     - Environment variables
   - **Feature Improvements**:
     - Filtering options
     - Sorting capabilities
     - Search functionality
     - Data transformations

1. **Identify New Features**

   - **Major Features**:
     - Web interface
     - REST API
     - Database backend
     - Authentication
   - **Integration Features**:
     - Webhook support
     - Notification systems
     - External API integrations
     - Plugin architecture
   - **Advanced Capabilities**:
     - Historical tracking
     - Trend analysis
     - Predictive analytics
     - Machine learning
   - **Deployment Features**:
     - Docker support
     - Cloud deployment
     - Auto-scaling
     - Monitoring

1. **Identify Refactoring Needs**

   - **Code Quality**:
     - Duplicate code (DRY violations)
     - Long functions (>50 lines)
     - Complex functions (cyclomatic complexity >10)
     - God classes (too many responsibilities)
   - **Design Patterns**:
     - Missing abstractions
     - Tight coupling
     - Poor separation of concerns
     - Strategy pattern opportunities
   - **Type Safety**:
     - Missing type hints
     - Weak typing
     - Runtime type checking
     - Pydantic model opportunities
   - **Testing Infrastructure**:
     - Test utilities
     - Fixtures consolidation
     - Mock improvements
     - Test data management

1. **Identify Security Issues**

   - **Vulnerabilities**:
     - Dependency vulnerabilities (pip-audit, safety)
     - Code vulnerabilities (bandit)
     - Secret exposure risks
     - Injection vulnerabilities
   - **Security Hardening**:
     - Input validation
     - Output sanitization
     - Authentication/authorization
     - Rate limiting
   - **Security Policies**:
     - SECURITY.md file
     - Vulnerability disclosure
     - Security scanning in CI
     - Dependency updates (Dependabot)
   - **Data Protection**:
     - PII handling
     - Log sanitization
     - Secure storage
     - Encryption

1. **Generate Tasks for Each Finding**

   For each identified improvement:

   - Use `/create-task` workflow from `.claude/commands/create-task.md`
   - Analyze and categorize the issue
   - Assign appropriate priority
   - Estimate effort
   - Create detailed implementation plan
   - Write task file to `tasks/{category}/{id}-{slug}.md`
   - Update `tasks/README.md`
   - Create GitHub issue
   - Link task and issue

## Analysis Methodology

### Code Quality Analysis

**Static Analysis Tools:**

```bash
# Complexity analysis
radon cc src/ -a -nb

# Maintainability index
radon mi src/ -nb

# Code quality
ruff check src/

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Dependency vulnerabilities
pip-audit
```

**Code Metrics to Check:**

- Cyclomatic complexity (target: \<10)
- Maintainability index (target: >65)
- Test coverage (target: >80%)
- Docstring coverage (target: 100%)
- Type hint coverage (target: 100%)
- Lines of code per function (target: \<50)
- Function parameters (target: \<5)
- Class size (target: \<300 lines)

### Performance Analysis

**Profile Points:**

```python
# API call performance
- Response times
- Rate limiting delays
- Connection overhead
- Parsing time

# Algorithm complexity
- Loop iterations
- Nested loops
- Recursive calls
- Data structure operations

# Memory usage
- Object sizes
- Collection growth
- Cache sizes
- Memory leaks
```

**Benchmarking:**

```bash
# Time profiling
python -m cProfile -o profile.stats -m nhl_scrabble analyze

# Memory profiling
python -m memory_profiler script.py

# Line profiling
kernprof -l -v script.py
```

### Security Analysis

**Security Checklist:**

- [ ] Dependency scanning (pip-audit, safety)
- [ ] Code scanning (bandit, semgrep)
- [ ] Secret detection (detect-secrets)
- [ ] Input validation review
- [ ] Output sanitization review
- [ ] Authentication/authorization check
- [ ] Rate limiting implementation
- [ ] HTTPS/TLS verification
- [ ] Error message information leakage
- [ ] SQL/command injection risks
- [ ] XSS vulnerabilities
- [ ] CSRF protection
- [ ] Security headers
- [ ] Logging sensitive data

### Test Coverage Analysis

**Coverage Gaps:**

```bash
# Run coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Identify gaps
# - Uncovered lines
# - Uncovered branches
# - Missing edge cases
# - Error path coverage
# - Integration test gaps
```

**Test Quality Metrics:**

- Line coverage (target: >80%)
- Branch coverage (target: >75%)
- Test-to-code ratio (target: >1:1)
- Assertion density
- Test duplication
- Flaky tests
- Slow tests (>1s)

## Task Generation Strategy

### Priority Assignment Logic

**CRITICAL Priority:**

- Security vulnerabilities (CVE, high severity)
- Data loss risks
- Application crashes
- Critical functionality broken
- Production blockers

**HIGH Priority:**

- Important bugs affecting users
- Security issues (medium severity)
- Significant performance problems (\<10x slowdown)
- Key feature requests
- Test coverage \<60%

**MEDIUM Priority:**

- Minor bugs
- Performance optimizations (2-10x improvement)
- Nice-to-have features
- Code quality improvements
- Test coverage 60-80%

**LOW Priority:**

- Cosmetic improvements
- Minor refactoring
- Nice-to-have features
- Long-term enhancements
- Test coverage >80%

### Effort Estimation Guidelines

**Small (1-2h):**

- Simple bug fixes
- Configuration changes
- Documentation updates
- Minor refactoring

**Medium (2-4h):**

- Moderate bug fixes
- Feature enhancements
- Refactoring a module
- Adding test coverage

**Large (4-8h):**

- Complex bug fixes
- New features
- Major refactoring
- Integration changes

**Extra Large (8-16h):**

- Architectural changes
- Major features
- System redesign
- Large-scale refactoring

**Epic (16-40h):**

- Complete subsystems
- Web interfaces
- API servers
- Database backends

## Analysis Categories

### 1. Bug Fixes Analysis

**Look for:**

```python
# Error handling gaps
try:
    result = risky_operation()
except Exception:  # Too broad!
    pass  # Silent failure!

# Missing validation
def process(data: str):  # No validation!
    return data.upper()

# Race conditions
# Unclosed resources
# Memory leaks
# Edge cases not handled
```

**Example Findings:**

- Missing NHLApiNotFoundError handling
- Config validation gaps
- Session cleanup safety net needed
- Rate limiting logic incorrect
- Missing exponential backoff

### 2. Optimization Analysis

**Look for:**

```python
# N+1 queries
for team in teams:
    roster = fetch_roster(team)  # Sequential!

# Missing caching
def expensive_operation():
    # No @lru_cache or Redis
    return compute_for_minutes()

# Inefficient algorithms
for i in range(len(items)):  # O(n²)
    for j in range(len(items)):
        if items[i] == items[j]:
            ...

# Unnecessary work
data = [process(x) for x in huge_list]  # Process all
result = data[:10]  # Use only 10!
```

**Example Findings:**

- API response caching opportunity
- Parallel API requests possible
- Lazy report generation
- Memoized scoring functions
- Memory optimization for large datasets

### 3. Enhancement Analysis

**Look for:**

```python
# Missing features users want
# Poor error messages
print("Error")  # Not helpful!

# No progress feedback
for item in huge_list:  # Silent processing
    process(item)

# Limited output formats
# Missing configuration options
# No filtering/sorting
# Hardcoded values
```

**Example Findings:**

- HTML output format
- Progress bars needed
- Interactive mode
- Historical data tracking
- CSV/Excel export
- Custom scoring rules

### 4. New Feature Analysis

**Look for:**

```python
# Missing major capabilities
# No web interface
# No API server
# No database backend
# No authentication
# No notification system
# No plugin architecture
# No offline mode
# No Docker support
```

**Example Findings:**

- Web interface with FastAPI
- REST API server
- PostgreSQL backend
- Redis caching layer
- Webhook notifications
- Docker containerization

### 5. Refactoring Analysis

**Look for:**

```python
# Duplicate code
def report_a():
    setup_common()  # Duplicated
    format_header()  # Duplicated
    do_a_specific()

def report_b():
    setup_common()  # Duplicated
    format_header()  # Duplicated
    do_b_specific()

# God classes
class DoEverything:  # 1000+ lines
    def fetch_data(self): ...
    def process_data(self): ...
    def format_output(self): ...
    def send_email(self): ...
    # 50 more methods...

# Long functions
def monolithic(data):  # 200 lines
    # Everything in one function

# No abstractions
# Tight coupling
# Poor naming
```

**Example Findings:**

- Extract retry logic to decorator
- Consolidate report base classes
- Improve type safety with Pydantic
- Unified config management
- Error handling strategy

### 6. Security Analysis

**Look for:**

```python
# Vulnerabilities
import subprocess
subprocess.call(user_input)  # Command injection!

# Missing validation
def api_call(url):  # SSRF risk!
    return requests.get(url)

# Secret exposure
API_KEY = "hardcoded-secret"  # In code!
print(f"Error: {password}")  # In logs!

# Missing security headers
# No rate limiting
# No input sanitization
# Weak authentication
```

**Example Findings:**

- Add Dependabot for dependencies
- Create SECURITY.md policy
- Implement log sanitization
- Input validation layer
- SSRF protection
- Rate limit enforcement

## Example Output

```
🔍 Project Analysis Complete

Repository: NHL Scrabble Score Analyzer
Python Files: 42 modules
Test Files: 36 tests
Configuration: 8 files
Documentation: 18 files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Analysis Results

🐛 Bug Fixes Identified: 6
  CRITICAL (1):
    - Fix config validation (data loss risk)
  HIGH (2):
    - Implement NHLApiNotFoundError properly
    - Add session cleanup safety net
  MEDIUM (2):
    - Fix rate limiting logic
    - Implement exponential backoff
  LOW (1):
    - Validate CLI output paths

⚡ Optimizations Identified: 6
  HIGH (1):
    - Implement API response cache (5-10x speedup)
  MEDIUM (2):
    - Parallel API requests (2-3x speedup)
    - Lazy report generation
  LOW (3):
    - Memoized scoring functions
    - Memory optimization
    - Log level optimization

✨ Enhancements Identified: 10
  MEDIUM (3):
    - Implement HTML output
    - Add progress bars
    - Interactive mode
  LOW (7):
    - Historical data tracking
    - CSV/Excel export
    - Filtering options
    - Custom scoring rules
    - Statistics dashboard
    - Watch mode
    - Player search

🚀 New Features Identified: 10
  MEDIUM (1):
    - REST API server
  LOW (9):
    - Build web interface
    - Database backend
    - Notification system
    - Player comparison tool
    - Offline mode
    - Config profiles
    - Plugin system
    - Docker support
    - Data export/import

🔧 Refactoring Identified: 6
  MEDIUM (2):
    - Extract retry logic
    - Consolidate reports
  LOW (4):
    - Improve type safety
    - Unified config management
    - Error handling strategy
    - Dependency injection

🔒 Security Issues Identified: 10
  CRITICAL (1):
    - Add GitHub Dependabot
  HIGH (2):
    - Create SECURITY.md policy
    - Implement log sanitization
  MEDIUM (4):
    - Input validation layer
    - SSRF protection
    - Rate limit enforcement
    - DoS prevention
  LOW (3):
    - SSL verification
    - PII logging prevention
    - Config injection protection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Total Tasks to Create: 48

Estimated Effort:
  Bug Fixes: 8.5-14h
  Optimizations: 20-30h
  Enhancements: 40-60h
  New Features: 80-120h
  Refactoring: 15-25h
  Security: 10-15h

Total: 173.5-264 hours

Generate all 48 tasks? [y/N]
```

After confirmation:

```
✅ Creating tasks...

📁 Bug Fixes (6 tasks)
  ✅ tasks/bug-fixes/001-config-validation.md → Issue #52
  ✅ tasks/bug-fixes/002-unused-exception.md → Issue #53
  ✅ tasks/bug-fixes/003-session-cleanup.md → Issue #54
  ✅ tasks/bug-fixes/004-rate-limiting.md → Issue #55
  ✅ tasks/bug-fixes/005-exponential-backoff.md → Issue #56
  ✅ tasks/bug-fixes/006-output-validation.md → Issue #57

⚡ Optimizations (6 tasks)
  ✅ tasks/optimization/001-api-caching.md → Issue #58
  ✅ tasks/optimization/002-parallel-requests.md → Issue #59
  ✅ tasks/optimization/003-lazy-reports.md → Issue #60
  ✅ tasks/optimization/004-memoized-scoring.md → Issue #61
  ✅ tasks/optimization/005-memory-opt.md → Issue #62
  ✅ tasks/optimization/006-log-optimization.md → Issue #63

✨ Enhancements (10 tasks)
  ✅ tasks/enhancement/001-html-output.md → Issue #64
  ✅ tasks/enhancement/002-progress-bars.md → Issue #65
  ... 8 more

🚀 New Features (10 tasks)
  ✅ tasks/new-features/001-web-interface.md → Issue #74
  ✅ tasks/new-features/002-rest-api.md → Issue #75
  ... 8 more

🔧 Refactoring (6 tasks)
  ✅ tasks/refactoring/001-retry-logic.md → Issue #84
  ... 5 more

🔒 Security (10 tasks)
  ✅ tasks/security/001-dependabot.md → Issue #90
  ✅ tasks/security/002-security-policy.md → Issue #91
  ... 8 more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Task Generation Complete!

Created: 48 task files
GitHub Issues: #52-#99
Updated: tasks/README.md

Next Steps:
1. Review tasks: ls -la tasks/*/
2. Check GitHub issues: gh issue list
3. Start with CRITICAL tasks
4. Follow recommended implementation order in tasks/README.md
```

## Usage

```bash
# Full project analysis
/analyze-project

# The command will:
# 1. Comprehensively analyze the entire project
# 2. Identify all improvement opportunities
# 3. Categorize and prioritize each finding
# 4. Show summary with task counts and effort estimates
# 5. Ask for confirmation
# 6. Generate all task files using /create-task
# 7. Create GitHub issues for all tasks
# 8. Update tasks/README.md
# 9. Provide summary and next steps
```

## Configuration Options

Can be customized to focus on specific areas:

```bash
# Focus on specific categories
/analyze-project --focus=security,bugs

# Set minimum priority
/analyze-project --min-priority=HIGH

# Limit task count
/analyze-project --max-tasks=20

# Skip GitHub issue creation
/analyze-project --no-issues

# Dry run (analysis only, no task creation)
/analyze-project --dry-run
```

## Analysis Tools Used

**Static Analysis:**

- ruff - Linting and code quality
- mypy - Type checking
- bandit - Security scanning
- radon - Complexity analysis
- interrogate - Docstring coverage
- vulture - Dead code detection

**Dynamic Analysis:**

- pytest --cov - Test coverage
- cProfile - Performance profiling
- memory_profiler - Memory analysis
- locust - Load testing (if applicable)

**Security Tools:**

- pip-audit - Dependency vulnerabilities
- safety - Known security issues
- detect-secrets - Secret scanning
- semgrep - Code patterns

**Dependency Analysis:**

- deptry - Dependency checker
- pip-audit - Vulnerability scanner
- pip list --outdated - Update checker

## Best Practices

**Analysis Frequency:**

- **Weekly**: Quick scan for critical issues
- **Sprint Start**: Full analysis for sprint planning
- **Before Release**: Comprehensive security and quality check
- **Quarterly**: Deep dive with manual review

**Task Management:**

- Review generated tasks before implementation
- Adjust priorities based on business needs
- Group related tasks into epics
- Track progress in tasks/README.md

**Quality Gates:**

Don't generate tasks for:

- Issues already documented
- Design decisions (not bugs)
- External dependencies (not in our control)
- Known limitations (documented)

## Integration

This command integrates with:

- `/create-task` - Task generation
- `/update-docs` - Documentation analysis
- `/security-review` - Security focus
- `/optimize` - Performance focus
- GitHub Issues - Issue tracking
- tasks/README.md - Task index

## Safety Considerations

Before generating tasks:

- ✅ Ensure clean git state
- ✅ Review analysis results
- ✅ Confirm task count is reasonable
- ✅ Check GitHub API rate limits
- ✅ Verify tasks/ directory structure
- ✅ Backup existing tasks if needed

## Output Files

**Generated files:**

```
tasks/
├── bug-fixes/
│   ├── 001-config-validation.md
│   ├── 002-unused-exception.md
│   └── ... (all bug fix tasks)
├── optimization/
│   ├── 001-api-caching.md
│   └── ... (all optimization tasks)
├── enhancement/
│   └── ... (all enhancement tasks)
├── new-features/
│   └── ... (all new feature tasks)
├── refactoring/
│   └── ... (all refactoring tasks)
├── security/
│   └── ... (all security tasks)
└── README.md (updated with all tasks)
```

**GitHub Issues:**

- One issue per task
- Proper labels (category + priority)
- Linked to task files
- Milestone assignment (if configured)

## Tips

- Run this command after major changes
- Use to plan sprints and releases
- Great for identifying technical debt
- Helps with roadmap planning
- Useful for new team members
- Creates comprehensive backlog
- Identifies quick wins vs. long-term work

## Related Commands

- `/create-task` - Create individual task
- `/update-docs` - Update documentation
- `/security-review` - Security-focused review
- `/optimize` - Performance-focused review
- `/gh:list-issues` - View created issues
- `/git:commit` - Commit generated tasks

## Notes

- Analysis is read-only until task generation
- Can be run multiple times (generates new IDs)
- Skips already-documented tasks (checks existing files)
- Updates existing tasks if pattern detected
- Creates single commit with all task files
- Respects .gitignore and excluded paths
- Can be interrupted and resumed
- Generates detailed analysis log for review
