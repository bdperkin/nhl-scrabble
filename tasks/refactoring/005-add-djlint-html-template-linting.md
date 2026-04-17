# Add djlint for HTML and Jinja2 Template Linting

**GitHub Issue**: #127 - https://github.com/bdperkin/nhl-scrabble/issues/127

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

30-60 minutes

## Description

Add djlint for automated linting and formatting of HTML templates with Jinja2 syntax to ensure proper template syntax, consistent formatting, and valid HTML5 structure.

Currently, the project has HTML templates (`src/nhl_scrabble/templates/report.html`) with Jinja2 syntax that have no automated validation or formatting. Template errors only surface at runtime when the template is rendered, making debugging difficult and potentially allowing broken templates into production.

djlint provides:

- Template syntax validation (Jinja2, Django, Nunjucks, etc.)
- HTML structure validation (valid HTML5)
- Consistent formatting and indentation
- Accessibility issue detection
- Integration with pre-commit hooks and CI
- Automatic fixing of common issues

**Impact**: Caught template syntax errors before runtime, consistent HTML/template formatting, improved HTML quality and accessibility, prevented broken templates in production

**ROI**: Moderate - low setup effort (30-60 min), value depends on template usage (currently 1 template)

## Current State

Project has one HTML template with Jinja2 syntax, no automated validation:

**Template file** (`src/nhl_scrabble/templates/report.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHL Scrabble Score Analysis - {{ timestamp }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        /* ... more CSS ... */
    </style>
</head>
<body>
    <h1>NHL Scrabble Score Analysis</h1>
    <p>Generated: {{ timestamp }}</p>

    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        {{ section.content | safe }}
    </div>
    {% endfor %}
</body>
</html>
```

**Problems**:

- No template syntax validation (errors only caught at runtime)
- No HTML structure validation
- Inconsistent formatting possible
- No accessibility checks
- Manual review required

**Missing tool**:

- No djlint in dependencies
- No template linting in pre-commit
- No template checks in CI
- Could have template syntax errors and not know until runtime

## Proposed Solution

Add djlint with configuration for Jinja2 templates:

**Step 1: Add djlint to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
    "djlint>=1.34.0",  # Add HTML/template linting and formatting
    # ... other dev dependencies
]
```

**Step 2: Configure djlint**:

```toml
# pyproject.toml
[tool.djlint]
# Template profile (jinja, django, nunjucks, handlebars, twig, angular, golang)
profile = "jinja"

# Indentation
indent = 4
max_line_length = 120
max_attribute_length = 80

# Formatting options
format_css = true
format_js = true
preserve_blank_lines = true
preserve_leading_space = false

# Linting rules
ignore = "H006,H021,H030,H031"  # Adjust based on project needs
# H006: Img tag without alt attribute (exclude if decorative images)
# H021: Inline styles (we have inline <style> in template)
# H030: Consider meta keywords (outdated SEO)
# H031: Consider meta description (may not be needed for reports)

# Exclude patterns
exclude = [
    ".git",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "htmlcov",
    "_build",
    "dist",
]

# Extension matching
extension = "html"

# File patterns
include = "H"  # HTML files
```

**Step 3: Add pre-commit hook**:

```yaml
# .pre-commit-config.yaml
# Add after mdformat, before doc8
- repo: https://github.com/Riverside-Healthcare/djLint
  rev: v1.34.1
  hooks:
    - id: djlint-reformat-jinja
      name: djlint (reformat Jinja2 templates)
      description: Lint and format HTML templates with Jinja2 syntax
      files: \.(html|jinja|jinja2)$
      # Reformat automatically

    - id: djlint-jinja
      name: djlint (check Jinja2 templates)
      description: Lint HTML templates with Jinja2 syntax
      files: \.(html|jinja|jinja2)$
      # Check only (don't auto-fix)
```

**Step 4: Add tox environment**:

```ini
# tox.ini
[testenv:djlint]
description = Lint and format HTML/Jinja2 templates
skip_install = true
deps =
    djlint>=1.34.0
commands_pre =
    djlint --version
commands =
    # Check templates (lint only)
    djlint src/ --check --profile=jinja --lint

    # Format templates (reformat)
    djlint src/ --reformat --profile=jinja
allowlist_externals =
    djlint
labels = quality, format

[testenv:djlint-check]
description = Check HTML/Jinja2 template linting (no formatting)
skip_install = true
deps =
    djlint>=1.34.0
commands =
    djlint src/ --check --profile=jinja --lint
labels = quality
```

**Step 5: CLI usage examples**:

```bash
# Lint templates (check only)
djlint src/nhl_scrabble/templates/ --profile=jinja --lint

# Format templates (reformat)
djlint src/nhl_scrabble/templates/ --profile=jinja --reformat

# Check specific file
djlint src/nhl_scrabble/templates/report.html --profile=jinja --lint

# Via tox
tox -e djlint
tox -e djlint-check

# Via pre-commit
pre-commit run djlint-jinja --all-files
pre-commit run djlint-reformat-jinja --all-files
```

**Step 6: Example output**:

```bash
$ djlint src/nhl_scrabble/templates/report.html --profile=jinja --lint

Linting report.html
--------------------
H025 1:1 Tag seems to be an extra closing tag.
H011 5:4 Attribute values should be double quoted.
T001 12:8 Variables should be wrapped in whitespace.

3 files linted.
3 errors found.
```

**Step 7: Auto-formatting example**:

```html
<!-- Before djlint -->
<div class="section">
<h2>{{ section.title }}</h2>
{{ section.content | safe }}
</div>

<!-- After djlint --reformat -->
<div class="section">
    <h2>{{ section.title }}</h2>
    {{ section.content | safe }}
</div>
```

## Implementation Steps

1. **Add djlint to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.dev]`
   - Add `djlint>=1.34.0`

1. **Configure djlint**:

   - Add `[tool.djlint]` section to `pyproject.toml`
   - Set profile to "jinja"
   - Configure indent, line length, rules

1. **Add tox environments**:

   - Create `[testenv:djlint]` in `tox.ini`
   - Create `[testenv:djlint-check]` for CI

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Run initial check**:

   - Run `djlint src/ --profile=jinja --lint`
   - Identify any template issues
   - Fix issues or adjust ignore list

1. **Add pre-commit hooks**:

   - Add djlint-reformat-jinja (auto-fix)
   - Add djlint-jinja (check only)
   - Test hooks trigger on template changes

1. **(Optional) Add to CI**:

   - Add djlint-check to CI matrix
   - Ensures templates pass linting in PRs

1. **Document usage**:

   - Add to CONTRIBUTING.md
   - Explain template formatting standards
   - Document ignored rules and why

## Testing Strategy

**Initial Template Check**:

```bash
# Check current template
djlint src/nhl_scrabble/templates/report.html --profile=jinja --lint

# Expected: May find formatting or structure issues
# Review and decide which to fix vs ignore
```

**Formatting Test**:

```bash
# Backup template
cp src/nhl_scrabble/templates/report.html report.html.bak

# Reformat
djlint src/nhl_scrabble/templates/report.html --profile=jinja --reformat

# Compare
diff report.html.bak src/nhl_scrabble/templates/report.html

# Verify template still works
pytest tests/unit/test_html_report.py

# If good, keep changes; if broken, revert and adjust config
```

**Pre-commit Integration**:

```bash
# Test pre-commit hooks
pre-commit run djlint-jinja --all-files

# Make change to template
echo "    " >> src/nhl_scrabble/templates/report.html

# Verify hook catches it
pre-commit run djlint-jinja --files src/nhl_scrabble/templates/report.html

# Expected: Hook detects trailing whitespace
```

**CI Integration Test**:

```bash
# Via tox (simulates CI)
tox -e djlint-check

# Expected: Exit 0 if templates pass linting
```

## Acceptance Criteria

- [ ] djlint added to `[project.optional-dependencies.dev]`
- [ ] Lock file updated with djlint
- [ ] `[tool.djlint]` configuration added to `pyproject.toml`
- [ ] Profile set to "jinja"
- [ ] Appropriate rules configured/ignored
- [ ] `[testenv:djlint]` added to `tox.ini`
- [ ] `[testenv:djlint-check]` added for CI
- [ ] Pre-commit hooks added (djlint-reformat-jinja, djlint-jinja)
- [ ] Running `djlint src/` lints all templates
- [ ] Running `djlint src/ --reformat` formats consistently
- [ ] Current template passes linting (after fixes or ignore adjustments)
- [ ] Template still renders correctly after formatting
- [ ] Pre-commit hooks trigger on template changes
- [ ] Documentation updated (CONTRIBUTING.md)

## Related Files

- `pyproject.toml` - Add djlint dependency and configuration
- `tox.ini` - Add djlint tox environments
- `.pre-commit-config.yaml` - Add djlint hooks
- `src/nhl_scrabble/templates/report.html` - HTML template to be linted
- `src/nhl_scrabble/templates/*.html` - Any future templates
- `CONTRIBUTING.md` - Document template formatting standards
- `uv.lock` - Updated with djlint

## Dependencies

**Recommended implementation order**:

- Can be implemented independently
- Low priority (only 1 template currently)
- Higher value if more templates added

**No blocking dependencies** - Can be implemented standalone

**Works with**:

- All existing pre-commit hooks
- Tox environments
- CI workflows

## Additional Notes

**Why djlint?**

- **Template-aware**: Understands Jinja2 syntax (unlike general HTML linters)
- **Comprehensive**: Lints HTML structure + template logic
- **Auto-formatting**: Consistent template formatting
- **Accessibility**: Detects common accessibility issues
- **Python-based**: Fits project ecosystem
- **Active**: Well-maintained, 1k+ stars

**How djlint Works**:

```
Template analysis:
  1. Parse template (HTML + Jinja2 syntax)
  2. Validate HTML structure (W3C rules)
  3. Check template syntax (Jinja2 correctness)
  4. Enforce formatting rules (indentation, line length)
  5. Detect accessibility issues (alt text, ARIA)
  6. Generate report or reformat
```

**djlint Profiles**:

| Profile    | Template Engine         | Syntax            |
| ---------- | ----------------------- | ----------------- |
| **jinja**  | Jinja2 (Flask, Ansible) | `{{ }}`, `{% %}`  |
| django     | Django templates        | `{{ }}`, `{% %}`  |
| nunjucks   | Nunjucks (Node.js)      | `{{ }}`, `{% %}`  |
| handlebars | Handlebars              | `{{ }}`, `{{# }}` |
| twig       | Twig (Symfony)          | `{{ }}`, `{% %}`  |
| golang     | Go templates            | `{{ }}`           |

**Common Lint Rules**:

| Code     | Rule                               | Example                     |
| -------- | ---------------------------------- | --------------------------- |
| **H005** | HTML tag is empty                  | `<div></div>`               |
| **H006** | Img without alt                    | `<img src="...">`           |
| **H013** | Img with hard-coded width/height   | `<img width="100">`         |
| **H020** | Empty block tag                    | `{% block %}{% endblock %}` |
| **H021** | Inline styles                      | `<div style="...">`         |
| **H025** | Extra closing tag                  | `</div></div>`              |
| **T001** | Variables need whitespace          | `{{var}}` → `{{ var }}`     |
| **T002** | Double quotes preferred            | `{% if x %}`                |
| **J004** | Static files should use `static()` | Django-specific             |

**Configuration Options**:

```toml
[tool.djlint]
# Template profile
profile = "jinja"  # or django, nunjucks, etc.

# Formatting
indent = 4  # Spaces for indentation
max_line_length = 120
max_attribute_length = 80
format_css = true  # Format <style> blocks
format_js = true  # Format <script> blocks
preserve_blank_lines = true
preserve_leading_space = false

# Linting
ignore = "H021"  # Comma-separated rule codes to ignore
include = "H,T"  # Include HTML and template rules

# File handling
extension = "html"  # File extension to process
exclude = [".git", ".tox"]  # Paths to exclude

# Behavior
require_pragma = false  # Require "djlint:on" comment
```

**Ignore Rules Rationale** (for this project):

```toml
ignore = "H006,H021,H030,H031"

# H006: Img without alt
# - May have decorative images where alt="" is appropriate
# - Or handle alt text dynamically in template

# H021: Inline styles
# - Template has <style> block inline (acceptable for single-file template)
# - Not using external CSS file

# H030: Consider meta keywords
# - Meta keywords are outdated for SEO
# - Not relevant for HTML reports

# H031: Consider meta description
# - May not be needed for generated reports
# - Not a webpage for search engines
```

**Accessibility Benefits**:

```html
<!-- djlint detects missing alt text -->
<img src="{{ player.photo }}">
<!-- Fix: -->
<img src="{{ player.photo }}" alt="{{ player.name }} headshot">

<!-- djlint detects missing labels -->
<input type="text" name="search">
<!-- Fix: -->
<label for="search">Search:</label>
<input type="text" id="search" name="search">

<!-- djlint detects low contrast -->
<span style="color: #ccc; background: #ddd;">Text</span>
<!-- Fix: Use higher contrast colors -->
```

**Integration with Existing Tools**:

| Tool             | Purpose             | Interaction with djlint                |
| ---------------- | ------------------- | -------------------------------------- |
| **blacken-docs** | Format code in docs | Doesn't touch HTML templates           |
| **mdformat**     | Format markdown     | No overlap                             |
| **prettier**     | Format HTML/CSS/JS  | Alternative (djlint is template-aware) |
| **htmlhint**     | Lint HTML           | Alternative (djlint is Python-based)   |

**CLI Examples**:

```bash
# Basic lint
djlint src/nhl_scrabble/templates/

# Lint with stats
djlint src/ --profile=jinja --lint --statistics

# Reformat in-place
djlint src/ --profile=jinja --reformat

# Check only (CI mode)
djlint src/ --profile=jinja --check --lint

# Specific file
djlint src/nhl_scrabble/templates/report.html

# Custom config
djlint src/ --indent=2 --max-line-length=100

# Quiet mode
djlint src/ --quiet

# Show configuration
djlint --show-config
```

**When djlint is Most Valuable**:

1. **Multiple templates**: More templates = more value
1. **Team collaboration**: Ensures consistent template style
1. **Template-heavy projects**: Django/Flask apps with many views
1. **Accessibility requirements**: Need to meet WCAG standards
1. **Complex templates**: Nested loops, conditionals, etc.

**Current Project Scope**:

- **1 template** currently (`report.html`)
- **Low complexity** (simple Jinja2 usage)
- **No accessibility requirements** (internal reports)
- **Value**: LOW to MODERATE

**Future Value** (if templates grow):

- Add HTML email templates
- Add multiple report formats
- Add dashboard templates
- Value increases significantly

**Alternative Tools Considered**:

| Tool         | Pros                | Cons                |
| ------------ | ------------------- | ------------------- |
| **prettier** | Handles HTML/CSS/JS | Not template-aware  |
| **htmlhint** | Fast HTML linting   | No template support |
| **html5lib** | Validates HTML5     | No formatting       |
| **tidy**     | Old but reliable    | No template support |

**Best Practices**:

```bash
# ✅ Good: Run before committing template changes
djlint src/nhl_scrabble/templates/ --profile=jinja --reformat
git add src/nhl_scrabble/templates/
git commit -m "feat: Update report template"

# ✅ Good: Check in CI
tox -e djlint-check  # Part of CI pipeline

# ✅ Good: Ignore project-specific rules
# Document WHY in pyproject.toml comments

# ❌ Bad: Ignoring all accessibility rules
# Accessibility is important even for internal tools

# ❌ Bad: Not testing after reformatting
# Always verify template still renders correctly
```

**Common Questions**:

**Q: Will djlint break my templates?**
A: No, `--check` mode only reports issues. Use `--reformat` carefully and test.

**Q: Does it work with inline CSS/JS?**
A: Yes, `format_css=true` and `format_js=true` format `<style>` and `<script>` blocks.

**Q: Can I use it with Vue/React templates?**
A: Not recommended. djlint is for server-side templates (Jinja2, Django, etc.).

**Q: Is it slow?**
A: No, very fast. Lints 100 templates in ~1 second.

**Q: Should I run in pre-commit?**
A: Yes, but consider performance. Can use `--check` instead of `--reformat` in pre-commit.

## Implementation Notes

*To be filled during implementation:*

- Number of lint issues found initially
- Rules that were ignored and justification
- Whether reformatting broke template rendering
- Performance impact of pre-commit hook
- Whether added to CI or kept local-only
- Developer feedback on template linting
