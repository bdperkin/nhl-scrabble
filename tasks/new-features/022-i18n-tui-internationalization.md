# TUI/Interactive Mode Internationalization

**GitHub Issue**: #250 - https://github.com/bdperkin/nhl-scrabble/issues/250

**Parent Task**: #218 - Internationalization and Localization (sub-task 4 of 6)

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

3-4 hours

## Description

Internationalize the Terminal User Interface (TUI) / interactive shell mode by wrapping all prompts, commands, and output strings with translation markers. Fourth sub-task of i18n/l10n implementation.

**Parent Task**: tasks/new-features/016-internationalization-localization.md

## Proposed Solution

```python
# src/nhl_scrabble/interactive/shell.py
from nhl_scrabble.i18n import get_translator

_ = get_translator()

class InteractiveShell:
    def run(self):
        print(_("Welcome to NHL Scrabble Interactive Mode"))
        print(_("Commands: analyze, filter, export, quit"))

    def handle_command(self, cmd):
        if cmd == "analyze":
            print(_("Running analysis..."))
        # ... more commands
```

## Acceptance Criteria

- [ ] All TUI strings wrapped with \_()
- [ ] Interactive prompts internationalized
- [ ] Command help text translatable
- [ ] TUI strings extracted to messages.pot
- [ ] Tests pass
- [ ] Documentation updated

## Dependencies

- **Prerequisite**: Sub-task 1 (I18n Infrastructure)
- **Parent**: #218

## Implementation Notes

*To be filled during implementation*
