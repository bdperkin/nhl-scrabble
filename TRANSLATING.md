# Translation Guide

Thank you for your interest in translating NHL Scrabble! This guide will help you contribute translations to the project.

## Supported Locales

NHL Scrabble supports 12 locales covering major hockey markets worldwide:

| Region             | Locales                                     |
| ------------------ | ------------------------------------------- |
| **North America**  | `en_US`, `en_CA`, `fr_CA`                   |
| **Nordic**         | `sv_SE`, `fi_FI`                            |
| **Central Europe** | `cs_CZ`, `de_DE`, `de_CH`, `it_CH`, `sk_SK` |
| **Eastern Europe** | `ru_RU`, `lv_LV`                            |

## Translation Files

Translation files are located in:

```
src/nhl_scrabble/locales/
├── en_US/LC_MESSAGES/messages.po
├── en_CA/LC_MESSAGES/messages.po
├── fr_CA/LC_MESSAGES/messages.po
├── sv_SE/LC_MESSAGES/messages.po
├── ru_RU/LC_MESSAGES/messages.po
├── fi_FI/LC_MESSAGES/messages.po
├── cs_CZ/LC_MESSAGES/messages.po
├── de_DE/LC_MESSAGES/messages.po
├── de_CH/LC_MESSAGES/messages.po
├── it_CH/LC_MESSAGES/messages.po
├── sk_SK/LC_MESSAGES/messages.po
└── lv_LV/LC_MESSAGES/messages.po
```

## Quick Start

### 1. Choose Your Locale

Find the `.po` file for your locale in `src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po`.

### 2. Edit the Translation File

Each translation entry looks like this:

```po
#: src/nhl_scrabble/cli.py:123
msgid "Analysis complete!"
msgstr ""
```

- **msgid**: The English source text (do not modify)
- **msgstr**: Your translation (fill this in)

Add your translation:

```po
#: src/nhl_scrabble/cli.py:123
msgid "Analysis complete!"
msgstr "Analyse terminée!"
```

### 3. Compile Translations

After editing, compile the translations to binary format:

```bash
make i18n-compile
```

This creates `.mo` files that the application uses at runtime.

### 4. Test Your Translation

Test your translation by setting the locale:

```bash
# Test with environment variable
NHL_SCRABBLE_LANG=fr_CA nhl-scrabble analyze

# Or use the --locale option
nhl-scrabble analyze --locale fr_CA
```

### 5. Submit Your Translation

1. **Fork the repository** on GitHub
1. **Create a branch**: `git checkout -b translation/fr_CA`
1. **Commit your changes**: `git commit -m "feat(i18n): Add French Canadian translations"`
1. **Push to your fork**: `git push origin translation/fr_CA`
1. **Create a pull request** on GitHub

## Translation Tools

You can use various tools to edit `.po` files:

### Poedit (Recommended)

**Poedit** is a popular GUI editor for `.po` files with translation memory and spell checking.

- **Download**: https://poedit.net/
- **Features**: Translation memory, spell check, plural forms, context help
- **Usage**: Open the `.po` file directly in Poedit

### Lokalize (KDE)

**Lokalize** is a powerful translation tool from the KDE project.

- **Install**: `sudo dnf install lokalize` (Fedora) or `sudo apt install lokalize` (Ubuntu)
- **Features**: Translation memory, quality checks, glossary
- **Usage**: Open the `.po` file in Lokalize

### Text Editor

You can also use any text editor (VS Code, Vim, Emacs, etc.):

1. Open `src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po`
1. Find entries with empty `msgstr ""`
1. Add your translation
1. Save the file

### Weblate (Web-based)

For collaborative translation, we may set up a Weblate instance in the future. Check the project's GitHub page for updates.

## Translation Guidelines

### 1. Preserve Placeholders

**Important**: Always keep formatting placeholders exactly as they appear.

```po
# ✓ Correct
msgid "Found {count} players"
msgstr "Trouvé {count} joueurs"

# ✗ Wrong - placeholder changed
msgid "Found {count} players"
msgstr "Trouvé {nombre} joueurs"
```

Placeholders include:

- `{variable}` - Python string formatting
- `{0}`, `{1}` - Positional placeholders
- `%(name)s`, `%(count)d` - Named placeholders

### 2. Don't Translate Markup

Rich markup tags should remain unchanged:

```po
# ✓ Correct - only text translated
msgid "[green]Success![/green]"
msgstr "[green]Succès![/green]"

# ✗ Wrong - markup translated
msgid "[green]Success![/green]"
msgstr "[vert]Succès![/vert]"
```

### 3. Handle Emoji Appropriately

Consider cultural appropriateness of emoji:

```po
# Option 1: Keep emoji if culturally appropriate
msgid "🏒 NHL Roster Analyzer"
msgstr "🏒 Analyseur de listes NHL"

# Option 2: Remove if not culturally appropriate
msgid "🏒 NHL Roster Analyzer"
msgstr "Analyseur de listes NHL"
```

### 4. Hockey Terminology

Use standard hockey terminology in your language:

| English    | Français (Canada)    | Svenska   | Русский     |
| ---------- | -------------------- | --------- | ----------- |
| Team       | Équipe               | Lag       | Команда     |
| Player     | Joueur               | Spelare   | Игрок       |
| Division   | Division             | Division  | Дивизион    |
| Conference | Conférence           | Konferens | Конференция |
| Playoffs   | Séries éliminatoires | Slutspel  | Плей-офф    |

### 5. Context Comments

If the meaning of a string is unclear, add a translator comment:

```po
# Translator comment: "Scrabble" refers to the board game scoring system
msgid "Scrabble Score"
msgstr "Score Scrabble"
```

### 6. Plural Forms

Some languages have different plural rules. The `.po` file header defines the plural forms for your locale:

```po
"Plural-Forms: nplurals=2; plural=(n > 1);\n"
```

For plural translations:

```po
msgid "1 player"
msgid_plural "{count} players"
msgstr[0] "{count} joueur"
msgstr[1] "{count} joueurs"
```

## Workflow

### Initial Translation

1. **Extract current strings**:

   ```bash
   make i18n-extract
   ```

1. **Update your locale file**:

   ```bash
   make i18n-update
   ```

1. **Edit translations** in your `.po` file

1. **Compile**:

   ```bash
   make i18n-compile
   ```

1. **Test**:

   ```bash
   NHL_SCRABBLE_LANG=your_locale nhl-scrabble analyze
   ```

### Updating Existing Translations

When new strings are added to the application:

1. **Update translation files**:

   ```bash
   make i18n-update
   ```

1. **Find new/changed strings** (marked with `#, fuzzy`)

1. **Update translations**

1. **Compile and test**

## Quality Checks

### Before Submitting

1. **Compile without errors**:

   ```bash
   make i18n-compile
   ```

1. **Check for formatting issues**:

   ```bash
   msgfmt --check src/nhl_scrabble/locales/{locale}/LC_MESSAGES/messages.po
   ```

1. **Test in the application**:

   ```bash
   NHL_SCRABBLE_LANG=your_locale nhl-scrabble --help
   NHL_SCRABBLE_LANG=your_locale nhl-scrabble analyze
   NHL_SCRABBLE_LANG=your_locale nhl-scrabble interactive
   ```

1. **Check formatting**:

   - No broken placeholders
   - No translated markup
   - Consistent terminology
   - Proper punctuation

### Translation Statistics

Check translation completion:

```bash
make i18n-stats
```

Output:

```
Translation Statistics:
src/nhl_scrabble/locales/fr_CA/LC_MESSAGES/messages.po: 254 translated messages.
src/nhl_scrabble/locales/sv_SE/LC_MESSAGES/messages.po: 254 translated messages.
src/nhl_scrabble/locales/de_DE/LC_MESSAGES/messages.po: 0 translated, 254 untranslated.
```

## Translation Status

Current translation completion as of 2026-05-13:

| Locale | Language               | Status              | Completion | Reviewer Needed |
| ------ | ---------------------- | ------------------- | ---------- | --------------- |
| fr_CA  | French (Canada)        | ✅ Complete (DRAFT) | 254/254    | Yes             |
| sv_SE  | Swedish (Sweden)       | ✅ Complete (DRAFT) | 254/254    | Yes             |
| de_CH  | German (Switzerland)   | ✅ Complete (DRAFT) | 254/254    | Yes             |
| en_CA  | English (Canada)       | ✅ Complete         | 254/254    | No              |
| en_US  | English (US)           | 🔄 Source language  | -          | -               |
| ru_RU  | Russian (Russia)       | ✅ Complete (DRAFT) | 254/254    | Yes             |
| fi_FI  | Finnish (Finland)      | ✅ Complete (DRAFT) | 254/254    | Yes             |
| cs_CZ  | Czech (Czech Republic) | ✅ Complete (DRAFT) | 254/254    | Yes             |
| de_DE  | German (Germany)       | ✅ Complete (DRAFT) | 254/254    | Yes             |
| it_CH  | Italian (Switzerland)  | ⏳ Pending          | 0/254      | Yes             |
| sk_SK  | Slovak (Slovakia)      | ⏳ Pending          | 0/254      | Yes             |
| lv_LV  | Latvian (Latvia)       | ⏳ Pending          | 0/254      | Yes             |

**Note**: French Canadian (fr_CA), Swedish (sv_SE), and German Switzerland (de_CH) translations are AI-assisted drafts. They require review by native speakers to ensure:

- Natural, idiomatic language
- Proper hockey terminology for each region
- Cultural appropriateness
- UI string length compatibility
- Correct use of Swiss German conventions (ss instead of ß for de_CH)

**Want to help review?** Native speakers of French, Swedish, or German (Switzerland) who can verify the translations are welcome to contribute! See the [Contributing](#5-submit-your-translation) section above.

## Common Issues

### Issue: Compile Errors

```
Error: syntax error in line 42
```

**Solution**: Check for unescaped quotes or malformed entries. Each `msgid` must have a corresponding `msgstr`.

### Issue: Translation Not Showing

**Possible causes**:

1. **Not compiled**: Run `make i18n-compile`
1. **Wrong locale**: Verify `$NHL_SCRABBLE_LANG` or `--locale` setting
1. **Empty msgstr**: Translation must not be empty
1. **Cached**: Restart the application

### Issue: Fuzzy Translations

Entries marked with `#, fuzzy` are uncertain translations that won't be used until the fuzzy flag is removed:

```po
#, fuzzy
msgid "New feature"
msgstr "Ancienne traduction"
```

**Solution**: Review the translation, update if needed, and remove the `#, fuzzy` line.

## Need Help?

- **Documentation**: See `docs/reference/i18n.md` for technical details
- **Issues**: Report translation issues at https://github.com/bdperkin/nhl-scrabble/issues
- **Questions**: Ask in the GitHub Discussions
- **Contributing**: See `CONTRIBUTING.md` for general contribution guidelines

## Translation Credits

All translators will be credited in the project's `CONTRIBUTORS.md` file. Thank you for helping make NHL Scrabble accessible to hockey fans worldwide!

## License

Translations are distributed under the same license as the NHL Scrabble project (MIT License). By contributing translations, you agree to license your work under these terms.
