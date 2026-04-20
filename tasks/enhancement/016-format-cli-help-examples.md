# Format CLI Help Examples with Comments

**GitHub Issue**: #230 - https://github.com/bdperkin/nhl-scrabble/issues/230

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

15-30 minutes

## Description

Format CLI help examples onto separate lines with descriptive comments to improve readability and user experience. This makes the help text clearer and easier to understand for new users learning the CLI.

## Current State

**Current CLI Help Examples:**

The CLI help text currently shows examples in a compact format:

```python
# src/nhl_scrabble/cli.py
@cli.command()
def analyze(format, output, verbose, top_players, top_team_players):
    """Analyze NHL teams and calculate Scrabble scores.

    Fetches current NHL roster data and calculates Scrabble scores
    for player names. Generates comprehensive reports including team
    standings, division standings, conference standings, and playoff
    brackets.

    Examples:

        # Basic usage (text output to stdout)
        nhl-scrabble analyze

        # JSON output to file
        nhl-scrabble analyze -f json -o report.json

        # Verbose mode
        nhl-scrabble analyze -v

        # Custom display limits
        nhl-scrabble analyze --top-players 50 --top-team-players 10
    """
    pass
```

**Current Help Output:**

```bash
$ nhl-scrabble analyze --help
Usage: nhl-scrabble analyze [OPTIONS]

  Analyze NHL teams and calculate Scrabble scores.

  Fetches current NHL roster data and calculates Scrabble scores for player
  names. Generates comprehensive reports including team standings, division
  standings, conference standings, and playoff brackets.

  Examples:

      # Basic usage (text output to stdout)
      nhl-scrabble analyze

      # JSON output to file
      nhl-scrabble analyze -f json -o report.json

      # Verbose mode
      nhl-scrabble analyze -v

      # Custom display limits
      nhl-scrabble analyze --top-players 50 --top-team-players 10

Options:
  -f, --format [text|json]      Output format  [default: text]
  -o, --output PATH             Output file path
  -v, --verbose                 Enable verbose logging
  --top-players INTEGER         Number of top players  [default: 20]
  --top-team-players INTEGER    Number of top players per team  [default: 5]
  -h, --help                    Show this message and exit.
```

**Issues:**

1. **Comments Above Examples**: Comments are inline with examples (hash style)
1. **Readability**: Could be improved with better formatting
1. **Consistency**: Not following a clear pattern
1. **Descriptions**: Some examples lack clear purpose descriptions

## Proposed Solution

### Improved Example Formatting

Format examples with clear structure and descriptive comments:

```python
# src/nhl_scrabble/cli.py
@cli.command()
def analyze(format, output, verbose, top_players, top_team_players):
    """Analyze NHL teams and calculate Scrabble scores.

    Fetches current NHL roster data and calculates Scrabble scores
    for player names. Generates comprehensive reports including team
    standings, division standings, conference standings, and playoff
    brackets.

    \b
    Examples:
      Basic usage with text output to stdout:
        $ nhl-scrabble analyze

      JSON format output to file:
        $ nhl-scrabble analyze -f json -o report.json

      Enable verbose logging for debugging:
        $ nhl-scrabble analyze -v

      Customize number of players displayed:
        $ nhl-scrabble analyze --top-players 50 --top-team-players 10

      Combine multiple options:
        $ nhl-scrabble analyze -f json -o scores.json -v
    """
    pass
```

**Key Improvements:**

1. **`\b` Directive**: Prevents Click from reformatting (preserves exact formatting)
1. **Descriptive Comments**: Clear purpose before each example
1. **Shell Prompt**: Uses `$` to indicate shell commands
1. **Consistent Structure**: Description line, then command line
1. **More Examples**: Added combined options example

### Alternative Formatting Style

Another option using numbered examples:

```python
@cli.command()
def analyze(format, output, verbose, top_players, top_team_players):
    """Analyze NHL teams and calculate Scrabble scores.

    \b
    Examples:

    1. Basic usage (text output to stdout):
       $ nhl-scrabble analyze

    2. JSON output to file:
       $ nhl-scrabble analyze -f json -o report.json

    3. Verbose mode for debugging:
       $ nhl-scrabble analyze -v

    4. Custom player display limits:
       $ nhl-scrabble analyze --top-players 50 --top-team-players 10

    5. Combine multiple options:
       $ nhl-scrabble analyze -f json -o scores.json -v
    """
    pass
```

### Updated Help Output

**After Implementation:**

```bash
$ nhl-scrabble analyze --help
Usage: nhl-scrabble analyze [OPTIONS]

  Analyze NHL teams and calculate Scrabble scores.

  Fetches current NHL roster data and calculates Scrabble scores for player
  names. Generates comprehensive reports including team standings, division
  standings, conference standings, and playoff brackets.

Examples:
  Basic usage with text output to stdout:
    $ nhl-scrabble analyze

  JSON format output to file:
    $ nhl-scrabble analyze -f json -o report.json

  Enable verbose logging for debugging:
    $ nhl-scrabble analyze -v

  Customize number of players displayed:
    $ nhl-scrabble analyze --top-players 50 --top-team-players 10

  Combine multiple options:
    $ nhl-scrabble analyze -f json -o scores.json -v

Options:
  -f, --format [text|json]      Output format  [default: text]
  -o, --output PATH             Output file path
  -v, --verbose                 Enable verbose logging
  --top-players INTEGER         Number of top players  [default: 20]
  --top-team-players INTEGER    Number of top players per team  [default: 5]
  -h, --help                    Show this message and exit.
```

## Implementation Steps

1. **Update CLI Docstrings** (10 min)

   - Add `\b` directive before Examples section
   - Format each example with:
     - Descriptive comment line
     - Command line with `$` prompt
     - Blank line between examples
   - Ensure consistent indentation (2-4 spaces)

1. **Add More Examples** (5 min)

   - Add combined options example
   - Add edge case examples if applicable
   - Show common workflow patterns

1. **Test Help Output** (5 min)

   - Run: `nhl-scrabble --help`
   - Run: `nhl-scrabble analyze --help`
   - Verify formatting renders correctly
   - Check for any wrapping issues

1. **Update Documentation** (5 min)

   - Update CLI reference documentation
   - Ensure examples match help text
   - Update tutorials if they reference help

1. **Verify Consistency** (5 min)

   - Check all commands use same format
   - Ensure descriptions are clear and concise
   - Verify `$` prompt is used consistently

## Testing Strategy

### Manual Testing

```bash
# Test main help
nhl-scrabble --help
# Verify: Clean formatting, readable examples

# Test analyze help
nhl-scrabble analyze --help
# Verify: Examples section well-formatted
# Verify: No line wrapping issues
# Verify: Descriptions are clear

# Test in narrow terminal
export COLUMNS=60
nhl-scrabble analyze --help
# Verify: Examples still readable

# Test in wide terminal
export COLUMNS=120
nhl-scrabble analyze --help
# Verify: Examples look good
```

### Visual Inspection

Check for:

- [ ] Consistent indentation
- [ ] Clear descriptions
- [ ] Shell prompt (`$`) present
- [ ] Examples are actionable
- [ ] No unnecessary hash comments
- [ ] Blank lines between examples
- [ ] Proper use of `\b` directive

## Acceptance Criteria

- [ ] Examples section uses `\b` directive for formatting control
- [ ] Each example has a descriptive comment above it
- [ ] Command lines use `$` shell prompt
- [ ] Examples are on separate lines (not inline comments)
- [ ] Consistent indentation throughout
- [ ] At least 4-5 examples showing different use cases
- [ ] Combined options example included
- [ ] Help output renders correctly in terminal
- [ ] No line wrapping issues in standard 80-column terminal
- [ ] Examples are copy-pasteable (no hash comments in command lines)
- [ ] Documentation updated to match help text

## Related Files

**Modified Files:**

- `src/nhl_scrabble/cli.py` - Update docstrings with better formatting
- `docs/reference/cli.md` - Ensure examples match (if applicable)

**No New Files** - Pure enhancement to existing code

## Dependencies

**No External Dependencies** - Click handles docstring rendering

**No Task Dependencies** - Standalone enhancement

**Related Tasks:**

- Task 015 (Add CLI Short Options) - Coordinate if examples need short options

## Additional Notes

### Click `\b` Directive

**Purpose**: The `\b` directive tells Click to preserve exact formatting:

```python
# Without \b - Click reformats text
"""
Examples:
    nhl-scrabble analyze
    nhl-scrabble analyze -v
"""
# Output: Reformatted, potentially rewrapped

# With \b - Preserves formatting
"""
\b
Examples:
  Basic usage:
    $ nhl-scrabble analyze

  Verbose mode:
    $ nhl-scrabble analyze -v
"""
# Output: Exactly as written
```

### Formatting Best Practices

**DO:**

- ✅ Use `\b` directive for examples
- ✅ Use `$` to indicate shell commands
- ✅ Put descriptions before commands
- ✅ Use consistent indentation
- ✅ Include blank lines between examples
- ✅ Show realistic use cases

**DON'T:**

- ❌ Use hash comments in command lines
- ❌ Make examples too complex
- ❌ Include output in help text (too verbose)
- ❌ Forget to test in actual terminal
- ❌ Mix formatting styles

### Example Formatting Templates

**Template 1: Simple Description + Command**

```
\b
Examples:
  Description of what this does:
    $ nhl-scrabble command --option value

  Another example:
    $ nhl-scrabble command -o value
```

**Template 2: Numbered Examples**

```
\b
Examples:

1. Description:
   $ nhl-scrabble command

2. Another example:
   $ nhl-scrabble command --option
```

**Template 3: Workflow-Based**

```
\b
Common Workflows:

Quick analysis:
  $ nhl-scrabble analyze

Generate JSON report:
  $ nhl-scrabble analyze -f json -o report.json
```

### Readability Comparison

**Before (Hash Comments):**

```
Examples:
    # Basic usage
    nhl-scrabble analyze

    # JSON output
    nhl-scrabble analyze -f json -o report.json
```

**Issues:**

- Hash comments not copy-pasteable
- Unclear if hash is part of command
- Less professional appearance

**After (Descriptive Lines):**

```
\b
Examples:
  Basic usage with default text output:
    $ nhl-scrabble analyze

  JSON format output to file:
    $ nhl-scrabble analyze -f json -o report.json
```

**Benefits:**

- Clear separation of description and command
- Copy-paste friendly
- More professional
- Follows industry standards (man pages, etc.)

### Industry Examples

**Git:**

```bash
$ git commit --help
...
EXAMPLES
       Start a new topic branch:
           $ git checkout -b my-topic

       Commit with a message:
           $ git commit -m "Add feature"
```

**Docker:**

```bash
$ docker run --help
...
Examples:
  Run a container in interactive mode:
    $ docker run -it ubuntu bash

  Run with volume mount:
    $ docker run -v /host:/container ubuntu
```

**NPM:**

```bash
$ npm install --help
...
Examples:
  Install a package locally:
    $ npm install lodash

  Install as dev dependency:
    $ npm install --save-dev typescript
```

**NHL Scrabble (Improved):**

```bash
$ nhl-scrabble analyze --help
...
Examples:
  Basic usage with text output:
    $ nhl-scrabble analyze

  JSON output to file:
    $ nhl-scrabble analyze -f json -o report.json
```

### Terminal Width Considerations

**80 Columns (Standard):**

```
Examples:
  Basic usage with text output to stdout:
    $ nhl-scrabble analyze
```

**120 Columns (Wide):**

```
Examples:
  Basic usage with text output to stdout:
    $ nhl-scrabble analyze
```

**60 Columns (Narrow):**

```
Examples:
  Basic usage with text
  output to stdout:
    $ nhl-scrabble analyze
```

**Testing Strategy:**

- Test at 60, 80, 120 column widths
- Ensure descriptions don't wrap awkwardly
- Keep descriptions concise if needed

### Breaking Changes

**None** - This is purely cosmetic:

- No functionality changes
- No API changes
- Only docstring formatting updated
- Help output improved, not changed semantically

### User Impact

**Positive:**

- Clearer help text
- Easier to learn CLI
- More professional appearance
- Better first impression

**Neutral:**

- No behavior changes
- Existing users unaffected
- Scripts unchanged

### Documentation Updates

**Files to Update:**

1. **CLI Reference** (`docs/reference/cli.md`):

   - Update examples to match help text
   - Ensure consistent formatting

1. **Getting Started** (`docs/tutorials/01-getting-started.md`):

   - Reference improved help text
   - Use same formatting style

1. **README.md**:

   - Update quick start examples
   - Match help text style

### Testing Checklist

- [ ] `nhl-scrabble --help` - Main help displays correctly
- [ ] `nhl-scrabble analyze --help` - Command help formatted well
- [ ] Examples are copy-pasteable from terminal
- [ ] No hash comments in command lines
- [ ] `$` prompt present and consistent
- [ ] Descriptions are clear and concise
- [ ] No line wrapping issues
- [ ] `\b` directive prevents reformatting
- [ ] Blank lines between examples
- [ ] Indentation consistent throughout

### Future Enhancements

After initial implementation:

- **Man Page**: Generate man page with same formatting
- **Markdown Export**: Export help to markdown for docs
- **Interactive Examples**: Add interactive tutorial mode
- **Example Testing**: Automated testing of help examples
- **Localization**: Translate help text to other languages

### Accessibility

**Benefits:**

- Clearer structure helps screen readers
- Consistent formatting aids comprehension
- Descriptive text before commands provides context
- Shell prompt indicates command boundaries

### Performance

**Impact**: None

- Docstrings loaded at import time
- Help rendering unchanged
- No runtime performance impact

### Success Metrics

**Qualitative:**

- [ ] Help text is more professional
- [ ] New users find CLI easier to learn
- [ ] Examples are actually used (copy-pasted)
- [ ] Fewer questions about CLI usage

**Quantitative:**

- [ ] 100% of commands have formatted examples
- [ ] 100% of examples use `\b` directive
- [ ] 0 hash comments in command lines
- [ ] 100% of examples have descriptions
