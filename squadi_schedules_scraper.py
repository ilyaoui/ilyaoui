#!/usr/bin/env python3
"""
Squadi Schedules Scraper
------------------------
Scraper pour récupérer tous les schedules à venir depuis registration.us.squadi.com

Ce scraper utilise plusieurs techniques pour contourner les protections anti-bot:
1. Selenium avec navigateur headless
2. Requêtes HTTP avancées avec sessions
3. Détection et extraction d'API endpoints
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SquadiSchedulesScraper:
    """
    Scraper pour les schedules Squadi
    """

    BASE_URL = "https://registration.us.squadi.com"

    def __init__(self):
        """Initialise le scraper"""
        self.schedules = []
        self.use_selenium = False

    def scrape_with_selenium(self) -> List[Dict]:
        """
        Scrape avec Selenium pour contourner les protections JavaScript

        Returns:
            Liste des schedules trouvés
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager

            logger.info("Initialisation de Selenium...")

            # Configuration Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Initialiser le driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                logger.info(f"Accès à {self.BASE_URL}...")
                driver.get(self.BASE_URL)

                # Attendre le chargement de la page
                time.sleep(5)

                # Capturer le contenu de la page
                page_source = driver.page_source

                # Extraire les données de la page
                schedules = self._parse_page_content(page_source)

                # Chercher des liens vers des schedules
                schedule_links = self._find_schedule_links(driver)

                # Visiter chaque lien de schedule
                for link in schedule_links[:10]:  # Limiter à 10 pour commencer
                    try:
                        logger.info(f"Scraping schedule: {link}")
                        driver.get(link)
                        time.sleep(2)

                        schedule_data = self._extract_schedule_data(driver)
                        if schedule_data:
                            schedules.append(schedule_data)

                    except Exception as e:
                        logger.error(f"Erreur sur {link}: {e}")
                        continue

                # Intercepter les requêtes réseau (si possible)
                logs = driver.get_log('performance')
                api_endpoints = self._extract_api_from_logs(logs)

                if api_endpoints:
                    logger.info(f"API endpoints découverts: {api_endpoints}")
                    # Essayer d'accéder directement aux APIs
                    for endpoint in api_endpoints:
                        api_data = self._fetch_api_data(endpoint)
                        if api_data:
                            schedules.extend(self._parse_api_response(api_data))

                return schedules

            finally:
                driver.quit()

        except ImportError:
            logger.error("Selenium n'est pas installé. Installation requise:")
            logger.error("  pip install selenium webdriver-manager")
            return []
        except Exception as e:
            logger.error(f"Erreur Selenium: {e}")
            return []

    def scrape_with_requests(self) -> List[Dict]:
        """
        Tente de scraper avec requests et cloudscraper

        Returns:
            Liste des schedules
        """
        schedules = []

        # Essayer cloudscraper pour contourner Cloudflare
        try:
            import cloudscraper

            logger.info("Utilisation de cloudscraper...")
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )

            response = scraper.get(self.BASE_URL)

            if response.status_code == 200:
                logger.info("✓ Accès réussi avec cloudscraper")
                schedules = self._parse_page_content(response.text)

                # Chercher des API endpoints dans le HTML
                api_urls = self._find_api_endpoints_in_html(response.text)

                for api_url in api_urls:
                    try:
                        api_response = scraper.get(api_url)
                        if api_response.status_code == 200:
                            api_data = api_response.json()
                            schedules.extend(self._parse_api_response(api_data))
                    except Exception as e:
                        logger.debug(f"Erreur API {api_url}: {e}")

            else:
                logger.warning(f"Code de statut: {response.status_code}")

        except ImportError:
            logger.warning("cloudscraper non installé. Installation recommandée:")
            logger.warning("  pip install cloudscraper")
        except Exception as e:
            logger.error(f"Erreur avec cloudscraper: {e}")

        return schedules

    def scrape_api_directly(self) -> List[Dict]:
        """
        Tente de découvrir et accéder directement aux APIs Squadi

        Returns:
            Liste des schedules
        """
        schedules = []

        # Endpoints potentiels de l'API Squadi
        potential_endpoints = [
            f"{self.BASE_URL}/api/schedules",
            f"{self.BASE_URL}/api/events",
            f"{self.BASE_URL}/api/tournaments",
            f"{self.BASE_URL}/api/v1/schedules",
            f"{self.BASE_URL}/api/v1/events",
            f"{self.BASE_URL}/api/upcoming",
            "https://api.squadi.com/schedules",
            "https://api.squadi.com/events",
            "https://api.squadi.com/v1/schedules",
        ]

        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
        except ImportError:
            import requests
            scraper = requests.Session()
            scraper.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': self.BASE_URL,
            })

        for endpoint in potential_endpoints:
            try:
                logger.info(f"Test endpoint: {endpoint}")
                response = scraper.get(endpoint, timeout=10)

                if response.status_code == 200:
                    logger.info(f"✓ Endpoint actif: {endpoint}")

                    # Essayer de parser en JSON
                    try:
                        data = response.json()
                        parsed = self._parse_api_response(data)
                        if parsed:
                            schedules.extend(parsed)
                            logger.info(f"  → {len(parsed)} schedule(s) trouvé(s)")
                    except json.JSONDecodeError:
                        # Ce n'est pas du JSON
                        logger.debug(f"Endpoint ne retourne pas de JSON")

            except Exception as e:
                logger.debug(f"Endpoint {endpoint}: {e}")
                continue

        return schedules

    def _parse_page_content(self, html: str) -> List[Dict]:
        """
        Parse le contenu HTML de la page pour extraire les schedules

        Args:
            html: Contenu HTML

        Returns:
            Liste des schedules
        """
        schedules = []

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, 'html.parser')

            # Chercher des données JSON embarquées
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Chercher des patterns JSON
                    json_patterns = [
                        r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                        r'window\.__PRELOADED_STATE__\s*=\s*({.+?});',
                        r'var\s+schedules\s*=\s*({.+?});',
                        r'var\s+events\s*=\s*(\[.+?\]);',
                        r'"schedules"\s*:\s*(\[.+?\])',
                    ]

                    for pattern in json_patterns:
                        matches = re.findall(pattern, script.string, re.DOTALL)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                parsed = self._parse_api_response(data)
                                if parsed:
                                    schedules.extend(parsed)
                            except json.JSONDecodeError:
                                continue

            # Chercher des éléments HTML de schedule
            schedule_elements = soup.find_all(['div', 'section', 'article'],
                                             class_=re.compile(r'schedule|event|tournament', re.I))

            for elem in schedule_elements:
                schedule = self._extract_schedule_from_element(elem)
                if schedule:
                    schedules.append(schedule)

        except ImportError:
            logger.error("BeautifulSoup4 non installé. Installation requise:")
            logger.error("  pip install beautifulsoup4")
        except Exception as e:
            logger.error(f"Erreur parsing HTML: {e}")

        return schedules

    def _extract_schedule_from_element(self, element) -> Optional[Dict]:
        """
        Extrait les données d'un schedule depuis un élément HTML

        Args:
            element: Élément BeautifulSoup

        Returns:
            Dictionnaire du schedule ou None
        """
        try:
            schedule = {}

            # Titre/Nom
            title = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if title:
                schedule['title'] = title.get_text(strip=True)

            # Date
            date_elem = element.find(['time', 'span', 'div'], class_=re.compile(r'date', re.I))
            if date_elem:
                schedule['date'] = date_elem.get_text(strip=True)
                if date_elem.get('datetime'):
                    schedule['datetime'] = date_elem['datetime']

            # Lieu
            location_elem = element.find(['span', 'div'], class_=re.compile(r'location|venue', re.I))
            if location_elem:
                schedule['location'] = location_elem.get_text(strip=True)

            # Lien
            link = element.find('a', href=True)
            if link:
                schedule['url'] = link['href']

            # ID
            if element.get('data-id') or element.get('id'):
                schedule['id'] = element.get('data-id') or element.get('id')

            return schedule if len(schedule) > 0 else None

        except Exception as e:
            logger.debug(f"Erreur extraction schedule: {e}")
            return None

    def _find_schedule_links(self, driver) -> List[str]:
        """
        Trouve tous les liens vers des schedules

        Args:
            driver: WebDriver Selenium

        Returns:
            Liste des URLs de schedules
        """
        links = []

        try:
            from selenium.webdriver.common.by import By

            # Chercher tous les liens
            elements = driver.find_elements(By.TAG_NAME, 'a')

            for elem in elements:
                href = elem.get_attribute('href')
                if href and ('schedule' in href.lower() or 'event' in href.lower()):
                    if href not in links:
                        links.append(href)

        except Exception as e:
            logger.error(f"Erreur recherche liens: {e}")

        return links

    def _extract_schedule_data(self, driver) -> Optional[Dict]:
        """
        Extrait les données d'un schedule depuis une page

        Args:
            driver: WebDriver Selenium

        Returns:
            Données du schedule
        """
        try:
            schedule = {
                'url': driver.current_url,
                'title': driver.title,
                'scraped_at': datetime.now().isoformat()
            }

            # Parser le contenu avec BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extraire les informations
            # Date
            date_elem = soup.find(['time', 'span', 'div'], class_=re.compile(r'date', re.I))
            if date_elem:
                schedule['date'] = date_elem.get_text(strip=True)

            # Description
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description', re.I))
            if desc_elem:
                schedule['description'] = desc_elem.get_text(strip=True)

            # Tables de données
            tables = soup.find_all('table')
            if tables:
                schedule['tables_data'] = []
                for table in tables:
                    table_data = self._extract_table_data(table)
                    if table_data:
                        schedule['tables_data'].append(table_data)

            return schedule

        except Exception as e:
            logger.error(f"Erreur extraction schedule: {e}")
            return None

    def _extract_table_data(self, table) -> List[Dict]:
        """Extrait les données d'une table HTML"""
        data = []

        try:
            # En-têtes
            headers = []
            header_row = table.find('thead') or table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            # Lignes
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if cells and headers:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell.get_text(strip=True)
                    if row_data:
                        data.append(row_data)

        except Exception as e:
            logger.debug(f"Erreur extraction table: {e}")

        return data

    def _find_api_endpoints_in_html(self, html: str) -> List[str]:
        """
        Trouve les endpoints API dans le code HTML

        Args:
            html: Contenu HTML

        Returns:
            Liste des URLs d'API
        """
        api_urls = []

        patterns = [
            r'https?://[^\s"\']+/api/[^\s"\']+',
            r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.[get|post]+\(["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                url = match if isinstance(match, str) else match[0]
                if url not in api_urls:
                    api_urls.append(url)

        return api_urls

    def _extract_api_from_logs(self, logs: List) -> List[str]:
        """
        Extrait les URLs d'API depuis les logs de performance Chrome

        Args:
            logs: Logs de performance

        Returns:
            Liste des URLs d'API
        """
        api_urls = []

        try:
            for log in logs:
                message = json.loads(log['message'])
                if 'message' in message:
                    method = message['message'].get('method', '')

                    if 'Network.requestWillBeSent' in method:
                        url = message['message']['params']['request']['url']
                        if 'api' in url.lower() or 'schedule' in url.lower():
                            if url not in api_urls:
                                api_urls.append(url)

        except Exception as e:
            logger.debug(f"Erreur extraction logs: {e}")

        return api_urls

    def _fetch_api_data(self, url: str) -> Optional[Dict]:
        """
        Récupère les données d'un endpoint API

        Args:
            url: URL de l'API

        Returns:
            Données JSON ou None
        """
        try:
            import requests

            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.debug(f"Erreur fetch API: {e}")

        return None

    def _parse_api_response(self, data: Dict) -> List[Dict]:
        """
        Parse la réponse d'une API pour extraire les schedules

        Args:
            data: Données JSON

        Returns:
            Liste des schedules
        """
        schedules = []

        # Récursif pour chercher les schedules dans toute la structure
        def extract_schedules(obj, path=""):
            if isinstance(obj, dict):
                # Chercher les clés qui pourraient contenir des schedules
                schedule_keys = ['schedules', 'events', 'tournaments', 'games', 'matches']

                for key in schedule_keys:
                    if key in obj and isinstance(obj[key], list):
                        for item in obj[key]:
                            if isinstance(item, dict):
                                schedules.append(item)

                # Continuer la recherche
                for key, value in obj.items():
                    extract_schedules(value, f"{path}.{key}")

            elif isinstance(obj, list):
                for item in obj:
                    extract_schedules(item, path)

        extract_schedules(data)

        return schedules

    def run(self, method: str = 'auto') -> List[Dict]:
        """
        Exécute le scraper

        Args:
            method: Méthode à utiliser ('auto', 'selenium', 'requests', 'api')

        Returns:
            Liste de tous les schedules trouvés
        """
        all_schedules = []

        if method == 'auto':
            # Essayer toutes les méthodes
            logger.info("Mode automatique - test de toutes les méthodes")

            # 1. Essayer l'API directement
            logger.info("\n=== Méthode 1: API directe ===")
            api_schedules = self.scrape_api_directly()
            if api_schedules:
                all_schedules.extend(api_schedules)
                logger.info(f"✓ {len(api_schedules)} schedule(s) via API")

            # 2. Essayer avec requests/cloudscraper
            logger.info("\n=== Méthode 2: Requests/Cloudscraper ===")
            request_schedules = self.scrape_with_requests()
            if request_schedules:
                all_schedules.extend(request_schedules)
                logger.info(f"✓ {len(request_schedules)} schedule(s) via requests")

            # 3. Essayer avec Selenium si nécessaire
            if not all_schedules:
                logger.info("\n=== Méthode 3: Selenium (dernier recours) ===")
                selenium_schedules = self.scrape_with_selenium()
                if selenium_schedules:
                    all_schedules.extend(selenium_schedules)
                    logger.info(f"✓ {len(selenium_schedules)} schedule(s) via Selenium")

        elif method == 'selenium':
            all_schedules = self.scrape_with_selenium()
        elif method == 'requests':
            all_schedules = self.scrape_with_requests()
        elif method == 'api':
            all_schedules = self.scrape_api_directly()

        # Dédupliquer
        unique_schedules = self._deduplicate_schedules(all_schedules)

        logger.info(f"\n✓ Total: {len(unique_schedules)} schedule(s) unique(s) trouvé(s)")

        return unique_schedules

    def _deduplicate_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """
        Supprime les doublons de la liste de schedules

        Args:
            schedules: Liste des schedules

        Returns:
            Liste sans doublons
        """
        seen = set()
        unique = []

        for schedule in schedules:
            # Créer une clé unique
            key = json.dumps(schedule, sort_keys=True)

            if key not in seen:
                seen.add(key)
                unique.append(schedule)

        return unique

    def export_to_json(self, schedules: List[Dict], filename: str):
        """
        Exporte les schedules en JSON

        Args:
            schedules: Liste des schedules
            filename: Nom du fichier
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'scraped_at': datetime.now().isoformat(),
                        'source': self.BASE_URL,
                        'total_schedules': len(schedules)
                    },
                    'schedules': schedules
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Données exportées vers {filename}")

        except Exception as e:
            logger.error(f"Erreur export JSON: {e}")

    def export_to_csv(self, schedules: List[Dict], filename: str):
        """
        Exporte les schedules en CSV

        Args:
            schedules: Liste des schedules
            filename: Nom du fichier
        """
        if not schedules:
            logger.warning("Aucun schedule à exporter")
            return

        try:
            # Déterminer toutes les colonnes
            fieldnames = set()
            for schedule in schedules:
                fieldnames.update(schedule.keys())
            fieldnames = sorted(list(fieldnames))

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for schedule in schedules:
                    # Convertir les objets complexes en strings
                    row = {}
                    for key, value in schedule.items():
                        if isinstance(value, (dict, list)):
                            row[key] = json.dumps(value)
                        else:
                            row[key] = value
                    writer.writerow(row)

            logger.info(f"✓ Données exportées vers {filename}")

        except Exception as e:
            logger.error(f"Erreur export CSV: {e}")


def main():
    """Fonction principale"""
    print("=" * 80)
    print("SQUADI SCHEDULES SCRAPER")
    print("=" * 80)
    print()
    print("Ce scraper récupère tous les schedules à venir depuis:")
    print("  → https://registration.us.squadi.com/")
    print()
    print("Méthodes disponibles:")
    print("  1. Auto (toutes les méthodes)")
    print("  2. API directe uniquement")
    print("  3. Requests/Cloudscraper")
    print("  4. Selenium (navigateur headless)")
    print()

    choice = input("Choisissez une méthode (1-4) [défaut: 1]: ").strip() or "1"

    method_map = {
        "1": "auto",
        "2": "api",
        "3": "requests",
        "4": "selenium"
    }

    method = method_map.get(choice, "auto")

    print(f"\nDémarrage du scraping (méthode: {method})...\n")

    scraper = SquadiSchedulesScraper()
    schedules = scraper.run(method=method)

    if schedules:
        print(f"\n✓ {len(schedules)} schedule(s) trouvé(s)\n")

        # Afficher un aperçu
        print("Aperçu des premiers schedules:")
        print("-" * 80)
        for i, schedule in enumerate(schedules[:5], 1):
            print(f"\n{i}. {schedule.get('title', schedule.get('name', 'N/A'))}")
            if 'date' in schedule:
                print(f"   Date: {schedule['date']}")
            if 'location' in schedule:
                print(f"   Lieu: {schedule['location']}")
            if 'url' in schedule:
                print(f"   URL: {schedule['url']}")

        if len(schedules) > 5:
            print(f"\n... et {len(schedules) - 5} autre(s)")

        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_file = f"squadi_schedules_{timestamp}.json"
        scraper.export_to_json(schedules, json_file)

        csv_file = f"squadi_schedules_{timestamp}.csv"
        scraper.export_to_csv(schedules, csv_file)

        print(f"\n✓ Fichiers générés:")
        print(f"  - {json_file}")
        print(f"  - {csv_file}")

    else:
        print("\n✗ Aucun schedule trouvé")
        print("\nSuggestions:")
        print("  1. Vérifiez que le site est accessible")
        print("  2. Installez les dépendances manquantes:")
        print("     pip install beautifulsoup4 cloudscraper selenium webdriver-manager")
        print("  3. Essayez avec la méthode Selenium (option 4)")

    print("\n" + "=" * 80)
    print("Scraping terminé!")
    print("=" * 80)


if __name__ == "__main__":
    main()
