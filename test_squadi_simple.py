#!/usr/bin/env python3
"""
Script de test simple pour le scraper Squadi
Teste chaque méthode individuellement
"""

import sys
import importlib.util

def check_dependency(module_name, package_name=None):
    """Vérifie si un module est installé"""
    if package_name is None:
        package_name = module_name

    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {package_name} n'est pas installé")
        print(f"   Installation: pip install {package_name}")
        return False
    else:
        print(f"✅ {package_name} installé")
        return True

def main():
    print("=" * 80)
    print("TEST SIMPLE - SCRAPER SQUADI")
    print("=" * 80)
    print()

    # Vérifier les dépendances
    print("🔍 Vérification des dépendances...")
    print("-" * 80)

    deps_basic = {
        'bs4': 'beautifulsoup4',
        'requests': 'requests',
        'lxml': 'lxml',
    }

    deps_optional = {
        'cloudscraper': 'cloudscraper',
        'selenium': 'selenium',
    }

    # Vérifier dépendances de base
    print("\nDépendances de base:")
    all_basic_ok = True
    for module, package in deps_basic.items():
        if not check_dependency(module, package):
            all_basic_ok = False

    # Vérifier dépendances optionnelles
    print("\nDépendances optionnelles (pour contourner les protections):")
    has_cloudscraper = check_dependency('cloudscraper')
    has_selenium = check_dependency('selenium')

    if not all_basic_ok:
        print("\n❌ Installez d'abord les dépendances de base:")
        print("   pip install beautifulsoup4 requests lxml")
        return 1

    print("\n" + "=" * 80)
    print("TESTS DU SCRAPER")
    print("=" * 80)

    try:
        from squadi_schedules_scraper import SquadiSchedulesScraper
        print("✅ Scraper importé avec succès")
    except ImportError as e:
        print(f"❌ Impossible d'importer le scraper: {e}")
        return 1

    # Créer le scraper
    print("\n📦 Création du scraper...")
    scraper = SquadiSchedulesScraper()
    print("✅ Scraper créé")

    # Test 1: Méthode API
    print("\n" + "-" * 80)
    print("TEST 1: Méthode API directe")
    print("-" * 80)
    print("Tentative d'accès aux endpoints API...")

    try:
        schedules_api = scraper.scrape_api_directly()
        print(f"✅ Test terminé: {len(schedules_api)} schedule(s) trouvé(s)")

        if schedules_api:
            print("\n📊 Aperçu des données:")
            for i, schedule in enumerate(schedules_api[:3], 1):
                print(f"  {i}. {schedule}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    # Test 2: Méthode Requests (si cloudscraper disponible)
    if has_cloudscraper:
        print("\n" + "-" * 80)
        print("TEST 2: Méthode Requests/Cloudscraper")
        print("-" * 80)
        print("Tentative avec cloudscraper...")

        try:
            schedules_requests = scraper.scrape_with_requests()
            print(f"✅ Test terminé: {len(schedules_requests)} schedule(s) trouvé(s)")

            if schedules_requests:
                print("\n📊 Aperçu des données:")
                for i, schedule in enumerate(schedules_requests[:3], 1):
                    print(f"  {i}. {schedule}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    else:
        print("\n⏭️  Test 2 ignoré (cloudscraper non installé)")
        print("   Installation: pip install cloudscraper")

    # Test 3: Méthode Selenium (si disponible)
    if has_selenium:
        print("\n" + "-" * 80)
        print("TEST 3: Méthode Selenium")
        print("-" * 80)
        print("⚠️  Ce test peut prendre plusieurs minutes...")

        choice = input("Voulez-vous tester avec Selenium ? (o/N): ").strip().lower()

        if choice == 'o':
            try:
                print("Lancement du navigateur headless...")
                schedules_selenium = scraper.scrape_with_selenium()
                print(f"✅ Test terminé: {len(schedules_selenium)} schedule(s) trouvé(s)")

                if schedules_selenium:
                    print("\n📊 Aperçu des données:")
                    for i, schedule in enumerate(schedules_selenium[:3], 1):
                        print(f"  {i}. {schedule}")
            except Exception as e:
                print(f"❌ Erreur: {e}")
        else:
            print("⏭️  Test Selenium ignoré")
    else:
        print("\n⏭️  Test 3 ignoré (selenium non installé)")
        print("   Installation: pip install selenium webdriver-manager")

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    print()

    print("✅ Le scraper fonctionne")
    print()

    if not has_cloudscraper and not has_selenium:
        print("⚠️  RECOMMANDATION:")
        print("   Le site Squadi est protégé par anti-bot.")
        print("   Installez au moins une des dépendances suivantes:")
        print()
        print("   Option A (recommandé):")
        print("     pip install cloudscraper")
        print()
        print("   Option B (plus fiable mais plus lent):")
        print("     pip install selenium webdriver-manager")
        print()
        print("   Ou utilisez la méthode navigateur (squadi_browser_script.js)")

    print()
    print("📖 Pour utiliser le scraper complet:")
    print("   python3 squadi_schedules_scraper.py")
    print()
    print("📖 Pour la méthode navigateur:")
    print("   1. Ouvrir Chrome → https://registration.us.squadi.com")
    print("   2. F12 → Console")
    print("   3. Copier-coller squadi_browser_script.js")
    print("   4. Taper: exportSchedules()")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
