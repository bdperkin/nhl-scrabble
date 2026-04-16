# Implement Procida's Documentation Model (Diátaxis Framework)

**GitHub Issue**: #63 - https://github.com/bdperkin/nhl-scrabble/issues/63

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

8-12 hours

## Description

Reorganize and enhance project documentation following Daniele Procida's documentation framework (Diátaxis), which divides documentation into four distinct quadrants based on user needs and learning modes:

1. **Tutorials** - Learning-oriented lessons for beginners
2. **How-to Guides** - Action-oriented guides solving specific problems
3. **Reference** - Technical descriptions of machinery (APIs, code)
4. **Explanation** - Background information and high-level architectural understanding

This systematic approach improves documentation discoverability, usability, and completeness by organizing content according to what users need to accomplish.

## Current State

The project has comprehensive documentation, but it's not systematically organized:

**Existing Documentation:**
```
nhl-scrabble/
├── README.md              # Mix of tutorial, reference, and explanation
├── CONTRIBUTING.md        # Mix of how-to and explanation
├── CHANGELOG.md           # Historical reference
├── CLAUDE.md              # Mix of reference and explanation
├── SECURITY.md            # Policy reference
├── SUPPORT.md             # How-to and reference
├── LICENSE                # Legal reference
└── docs/
    ├── MAKEFILE.md        # Reference documentation
    ├── DEVELOPMENT.md     # Mix of how-to and reference
    ├── TOX.md             # Reference documentation
    ├── TOX-UV.md          # How-to and reference
    ├── UV.md              # Mix of explanation and reference
    ├── UV-QUICKREF.md     # Quick reference
    ├── UV-ECOSYSTEM.md    # Explanation and reference
    └── PRECOMMIT-UV.md    # How-to and reference
```

**Issues:**
- Content mixes different documentation types in single files
- No clear entry point for beginners (no dedicated tutorial)
- How-to guides scattered across multiple files
- Reference documentation mixed with explanations
- Hard to find specific information quickly
- No architectural explanations separate from technical details

## Proposed Solution

Reorganize documentation following the Diátaxis framework with four distinct directories:

### 1. Tutorials (Learning-Oriented)

**Purpose**: Take beginners by the hand through complete workflows

**Create**: `docs/tutorials/`

```markdown
docs/tutorials/
├── README.md                    # Tutorial index
├── 01-getting-started.md        # First-time setup and basic usage
├── 02-understanding-output.md   # Understanding the reports
└── 03-first-contribution.md     # Making your first contribution
```

**Example: `docs/tutorials/01-getting-started.md`**
```markdown
# Getting Started with NHL Scrabble

In this tutorial, you'll learn how to:
- Install NHL Scrabble on your system
- Run your first analysis
- Understand the output
- Customize basic settings

## Prerequisites

- Python 3.10 or higher installed
- Basic command-line knowledge
- Internet connection (to fetch NHL data)

## Step 1: Install NHL Scrabble

Clone the repository:
```bash
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble
```

[... detailed step-by-step walkthrough ...]

## What You've Learned

By completing this tutorial, you've:
- ✅ Installed NHL Scrabble
- ✅ Run your first analysis
- ✅ Understood the Scrabble scoring system
- ✅ Customized output settings

## Next Steps

- Try the [Understanding Output Tutorial](02-understanding-output.md)
- Explore [How-to Guides](../how-to/) for specific tasks
- Read [Architecture Explanation](../explanation/architecture.md) to understand how it works
```

### 2. How-to Guides (Problem-Oriented)

**Purpose**: Guide users through solving specific, real-world problems

**Create**: `docs/how-to/`

```markdown
docs/how-to/
├── README.md                        # How-to index
├── installation.md                  # Installation variations
├── add-report-type.md               # Add a new report generator
├── configure-api-settings.md        # Configure NHL API settings
├── run-tests.md                     # Run different test configurations
├── debug-api-issues.md              # Debug API connection problems
├── use-uv-package-manager.md        # Use UV for fast package management
├── setup-pre-commit-hooks.md        # Set up and customize pre-commit
├── customize-output-format.md       # Customize report formatting
├── export-to-json.md                # Export data to JSON
└── contribute-code.md               # Contribute code changes
```

**Example: `docs/how-to/add-report-type.md`**
```markdown
# How to Add a New Report Type

This guide shows you how to create a custom report generator for NHL Scrabble.

## Problem

You want to add a new type of report (e.g., player comparison report) to the NHL Scrabble analyzer.

## Solution

Follow these steps to create and integrate a new report type:

### 1. Create Report Class

Create a new file `src/nhl_scrabble/reports/your_report.py`:

```python
from nhl_scrabble.reports.base import BaseReport

class YourReport(BaseReport):
    """Your custom report generator."""
    
    def generate(self) -> str:
        # Implementation
        pass
```

### 2. Add Tests

[... specific steps with code examples ...]

### 3. Register Report

[... configuration steps ...]

## Verification

Test your new report:
```bash
pytest tests/unit/test_your_report.py -vv
```

## Related

- [Reference: Report API](../reference/code-api.md#reports)
- [Explanation: Report Architecture](../explanation/report-system.md)
```

### 3. Reference (Information-Oriented)

**Purpose**: Provide technical descriptions of the machinery

**Create**: `docs/reference/`

```markdown
docs/reference/
├── README.md                # Reference index
├── cli.md                   # Complete CLI command reference
├── configuration.md         # All configuration options
├── nhl-api.md               # NHL API endpoints used
├── code-api.md              # Python API for library usage
├── makefile.md              # Makefile targets (move from docs/MAKEFILE.md)
├── environment-variables.md # All environment variables
└── scrabble-values.md       # Letter values and scoring rules
```

**Example: `docs/reference/cli.md`**
```markdown
# CLI Reference

Complete reference for the `nhl-scrabble` command-line interface.

## Commands

### `nhl-scrabble analyze`

Run the NHL Scrabble score analyzer.

**Usage:**
```bash
nhl-scrabble analyze [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | choice | `text` | Output format: `text` or `json` |
| `-o, --output` | path | stdout | Output file path |
| `-v, --verbose` | flag | false | Enable verbose logging |
| `--top-players` | int | 20 | Number of top players to show |
| `--top-team-players` | int | 5 | Top players per team |

**Examples:**

```bash
# Basic usage
nhl-scrabble analyze

# JSON output to file
nhl-scrabble analyze --format json --output report.json

# Verbose mode with more players
nhl-scrabble analyze --verbose --top-players 50
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | API error |
| 3 | Configuration error |

## Environment Variables

See [Environment Variables Reference](environment-variables.md).
```

### 4. Explanation (Understanding-Oriented)

**Purpose**: Clarify and illuminate topics with background and context

**Create**: `docs/explanation/`

```markdown
docs/explanation/
├── README.md                  # Explanation index
├── architecture.md            # System architecture overview
├── why-scrabble-scoring.md    # Why use Scrabble scores?
├── nhl-api-strategy.md        # NHL API integration approach
├── testing-philosophy.md      # Testing strategy and rationale
├── uv-ecosystem.md            # UV benefits and integration (move from docs/UV-ECOSYSTEM.md)
├── report-system.md           # How the report system works
└── development-workflow.md    # Development process and decisions
```

**Example: `docs/explanation/architecture.md`**
```markdown
# Architecture Overview

Understanding the NHL Scrabble Score Analyzer's architecture.

## System Design

NHL Scrabble is designed as a modular Python package with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                    CLI Layer                         │
│           (click-based command interface)            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  Processors  │  │   Scoring    │                │
│  └──────┬───────┘  └──────┬───────┘                │
└─────────┼──────────────────┼──────────────────────┘
          │                  │
┌─────────▼──────────────────▼──────────────────────┐
│               Data Layer                           │
│  ┌──────────────┐  ┌──────────────┐               │
│  │   Models     │  │  API Client  │               │
│  └──────────────┘  └──────┬───────┘               │
└────────────────────────────┼───────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   NHL API        │
                    │  (External)      │
                    └──────────────────┘
```

## Why This Architecture?

### Separation of Concerns

Each layer has a specific responsibility:

1. **CLI Layer**: User interface and command handling
   - Minimal logic, delegates to business layer
   - Handles argument parsing and validation
   - Manages output formatting selection

2. **Business Logic Layer**: Core functionality
   - **Processors**: Aggregate and transform data
   - **Scoring**: Calculate Scrabble scores
   - **Reports**: Generate various report types

3. **Data Layer**: Data acquisition and modeling
   - **Models**: Type-safe Pydantic models
   - **API Client**: NHL API integration with retry logic

[... detailed explanation continues ...]

## Trade-offs and Decisions

### Why Pydantic?

We chose Pydantic for data modeling because:
- Type safety at runtime
- Automatic validation
- JSON serialization
- Clear error messages

[... more explanations ...]
```

### Directory Structure Migration

**Move and reorganize existing content:**

1. **Create new directories**:
   ```bash
   mkdir -p docs/{tutorials,how-to,reference,explanation}
   ```

2. **Migrate existing docs**:
   ```
   docs/MAKEFILE.md → docs/reference/makefile.md
   docs/UV-ECOSYSTEM.md → docs/explanation/uv-ecosystem.md
   docs/TOX.md + docs/TOX-UV.md → docs/how-to/use-tox.md + docs/reference/tox.md
   docs/UV.md + docs/UV-QUICKREF.md → docs/how-to/use-uv.md + docs/reference/uv.md
   docs/PRECOMMIT-UV.md → docs/how-to/setup-pre-commit-hooks.md
   docs/DEVELOPMENT.md → Split into tutorials, how-to, and explanation
   ```

3. **Update cross-references**: Update all internal links to new locations

4. **Create index files**: Each directory gets a README.md index

### Update README.md

Update the main README.md to serve as a navigation hub:

```markdown
## Documentation

Documentation is organized by purpose:

- **[Tutorials](docs/tutorials/)** - Step-by-step lessons for beginners
  - [Getting Started](docs/tutorials/01-getting-started.md)
  - [Understanding Output](docs/tutorials/02-understanding-output.md)
  
- **[How-to Guides](docs/how-to/)** - Solutions to specific problems
  - [Add a Report Type](docs/how-to/add-report-type.md)
  - [Configure API Settings](docs/how-to/configure-api-settings.md)
  - [Run Tests](docs/how-to/run-tests.md)
  
- **[Reference](docs/reference/)** - Technical specifications
  - [CLI Reference](docs/reference/cli.md)
  - [Configuration](docs/reference/configuration.md)
  - [Code API](docs/reference/code-api.md)
  
- **[Explanation](docs/explanation/)** - Background and concepts
  - [Architecture](docs/explanation/architecture.md)
  - [Why Scrabble Scoring?](docs/explanation/why-scrabble-scoring.md)
  - [Testing Philosophy](docs/explanation/testing-philosophy.md)

### Community

- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Support](SUPPORT.md)
```

## Implementation Steps

1. **Create directory structure**
   ```bash
   mkdir -p docs/{tutorials,how-to,reference,explanation}
   ```

2. **Create tutorial content** (3-4h)
   - Write `docs/tutorials/01-getting-started.md`
   - Write `docs/tutorials/02-understanding-output.md`
   - Write `docs/tutorials/03-first-contribution.md`
   - Create `docs/tutorials/README.md` index

3. **Create how-to guides** (2-3h)
   - Write 8-10 problem-focused guides
   - Create `docs/how-to/README.md` index
   - Migrate relevant content from CONTRIBUTING.md

4. **Create reference documentation** (2-3h)
   - Write `docs/reference/cli.md`
   - Write `docs/reference/configuration.md`
   - Write `docs/reference/code-api.md`
   - Migrate `docs/MAKEFILE.md` → `docs/reference/makefile.md`
   - Create `docs/reference/README.md` index

5. **Create explanations** (1-2h)
   - Write `docs/explanation/architecture.md`
   - Write `docs/explanation/why-scrabble-scoring.md`
   - Migrate `docs/UV-ECOSYSTEM.md` → `docs/explanation/uv-ecosystem.md`
   - Create `docs/explanation/README.md` index

6. **Update navigation** (1h)
   - Update README.md with new structure
   - Update CONTRIBUTING.md with new doc references
   - Update CLAUDE.md with new doc references
   - Create cross-references between docs

7. **Clean up** (30min)
   - Remove old doc files (keep for reference initially)
   - Update all internal links
   - Verify all links work
   - Run documentation linters

## Testing Strategy

### Manual Verification

1. **Navigation test**: Verify all links work
   ```bash
   # Use markdown link checker
   npm install -g markdown-link-check
   find docs -name "*.md" -exec markdown-link-check {} \;
   ```

2. **Completeness test**: Ensure all documentation types covered
   - ✅ At least 2 tutorials
   - ✅ At least 8 how-to guides
   - ✅ Complete reference for CLI, config, API
   - ✅ At least 3 explanations

3. **Readability test**: Have someone unfamiliar with the project:
   - Follow a tutorial from scratch
   - Find and use a how-to guide
   - Look up something in reference
   - Read an explanation

### Automated Checks

1. **Link checking**: All internal links must work
2. **Markdown linting**: `pymarkdown` must pass
3. **Spelling**: `codespell` must pass
4. **Formatting**: `mdformat` must pass

## Acceptance Criteria

- [x] Four documentation directories created (tutorials, how-to, reference, explanation)
- [ ] At least 3 complete tutorials written
- [ ] At least 8 how-to guides created
- [ ] Complete reference documentation for CLI, config, and API
- [ ] At least 4 explanation documents written
- [ ] All index README.md files created for each directory
- [ ] README.md updated with clear documentation navigation
- [ ] All existing documentation migrated or linked appropriately
- [ ] All internal links verified working
- [ ] Documentation passes all linters (pymarkdown, mdformat, codespell)
- [ ] Old documentation files archived or removed
- [ ] CONTRIBUTING.md updated with new documentation structure
- [ ] CLAUDE.md updated to reference new structure

## Related Files

- `README.md` - Main navigation hub (needs update)
- `docs/` - Documentation directory (needs reorganization)
- `CONTRIBUTING.md` - Contributing guide (needs update)
- `CLAUDE.md` - Project overview (needs update)
- All existing documentation in `docs/` directory

## Dependencies

None - can be implemented independently.

**Recommended to complete first**:
- None

**Recommended to complete after**:
- This improves discoverability for all future documentation

## Additional Notes

### Benefits

1. **For New Users**:
   - Clear entry point with tutorials
   - Easy to find solutions to specific problems
   - Less overwhelming than current mixed documentation

2. **For Experienced Users**:
   - Quick reference lookup
   - Deep dives into architecture and design decisions
   - Better understanding of system rationale

3. **For Contributors**:
   - Clear how-to guides for common tasks
   - Explanations of design decisions
   - Better onboarding experience

4. **For Maintainers**:
   - Systematic organization makes maintenance easier
   - Clear where to add new documentation
   - Reduces duplication

### The Diátaxis Framework

Daniele Procida's documentation framework divides documentation along two axes:

**Theoretical/Practical × Learning/Working**

```
                Learning          Working
              ┌─────────────┬─────────────┐
  Practical   │  TUTORIALS  │  HOW-TO     │
              │             │  GUIDES     │
              ├─────────────┼─────────────┤
Theoretical   │ EXPLANATION │ REFERENCE   │
              │             │             │
              └─────────────┴─────────────┘
```

- **Tutorials** (practical learning): "Take me by the hand"
- **How-to Guides** (practical working): "Show me how to solve this"
- **Reference** (theoretical working): "Tell me the facts"
- **Explanation** (theoretical learning): "Help me understand"

### References

- **Diátaxis Framework**: https://diataxis.fr/
- **Procida's Talk**: "What nobody tells you about documentation" (PyCon 2017)
- **Examples**:
  - Django docs: https://docs.djangoproject.com/
  - NumPy docs: https://numpy.org/doc/
  - FastAPI docs: https://fastapi.tiangolo.com/

### Migration Strategy

**Phased approach**:

1. **Phase 1** (3h): Create structure + tutorials
   - Immediate value for new users
   - Sets the pattern for other content

2. **Phase 2** (3h): Create how-to guides
   - High-impact for existing users
   - Extracts practical content from existing docs

3. **Phase 3** (2h): Create reference docs
   - Consolidates existing reference material
   - Makes lookup easy

4. **Phase 4** (2h): Create explanations
   - Deepens understanding
   - Documents design decisions

**Can be implemented incrementally** - each phase delivers value independently.

### Content Reuse

Much existing content can be **reorganized** rather than rewritten:

- CONTRIBUTING.md → Split into how-to guides
- DEVELOPMENT.md → Split into tutorials and how-to
- MAKEFILE.md → Move to reference/makefile.md
- UV docs → Split into how-to and explanation
- TOX docs → Split into how-to and reference

**Estimated new writing**: 30-40% of content
**Reorganization/editing**: 60-70% of effort

### Long-term Maintenance

Once established, the structure makes documentation **easier to maintain**:

- Clear where new docs belong
- Less duplication
- Easier to identify gaps
- Better user feedback ("I couldn't find a how-to for X")

## Implementation Notes

*To be filled during implementation:*
- Actual structure created
- Content migration decisions
- User feedback on new organization
- Actual effort vs estimated effort
