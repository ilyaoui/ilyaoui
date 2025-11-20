#!/usr/bin/env python3
"""
Quick Start Script pour NFL Flag Scraper
-----------------------------------------
Script de démarrage rapide pour tester le scraper sans configuration
"""

import sys
import os

def print_banner():
    """Affiche la bannière du programme"""
    print("\n" + "=" * 80)
    print(" " * 25 + "NFL FLAG SCRAPER - QUICK START")
    print("=" * 80 + "\n")

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    required = ['requests', 'bs4']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("⚠️  Dépendances manquantes détectées!\n")
        print(f"Packages manquants: {', '.join(missing)}\n")
        print("Installation requise:")
        print("  pip install -r requirements.txt\n")
        return False

    print("✓ Toutes les dépendances sont installées\n")
    return True

def check_config():
    """Vérifie si la configuration existe"""
    if os.path.exists('config.json'):
        print("✓ Configuration trouvée (config.json)")
        return True
    else:
        print("⚠️  Pas de configuration trouvée")
        print("   Pour utiliser l'API TeamSnap, exécutez: python oauth_helper.py\n")
        return False

def demo_web_scraping():
    """Démo du web scraping"""
    print("\n--- DÉMONSTRATION WEB SCRAPING ---\n")
    print("Test de découverte d'APIs publiques...\n")

    try:
        from nfl_flag_scraper import NFLFlagWebScraper
        from datetime import datetime

        scraper = NFLFlagWebScraper()

        print("Recherche d'endpoints API publics...")
        tournaments = scraper.search_tournaments_api()

        if tournaments:
            print(f"\n✓ {len(tournaments)} endpoint(s) découvert(s)!")

            for idx, t in enumerate(tournaments, 1):
                print(f"  {idx}. {t['endpoint']}")

            # Sauvegarder les résultats
            import json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_start_results_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(tournaments, f, indent=2)

            print(f"\n✓ Résultats sauvegardés dans: {filename}")

        else:
            print("\n⚠️  Aucun endpoint public accessible automatiquement")
            print("\nCela peut signifier:")
            print("  1. Les APIs nécessitent une authentification")
            print("  2. Les endpoints sont protégés")
            print("  3. La structure des APIs a changé")

            print("\n💡 Solutions:")
            print("  • Utilisez le mode API avec authentification (oauth_helper.py)")
            print("  • Fournissez une URL spécifique de tournoi à scraper")
            print("  • Consultez la documentation TeamSnap pour les endpoints actuels")

    except ImportError as e:
        print(f"✗ Erreur d'import: {e}")
        print("Assurez-vous que les dépendances sont installées.")
        return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

    return True

def demo_api():
    """Démo de l'API TeamSnap"""
    print("\n--- DÉMONSTRATION API TEAMSNAP ---\n")

    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)

        from nfl_flag_scraper import TeamSnapAPIClient

        print("Connexion à l'API TeamSnap...")
        client = TeamSnapAPIClient(config['access_token'])

        print("Récupération de l'utilisateur actuel...")
        user = client.get_current_user()

        if user:
            print(f"✓ Connecté!")
            print(f"  User ID: {user.get('id', 'N/A')}")

            print("\nRécupération des équipes...")
            teams = client.get_teams()
            print(f"✓ {len(teams)} équipe(s) trouvée(s)")

            if teams:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"teams_api_{timestamp}.json"

                with open(filename, 'w') as f:
                    json.dump(teams, f, indent=2)

                print(f"✓ Données sauvegardées dans: {filename}")

        else:
            print("✗ Erreur de connexion - vérifiez votre token")
            return False

    except FileNotFoundError:
        print("✗ Fichier config.json non trouvé")
        return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

    return True

def show_menu():
    """Affiche le menu principal"""
    print("\nQue voulez-vous faire?\n")
    print("  1. Tester le Web Scraping (pas d'auth requise)")
    print("  2. Tester l'API TeamSnap (nécessite config.json)")
    print("  3. Configurer l'authentification OAuth2")
    print("  4. Afficher l'aide")
    print("  5. Quitter\n")

def show_help():
    """Affiche l'aide"""
    print("\n--- AIDE ---\n")
    print("Fichiers disponibles:")
    print("  • nfl_flag_scraper.py     - Scraper principal")
    print("  • advanced_scraper.py     - Scraper avancé avec BeautifulSoup")
    print("  • oauth_helper.py         - Configuration OAuth2")
    print("  • quick_start.py          - Ce script")
    print()
    print("Commandes utiles:")
    print("  python nfl_flag_scraper.py      - Lance le scraper interactif")
    print("  python advanced_scraper.py      - Lance le scraper avancé")
    print("  python oauth_helper.py          - Configure OAuth2")
    print("  python oauth_helper.py test     - Test la configuration")
    print()
    print("Documentation:")
    print("  README.md contient la documentation complète")
    print()

def main():
    """Fonction principale"""
    print_banner()

    print("Vérification de l'environnement...\n")

    # Vérifier les dépendances
    if not check_dependencies():
        print("\n⚠️  Veuillez installer les dépendances avant de continuer.")
        sys.exit(1)

    # Vérifier la configuration
    has_config = check_config()

    # Menu
    while True:
        show_menu()
        choice = input("Votre choix (1-5): ").strip()

        if choice == "1":
            demo_web_scraping()
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "2":
            if not has_config:
                print("\n⚠️  Configuration requise!")
                print("Exécutez d'abord: python oauth_helper.py\n")
                input("Appuyez sur Entrée pour continuer...")
            else:
                demo_api()
                input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "3":
            print("\n--- CONFIGURATION OAUTH2 ---\n")
            print("Pour configurer l'authentification OAuth2:")
            print("  python oauth_helper.py\n")
            print("Suivez les instructions à l'écran.\n")
            input("Appuyez sur Entrée pour continuer...")

        elif choice == "4":
            show_help()
            input("Appuyez sur Entrée pour continuer...")

        elif choice == "5":
            print("\n👋 Au revoir!\n")
            break

        else:
            print("\n⚠️  Choix invalide. Veuillez choisir 1-5.\n")
            input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption détectée. Au revoir!\n")
        sys.exit(0)
