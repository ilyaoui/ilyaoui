#!/usr/bin/env python3
"""
Script pour scraper le site ECNL (Elite Clubs National League)
"""

import os
import sys
from generic_sports_scraper import GenericSportsMatchScraper
from datetime import datetime

# Désactiver le proxy si nécessaire
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'


def scrape_ecnl_page(url, output_dir='ecnl_data'):
    """Scrape une page ECNL"""
    print(f"🏆 Scraping ECNL: {url}\n")

    # Créer le scraper avec rate limiting approprié
    scraper = GenericSportsMatchScraper(
        rate_limit=2.0,  # 2 secondes entre requêtes
        max_retries=5    # 5 tentatives max
    )

    # Modifier pour désactiver le proxy dans requests
    original_request = scraper._make_request

    def no_proxy_request(url_req, method='GET', **kwargs):
        # Désactiver explicitement le proxy
        kwargs['proxies'] = {'http': None, 'https': None}
        return original_request(url_req, method, **kwargs)

    scraper._make_request = no_proxy_request

    # Scraper la page
    print("⏳ Extraction en cours...")
    matches = scraper.scrape_matches_from_url(url)

    if not matches:
        print("❌ Aucun match trouvé")
        print("\n💡 Conseils:")
        print("   - Vérifiez que l'URL contient des matchs")
        print("   - Essayez avec une autre URL ECNL")
        print("   - Consultez le guide: GUIDE_ECNL_SCRAPING.md")
        return

    print(f"✓ {len(matches)} matchs extraits\n")

    # Export CSV
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/ecnl_matches_{timestamp}.csv"
    scraper.export_to_csv(matches, filename)

    print(f"💾 Export réussi: {filename}\n")

    # Statistiques
    print("=" * 70)
    print("STATISTIQUES")
    print("=" * 70)

    # Statuts
    statuses = {}
    for match in matches:
        status = match.status or 'unknown'
        statuses[status] = statuses.get(status, 0) + 1

    print(f"\nTotal matchs: {len(matches)}")
    if statuses:
        print("\nPar status:")
        for status, count in sorted(statuses.items()):
            print(f"  - {status}: {count}")

    # Équipes uniques
    teams = set()
    for match in matches:
        if match.home_team:
            teams.add(match.home_team)
        if match.away_team:
            teams.add(match.away_team)

    if teams:
        print(f"\nÉquipes uniques: {len(teams)}")

    # Divisions
    divisions = set(m.division for m in matches if m.division)
    if divisions:
        print(f"Divisions: {len(divisions)}")
        for div in sorted(divisions):
            print(f"  - {div}")

    # Lieux
    venues = set(m.venue for m in matches if m.venue)
    if venues:
        print(f"\nLieux: {len(venues)}")
        for venue in sorted(venues):
            print(f"  - {venue}")

    # Afficher aperçu
    print("\n" + "=" * 70)
    print("APERÇU DES MATCHS")
    print("=" * 70 + "\n")

    for i, match in enumerate(matches[:10], 1):
        print(f"Match #{i}")
        print("-" * 40)

        if match.date and match.time:
            print(f"📅 {match.date} à {match.time}")
        elif match.date:
            print(f"📅 {match.date}")

        if match.home_team and match.away_team:
            home_str = match.home_team
            away_str = match.away_team

            if match.home_score is not None and match.away_score is not None:
                print(f"🏠 {home_str} ({match.home_score})")
                print(f"✈️  {away_str} ({match.away_score})")
                print(f"📊 Score: {match.home_score} - {match.away_score}")
            else:
                print(f"🏠 {home_str}")
                print(f"✈️  {away_str}")

        if match.status:
            print(f"⚡ Status: {match.status}")

        if match.venue:
            location = match.venue
            if match.city and match.state:
                location += f", {match.city}, {match.state}"
            elif match.city:
                location += f", {match.city}"
            print(f"📍 {location}")

        if match.division:
            print(f"🔰 Division: {match.division}")

        print()

    if len(matches) > 10:
        print(f"... et {len(matches) - 10} autres matchs\n")

    print("=" * 70)
    print(f"✓ Scraping terminé avec succès!")
    print("=" * 70)

    return matches


def scrape_all_ecnl_calendars(base_url='https://theecnl.com', output_dir='ecnl_all_calendars'):
    """Découvre et scrape tous les calendriers ECNL"""
    print(f"🔍 Découverte des calendriers depuis {base_url}\n")

    scraper = GenericSportsMatchScraper(rate_limit=2.0)

    # Désactiver le proxy
    original_request = scraper._make_request

    def no_proxy_request(url_req, method='GET', **kwargs):
        kwargs['proxies'] = {'http': None, 'https': None}
        return original_request(url_req, method, **kwargs)

    scraper._make_request = no_proxy_request

    # Découvrir les calendriers
    print("⏳ Crawling en cours (cela peut prendre quelques minutes)...\n")
    calendars = scraper.discover_calendars(base_url, max_depth=3)

    if not calendars:
        print("❌ Aucun calendrier découvert")
        print("\n💡 Essayez:")
        print("   - Utiliser une URL plus spécifique (ex: /schedule)")
        print("   - Augmenter la profondeur de crawling")
        return

    print(f"\n✓ {len(calendars)} calendriers découverts:\n")

    for i, cal in enumerate(calendars, 1):
        print(f"  {i}. {cal.name}")
        print(f"     URL: {cal.url}")

    # Scraper chaque calendrier
    print(f"\n⏳ Scraping de tous les calendriers...\n")

    all_matches = []
    for i, calendar in enumerate(calendars, 1):
        print(f"[{i}/{len(calendars)}] {calendar.name}")
        matches = scraper.scrape_matches_from_url(calendar.url)
        calendar.matches = matches
        all_matches.extend(matches)
        print(f"  → {len(matches)} matchs\n")

    # Export
    os.makedirs(output_dir, exist_ok=True)
    scraper.export_calendars_to_csv(calendars, output_dir)

    # Export récapitulatif
    if all_matches:
        summary_file = f"{output_dir}/all_matches.csv"
        scraper.export_to_csv(all_matches, summary_file)

    print("\n" + "=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    print(f"\n✓ Total: {len(all_matches)} matchs extraits depuis {len(calendars)} calendriers")
    print(f"✓ Fichiers sauvegardés dans {output_dir}/")
    print("=" * 70)

    return all_matches


def show_help():
    """Affiche l'aide"""
    help_text = """
═══════════════════════════════════════════════════════════════════
                    ECNL SCRAPER - AIDE
═══════════════════════════════════════════════════════════════════

UTILISATION:

  Mode 1: Scraper une page spécifique
  ────────────────────────────────────
  python scrape_ecnl.py <URL>

  Exemple:
  python scrape_ecnl.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"


  Mode 2: Mode interactif
  ────────────────────────
  python scrape_ecnl.py

  Affiche un menu pour choisir entre:
    1. Scraper une page spécifique
    2. Découvrir tous les calendriers ECNL


  Mode 3: Découverte automatique
  ───────────────────────────────
  python scrape_ecnl.py discover [URL_BASE]

  Exemple:
  python scrape_ecnl.py discover "https://theecnl.com"


OPTIONS:

  --help, -h       Affiche cette aide
  discover         Mode découverte de calendriers


EXEMPLES:

  # Scraper une page de matchs
  python scrape_ecnl.py "https://theecnl.com/sports/2023/8/8/..."

  # Mode interactif
  python scrape_ecnl.py

  # Découvrir tous les calendriers depuis la page d'accueil
  python scrape_ecnl.py discover "https://theecnl.com"

  # Découvrir depuis une section spécifique
  python scrape_ecnl.py discover "https://theecnl.com/schedule"


FICHIERS DE SORTIE:

  • ecnl_data/ecnl_matches_YYYYMMDD_HHMMSS.csv
    Matchs d'une page spécifique

  • ecnl_all_calendars/Calendar_Name_1.csv
  • ecnl_all_calendars/Calendar_Name_2.csv
  • ecnl_all_calendars/all_matches.csv
    Tous les calendriers découverts + récapitulatif


DOCUMENTATION:

  • Guide complet: GUIDE_ECNL_SCRAPING.md
  • Documentation générale: GENERIC_SCRAPER_README.md
  • Interface interactive: python interactive_scraper.py


SUPPORT:

  En cas de problème:
    1. Vérifiez votre connexion internet
    2. Consultez GUIDE_ECNL_SCRAPING.md
    3. Essayez avec --verbose pour plus de détails

═══════════════════════════════════════════════════════════════════
"""
    print(help_text)


def main():
    """Fonction principale"""

    # Vérifier les arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Aide
        if arg in ['--help', '-h', 'help']:
            show_help()
            return

        # Mode découverte
        if arg == 'discover':
            base_url = sys.argv[2] if len(sys.argv) > 2 else 'https://theecnl.com'
            scrape_all_ecnl_calendars(base_url)
            return

        # URL passée en argument
        if arg.startswith('http'):
            scrape_ecnl_page(arg)
            return

        # Argument invalide
        print(f"❌ Argument invalide: {arg}")
        print("Utilisez --help pour voir l'aide")
        return

    # Mode interactif
    print("=" * 70)
    print("           🏆 ECNL SCRAPER 🏆")
    print("    Elite Clubs National League Match Scraper")
    print("=" * 70)
    print()

    print("Que voulez-vous faire ?\n")
    print("1. Scraper une page spécifique")
    print("2. Découvrir tous les calendriers ECNL")
    print("3. Afficher l'aide")
    print("0. Quitter")
    print()

    choice = input("Votre choix (0-3): ").strip()

    if choice == '1':
        print()
        url = input("URL de la page ECNL: ").strip()
        if url:
            print()
            scrape_ecnl_page(url)
        else:
            print("❌ URL requise")

    elif choice == '2':
        print()
        base_url = input("URL de base [https://theecnl.com]: ").strip()
        if not base_url:
            base_url = 'https://theecnl.com'
        print()
        scrape_all_ecnl_calendars(base_url)

    elif choice == '3':
        show_help()

    elif choice == '0':
        print("\n👋 Au revoir !\n")

    else:
        print("❌ Choix invalide")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrompu par l'utilisateur\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")
        print("💡 Consultez GUIDE_ECNL_SCRAPING.md pour plus d'informations")
        sys.exit(1)
