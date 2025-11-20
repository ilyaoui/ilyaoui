#!/usr/bin/env python3
"""
Advanced NFL Flag Scraper
-------------------------
Version avancée avec support pour BeautifulSoup et scraping HTML complet
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re
from urllib.parse import urljoin, urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedNFLFlagScraper:
    """
    Scraper avancé pour les données NFL Flag avec parsing HTML complet
    """

    def __init__(self, rate_limit: float = 1.0):
        """
        Initialise le scraper

        Args:
            rate_limit: Délai en secondes entre les requêtes (rate limiting)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def _rate_limit_request(self):
        """Applique le rate limiting entre les requêtes"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def discover_nfl_flag_events(self) -> List[Dict]:
        """
        Découvre les événements NFL Flag depuis la page principale

        Returns:
            Liste des événements découverts
        """
        events = []

        try:
            self._rate_limit_request()
            logger.info("Récupération de la page des événements NFL Flag...")

            response = self.session.get("https://nflflag.com/events")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Chercher les liens d'événements
            event_links = soup.find_all('a', href=re.compile(r'/events/'))

            for link in event_links:
                href = link.get('href')
                if href and href not in [e['url'] for e in events]:
                    event_data = {
                        'url': urljoin("https://nflflag.com", href),
                        'title': link.get_text(strip=True),
                        'type': 'event'
                    }
                    events.append(event_data)
                    logger.info(f"Événement trouvé: {event_data['title']}")

            # Chercher des données JSON embarquées
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'events' in data or 'tournaments' in data:
                        events.append({
                            'type': 'embedded_json',
                            'data': data
                        })
                except json.JSONDecodeError:
                    continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des événements: {e}")

        return events

    def scrape_tournament_page(self, url: str) -> Dict:
        """
        Scrape une page de tournoi spécifique

        Args:
            url: URL de la page du tournoi

        Returns:
            Dictionnaire contenant les données du tournoi
        """
        tournament_data = {
            'url': url,
            'title': '',
            'divisions': [],
            'teams': [],
            'schedule': [],
            'locations': [],
            'metadata': {}
        }

        try:
            self._rate_limit_request()
            logger.info(f"Scraping de: {url}")

            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraire le titre
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                tournament_data['title'] = title_tag.get_text(strip=True)

            # Chercher les divisions
            division_elements = soup.find_all(['div', 'section'], class_=re.compile(r'division', re.I))
            for div_elem in division_elements:
                division = self._extract_division_data(div_elem)
                if division:
                    tournament_data['divisions'].append(division)

            # Chercher les équipes
            team_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'team', re.I))
            for team_elem in team_elements:
                team = self._extract_team_data(team_elem)
                if team:
                    tournament_data['teams'].append(team)

            # Chercher des tables de données
            tables = soup.find_all('table')
            for table in tables:
                table_data = self._extract_table_data(table)
                if table_data:
                    # Déterminer le type de table
                    if 'team' in str(table).lower():
                        tournament_data['teams'].extend(table_data)
                    elif 'schedule' in str(table).lower():
                        tournament_data['schedule'].extend(table_data)

            # Chercher des API calls dans le JavaScript
            api_calls = self._extract_api_calls_from_scripts(soup)
            if api_calls:
                tournament_data['discovered_apis'] = api_calls

            logger.info(f"✓ Tournoi scrapé: {len(tournament_data['teams'])} équipes, "
                       f"{len(tournament_data['divisions'])} divisions")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors du scraping: {e}")

        return tournament_data

    def _extract_division_data(self, element) -> Optional[Dict]:
        """Extrait les données d'une division depuis un élément HTML"""
        try:
            division = {}

            # Chercher le nom
            name_elem = element.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'name|title', re.I))
            if name_elem:
                division['name'] = name_elem.get_text(strip=True)

            # Chercher l'ID
            if element.get('data-division-id'):
                division['id'] = element['data-division-id']

            return division if division else None
        except Exception:
            return None

    def _extract_team_data(self, element) -> Optional[Dict]:
        """Extrait les données d'une équipe depuis un élément HTML"""
        try:
            team = {}

            # Chercher le nom de l'équipe
            name_elem = element.find(['span', 'td', 'div'], class_=re.compile(r'team-?name', re.I))
            if not name_elem:
                name_elem = element.find(['strong', 'b'])

            if name_elem:
                team['name'] = name_elem.get_text(strip=True)

            # Chercher d'autres attributs
            if element.get('data-team-id'):
                team['id'] = element['data-team-id']

            # Organisation
            org_elem = element.find(['span', 'div'], class_=re.compile(r'org|organization', re.I))
            if org_elem:
                team['organization'] = org_elem.get_text(strip=True)

            # Coach
            coach_elem = element.find(['span', 'div'], class_=re.compile(r'coach', re.I))
            if coach_elem:
                team['coach'] = coach_elem.get_text(strip=True)

            return team if team else None
        except Exception:
            return None

    def _extract_table_data(self, table) -> List[Dict]:
        """Extrait les données d'une table HTML"""
        data = []

        try:
            headers = []
            header_row = table.find('thead') or table.find('tr')

            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

            # Extraire les lignes
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if cells and headers:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell.get_text(strip=True)
                    if row_data:
                        data.append(row_data)

        except Exception as e:
            logger.debug(f"Erreur lors de l'extraction de table: {e}")

        return data

    def _extract_api_calls_from_scripts(self, soup) -> List[str]:
        """Extrait les URLs d'API depuis les scripts JavaScript"""
        api_calls = []

        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Chercher des patterns d'URLs d'API
                api_patterns = [
                    r'https?://[^\s"\']+/api/[^\s"\']+',
                    r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                ]

                for pattern in api_patterns:
                    matches = re.findall(pattern, script.string)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0]
                        if url not in api_calls:
                            api_calls.append(url)
                            logger.info(f"API découverte: {url}")

        return api_calls

    def try_api_endpoint(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Essaye d'accéder à un endpoint API découvert

        Args:
            endpoint: URL de l'endpoint
            params: Paramètres optionnels

        Returns:
            Données JSON si succès, None sinon
        """
        try:
            self._rate_limit_request()
            logger.info(f"Test de l'endpoint: {endpoint}")

            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            # Vérifier si c'est du JSON
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                logger.debug(f"Endpoint ne retourne pas du JSON: {content_type}")
                return None

        except requests.exceptions.RequestException as e:
            logger.debug(f"Endpoint inaccessible: {endpoint} - {e}")
            return None

    def scrape_bluesombrero_tournament(self, tournament_id: str) -> Dict:
        """
        Scrape un tournoi spécifique sur BlueSombrero

        Args:
            tournament_id: ID du tournoi (tabid)

        Returns:
            Données du tournoi
        """
        url = f"https://leagues.bluesombrero.com/Default.aspx?tabid={tournament_id}"
        return self.scrape_tournament_page(url)

    def export_enriched_csv(self, teams: List[Dict], filename: str):
        """
        Exporte les équipes dans un CSV riche en informations

        Args:
            teams: Liste des équipes
            filename: Nom du fichier de sortie
        """
        if not teams:
            logger.warning("Aucune équipe à exporter")
            return

        # Enrichir les données
        enriched_teams = []
        for team in teams:
            enriched = {
                'team_name': team.get('name', 'N/A'),
                'team_id': team.get('id', 'N/A'),
                'organization': team.get('organization', 'N/A'),
                'coach': team.get('coach', 'N/A'),
                'division': team.get('division', 'N/A'),
                'division_id': team.get('division_id', 'N/A'),
                'location': team.get('location', 'N/A'),
                'city': team.get('city', 'N/A'),
                'state': team.get('state', 'N/A'),
                'roster_size': team.get('roster_size', 'N/A'),
                'wins': team.get('wins', 0),
                'losses': team.get('losses', 0),
                'url': team.get('url', 'N/A'),
                'scraped_at': datetime.now().isoformat(),
            }
            enriched_teams.append(enriched)

        # Écrire le CSV
        try:
            fieldnames = list(enriched_teams[0].keys())
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enriched_teams)

            logger.info(f"✓ {len(enriched_teams)} équipes exportées vers {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")


def main():
    """Fonction principale de démonstration"""
    print("=" * 80)
    print("ADVANCED NFL FLAG SCRAPER")
    print("=" * 80)
    print()

    scraper = AdvancedNFLFlagScraper(rate_limit=1.5)

    print("Options disponibles:")
    print("  1. Découvrir les événements NFL Flag")
    print("  2. Scraper un tournoi spécifique (URL)")
    print("  3. Scraper un tournoi BlueSombrero (ID)")
    print()

    choice = input("Choisissez une option (1-3): ").strip()

    if choice == "1":
        print("\n--- DÉCOUVERTE D'ÉVÉNEMENTS ---")
        events = scraper.discover_nfl_flag_events()

        if events:
            print(f"\n✓ {len(events)} événement(s) trouvé(s)")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nfl_flag_events_{timestamp}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)

            print(f"✓ Événements sauvegardés dans {filename}")

            # Afficher les premiers événements
            for i, event in enumerate(events[:5], 1):
                print(f"  {i}. {event.get('title', 'N/A')}")

    elif choice == "2":
        print("\n--- SCRAPING D'UN TOURNOI ---")
        url = input("Entrez l'URL du tournoi: ").strip()

        if url:
            tournament_data = scraper.scrape_tournament_page(url)

            if tournament_data['teams'] or tournament_data['divisions']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Export JSON
                json_file = f"tournament_data_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(tournament_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Données JSON sauvegardées: {json_file}")

                # Export CSV
                if tournament_data['teams']:
                    csv_file = f"tournament_teams_{timestamp}.csv"
                    scraper.export_enriched_csv(tournament_data['teams'], csv_file)
                    print(f"✓ Équipes CSV sauvegardées: {csv_file}")

    elif choice == "3":
        print("\n--- SCRAPING BLUESOMBRERO ---")
        tournament_id = input("Entrez l'ID du tournoi (tabid): ").strip()

        if tournament_id:
            tournament_data = scraper.scrape_bluesombrero_tournament(tournament_id)

            if tournament_data['teams'] or tournament_data['divisions']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                json_file = f"bluesombrero_{tournament_id}_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(tournament_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Données sauvegardées: {json_file}")

                if tournament_data['teams']:
                    csv_file = f"bluesombrero_teams_{tournament_id}_{timestamp}.csv"
                    scraper.export_enriched_csv(tournament_data['teams'], csv_file)

    print("\n" + "=" * 80)
    print("Scraping terminé!")
    print("=" * 80)


if __name__ == "__main__":
    main()
