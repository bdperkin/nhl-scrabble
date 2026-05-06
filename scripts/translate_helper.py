#!/usr/bin/env python3
"""Helper script for creating initial translation drafts.

This script creates machine-translated drafts that require native speaker review.
"""

import re
from pathlib import Path
from typing import Dict

# French Canadian translations for common NHL Scrabble terms
FR_CA_TRANSLATIONS: Dict[str, str] = {
    # App title and headers
    "🏒 NHL Roster Scrabble Score Analyzer 🏒": "🏒 Analyseur de scores Scrabble des effectifs LNH 🏒",

    # Common terms
    "Team": "Équipe",
    "Teams": "Équipes",
    "Player": "Joueur",
    "Players": "Joueurs",
    "Score": "Score",
    "Scores": "Scores",
    "Division": "Division",
    "Divisions": "Divisions",
    "Conference": "Conférence",
    "Conferences": "Conférences",
    "Playoff": "Séries éliminatoires",
    "Playoffs": "Séries éliminatoires",
    "Roster": "Effectif",
    "Season": "Saison",

    # Actions
    "Analyzing": "Analyse",
    "Loading": "Chargement",
    "Processing": "Traitement",
    "Fetching": "Récupération",
    "Generating": "Génération",
    "Compiling": "Compilation",

    # Output formats
    "Output format (default: text)": "Format de sortie (par défaut : texte)",
    "Output file path (default: stdout)": "Chemin du fichier de sortie (par défaut : stdout)",

    # Filters
    "Filter by divisions (comma-separated: Atlantic,Metropolitan,Central,Pacific)":
        "Filtrer par divisions (séparées par virgule : Atlantic,Metropolitan,Central,Pacific)",
    "Filter by conferences (comma-separated: Eastern,Western)":
        "Filtrer par conférences (séparées par virgule : Eastern,Western)",
    "Filter by teams (comma-separated abbreviations: TOR,MTL,BOS)":
        "Filtrer par équipes (abréviations séparées par virgule : TOR,MTL,BOS)",
    "Exclude teams (comma-separated abbreviations: NYR,PHI)":
        "Exclure des équipes (abréviations séparées par virgule : NYR,PHI)",

    # Common options
    "Enable verbose logging": "Activer la journalisation détaillée",
    "Suppress progress bars and status messages": "Supprimer les barres de progression et les messages d'état",
    "Disable API response caching (always fetch fresh data)":
        "Désactiver la mise en cache des réponses de l'API (toujours récupérer des données fraîches)",
    "Clear API cache before running": "Effacer le cache de l'API avant l'exécution",

    # Status messages
    "Filters active:": "Filtres actifs :",

    # Numbers and ranges
    "Number of top players to show (default: 20, range: 1-100)":
        "Nombre de meilleurs joueurs à afficher (par défaut : 20, plage : 1-100)",
    "Number of top players per team to show (default: 5, range: 1-50)":
        "Nombre de meilleurs joueurs par équipe à afficher (par défaut : 5, plage : 1-50)",

    # Scores
    "Minimum player score to include": "Score minimum du joueur à inclure",
    "Maximum player score to include": "Score maximum du joueur à inclure",

    # Locale
    "Display locale (e.g., fr_CA for Canadian French)":
        "Locale d'affichage (par ex., fr_CA pour le français canadien)",

    # Reports
    "Generate specific report only (default: all reports)":
        "Générer uniquement un rapport spécifique (par défaut : tous les rapports)",

    # Scoring
    "Built-in scoring system to use (default: scrabble)":
        "Système de notation intégré à utiliser (par défaut : scrabble)",
    "Path to custom scoring configuration JSON file":
        "Chemin vers le fichier JSON de configuration de notation personnalisée",

    # Templates
    "Custom template file path (required for --format template)":
        "Chemin du fichier de modèle personnalisé (requis pour --format template)",
    "Comma-separated list of sheets for Excel export (teams,players,divisions,conferences,playoffs)":
        "Liste séparée par virgules de feuilles pour l'export Excel (teams,players,divisions,conferences,playoffs)",

    # Season
    "Analyze specific season (format: YYYYYYYY, e.g., 20222023 for 2022-23)":
        "Analyser une saison spécifique (format : AAAAAAAA, par ex., 20222023 pour 2022-23)",

    # Symbols
    "=": "=",
    "\n": "\n",
}

# Swedish translations for common NHL Scrabble terms
SV_SE_TRANSLATIONS: Dict[str, str] = {
    # App title and headers
    "🏒 NHL Roster Scrabble Score Analyzer 🏒": "🏒 NHL Spelartrupp Scrabble Poäng Analysator 🏒",

    # Common terms
    "Team": "Lag",
    "Teams": "Lag",
    "Player": "Spelare",
    "Players": "Spelare",
    "Score": "Poäng",
    "Scores": "Poäng",
    "Division": "Division",
    "Divisions": "Divisioner",
    "Conference": "Konferens",
    "Conferences": "Konferenser",
    "Playoff": "Slutspel",
    "Playoffs": "Slutspel",
    "Roster": "Spelartrupp",
    "Season": "Säsong",

    # Actions
    "Analyzing": "Analyserar",
    "Loading": "Laddar",
    "Processing": "Bearbetar",
    "Fetching": "Hämtar",
    "Generating": "Genererar",
    "Compiling": "Kompilerar",

    # Output formats
    "Output format (default: text)": "Utdataformat (standard: text)",
    "Output file path (default: stdout)": "Utdatafilsökväg (standard: stdout)",

    # Filters
    "Filter by divisions (comma-separated: Atlantic,Metropolitan,Central,Pacific)":
        "Filtrera efter divisioner (kommaseparerade: Atlantic,Metropolitan,Central,Pacific)",
    "Filter by conferences (comma-separated: Eastern,Western)":
        "Filtrera efter konferenser (kommaseparerade: Eastern,Western)",
    "Filter by teams (comma-separated abbreviations: TOR,MTL,BOS)":
        "Filtrera efter lag (kommaseparerade förkortningar: TOR,MTL,BOS)",
    "Exclude teams (comma-separated abbreviations: NYR,PHI)":
        "Exkludera lag (kommaseparerade förkortningar: NYR,PHI)",

    # Common options
    "Enable verbose logging": "Aktivera utförlig loggning",
    "Suppress progress bars and status messages": "Undertryck förloppsindikator och statusmeddelanden",
    "Disable API response caching (always fetch fresh data)":
        "Inaktivera API-svar cachning (hämta alltid färsk data)",
    "Clear API cache before running": "Rensa API-cache före körning",

    # Status messages
    "Filters active:": "Aktiva filter:",

    # Numbers and ranges
    "Number of top players to show (default: 20, range: 1-100)":
        "Antal toppspelare att visa (standard: 20, intervall: 1-100)",
    "Number of top players per team to show (default: 5, range: 1-50)":
        "Antal toppspelare per lag att visa (standard: 5, intervall: 1-50)",

    # Scores
    "Minimum player score to include": "Minsta spelarpoäng att inkludera",
    "Maximum player score to include": "Högsta spelarpoäng att inkludera",

    # Locale
    "Display locale (e.g., fr_CA for Canadian French)":
        "Visningsspråk (t.ex. sv_SE för svenska)",

    # Reports
    "Generate specific report only (default: all reports)":
        "Generera endast specifik rapport (standard: alla rapporter)",

    # Scoring
    "Built-in scoring system to use (default: scrabble)":
        "Inbyggt poängsystem att använda (standard: scrabble)",
    "Path to custom scoring configuration JSON file":
        "Sökväg till anpassad poängkonfiguration JSON-fil",

    # Templates
    "Custom template file path (required for --format template)":
        "Anpassad mallfilsökväg (krävs för --format template)",
    "Comma-separated list of sheets for Excel export (teams,players,divisions,conferences,playoffs)":
        "Kommaseparerad lista över ark för Excel-export (teams,players,divisions,conferences,playoffs)",

    # Season
    "Analyze specific season (format: YYYYYYYY, e.g., 20222023 for 2022-23)":
        "Analysera specifik säsong (format: ÅÅÅÅÅÅÅ, t.ex. 20222023 för 2022-23)",

    # Symbols
    "=": "=",
    "\n": "\n",
}


def translate_string(msgid: str, target_lang: str) -> str:
    """Translate a string to the target language.

    Args:
        msgid: Source string in English
        target_lang: Target language code ('fr_CA' or 'sv_SE')

    Returns:
        Translated string
    """
    if target_lang == "fr_CA":
        translations = FR_CA_TRANSLATIONS
    elif target_lang == "sv_SE":
        translations = SV_SE_TRANSLATIONS
    else:
        return msgid

    # Direct lookup
    if msgid in translations:
        return translations[msgid]

    # For strings with placeholders, try pattern matching
    # This is a simple version - would need more sophisticated handling in production
    return msgid  # Return original if no translation found


if __name__ == "__main__":
    print("Translation helper loaded")
    print(f"French Canadian terms: {len(FR_CA_TRANSLATIONS)}")
    print(f"Swedish terms: {len(SV_SE_TRANSLATIONS)}")
