#!/usr/bin/env python3
"""
Squadi Manual Explorer
----------------------
Script d'aide pour explorer manuellement le site Squadi et
découvrir comment accéder aux schedules.

Ce script vous guide étape par étape pour:
1. Identifier les protections du site
2. Découvrir la structure de l'API
3. Trouver les endpoints de schedules
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_basic_access():
    """Test l'accès basique au site"""
    print("\n" + "=" * 80)
    print("1. TEST D'ACCÈS BASIQUE")
    print("=" * 80)

    url = "https://registration.us.squadi.com"

    print(f"\nTest: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Headers:")

        for key, value in response.headers.items():
            if key.lower() in ['server', 'content-type', 'cf-ray', 'x-powered-by']:
                print(f"  - {key}: {value}")

        # Détecter les protections
        if 'cloudflare' in str(response.headers).lower():
            print("\n⚠️  Protection détectée: Cloudflare")
            print("   Solution: Utilisez cloudscraper ou Selenium")

        if response.status_code == 403:
            print("\n❌ Accès bloqué (403 Forbidden)")
            print("   Solutions possibles:")
            print("   1. Utiliser un User-Agent différent")
            print("   2. Utiliser cloudscraper")
            print("   3. Utiliser Selenium avec un navigateur réel")

        elif response.status_code == 200:
            print("\n✓ Accès réussi!")

            # Analyser le contenu
            content_length = len(response.text)
            print(f"✓ Taille du contenu: {content_length} caractères")

            # Chercher des indices d'API
            if 'api' in response.text.lower():
                print("✓ Le code contient des références à 'api'")

            if 'schedule' in response.text.lower():
                print("✓ Le code contient des références à 'schedule'")

            # Sauvegarder la page
            filename = f"squadi_homepage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n✓ Page sauvegardée: {filename}")
            print("  → Ouvrez ce fichier pour inspecter le code HTML")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")


def test_with_cloudscraper():
    """Test avec cloudscraper"""
    print("\n" + "=" * 80)
    print("2. TEST AVEC CLOUDSCRAPER")
    print("=" * 80)

    try:
        import cloudscraper

        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )

        url = "https://registration.us.squadi.com"
        print(f"\nTest: {url}")

        response = scraper.get(url, timeout=15)

        print(f"✓ Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ Accès réussi avec cloudscraper!")

            # Analyser le contenu
            content = response.text

            # Chercher des patterns d'API
            import re

            # Patterns pour trouver les URLs d'API
            api_patterns = [
                r'https?://[^\s"\']+/api/[^\s"\']+',
                r'["\'](\/api\/[^\s"\']+)["\']',
                r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'baseURL["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            ]

            found_apis = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    found_apis.add(match)

            if found_apis:
                print("\n✓ API endpoints découverts:")
                for api in sorted(found_apis):
                    print(f"  - {api}")

                # Sauvegarder
                with open('squadi_apis.json', 'w') as f:
                    json.dump(list(found_apis), f, indent=2)
                print("\n✓ APIs sauvegardées dans: squadi_apis.json")

            # Chercher des données JSON embarquées
            json_pattern = r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>'
            json_scripts = re.findall(json_pattern, content, re.DOTALL)

            if json_scripts:
                print(f"\n✓ {len(json_scripts)} script(s) JSON trouvé(s)")

                for i, script in enumerate(json_scripts[:3], 1):
                    try:
                        data = json.loads(script)
                        print(f"\n  Script {i}:")
                        print(f"  Clés: {list(data.keys())}")

                        # Sauvegarder
                        with open(f'squadi_json_data_{i}.json', 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"  ✓ Sauvegardé: squadi_json_data_{i}.json")

                    except json.JSONDecodeError:
                        continue

            # Sauvegarder la page complète
            filename = f"squadi_cloudscraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✓ Page complète sauvegardée: {filename}")

        else:
            print(f"❌ Échec: Status {response.status_code}")

    except ImportError:
        print("\n❌ cloudscraper n'est pas installé")
        print("   Installation: pip install cloudscraper")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def guide_selenium():
    """Guide pour utiliser Selenium"""
    print("\n" + "=" * 80)
    print("3. GUIDE SELENIUM")
    print("=" * 80)

    print("""
Selenium est la méthode la plus fiable pour scraper un site protégé.
Voici comment l'utiliser:

1. Installation:
   pip install selenium webdriver-manager

2. Code de base:

   from selenium import webdriver
   from selenium.webdriver.chrome.options import Options
   from selenium.webdriver.chrome.service import Service
   from webdriver_manager.chrome import ChromeDriverManager

   # Configuration
   options = Options()
   options.add_argument('--headless')
   options.add_argument('--no-sandbox')
   options.add_argument('--disable-dev-shm-usage')

   # Créer le driver
   service = Service(ChromeDriverManager().install())
   driver = webdriver.Chrome(service=service, options=options)

   # Accéder à la page
   driver.get('https://registration.us.squadi.com')

   # Attendre le chargement
   import time
   time.sleep(5)

   # Récupérer le contenu
   html = driver.page_source

   # Fermer
   driver.quit()

3. Pour intercepter les requêtes réseau (avancé):

   # Activer les logs de performance
   options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

   # Après avoir chargé la page
   logs = driver.get_log('performance')

   # Analyser les logs pour trouver les requêtes API
   for log in logs:
       message = json.loads(log['message'])
       if 'Network.requestWillBeSent' in message['message']['method']:
           url = message['message']['params']['request']['url']
           if 'api' in url or 'schedule' in url:
               print(url)

4. Utiliser le scraper fourni:
   python squadi_schedules_scraper.py
   # Choisir l'option 4 (Selenium)
""")


def manual_inspection_guide():
    """Guide pour l'inspection manuelle"""
    print("\n" + "=" * 80)
    print("4. GUIDE D'INSPECTION MANUELLE")
    print("=" * 80)

    print("""
Si les méthodes automatiques échouent, inspectez manuellement:

1. Ouvrez https://registration.us.squadi.com dans Chrome

2. Ouvrez les DevTools (F12)

3. Allez dans l'onglet "Network" (Réseau)

4. Rafraîchissez la page (F5)

5. Cherchez les requêtes qui contiennent:
   - "api"
   - "schedule"
   - "event"
   - "tournament"

6. Cliquez sur une requête intéressante et notez:
   - L'URL complète
   - Les headers (surtout Authorization)
   - Les paramètres Query
   - Le corps de la réponse

7. Dans l'onglet "Console", essayez:

   // Chercher des variables globales
   console.log(window)

   // Chercher des données de schedules
   Object.keys(window).filter(k => k.toLowerCase().includes('schedule'))

   // Chercher des configurations d'API
   Object.keys(window).filter(k => k.toLowerCase().includes('api'))

8. Dans l'onglet "Sources", cherchez dans les fichiers JS:
   - Recherchez "schedule"
   - Recherchez "apiUrl" ou "baseURL"
   - Recherchez les fonctions fetch() ou axios()

9. Une fois que vous avez trouvé l'URL de l'API, testez-la:

   import requests

   url = "https://api.squadi.com/v1/schedules"  # Remplacez par l'URL trouvée
   headers = {
       'Authorization': 'Bearer TOKEN',  # Si nécessaire
       'Content-Type': 'application/json'
   }

   response = requests.get(url, headers=headers)
   data = response.json()
   print(json.dumps(data, indent=2))
""")


def create_browser_script():
    """Crée un script pour exécution dans le navigateur"""
    print("\n" + "=" * 80)
    print("5. SCRIPT POUR LE NAVIGATEUR")
    print("=" * 80)

    script = """
// ==================================================================
// Script à exécuter dans la console du navigateur (F12 -> Console)
// ==================================================================

// 1. Intercepter toutes les requêtes fetch
(function() {
    const originalFetch = window.fetch;
    const capturedRequests = [];

    window.fetch = function(...args) {
        const url = args[0];

        // Capturer l'URL
        if (url && (url.includes('api') || url.includes('schedule'))) {
            console.log('🔍 API Request:', url);
            capturedRequests.push(url);
        }

        return originalFetch.apply(this, args);
    };

    // Fonction pour afficher toutes les URLs capturées
    window.getCapturedRequests = () => {
        console.log('📋 Captured Requests:', capturedRequests);
        return capturedRequests;
    };

    console.log('✓ Fetch interceptor installé!');
    console.log('  Utilisez getCapturedRequests() pour voir les URLs');
})();

// 2. Chercher des données de schedules dans le DOM
function findScheduleData() {
    // Chercher dans tous les scripts JSON
    const scripts = document.querySelectorAll('script[type="application/json"]');
    const jsonData = [];

    scripts.forEach((script, index) => {
        try {
            const data = JSON.parse(script.textContent);
            console.log(`📄 JSON Script ${index + 1}:`, data);
            jsonData.push(data);
        } catch (e) {
            // Pas du JSON valide
        }
    });

    return jsonData;
}

// 3. Chercher dans window/global scope
function findGlobalScheduleData() {
    const matches = [];

    for (let key in window) {
        const lowerKey = key.toLowerCase();
        if (lowerKey.includes('schedule') || lowerKey.includes('event') || lowerKey.includes('api')) {
            try {
                const value = window[key];
                console.log(`🔑 window.${key}:`, value);
                matches.push({ key, value });
            } catch (e) {
                // Propriété non accessible
            }
        }
    }

    return matches;
}

// 4. Exporter les données
function exportSchedules() {
    const jsonData = findScheduleData();
    const globalData = findGlobalScheduleData();

    const exportData = {
        timestamp: new Date().toISOString(),
        jsonScripts: jsonData,
        globalData: globalData,
        capturedRequests: window.getCapturedRequests ? window.getCapturedRequests() : []
    };

    // Télécharger en JSON
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'squadi_export_' + Date.now() + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✓ Données exportées!');
}

console.log('');
console.log('='.repeat(60));
console.log('SQUADI SCHEDULE EXTRACTOR - Ready!');
console.log('='.repeat(60));
console.log('');
console.log('Commandes disponibles:');
console.log('  findScheduleData()      - Chercher JSON dans le DOM');
console.log('  findGlobalScheduleData() - Chercher dans window');
console.log('  getCapturedRequests()   - Voir les requêtes capturées');
console.log('  exportSchedules()       - Télécharger toutes les données');
console.log('');
console.log('Naviguez sur le site, puis utilisez exportSchedules()');
console.log('');
"""

    filename = "squadi_browser_script.js"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"✓ Script créé: {filename}")
    print("\nUtilisation:")
    print("1. Ouvrez https://registration.us.squadi.com")
    print("2. Ouvrez la console (F12 -> Console)")
    print(f"3. Copiez-collez le contenu de {filename}")
    print("4. Naviguez sur le site")
    print("5. Tapez: exportSchedules()")
    print("6. Un fichier JSON sera téléchargé avec toutes les données")


def main():
    """Fonction principale"""
    print("=" * 80)
    print("SQUADI MANUAL EXPLORER")
    print("=" * 80)
    print("\nCe script va vous aider à explorer le site Squadi et")
    print("découvrir comment accéder aux schedules.")

    # Test 1: Accès basique
    test_basic_access()

    # Test 2: Cloudscraper
    test_with_cloudscraper()

    # Guide Selenium
    guide_selenium()

    # Guide inspection manuelle
    manual_inspection_guide()

    # Script navigateur
    create_browser_script()

    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print("""
Méthodes disponibles (par ordre de facilité):

1. ✅ Script navigateur (squadi_browser_script.js)
   → Copier-coller dans la console Chrome
   → Capture automatiquement les données

2. ✅ Inspection manuelle
   → DevTools -> Network
   → Identifier les requêtes API

3. ✅ Cloudscraper (si fichiers HTML générés)
   → Analyser les fichiers squadi_*.html
   → Chercher les endpoints API

4. ✅ Selenium
   → python squadi_schedules_scraper.py
   → Choisir option 4

Fichiers générés:
- squadi_browser_script.js (à utiliser dans le navigateur)
- squadi_*.html (pages sauvegardées)
- squadi_apis.json (endpoints découverts)
- squadi_json_data_*.json (données JSON trouvées)
""")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
