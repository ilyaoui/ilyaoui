#!/usr/bin/env python3
"""
Total Global Sports (TGS) API Investigation
-------------------------------------------
Script pour investiguer et documenter l'API de public.totalglobalsports.com

Ce script teste différents endpoints API potentiels et documente les résultats.
"""

import requests
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TGSAPIInvestigator:
    """
    Investigateur pour l'API Total Global Sports
    """

    BASE_URLS = [
        "https://public.totalglobalsports.com",
        "https://api.totalglobalsports.com",
        "https://admin.totalglobalsports.com",
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://public.totalglobalsports.com',
            'Referer': 'https://public.totalglobalsports.com/',
        })
        self.findings = {
            'accessible_endpoints': [],
            'blocked_endpoints': [],
            'discovered_patterns': [],
            'api_structure': {},
            'timestamp': datetime.now().isoformat()
        }

    def test_endpoint(self, url: str, method: str = 'GET', **kwargs) -> Dict:
        """
        Teste un endpoint API

        Args:
            url: URL de l'endpoint
            method: Méthode HTTP (GET, POST, etc.)
            **kwargs: Arguments supplémentaires pour requests

        Returns:
            Dictionnaire avec les résultats du test
        """
        result = {
            'url': url,
            'method': method,
            'status_code': None,
            'accessible': False,
            'content_type': None,
            'response_sample': None,
            'error': None
        }

        try:
            logger.info(f"Testing {method} {url}")

            if method == 'GET':
                response = self.session.get(url, timeout=10, **kwargs)
            elif method == 'POST':
                response = self.session.post(url, timeout=10, **kwargs)
            else:
                response = self.session.request(method, url, timeout=10, **kwargs)

            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('Content-Type', '')

            if response.status_code == 200:
                result['accessible'] = True
                logger.info(f"✓ Accessible: {url} (Status: {response.status_code})")

                # Essayer de parser le JSON
                if 'application/json' in result['content_type']:
                    try:
                        json_data = response.json()
                        # Limiter la taille de l'échantillon
                        result['response_sample'] = str(json_data)[:500]
                        result['json_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else None
                    except json.JSONDecodeError:
                        result['response_sample'] = response.text[:500]
                else:
                    result['response_sample'] = response.text[:500]

                self.findings['accessible_endpoints'].append(result)
            else:
                logger.debug(f"✗ Non accessible: {url} (Status: {response.status_code})")
                result['error'] = f"HTTP {response.status_code}"
                self.findings['blocked_endpoints'].append(result)

        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            logger.debug(f"✗ Erreur: {url} - {e}")
            self.findings['blocked_endpoints'].append(result)

        return result

    def test_common_api_patterns(self):
        """
        Teste les patterns d'API communs
        """
        logger.info("\n=== Test des patterns d'API communs ===\n")

        endpoints_to_test = [
            # API publique
            ("/api/events", "GET"),
            ("/api/v1/events", "GET"),
            ("/api/v2/events", "GET"),
            ("/api/tournaments", "GET"),
            ("/api/schedules", "GET"),
            ("/api/games", "GET"),
            ("/api/teams", "GET"),

            # Endpoints publics connus
            ("/public/event", "GET"),
            ("/public/events", "GET"),
            ("/public/tournament", "GET"),
            ("/public/schedule", "GET"),

            # WordPress API (trouvé dans la recherche)
            ("/wp-json/tribe/events/v1/events", "GET"),
            ("/wp-json/wp/v2/events", "GET"),

            # Auth endpoints
            ("/auth/user-information", "GET"),
            ("/auth/roles-select", "GET"),

            # GraphQL endpoints
            ("/graphql", "POST"),
            ("/api/graphql", "POST"),
        ]

        for base_url in self.BASE_URLS:
            logger.info(f"\nTesting base URL: {base_url}")
            for endpoint, method in endpoints_to_test:
                url = f"{base_url}{endpoint}"
                self.test_endpoint(url, method)

    def test_event_id_patterns(self):
        """
        Teste l'accès à des événements spécifiques avec différents IDs
        """
        logger.info("\n=== Test des patterns d'événements spécifiques ===\n")

        # IDs d'exemple à tester (basé sur les URLs trouvées)
        test_ids = [3973, 1, 100, 1000]

        patterns = [
            "/public/event/{id}",
            "/public/event/{id}/schedules",
            "/public/event/{id}/schedules-standings",
            "/public/event/{id}/teams",
            "/public/event/{id}/games",
            "/api/events/{id}",
            "/api/v1/events/{id}",
        ]

        for base_url in ["https://public.totalglobalsports.com"]:
            for pattern in patterns:
                for event_id in test_ids:
                    url = f"{base_url}{pattern.format(id=event_id)}"
                    result = self.test_endpoint(url)

                    if result['accessible']:
                        logger.info(f"✓✓✓ FOUND WORKING PATTERN: {pattern}")
                        self.findings['discovered_patterns'].append(pattern)
                        break  # Ne tester qu'un seul ID si le pattern fonctionne

    def test_discovered_api_endpoints(self):
        """
        Teste les endpoints API découverts via d'autres sources
        """
        logger.info("\n=== Test des endpoints découverts ===\n")

        # Basé sur les résultats de recherche précédents
        discovered_urls = [
            "https://www.totalglobalsports.com/wp-json/tribe/events/v1/events",
            "https://public.totalglobalsports.com/auth/user-information",
            "https://public.totalglobalsports.com/auth/roles-select",
            "https://public.totalglobalsports.com/public/event/3973/schedules-standings",
        ]

        for url in discovered_urls:
            self.test_endpoint(url)

    def investigate_javascript_api_calls(self):
        """
        Tente de découvrir les appels API en examinant le JavaScript de la page
        """
        logger.info("\n=== Investigation du JavaScript ===\n")

        try:
            # Récupérer la page principale
            response = self.session.get("https://public.totalglobalsports.com", timeout=10)

            if response.status_code == 200:
                html = response.text

                # Chercher des patterns d'API dans le HTML/JS
                import re

                # Patterns à chercher
                api_patterns = [
                    r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'baseURL["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'axios\.(get|post)\(["\']([^"\']+)["\']',
                    r'https?://[a-zA-Z0-9.-]+totalglobalsports\.com/[a-zA-Z0-9/._-]+',
                ]

                discovered_urls = set()
                for pattern in api_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        url = match if isinstance(match, str) else (match[1] if len(match) > 1 else match[0])
                        if 'totalglobalsports' in url or url.startswith('/'):
                            discovered_urls.add(url)

                logger.info(f"URLs découvertes dans le JavaScript: {len(discovered_urls)}")
                self.findings['discovered_urls_from_js'] = list(discovered_urls)

                # Tester les URLs découvertes
                for url in list(discovered_urls)[:10]:  # Limiter aux 10 premières
                    if url.startswith('/'):
                        url = f"https://public.totalglobalsports.com{url}"
                    if url.startswith('http'):
                        self.test_endpoint(url)

        except Exception as e:
            logger.error(f"Erreur lors de l'investigation du JavaScript: {e}")

    def test_graphql_introspection(self):
        """
        Teste si un endpoint GraphQL est disponible avec introspection
        """
        logger.info("\n=== Test GraphQL Introspection ===\n")

        introspection_query = {
            "query": """
                {
                    __schema {
                        types {
                            name
                            kind
                            description
                        }
                    }
                }
            """
        }

        graphql_urls = [
            "https://public.totalglobalsports.com/graphql",
            "https://api.totalglobalsports.com/graphql",
            "https://public.totalglobalsports.com/api/graphql",
        ]

        for url in graphql_urls:
            result = self.test_endpoint(url, method='POST', json=introspection_query)
            if result['accessible']:
                logger.info(f"✓✓✓ GraphQL endpoint trouvé: {url}")

    def generate_report(self) -> str:
        """
        Génère un rapport complet de l'investigation

        Returns:
            Rapport formaté en markdown
        """
        report = []
        report.append("# Investigation de l'API Total Global Sports")
        report.append(f"\nDate: {self.findings['timestamp']}")
        report.append("\n## Résumé\n")

        total_tested = len(self.findings['accessible_endpoints']) + len(self.findings['blocked_endpoints'])
        accessible_count = len(self.findings['accessible_endpoints'])

        report.append(f"- Endpoints testés: {total_tested}")
        report.append(f"- Endpoints accessibles: {accessible_count}")
        report.append(f"- Endpoints bloqués: {len(self.findings['blocked_endpoints'])}")
        report.append(f"- Patterns découverts: {len(self.findings['discovered_patterns'])}")

        if self.findings['accessible_endpoints']:
            report.append("\n## ✓ Endpoints Accessibles\n")
            for endpoint in self.findings['accessible_endpoints']:
                report.append(f"\n### {endpoint['method']} {endpoint['url']}")
                report.append(f"- Status: {endpoint['status_code']}")
                report.append(f"- Content-Type: {endpoint['content_type']}")
                if endpoint.get('json_keys'):
                    report.append(f"- JSON Keys: {', '.join(endpoint['json_keys'])}")
                if endpoint.get('response_sample'):
                    report.append(f"- Échantillon de réponse:")
                    report.append(f"```\n{endpoint['response_sample']}\n```")

        if self.findings['discovered_patterns']:
            report.append("\n## 🔍 Patterns d'URL Fonctionnels\n")
            for pattern in set(self.findings['discovered_patterns']):
                report.append(f"- `{pattern}`")

        if self.findings.get('discovered_urls_from_js'):
            report.append("\n## 📜 URLs Découvertes dans le JavaScript\n")
            for url in self.findings['discovered_urls_from_js'][:20]:
                report.append(f"- {url}")

        report.append("\n## Endpoints Bloqués (échantillon)\n")
        for endpoint in self.findings['blocked_endpoints'][:10]:
            report.append(f"- {endpoint['method']} {endpoint['url']} - {endpoint['error']}")

        report.append("\n## Recommandations\n")

        if accessible_count > 0:
            report.append("\n✓ Des endpoints API ont été découverts !")
            report.append("\nPour utiliser ces endpoints:")
            report.append("1. Examinez la structure de réponse JSON")
            report.append("2. Identifiez les paramètres requis (query params, headers)")
            report.append("3. Testez l'authentification si nécessaire")
            report.append("4. Documentez les endpoints fonctionnels")
        else:
            report.append("\n✗ Aucun endpoint API public n'a été trouvé.")
            report.append("\nOptions:")
            report.append("1. **Contacter TGS directement** pour demander accès à l'API")
            report.append("2. **Web Scraping** des pages publiques HTML")
            report.append("3. **Reverse engineering** de l'application web (avec autorisation)")
            report.append("4. **Utiliser le mode développeur du navigateur** pour observer les appels API réels")

        return "\n".join(report)

    def save_findings(self, json_file: str = "tgs_api_findings.json",
                      report_file: str = "tgs_api_investigation_report.md"):
        """
        Sauvegarde les résultats de l'investigation

        Args:
            json_file: Fichier JSON pour les données brutes
            report_file: Fichier Markdown pour le rapport
        """
        # Sauvegarder le JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Données brutes sauvegardées: {json_file}")

        # Sauvegarder le rapport
        report = self.generate_report()
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"✓ Rapport sauvegardé: {report_file}")


def main():
    """
    Fonction principale pour lancer l'investigation complète
    """
    print("=" * 80)
    print("INVESTIGATION DE L'API TOTAL GLOBAL SPORTS")
    print("=" * 80)
    print()
    print("Ce script va tester différents endpoints API potentiels de TGS")
    print("pour déterminer s'il existe une API publique accessible.")
    print()

    investigator = TGSAPIInvestigator()

    # Lancer les différents tests
    investigator.test_common_api_patterns()
    investigator.test_event_id_patterns()
    investigator.test_discovered_api_endpoints()
    investigator.investigate_javascript_api_calls()
    investigator.test_graphql_introspection()

    # Générer et sauvegarder les résultats
    print("\n" + "=" * 80)
    print("GÉNÉRATION DU RAPPORT")
    print("=" * 80)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"tgs_api_findings_{timestamp}.json"
    report_file = f"tgs_api_investigation_{timestamp}.md"

    investigator.save_findings(json_file, report_file)

    print("\n" + "=" * 80)
    print("INVESTIGATION TERMINÉE")
    print("=" * 80)
    print()
    print("Fichiers générés:")
    print(f"  - {json_file} (données brutes JSON)")
    print(f"  - {report_file} (rapport détaillé)")
    print()

    # Afficher un résumé
    accessible_count = len(investigator.findings['accessible_endpoints'])
    total_tested = accessible_count + len(investigator.findings['blocked_endpoints'])

    print(f"Résumé: {accessible_count}/{total_tested} endpoints accessibles")

    if accessible_count > 0:
        print("\n✓ Des endpoints API ont été découverts !")
        print("\nEndpoints accessibles:")
        for ep in investigator.findings['accessible_endpoints']:
            print(f"  - {ep['method']} {ep['url']} (Status: {ep['status_code']})")
    else:
        print("\n✗ Aucun endpoint API public trouvé.")
        print("Consultez le rapport pour les recommandations.")


if __name__ == "__main__":
    main()
