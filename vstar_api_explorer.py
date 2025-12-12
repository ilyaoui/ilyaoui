#!/usr/bin/env python3
"""
Vstar Volleyball API Explorer
------------------------------
Outil de recherche et d'analyse des endpoints potentiels de l'API vstarvolleyball.com

Ce script teste différents endpoints pour déterminer s'il existe une API accessible
pour récupérer les données de calendriers, matchs, équipes, etc.
"""

import requests
import json
import re
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VstarAPIExplorer:
    """
    Explorateur d'API pour vstarvolleyball.com
    """

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialise l'explorateur

        Args:
            rate_limit: Délai en secondes entre les requêtes
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://ntr.vstarvolleyball.com/',
        })
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.discovered_endpoints = []

    def _rate_limit_request(self):
        """Applique le rate limiting entre les requêtes"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def test_endpoint(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Teste un endpoint spécifique

        Args:
            url: URL de l'endpoint
            params: Paramètres optionnels

        Returns:
            Dictionnaire avec les résultats du test
        """
        result = {
            'url': url,
            'params': params,
            'status': 'failed',
            'status_code': None,
            'content_type': None,
            'is_json': False,
            'data': None,
            'error': None
        }

        try:
            self._rate_limit_request()
            logger.info(f"Test: {url} {params or ''}")

            response = self.session.get(url, params=params, timeout=10)
            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('Content-Type', '')

            if response.status_code == 200:
                result['status'] = 'success'

                # Vérifier si c'est du JSON
                if 'application/json' in result['content_type']:
                    result['is_json'] = True
                    result['data'] = response.json()
                    logger.info(f"✓ JSON trouvé: {url}")
                else:
                    # Essayer de parser quand même
                    try:
                        result['data'] = response.json()
                        result['is_json'] = True
                        logger.info(f"✓ JSON trouvé (non déclaré): {url}")
                    except json.JSONDecodeError:
                        result['data'] = response.text[:500]  # Premiers 500 caractères
                        logger.info(f"✓ HTML/Texte: {url}")

            elif response.status_code == 403:
                result['error'] = 'Accès refusé (403)'
                logger.warning(f"✗ 403 Forbidden: {url}")
            elif response.status_code == 404:
                result['error'] = 'Non trouvé (404)'
                logger.debug(f"✗ 404 Not Found: {url}")
            else:
                result['error'] = f'HTTP {response.status_code}'
                logger.debug(f"✗ {result['error']}: {url}")

        except requests.exceptions.Timeout:
            result['error'] = 'Timeout'
            logger.debug(f"✗ Timeout: {url}")
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            logger.debug(f"✗ Erreur: {url} - {e}")

        if result['status'] == 'success':
            self.discovered_endpoints.append(result)

        return result

    def explore_api_patterns(self) -> List[Dict]:
        """
        Explore les patterns d'API courants pour vstarvolleyball.com

        Returns:
            Liste des endpoints découverts
        """
        logger.info("=== Exploration des patterns d'API ===")

        # Patterns d'API à tester
        base_urls = [
            "https://ntr.vstarvolleyball.com",
            "https://results.vstarvolleyball.com",
            "https://api.vstarvolleyball.com",
            "https://vstarvolleyball.com",
        ]

        api_paths = [
            "/api/schedule",
            "/api/tournaments",
            "/api/events",
            "/api/matches",
            "/api/teams",
            "/api/divisions",
            "/api/v1/schedule",
            "/api/v1/tournaments",
            "/data/schedule.json",
            "/data/tournaments.json",
            "/Internet/api/schedule",
            "/Internet/api/tournaments",
        ]

        results = []

        for base in base_urls:
            for path in api_paths:
                url = base + path
                result = self.test_endpoint(url)
                results.append(result)

        return results

    def explore_php_endpoints(self) -> List[Dict]:
        """
        Explore les endpoints PHP connus avec différents paramètres

        Returns:
            Liste des résultats
        """
        logger.info("=== Exploration des endpoints PHP ===")

        results = []

        # Endpoints connus
        endpoints = [
            {
                'url': 'https://ntr.vstarvolleyball.com/Internet/schedule.php',
                'params_to_test': [
                    {},
                    {'format': 'json'},
                    {'output': 'json'},
                    {'ajax': '1'},
                    {'Tournament_ID': '430'},
                    {'Tournament_ID': '1409'},
                ]
            },
            {
                'url': 'https://ntr.vstarvolleyball.com/Internet/event_info.php',
                'params_to_test': [
                    {'Tournament_ID': '430'},
                    {'Tournament_ID': '430', 'format': 'json'},
                    {'Tournament_ID': '1409'},
                    {'Tournament_ID': '1409', 'format': 'json'},
                ]
            },
            {
                'url': 'https://ntr.vstarvolleyball.com/Internet/results.php',
                'params_to_test': [
                    {},
                    {'format': 'json'},
                    {'Tournament_ID': '430'},
                ]
            },
        ]

        for endpoint_config in endpoints:
            url = endpoint_config['url']
            for params in endpoint_config['params_to_test']:
                result = self.test_endpoint(url, params)
                results.append(result)

        return results

    def analyze_html_for_ajax(self, url: str) -> Dict:
        """
        Analyse le HTML d'une page pour découvrir des appels AJAX

        Args:
            url: URL de la page à analyser

        Returns:
            Dictionnaire des endpoints AJAX découverts
        """
        logger.info(f"=== Analyse AJAX de {url} ===")

        result = {
            'url': url,
            'ajax_endpoints': [],
            'api_urls': [],
            'json_data': []
        }

        try:
            self._rate_limit_request()
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                html = response.text

                # Chercher des URLs d'API dans le JavaScript
                api_patterns = [
                    r'https?://[^"\'\s]+\.php\?[^"\'\s]+',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'ajax\(["\']([^"\']+)["\']',
                    r'\$\.get\(["\']([^"\']+)["\']',
                    r'\$\.post\(["\']([^"\']+)["\']',
                    r'url\s*:\s*["\']([^"\']+)["\']',
                ]

                for pattern in api_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match not in result['ajax_endpoints']:
                            result['ajax_endpoints'].append(match)
                            logger.info(f"  Endpoint AJAX trouvé: {match}")

                # Chercher des données JSON embarquées
                json_patterns = [
                    r'var\s+\w+\s*=\s*(\{.+?\});',
                    r'<script[^>]*type="application/json"[^>]*>(.+?)</script>',
                ]

                for pattern in json_patterns:
                    matches = re.findall(pattern, html, re.DOTALL)
                    for match in matches[:5]:  # Limiter à 5 pour éviter trop de données
                        try:
                            data = json.loads(match)
                            result['json_data'].append(data)
                            logger.info(f"  Données JSON trouvées dans la page")
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'analyse: {e}")

        return result

    def generate_report(self, output_file: str = None):
        """
        Génère un rapport des endpoints découverts

        Args:
            output_file: Fichier de sortie optionnel
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_discovered': len(self.discovered_endpoints),
            'endpoints': self.discovered_endpoints,
            'summary': {
                'json_endpoints': len([e for e in self.discovered_endpoints if e['is_json']]),
                'html_endpoints': len([e for e in self.discovered_endpoints if not e['is_json']]),
            }
        }

        # Afficher le résumé
        print("\n" + "=" * 80)
        print("RAPPORT D'EXPLORATION DE L'API VSTAR VOLLEYBALL")
        print("=" * 80)
        print(f"\nTotal d'endpoints testés: {len(self.discovered_endpoints)}")
        print(f"Endpoints JSON: {report['summary']['json_endpoints']}")
        print(f"Endpoints HTML: {report['summary']['html_endpoints']}")

        if report['summary']['json_endpoints'] > 0:
            print("\n✓ ENDPOINTS JSON DÉCOUVERTS:")
            for endpoint in self.discovered_endpoints:
                if endpoint['is_json']:
                    print(f"  • {endpoint['url']}")
                    if endpoint['params']:
                        print(f"    Paramètres: {endpoint['params']}")

        # Sauvegarder le rapport
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Rapport complet sauvegardé: {output_file}")

        return report


def main():
    """Fonction principale"""
    print("=" * 80)
    print("VSTAR VOLLEYBALL API EXPLORER")
    print("=" * 80)
    print("\nCet outil explore les endpoints potentiels de l'API vstarvolleyball.com")
    print("pour déterminer s'il existe des APIs accessibles pour récupérer les données")
    print("de calendriers, matchs, équipes, etc.")
    print()

    explorer = VstarAPIExplorer(rate_limit=1.5)

    # 1. Explorer les patterns d'API standards
    print("\n[1/3] Test des patterns d'API standards...")
    api_results = explorer.explore_api_patterns()

    # 2. Explorer les endpoints PHP avec paramètres
    print("\n[2/3] Test des endpoints PHP avec paramètres...")
    php_results = explorer.explore_php_endpoints()

    # 3. Analyser le HTML pour des appels AJAX
    print("\n[3/3] Analyse du HTML pour appels AJAX...")
    ajax_analysis = explorer.analyze_html_for_ajax('https://ntr.vstarvolleyball.com/Internet/schedule.php')

    # Générer le rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"vstar_api_exploration_{timestamp}.json"
    report = explorer.generate_report(report_file)

    # Afficher les résultats AJAX
    if ajax_analysis['ajax_endpoints']:
        print("\n✓ ENDPOINTS AJAX DÉCOUVERTS DANS LE HTML:")
        for endpoint in ajax_analysis['ajax_endpoints'][:10]:
            print(f"  • {endpoint}")

    print("\n" + "=" * 80)
    print("Exploration terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()
