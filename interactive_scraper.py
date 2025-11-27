#!/usr/bin/env python3
"""
Interface Interactive pour Generic Sports Match Scraper
========================================================
Interface conviviale pour scraper des matchs sportifs depuis n'importe quel site web
"""

import sys
import os
from generic_sports_scraper import GenericSportsMatchScraper, Calendar, Match
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """Couleurs ANSI pour terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Affiche le banner de bienvenue"""
    banner = f"""
{Colors.OKBLUE}╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🏆  GENERIC SPORTS MATCH SCRAPER  🏆                      ║
║                                                                ║
║     Scraper universel de matchs sportifs                      ║
║     Compatible avec tous les sites web                        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)


def print_menu():
    """Affiche le menu principal"""
    print(f"\n{Colors.BOLD}╔═══ MENU PRINCIPAL ═══╗{Colors.ENDC}")
    print(f"{Colors.OKCYAN}1.{Colors.ENDC} Scraper une page unique (URL directe)")
    print(f"{Colors.OKCYAN}2.{Colors.ENDC} Découvrir et scraper tous les calendriers (crawling)")
    print(f"{Colors.OKCYAN}3.{Colors.ENDC} Mode avancé (configuration personnalisée)")
    print(f"{Colors.OKCYAN}4.{Colors.ENDC} Afficher les exemples d'utilisation")
    print(f"{Colors.OKCYAN}5.{Colors.ENDC} À propos / Aide")
    print(f"{Colors.OKCYAN}0.{Colors.ENDC} Quitter")
    print(f"{Colors.BOLD}╚══════════════════════╝{Colors.ENDC}\n")


def get_user_input(prompt: str, default: str = None) -> str:
    """Récupère une entrée utilisateur avec valeur par défaut"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(f"{Colors.OKGREEN}{prompt}{Colors.ENDC}").strip()
    return value if value else default


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Récupère une réponse oui/non"""
    default_str = "O/n" if default else "o/N"
    response = input(f"{Colors.OKGREEN}{prompt} [{default_str}]: {Colors.ENDC}").strip().lower()

    if not response:
        return default

    return response in ['o', 'oui', 'y', 'yes']


def scrape_single_page():
    """Mode 1: Scraper une page unique"""
    print(f"\n{Colors.HEADER}═══ MODE PAGE UNIQUE ═══{Colors.ENDC}\n")

    url = get_user_input("Entrez l'URL de la page contenant les matchs")

    if not url:
        print(f"{Colors.FAIL}❌ URL requise{Colors.ENDC}")
        return

    output_dir = get_user_input("Répertoire de sortie", "output")
    rate_limit = float(get_user_input("Délai entre requêtes (secondes)", "1.5"))

    print(f"\n{Colors.WARNING}⏳ Scraping en cours...{Colors.ENDC}")

    scraper = GenericSportsMatchScraper(rate_limit=rate_limit)
    matches = scraper.scrape_matches_from_url(url)

    if matches:
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)

        # Demander le nom du fichier
        filename = get_user_input("Nom du fichier CSV", "matches.csv")
        filepath = os.path.join(output_dir, filename)

        # Exporter
        scraper.export_to_csv(matches, filepath)

        print(f"\n{Colors.OKGREEN}✓ Succès !{Colors.ENDC}")
        print(f"  📊 {Colors.BOLD}{len(matches)}{Colors.ENDC} matchs extraits")
        print(f"  💾 Sauvegardé dans: {Colors.BOLD}{filepath}{Colors.ENDC}")

        # Afficher un aperçu
        if get_yes_no("\nAfficher un aperçu des données ?"):
            display_matches_preview(matches)
    else:
        print(f"\n{Colors.FAIL}❌ Aucun match trouvé sur cette page{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Conseils:{Colors.ENDC}")
        print("   - Vérifiez que l'URL est correcte")
        print("   - Essayez le mode 'Découverte de calendriers' (option 2)")
        print("   - Activez le mode verbose pour plus de détails")


def scrape_all_calendars():
    """Mode 2: Découvrir et scraper tous les calendriers"""
    print(f"\n{Colors.HEADER}═══ MODE DÉCOUVERTE DE CALENDRIERS ═══{Colors.ENDC}\n")

    url = get_user_input("Entrez l'URL de départ (page d'accueil ou section calendrier)")

    if not url:
        print(f"{Colors.FAIL}❌ URL requise{Colors.ENDC}")
        return

    output_dir = get_user_input("Répertoire de sortie", "output")
    max_depth = int(get_user_input("Profondeur maximale de crawling (1-5)", "3"))
    rate_limit = float(get_user_input("Délai entre requêtes (secondes)", "1.5"))

    print(f"\n{Colors.WARNING}⏳ Découverte des calendriers en cours...{Colors.ENDC}")
    print(f"{Colors.WARNING}   (Cela peut prendre quelques minutes selon la taille du site){Colors.ENDC}\n")

    scraper = GenericSportsMatchScraper(rate_limit=rate_limit)

    # Découvrir les calendriers
    calendars = scraper.discover_calendars(url, max_depth=max_depth)

    if not calendars:
        print(f"\n{Colors.FAIL}❌ Aucun calendrier trouvé{Colors.ENDC}")
        print(f"{Colors.WARNING}💡 Essayez:{Colors.ENDC}")
        print("   - Augmenter la profondeur de crawling")
        print("   - Utiliser une URL plus spécifique")
        print("   - Scraper une page unique (option 1)")
        return

    print(f"\n{Colors.OKGREEN}✓ {len(calendars)} calendrier(s) découvert(s):{Colors.ENDC}")
    for i, cal in enumerate(calendars, 1):
        print(f"  {i}. {Colors.BOLD}{cal.name}{Colors.ENDC}")
        print(f"     URL: {cal.url}")

    # Demander confirmation
    if not get_yes_no(f"\nScraper tous ces calendriers ?"):
        return

    print(f"\n{Colors.WARNING}⏳ Scraping des calendriers...{Colors.ENDC}\n")

    # Scraper chaque calendrier
    total_matches = 0
    for i, calendar in enumerate(calendars, 1):
        print(f"{Colors.OKCYAN}[{i}/{len(calendars)}] {calendar.name}{Colors.ENDC}")
        matches = scraper.scrape_matches_from_url(calendar.url)
        calendar.matches = matches
        total_matches += len(matches)
        print(f"  → {len(matches)} matchs extraits")

    # Exporter
    os.makedirs(output_dir, exist_ok=True)
    scraper.export_calendars_to_csv(calendars, output_dir)

    # Export récapitulatif
    all_matches = []
    for calendar in calendars:
        all_matches.extend(calendar.matches)

    if all_matches:
        summary_file = os.path.join(output_dir, 'all_matches.csv')
        scraper.export_to_csv(all_matches, summary_file)

    print(f"\n{Colors.OKGREEN}✓ Scraping terminé avec succès !{Colors.ENDC}")
    print(f"  📊 {Colors.BOLD}{len(calendars)}{Colors.ENDC} calendriers traités")
    print(f"  🏆 {Colors.BOLD}{total_matches}{Colors.ENDC} matchs extraits au total")
    print(f"  💾 Fichiers sauvegardés dans: {Colors.BOLD}{output_dir}/{Colors.ENDC}")

    if get_yes_no("\nAfficher un aperçu des données ?"):
        display_matches_preview(all_matches[:20])  # Limiter à 20 pour la lisibilité


def advanced_mode():
    """Mode 3: Configuration avancée"""
    print(f"\n{Colors.HEADER}═══ MODE AVANCÉ ═══{Colors.ENDC}\n")

    url = get_user_input("URL cible")
    if not url:
        print(f"{Colors.FAIL}❌ URL requise{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}Configuration:{Colors.ENDC}")

    # Mode de scraping
    print("\nMode de scraping:")
    print("  1. Page unique")
    print("  2. Découverte de calendriers")
    mode = get_user_input("Choix", "1")

    # Paramètres
    output_dir = get_user_input("Répertoire de sortie", "output")
    rate_limit = float(get_user_input("Rate limit (secondes)", "1.5"))
    max_retries = int(get_user_input("Nombre max de retry", "3"))

    if mode == "2":
        max_depth = int(get_user_input("Profondeur max de crawling", "3"))
    else:
        max_depth = 0

    # Options d'export
    print(f"\n{Colors.BOLD}Options d'export:{Colors.ENDC}")
    include_metadata = get_yes_no("Inclure les métadonnées (source_url, scraped_at) ?")

    # Mode verbose
    verbose = get_yes_no("Activer le mode verbose (debug) ?", False)

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Exécution
    print(f"\n{Colors.WARNING}⏳ Exécution...{Colors.ENDC}\n")

    scraper = GenericSportsMatchScraper(
        rate_limit=rate_limit,
        max_retries=max_retries
    )

    if mode == "2":
        # Mode découverte
        calendars = scraper.discover_calendars(url, max_depth=max_depth)

        if calendars:
            for calendar in calendars:
                matches = scraper.scrape_matches_from_url(calendar.url)
                calendar.matches = matches

            os.makedirs(output_dir, exist_ok=True)
            scraper.export_calendars_to_csv(calendars, output_dir)

            all_matches = []
            for calendar in calendars:
                all_matches.extend(calendar.matches)

            if all_matches:
                summary_file = os.path.join(output_dir, 'all_matches.csv')
                scraper.export_to_csv(all_matches, summary_file, include_metadata)

            print(f"\n{Colors.OKGREEN}✓ {len(all_matches)} matchs extraits{Colors.ENDC}")
    else:
        # Mode page unique
        matches = scraper.scrape_matches_from_url(url)

        if matches:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, 'matches.csv')
            scraper.export_to_csv(matches, filename, include_metadata)

            print(f"\n{Colors.OKGREEN}✓ {len(matches)} matchs extraits{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ Aucun match trouvé{Colors.ENDC}")


def show_examples():
    """Mode 4: Afficher les exemples"""
    print(f"\n{Colors.HEADER}═══ EXEMPLES D'UTILISATION ═══{Colors.ENDC}\n")

    examples = [
        {
            "titre": "Scraper une page de calendrier NFL Flag",
            "url": "https://www.nflflag.com/events",
            "commande": "python generic_sports_scraper.py https://www.nflflag.com/events",
            "description": "Scrape tous les événements NFL Flag"
        },
        {
            "titre": "Scraper avec profondeur limitée",
            "url": "https://example.com/sports",
            "commande": "python generic_sports_scraper.py https://example.com/sports -d 2",
            "description": "Crawl avec profondeur maximale de 2 niveaux"
        },
        {
            "titre": "Scraper une page unique (sans crawling)",
            "url": "https://example.com/matches",
            "commande": "python generic_sports_scraper.py https://example.com/matches --single-page",
            "description": "Scrape uniquement la page donnée"
        },
        {
            "titre": "Configuration personnalisée du rate limiting",
            "url": "https://example.com",
            "commande": "python generic_sports_scraper.py https://example.com -r 2.0",
            "description": "Attendre 2 secondes entre chaque requête"
        },
        {
            "titre": "Mode verbose pour debugging",
            "url": "https://example.com",
            "commande": "python generic_sports_scraper.py https://example.com -v",
            "description": "Affiche tous les détails du scraping"
        }
    ]

    for i, ex in enumerate(examples, 1):
        print(f"{Colors.OKCYAN}{i}. {Colors.BOLD}{ex['titre']}{Colors.ENDC}")
        print(f"   URL: {ex['url']}")
        print(f"   Commande: {Colors.OKGREEN}{ex['commande']}{Colors.ENDC}")
        print(f"   Description: {ex['description']}\n")

    print(f"{Colors.BOLD}Utilisation en ligne de commande:{Colors.ENDC}")
    print(f"{Colors.OKGREEN}python generic_sports_scraper.py [URL] [OPTIONS]{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Options disponibles:{Colors.ENDC}")
    print("  -o, --output DIR        Répertoire de sortie (défaut: output)")
    print("  -d, --depth N           Profondeur de crawling (défaut: 3)")
    print("  -r, --rate-limit N      Délai entre requêtes en secondes (défaut: 1.5)")
    print("  --single-page           Scraper uniquement la page donnée")
    print("  -v, --verbose           Mode verbose (debug)")

    print(f"\n{Colors.BOLD}Utilisation programmatique (Python):{Colors.ENDC}")
    code_example = """
from generic_sports_scraper import GenericSportsMatchScraper

# Créer le scraper
scraper = GenericSportsMatchScraper(rate_limit=1.5)

# Scraper une page
matches = scraper.scrape_matches_from_url('https://example.com/matches')

# Exporter en CSV
scraper.export_to_csv(matches, 'output/matches.csv')

# Découvrir et scraper tous les calendriers
calendars = scraper.discover_calendars('https://example.com', max_depth=3)
for calendar in calendars:
    matches = scraper.scrape_matches_from_url(calendar.url)
    calendar.matches = matches

scraper.export_calendars_to_csv(calendars, 'output/')
    """
    print(f"{Colors.OKGREEN}{code_example}{Colors.ENDC}")


def show_help():
    """Mode 5: Afficher l'aide"""
    print(f"\n{Colors.HEADER}═══ AIDE & À PROPOS ═══{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Generic Sports Match Scraper{Colors.ENDC}")
    print("Version 1.0.0\n")

    print(f"{Colors.BOLD}Description:{Colors.ENDC}")
    print("Système de scraping générique pour extraire des matchs sportifs")
    print("depuis n'importe quel site web et les enregistrer dans des fichiers")
    print("CSV bien organisés et structurés.\n")

    print(f"{Colors.BOLD}Fonctionnalités:{Colors.ENDC}")
    features = [
        "✓ Scraping adaptatif à différents sites web",
        "✓ Détection automatique de la structure des pages",
        "✓ Support de multiples formats (tables, listes, divs, JSON)",
        "✓ Découverte automatique des calendriers",
        "✓ Crawling intelligent avec rate limiting",
        "✓ Export CSV enrichi avec métadonnées complètes",
        "✓ Gestion des erreurs et retry automatique",
        "✓ Support multi-sports"
    ]
    for feature in features:
        print(f"  {Colors.OKGREEN}{feature}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Types de données extraites:{Colors.ENDC}")
    data_types = [
        "Équipes (domicile/extérieur)",
        "Scores",
        "Dates et heures",
        "Lieux (stades, villes, états)",
        "Compétitions et divisions",
        "Status des matchs",
        "Métadonnées enrichies"
    ]
    for dtype in data_types:
        print(f"  • {dtype}")

    print(f"\n{Colors.BOLD}Stratégies de scraping:{Colors.ENDC}")
    strategies = [
        "1. Extraction depuis tables HTML (<table>)",
        "2. Extraction depuis listes (<ul>, <ol>)",
        "3. Extraction depuis divs structurées",
        "4. Extraction depuis JSON-LD (structured data)",
        "5. Extraction depuis JSON embedded dans JavaScript"
    ]
    for strategy in strategies:
        print(f"  {strategy}")

    print(f"\n{Colors.BOLD}Format de sortie CSV:{Colors.ENDC}")
    print("Les fichiers CSV contiennent les colonnes suivantes:")
    print("  match_id, sport, date, time, datetime_iso,")
    print("  home_team, away_team, home_score, away_score, status,")
    print("  venue, city, state, competition, division, season,")
    print("  source_url, scraped_at, additional_info")

    print(f"\n{Colors.BOLD}Support:{Colors.ENDC}")
    print("  GitHub: https://github.com/votre-repo/generic-sports-scraper")
    print("  Documentation: Voir README.md")

    print(f"\n{Colors.WARNING}Notes importantes:{Colors.ENDC}")
    print("  • Respectez les conditions d'utilisation des sites")
    print("  • Utilisez un rate limiting approprié")
    print("  • Certains sites peuvent bloquer les scrapers")
    print("  • Vérifiez toujours les données extraites")


def display_matches_preview(matches: list, limit: int = 10):
    """Affiche un aperçu des matchs extraits"""
    print(f"\n{Colors.HEADER}═══ APERÇU DES DONNÉES ═══{Colors.ENDC}\n")

    display_limit = min(limit, len(matches))

    for i, match in enumerate(matches[:display_limit], 1):
        print(f"{Colors.BOLD}Match {i}:{Colors.ENDC}")
        if match.date:
            print(f"  📅 Date: {match.date}")
        if match.time:
            print(f"  🕐 Heure: {match.time}")
        if match.home_team and match.away_team:
            score_str = ""
            if match.home_score is not None and match.away_score is not None:
                score_str = f" ({match.home_score} - {match.away_score})"
            print(f"  🏆 Match: {Colors.OKGREEN}{match.home_team}{Colors.ENDC} vs "
                  f"{Colors.OKBLUE}{match.away_team}{Colors.ENDC}{score_str}")
        if match.venue:
            print(f"  📍 Lieu: {match.venue}")
        if match.division:
            print(f"  🏅 Division: {match.division}")
        if match.status:
            print(f"  ⚡ Status: {match.status}")
        print()

    if len(matches) > display_limit:
        print(f"{Colors.WARNING}... et {len(matches) - display_limit} autres matchs{Colors.ENDC}\n")


def main():
    """Boucle principale du menu interactif"""
    print_banner()

    while True:
        print_menu()

        try:
            choice = input(f"{Colors.OKGREEN}Votre choix: {Colors.ENDC}").strip()

            if choice == '1':
                scrape_single_page()
            elif choice == '2':
                scrape_all_calendars()
            elif choice == '3':
                advanced_mode()
            elif choice == '4':
                show_examples()
            elif choice == '5':
                show_help()
            elif choice == '0':
                print(f"\n{Colors.OKGREEN}👋 Au revoir !{Colors.ENDC}\n")
                sys.exit(0)
            else:
                print(f"{Colors.FAIL}❌ Choix invalide{Colors.ENDC}")

            input(f"\n{Colors.WARNING}Appuyez sur Entrée pour continuer...{Colors.ENDC}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKGREEN}👋 Au revoir !{Colors.ENDC}\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Erreur: {e}{Colors.ENDC}")
            input(f"\n{Colors.WARNING}Appuyez sur Entrée pour continuer...{Colors.ENDC}")


if __name__ == '__main__':
    main()
