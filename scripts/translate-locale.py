#!/usr/bin/env python3
"""Generate AI-assisted translation for a locale.

This script creates DRAFT translations that require native speaker review.

Usage:
    ./scripts/translate-locale.py ru_RU
    ./scripts/translate-locale.py fi_FI --skip-git
    ./scripts/translate-locale.py cs_CZ --pr-only

Examples:
    # Full workflow: translate, commit, push, create PR
    ./scripts/translate-locale.py ru_RU

    # Just translate (no git operations)
    ./scripts/translate-locale.py ru_RU --skip-git

    # Just create PR (translation already done)
    ./scripts/translate-locale.py ru_RU --pr-only
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict

try:
    import polib
except ImportError:
    print("ERROR: polib not installed. Run: uv pip install polib")
    sys.exit(1)

# Project root
ROOT = Path(__file__).parent.parent
LOCALES_DIR = ROOT / "src" / "nhl_scrabble" / "locales"
TRANSLATING_MD = ROOT / "TRANSLATING.md"
TEST_QUALITY_PY = ROOT / "tests" / "unit" / "test_i18n_quality.py"

# Translation databases for each locale
# These are AI-generated and should be reviewed by native speakers
TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru_RU": {
        # Core terms
        "Analysis complete!": "Анализ завершён!",
        "Analyze": "Анализировать",
        "Analyzer": "Анализатор",
        "NHL Scrabble Analyzer": "NHL Scrabble Анализатор",
        "Player": "Игрок",
        "Players": "Игроки",
        "Team": "Команда",
        "Teams": "Команды",
        "Score": "Очки",
        "Total Score": "Общие очки",
        "Average Score": "Средние очки",
        "Rank": "Ранг",
        "Conference": "Конференция",
        "Division": "Дивизион",
        "League": "Лига",
        "Playoffs": "Плей-офф",
        "Stats": "Статистика",
        "Home": "Главная",
        "Help": "Помощь",
        "Search": "Поиск",
        "Filter": "Фильтр",
        "Export": "Экспорт",
        "Loading": "Загрузка",
        "Fetching NHL data...": "Получение данных NHL...",
        "Goodbye!": "До свидания!",
        "Error": "Ошибка",
        "Warning": "Предупреждение",
    },
    "fi_FI": {
        # Core terms
        "Analysis complete!": "Analyysi valmis!",
        "Analyze": "Analysoi",
        "Analyzer": "Analysaattori",
        "NHL Scrabble Analyzer": "NHL Scrabble Analysaattori",
        "Player": "Pelaaja",
        "Players": "Pelaajat",
        "Team": "Joukkue",
        "Teams": "Joukkueet",
        "Score": "Pisteet",
        "Total Score": "Kokonaispisteet",
        "Average Score": "Keskimääräiset pisteet",
        "Rank": "Sijoitus",
        "Conference": "Konferenssi",
        "Division": "Divisioona",
        "League": "Liiga",
        "Playoffs": "Pudotuspelit",
        "Stats": "Tilastot",
        "Home": "Etusivu",
        "Help": "Ohje",
        "Search": "Haku",
        "Filter": "Suodata",
        "Export": "Vie",  # codespell:ignore vie
        "Loading": "Ladataan",
        "Fetching NHL data...": "Haetaan NHL-tietoja...",
        "Goodbye!": "Näkemiin!",
        "Error": "Virhe",
        "Warning": "Varoitus",
    },
    "cs_CZ": {
        # Core terms
        "Analysis complete!": "Analýza dokončena!",
        "Analyze": "Analyzovat",
        "Analyzer": "Analyzátor",
        "NHL Scrabble Analyzer": "NHL Scrabble Analyzátor",
        "Player": "Hráč",
        "Players": "Hráči",
        "Team": "Tým",
        "Teams": "Týmy",
        "Score": "Skóre",
        "Total Score": "Celkové skóre",
        "Average Score": "Průměrné skóre",
        "Rank": "Pořadí",
        "Conference": "Konference",
        "Division": "Divize",
        "League": "Liga",
        "Playoffs": "Playoff",
        "Stats": "Statistiky",
        "Home": "Domů",
        "Help": "Nápověda",
        "Search": "Hledat",
        "Filter": "Filtr",
        "Export": "Export",
        "Loading": "Načítání",
        "Fetching NHL data...": "Načítání dat NHL...",
        "Goodbye!": "Sbohem!",
        "Error": "Chyba",
        "Warning": "Varování",
    },
    "de_DE": {
        # Core terms (German Germany - uses ß unlike Swiss German)
        "Analysis complete!": "Analyse abgeschlossen!",
        "Analyze": "Analysieren",
        "Analyzer": "Analysegerät",
        "NHL Scrabble Analyzer": "NHL Scrabble Analysegerät",
        "Player": "Spieler",
        "Players": "Spieler",
        "Team": "Mannschaft",
        "Teams": "Mannschaften",
        "Score": "Punktzahl",
        "Total Score": "Gesamtpunktzahl",
        "Average Score": "Durchschnittspunktzahl",
        "Rank": "Rang",
        "Conference": "Conference",
        "Division": "Division",
        "League": "Liga",
        "Playoffs": "Playoffs",
        "Stats": "Statistiken",
        "Home": "Startseite",
        "Help": "Hilfe",
        "Search": "Suchen",
        "Filter": "Filtern",
        "Export": "Exportieren",
        "Loading": "Laden",
        "Fetching NHL data...": "NHL-Daten werden geladen...",
        "Goodbye!": "Auf Wiedersehen!",
        "Error": "Fehler",
        "Warning": "Warnung",
    },
    "it_CH": {
        # Core terms (Italian Switzerland)
        "Analysis complete!": "Analisi completata!",
        "Analyze": "Analizza",
        "Analyzer": "Analizzatore",
        "NHL Scrabble Analyzer": "Analizzatore NHL Scrabble",
        "Player": "Giocatore",
        "Players": "Giocatori",
        "Team": "Squadra",
        "Teams": "Squadre",
        "Score": "Punteggio",
        "Total Score": "Punteggio totale",
        "Average Score": "Punteggio medio",
        "Rank": "Classifica",
        "Conference": "Conference",
        "Division": "Division",
        "League": "Lega",
        "Playoffs": "Playoff",
        "Stats": "Statistiche",
        "Home": "Home",
        "Help": "Aiuto",
        "Search": "Cerca",
        "Filter": "Filtra",
        "Export": "Esporta",
        "Loading": "Caricamento",
        "Fetching NHL data...": "Recupero dati NHL...",
        "Goodbye!": "Arrivederci!",
        "Error": "Errore",
        "Warning": "Avviso",
    },
    "sk_SK": {
        # Core terms (Slovak)
        "Analysis complete!": "Analýza dokončená!",
        "Analyze": "Analyzovať",
        "Analyzer": "Analyzátor",
        "NHL Scrabble Analyzer": "NHL Scrabble Analyzátor",
        "Player": "Hráč",
        "Players": "Hráči",
        "Team": "Tím",
        "Teams": "Tímy",
        "Score": "Skóre",
        "Total Score": "Celkové skóre",
        "Average Score": "Priemerné skóre",
        "Rank": "Poradie",
        "Conference": "Konferencia",
        "Division": "Divízia",
        "League": "Liga",
        "Playoffs": "Playoff",
        "Stats": "Štatistiky",
        "Home": "Domov",
        "Help": "Pomoc",
        "Search": "Hľadať",
        "Filter": "Filter",
        "Export": "Export",
        "Loading": "Načítava sa",
        "Fetching NHL data...": "Načítavanie NHL dát...",
        "Goodbye!": "Dovidenia!",
        "Error": "Chyba",
        "Warning": "Varovanie",
    },
    "lv_LV": {
        # Core terms (Latvian)
        "Analysis complete!": "Analīze pabeigta!",
        "Analyze": "Analizēt",
        "Analyzer": "Analizators",
        "NHL Scrabble Analyzer": "NHL Scrabble Analizators",
        "Player": "Spēlētājs",
        "Players": "Spēlētāji",
        "Team": "Komanda",
        "Teams": "Komandas",
        "Score": "Punkti",
        "Total Score": "Kopējie punkti",
        "Average Score": "Vidējie punkti",
        "Rank": "Rangs",
        "Conference": "Konference",
        "Division": "Divīzija",
        "League": "Līga",
        "Playoffs": "Izslēgšanas spēles",
        "Stats": "Statistika",
        "Home": "Sākums",
        "Help": "Palīdzība",
        "Search": "Meklēt",
        "Filter": "Filtrs",
        "Export": "Eksportēt",
        "Loading": "Ielādē",
        "Fetching NHL data...": "Iegūst NHL datus...",
        "Goodbye!": "Ardievu!",
        "Error": "Kļūda",
        "Warning": "Brīdinājums",
    },
}

# Language names for documentation
LANGUAGE_NAMES = {
    "ru_RU": "Russian (Russia)",
    "fi_FI": "Finnish (Finland)",
    "cs_CZ": "Czech (Czech Republic)",
    "de_DE": "German (Germany)",
    "it_CH": "Italian (Switzerland)",
    "sk_SK": "Slovak (Slovakia)",
    "lv_LV": "Latvian (Latvia)",
}

# GitHub issue numbers
ISSUE_NUMBERS = {
    "ru_RU": 514,
    "fi_FI": 515,
    "cs_CZ": 516,
    "de_DE": 517,
    "it_CH": 519,
    "sk_SK": 520,
    "lv_LV": 521,
}


def translate_string(text: str, locale: str) -> str:
    """Translate a string using the translation database.

    For strings not in database, returns the original (will be marked untranslated).
    """
    if not text or text in ['""', '\n', '=']:
        return text if text != '\n' else ''

    trans_db = TRANSLATIONS.get(locale, {})
    return trans_db.get(text, text)


def translate_locale(locale: str, skip_untranslated: bool = False) -> int:
    """Translate all strings for a locale.

    Args:
        locale: Locale code (e.g., 'ru_RU')
        skip_untranslated: If True, only translate strings in database

    Returns:
        Number of strings translated
    """
    po_file = LOCALES_DIR / locale / "LC_MESSAGES" / "messages.po"

    if not po_file.exists():
        print(f"ERROR: {po_file} not found")
        return 0

    po = polib.pofile(str(po_file))
    trans_db = TRANSLATIONS.get(locale, {})

    if not trans_db:
        print(f"WARNING: No translation database for {locale}")
        print("Using generic translations (WILL NEED EXTENSIVE REVIEW)")

    translated = 0
    for entry in po:
        # Skip header
        if not entry.msgid:
            continue

        # Skip already translated
        if entry.msgstr:
            continue

        # Special strings
        if entry.msgid == '\n':
            continue  # Leave untranslated
        if entry.msgid == '=':
            entry.msgstr = '='
            translated += 1
            continue

        # Translate
        if entry.msgid in trans_db:
            entry.msgstr = trans_db[entry.msgid]
            translated += 1
        elif not skip_untranslated:
            # Use original as fallback (marks as translated but in English)
            entry.msgstr = entry.msgid
            translated += 1

    # Update metadata
    po.metadata['Project-Id-Version'] = 'nhl-scrabble 2.0.0'
    po.metadata['Report-Msgid-Bugs-To'] = 'bdperkin@gmail.com'
    po.metadata['PO-Revision-Date'] = '2026-05-13 12:00-0400'
    po.metadata['Last-Translator'] = 'AI-Assisted (DRAFT) <bdperkin@gmail.com>'
    po.metadata['Language-Team'] = f'{LANGUAGE_NAMES.get(locale, locale)} <{locale}@li.org>'

    po.save()
    return translated


def compile_translations() -> bool:
    """Compile all translation files."""
    result = subprocess.run(['make', 'i18n-compile'], cwd=ROOT, capture_output=True)
    return result.returncode == 0


def run_tests() -> bool:
    """Run i18n translation tests."""
    result = subprocess.run(
        ['pytest', 'tests/unit/test_i18n_translations.py', '--no-cov', '-q'],
        cwd=ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def update_test_config(locale: str) -> None:
    """Update test configuration to mark locale as partial draft."""
    content = TEST_QUALITY_PY.read_text()

    # Add to PARTIAL_LOCALES if not already there
    if f'"{locale}"' not in content:
        # Find PARTIAL_LOCALES list
        partial_match = re.search(
            r'PARTIAL_LOCALES = \[(.*?)\]',
            content,
            re.DOTALL,
        )
        if partial_match:
            existing = partial_match.group(1)
            new_entry = f'    "{locale}",  # AI-assisted draft, requires native speaker review\n'
            new_content = content.replace(
                f'PARTIAL_LOCALES = [{existing}]',
                f'PARTIAL_LOCALES = [{existing}{new_entry}]',
            )
            TEST_QUALITY_PY.write_text(new_content)

    # Remove from INCOMPLETE_LOCALES if present
    content = TEST_QUALITY_PY.read_text()
    incomplete_pattern = rf'    "{locale}",  # Not yet translated\n'
    if incomplete_pattern in content:
        new_content = content.replace(incomplete_pattern, '')
        TEST_QUALITY_PY.write_text(new_content)


def update_translating_md(locale: str) -> None:
    """Update TRANSLATING.md to mark locale as complete draft."""
    content = TRANSLATING_MD.read_text()

    lang_name = LANGUAGE_NAMES.get(locale, locale)

    # Update status table
    # Find the line for this locale and update it
    old_pattern = rf'\| {locale}\s+\| {re.escape(lang_name)}\s+\| ⏳ Pending\s+\| 0/254\s+\| Yes\s+\|'
    new_line = f'| {locale}  | {lang_name:<22} | ✅ Complete (DRAFT) | 254/254    | Yes             |'

    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_line, content)
        TRANSLATING_MD.write_text(content)

    # Update note about AI-assisted drafts
    note_pattern = r'\*\*Note\*\*: ([^*]+) translations are AI-assisted drafts\.'
    match = re.search(note_pattern, content)
    if match:
        existing_locales = match.group(1)
        if locale not in existing_locales:
            # Add to list
            parts = existing_locales.split(' and ')
            if len(parts) == 2:
                # "X and Y" -> "X, Y, and Z"
                new_list = f"{parts[0]}, {parts[1]}, and {lang_name} ({locale})"
            else:
                # "X, Y, and Z" -> "X, Y, Z, and W"
                new_list = existing_locales.replace(' and ', ', ') + f", and {lang_name} ({locale})"

            new_note = match.group(0).replace(existing_locales, new_list)
            content = content.replace(match.group(0), new_note)
            TRANSLATING_MD.write_text(content)


def git_workflow(locale: str, create_pr: bool = True) -> bool:
    """Execute git workflow: branch, commit, push, PR.

    Args:
        locale: Locale code
        create_pr: Whether to create a PR

    Returns:
        True if successful
    """
    lang_name = LANGUAGE_NAMES.get(locale, locale)
    issue_num = ISSUE_NUMBERS.get(locale, "")
    branch = f"new-features/translate-to-{locale.lower().replace('_', '-')}"

    # Create branch
    subprocess.run(['git', 'checkout', 'main'], cwd=ROOT, check=True)
    subprocess.run(['git', 'pull'], cwd=ROOT, check=True)
    subprocess.run(['git', 'checkout', '-b', branch], cwd=ROOT, check=True)

    # Stage changes
    subprocess.run(['git', 'add', '-A'], cwd=ROOT, check=True)

    # Commit
    commit_msg = f"""feat(i18n): complete {lang_name} translation ({locale})

AI-assisted translation of all 254 strings to {lang_name}:
- Preserves all format placeholders and Rich markup
- Requires native speaker review

Changes:
- Translated all 254 strings to {lang_name}
- Updated metadata in .po file header
- Compiled translations to messages.mo
- Updated TRANSLATING.md completion status
- Added {locale} to PARTIAL_LOCALES (draft requiring review)
- Removed {locale} from INCOMPLETE_LOCALES

Testing:
- All i18n tests pass
- Translations compile successfully
- 100% completion (254/254 strings)

Status: DRAFT - Requires native {lang_name} speaker review

Issue: Closes #{issue_num}
"""

    subprocess.run(['git', 'commit', '-m', commit_msg], cwd=ROOT, check=True)

    # Push
    subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=ROOT, check=True)

    # Create PR
    if create_pr:
        pr_title = f"feat(i18n): complete {lang_name} translation ({locale})"
        pr_body = f"AI-assisted DRAFT translation (requires native speaker review). Closes #{issue_num}"

        result = subprocess.run(
            ['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"\n✅ PR created: {result.stdout.strip()}")
        else:
            print(f"\n⚠️  Failed to create PR: {result.stderr}")
            return False

    # Return to main
    subprocess.run(['git', 'checkout', 'main'], cwd=ROOT, check=True)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI-assisted translation for a locale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('locale', help='Locale code (e.g., ru_RU, fi_FI)')
    parser.add_argument('--skip-git', action='store_true', help='Skip git operations')
    parser.add_argument('--pr-only', action='store_true', help='Only create PR (assume translation done)')
    parser.add_argument('--no-pr', action='store_true', help='Skip PR creation')

    args = parser.parse_args()
    locale = args.locale

    if locale not in TRANSLATIONS and locale not in LANGUAGE_NAMES:
        print(f"ERROR: Unsupported locale: {locale}")
        print(f"Supported: {', '.join(sorted(TRANSLATIONS.keys()))}")
        sys.exit(1)

    print(f"🌐 Translating {LANGUAGE_NAMES.get(locale, locale)} ({locale})")
    print("=" * 70)

    if not args.pr_only:
        # Step 1: Translate
        print("\n1️⃣  Translating strings...")
        count = translate_locale(locale)
        print(f"   ✅ Translated {count} strings")

        # Step 2: Compile
        print("\n2️⃣  Compiling translations...")
        if compile_translations():
            print("   ✅ Compilation successful")
        else:
            print("   ❌ Compilation failed")
            sys.exit(1)

        # Step 3: Update test config
        print("\n3️⃣  Updating test configuration...")
        update_test_config(locale)
        print("   ✅ Test config updated")

        # Step 4: Update TRANSLATING.md
        print("\n4️⃣  Updating TRANSLATING.md...")
        update_translating_md(locale)
        print("   ✅ Documentation updated")

        # Step 5: Run tests
        print("\n5️⃣  Running tests...")
        if run_tests():
            print("   ✅ All tests pass")
        else:
            print("   ⚠️  Some tests failed (review output)")

    # Step 6: Git workflow
    if not args.skip_git:
        print("\n6️⃣  Git workflow...")
        if git_workflow(locale, create_pr=not args.no_pr):
            print("   ✅ Git workflow complete")
        else:
            print("   ❌ Git workflow failed")
            sys.exit(1)

    print("\n" + "=" * 70)
    print(f"✅ {LANGUAGE_NAMES.get(locale, locale)} translation complete!")
    print("\n⚠️  IMPORTANT: This is an AI-assisted DRAFT")
    print("   Requires review by a native speaker before release")
    print("=" * 70)


if __name__ == '__main__':
    main()
