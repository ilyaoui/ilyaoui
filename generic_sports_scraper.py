#!/usr/bin/env python3
"""
Generic Sports Match Scraper
=============================
Scrape les matchs sportifs depuis n'importe quel site web et les enregistre
dans des fichiers CSV bien organisés et structurés.

Fonctionnalités:
- Scraping générique adaptatif à différents sites web
- Détection automatique de la structure des pages
- Découverte et parcours de tous les calendriers
- Export CSV enrichi avec métadonnées complètes
- Support multi-sports
- Gestion intelligente des erreurs et retry
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set, Any
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict, field
import os


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Match:
    """Modèle de données pour un match sportif"""
    match_id: Optional[str] = None
    sport: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    datetime_iso: Optional[str] = None

    # Équipes
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    home_team_id: Optional[str] = None
    away_team_id: Optional[str] = None

    # Scores
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None  # scheduled, live, finished, cancelled

    # Lieu
    venue: Optional[str] = None
    venue_id: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None

    # Compétition
    competition: Optional[str] = None
    competition_id: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[str] = None
    round: Optional[str] = None
    week: Optional[str] = None
    season: Optional[str] = None

    # Métadonnées
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertit le match en dictionnaire pour export CSV"""
        data = asdict(self)
        # Convertir additional_info en JSON string pour CSV
        if data['additional_info']:
            data['additional_info'] = json.dumps(data['additional_info'])
        return data


@dataclass
class Calendar:
    """Modèle de données pour un calendrier/schedule"""
    calendar_id: Optional[str] = None
    name: Optional[str] = None
    url: str = ""
    sport: Optional[str] = None
    season: Optional[str] = None
    division: Optional[str] = None
    matches: List[Match] = field(default_factory=list)
    discovered_at: Optional[str] = None


class GenericSportsMatchScraper:
    """
    Scraper générique pour matchs sportifs avec détection automatique
    de structure et découverte de calendriers
    """

    def __init__(self, rate_limit: float = 1.5, max_retries: int = 3):
        """
        Args:
            rate_limit: Délai minimum entre requêtes (secondes)
            max_retries: Nombre maximum de tentatives en cas d'échec
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.last_request_time = 0
        self.visited_urls: Set[str] = set()
        self.discovered_calendars: List[Calendar] = []

        # Headers réalistes pour éviter les blocages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

        # Patterns communs pour identifier les matchs dans HTML
        self.match_patterns = {
            'date': [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
            ],
            'time': [
                r'\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm))?',
                r'\d{1,2}h\d{2}',
            ],
            'score': [
                r'\d{1,3}\s*[-:]\s*\d{1,3}',
                r'\d{1,3}\s*vs?\s*\d{1,3}',
            ]
        }

        # Mots-clés pour identifier les liens de calendrier/schedule
        self.calendar_keywords = [
            'schedule', 'calendar', 'calendrier', 'matchs', 'matches',
            'games', 'fixtures', 'resultats', 'results', 'standings',
            'division', 'league', 'tournament', 'tournoi', 'championship'
        ]

    def _rate_limit_request(self):
        """Applique le rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Effectue une requête HTTP avec retry et rate limiting

        Args:
            url: URL cible
            method: Méthode HTTP (GET, POST, etc.)
            **kwargs: Arguments additionnels pour requests

        Returns:
            Response object ou None en cas d'échec
        """
        self._rate_limit_request()

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Requête {method} vers {url} (tentative {attempt + 1}/{self.max_retries})")

                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Échec de la requête (tentative {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Attente de {wait_time}s avant retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Échec définitif après {self.max_retries} tentatives")
                    return None

    def discover_calendars(self, base_url: str, max_depth: int = 3) -> List[Calendar]:
        """
        Découvre tous les calendriers/schedules disponibles sur un site

        Args:
            base_url: URL de départ
            max_depth: Profondeur maximale de crawling

        Returns:
            Liste des calendriers découverts
        """
        logger.info(f"Début de la découverte de calendriers depuis {base_url}")

        self.discovered_calendars = []
        self.visited_urls = set()

        self._crawl_for_calendars(base_url, depth=0, max_depth=max_depth)

        logger.info(f"Découverte terminée: {len(self.discovered_calendars)} calendriers trouvés")
        return self.discovered_calendars

    def _crawl_for_calendars(self, url: str, depth: int, max_depth: int):
        """Crawl récursif pour découvrir les calendriers"""
        if depth > max_depth or url in self.visited_urls:
            return

        self.visited_urls.add(url)
        logger.debug(f"Crawling {url} (profondeur {depth})")

        response = self._make_request(url)
        if not response:
            return

        soup = BeautifulSoup(response.content, 'lxml')

        # Vérifier si cette page contient un calendrier
        if self._is_calendar_page(soup, url):
            calendar = Calendar(
                url=url,
                name=self._extract_calendar_name(soup),
                discovered_at=datetime.now().isoformat()
            )
            self.discovered_calendars.append(calendar)
            logger.info(f"✓ Calendrier trouvé: {calendar.name} ({url})")

        # Chercher des liens vers d'autres calendriers
        if depth < max_depth:
            links = self._find_calendar_links(soup, url)
            for link in links:
                self._crawl_for_calendars(link, depth + 1, max_depth)

    def _is_calendar_page(self, soup: BeautifulSoup, url: str) -> bool:
        """Détermine si une page contient un calendrier de matchs"""
        # Vérifier l'URL
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in self.calendar_keywords):
            return True

        # Vérifier le contenu de la page
        text_content = soup.get_text().lower()

        # Chercher des patterns de matchs (équipes, dates, scores)
        match_indicators = 0

        # Présence de dates
        if any(re.search(pattern, text_content) for pattern in self.match_patterns['date']):
            match_indicators += 1

        # Présence d'heures
        if any(re.search(pattern, text_content) for pattern in self.match_patterns['time']):
            match_indicators += 1

        # Présence de tables (souvent utilisées pour les calendriers)
        tables = soup.find_all('table')
        if tables:
            match_indicators += 1

        # Présence de termes sportifs communs
        sports_terms = ['vs', 'versus', 'match', 'game', 'team', 'équipe', 'score']
        if any(term in text_content for term in sports_terms):
            match_indicators += 1

        return match_indicators >= 2

    def _extract_calendar_name(self, soup: BeautifulSoup) -> str:
        """Extrait le nom du calendrier depuis la page"""
        # Essayer le titre de la page
        if soup.title:
            return soup.title.string.strip()

        # Essayer les headers principaux
        for tag in ['h1', 'h2', 'h3']:
            header = soup.find(tag)
            if header:
                return header.get_text().strip()

        return "Calendrier sans nom"

    def _find_calendar_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Trouve tous les liens potentiels vers des calendriers"""
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)

            # Vérifier si le lien ou son texte contient des mots-clés
            link_text = a_tag.get_text().lower()
            href_lower = href.lower()

            if any(keyword in link_text or keyword in href_lower
                   for keyword in self.calendar_keywords):

                # Éviter les doublons et rester sur le même domaine
                if full_url not in self.visited_urls:
                    base_domain = urlparse(base_url).netloc
                    link_domain = urlparse(full_url).netloc

                    if base_domain == link_domain:
                        links.append(full_url)

        return links

    def scrape_matches_from_url(self, url: str) -> List[Match]:
        """
        Scrape tous les matchs depuis une URL donnée

        Args:
            url: URL de la page contenant des matchs

        Returns:
            Liste des matchs extraits
        """
        logger.info(f"Scraping des matchs depuis {url}")

        response = self._make_request(url)
        if not response:
            logger.error(f"Impossible de récupérer {url}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        matches = []

        # Essayer différentes stratégies d'extraction
        strategies = [
            self._extract_from_tables,
            self._extract_from_lists,
            self._extract_from_divs,
            self._extract_from_json_ld,
            self._extract_from_embedded_json,
        ]

        for strategy in strategies:
            try:
                extracted = strategy(soup, url)
                if extracted:
                    matches.extend(extracted)
                    logger.info(f"✓ Stratégie {strategy.__name__} a trouvé {len(extracted)} matchs")
            except Exception as e:
                logger.debug(f"Stratégie {strategy.__name__} a échoué: {e}")

        # Dédupliquer les matchs
        matches = self._deduplicate_matches(matches)

        logger.info(f"Total: {len(matches)} matchs uniques extraits depuis {url}")
        return matches

    def _extract_from_tables(self, soup: BeautifulSoup, url: str) -> List[Match]:
        """Extrait les matchs depuis des tables HTML"""
        matches = []
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')

            # Identifier les colonnes (header row)
            headers = []
            if rows:
                header_row = rows[0]
                headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]

            # Extraire les données
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                match = Match(
                    source_url=url,
                    scraped_at=datetime.now().isoformat()
                )

                # Parser les cellules selon les headers ou position
                for i, cell in enumerate(cells):
                    text = cell.get_text().strip()

                    if i < len(headers):
                        header = headers[i]
                        self._assign_field_by_header(match, header, text)
                    else:
                        # Essayer de deviner le type de donnée
                        self._guess_and_assign_field(match, text)

                if match.home_team or match.away_team:
                    matches.append(match)

        return matches

    def _extract_from_lists(self, soup: BeautifulSoup, url: str) -> List[Match]:
        """Extrait les matchs depuis des listes (ul, ol)"""
        matches = []
        lists = soup.find_all(['ul', 'ol'])

        for list_elem in lists:
            items = list_elem.find_all('li')

            for item in items:
                text = item.get_text()

                # Chercher des patterns "Team A vs Team B"
                vs_pattern = r'(.+?)\s+(?:vs\.?|versus|v\.?|-)\s+(.+?)(?:\s+\d|$)'
                vs_match = re.search(vs_pattern, text, re.IGNORECASE)

                if vs_match:
                    match = Match(
                        home_team=vs_match.group(1).strip(),
                        away_team=vs_match.group(2).strip(),
                        source_url=url,
                        scraped_at=datetime.now().isoformat()
                    )

                    # Extraire date/heure/score du reste du texte
                    self._extract_metadata_from_text(match, text)
                    matches.append(match)

        return matches

    def _extract_from_divs(self, soup: BeautifulSoup, url: str) -> List[Match]:
        """Extrait les matchs depuis des divs structurées"""
        matches = []

        # Chercher des divs avec classes communes pour les matchs
        match_keywords = ['match', 'game', 'fixture', 'event', 'contest']

        for keyword in match_keywords:
            divs = soup.find_all('div', class_=re.compile(keyword, re.I))

            for div in divs:
                match = Match(
                    source_url=url,
                    scraped_at=datetime.now().isoformat()
                )

                # Extraire toutes les infos du div
                text = div.get_text()
                self._extract_metadata_from_text(match, text)

                # Chercher des sous-éléments spécifiques
                team_elements = div.find_all(class_=re.compile('team', re.I))
                if len(team_elements) >= 2:
                    match.home_team = team_elements[0].get_text().strip()
                    match.away_team = team_elements[1].get_text().strip()

                score_elements = div.find_all(class_=re.compile('score', re.I))
                if len(score_elements) >= 2:
                    try:
                        match.home_score = int(re.search(r'\d+', score_elements[0].get_text()).group())
                        match.away_score = int(re.search(r'\d+', score_elements[1].get_text()).group())
                    except:
                        pass

                if match.home_team or match.away_team:
                    matches.append(match)

        return matches

    def _extract_from_json_ld(self, soup: BeautifulSoup, url: str) -> List[Match]:
        """Extrait les matchs depuis JSON-LD (structured data)"""
        matches = []

        json_ld_scripts = soup.find_all('script', type='application/ld+json')

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)

                # Gérer les cas où data est un dict ou une liste
                items = data if isinstance(data, list) else [data]

                for item in items:
                    if item.get('@type') in ['SportsEvent', 'Event']:
                        match = self._parse_sports_event_json(item, url)
                        if match:
                            matches.append(match)

            except Exception as e:
                logger.debug(f"Erreur lors du parsing JSON-LD: {e}")

        return matches

    def _extract_from_embedded_json(self, soup: BeautifulSoup, url: str) -> List[Match]:
        """Extrait les matchs depuis du JSON embedded dans des scripts"""
        matches = []

        scripts = soup.find_all('script')

        for script in scripts:
            if not script.string:
                continue

            # Chercher des patterns JSON dans le script
            json_patterns = [
                r'var\s+\w+\s*=\s*(\{.+?\});',
                r'const\s+\w+\s*=\s*(\{.+?\});',
                r'let\s+\w+\s*=\s*(\{.+?\});',
                r'window\.\w+\s*=\s*(\{.+?\});',
                r'(\{["\']matches["\']\s*:\s*\[.+?\]\})',
                r'(\{["\']games["\']\s*:\s*\[.+?\]\})',
            ]

            for pattern in json_patterns:
                try:
                    json_matches = re.findall(pattern, script.string, re.DOTALL)

                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            extracted = self._parse_json_data_for_matches(data, url)
                            matches.extend(extracted)
                        except:
                            continue
                except:
                    continue

        return matches

    def _parse_sports_event_json(self, event_data: Dict, url: str) -> Optional[Match]:
        """Parse un événement sportif au format JSON-LD"""
        try:
            match = Match(
                source_url=url,
                scraped_at=datetime.now().isoformat()
            )

            # Nom de l'événement
            if 'name' in event_data:
                match.additional_info['event_name'] = event_data['name']

            # Date
            if 'startDate' in event_data:
                match.datetime_iso = event_data['startDate']
                try:
                    dt = datetime.fromisoformat(event_data['startDate'].replace('Z', '+00:00'))
                    match.date = dt.strftime('%Y-%m-%d')
                    match.time = dt.strftime('%H:%M')
                except:
                    pass

            # Lieu
            if 'location' in event_data:
                location = event_data['location']
                if isinstance(location, dict):
                    match.venue = location.get('name')
                    if 'address' in location:
                        addr = location['address']
                        if isinstance(addr, dict):
                            match.city = addr.get('addressLocality')
                            match.state = addr.get('addressRegion')

            # Équipes (peut varier selon la structure)
            if 'competitor' in event_data:
                competitors = event_data['competitor']
                if isinstance(competitors, list) and len(competitors) >= 2:
                    match.home_team = competitors[0].get('name')
                    match.away_team = competitors[1].get('name')

            return match if match.home_team or match.away_team else None

        except Exception as e:
            logger.debug(f"Erreur parsing JSON-LD event: {e}")
            return None

    def _parse_json_data_for_matches(self, data: Any, url: str) -> List[Match]:
        """Parse récursivement des données JSON pour trouver des matchs"""
        matches = []

        if isinstance(data, dict):
            # Chercher des clés communes pour les matchs
            match_keys = ['matches', 'games', 'fixtures', 'events', 'schedule']

            for key in match_keys:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        match = self._parse_match_dict(item, url)
                        if match:
                            matches.append(match)

            # Recherche récursive dans les sous-dictionnaires
            for value in data.values():
                if isinstance(value, (dict, list)):
                    matches.extend(self._parse_json_data_for_matches(value, url))

        elif isinstance(data, list):
            for item in data:
                matches.extend(self._parse_json_data_for_matches(item, url))

        return matches

    def _parse_match_dict(self, data: Dict, url: str) -> Optional[Match]:
        """Parse un dictionnaire représentant un match"""
        try:
            match = Match(
                source_url=url,
                scraped_at=datetime.now().isoformat()
            )

            # Mapping de clés communes
            key_mappings = {
                'id': 'match_id',
                'match_id': 'match_id',
                'game_id': 'match_id',
                'home_team': 'home_team',
                'homeTeam': 'home_team',
                'home': 'home_team',
                'away_team': 'away_team',
                'awayTeam': 'away_team',
                'away': 'away_team',
                'home_score': 'home_score',
                'homeScore': 'home_score',
                'away_score': 'away_score',
                'awayScore': 'away_score',
                'date': 'date',
                'time': 'time',
                'datetime': 'datetime_iso',
                'venue': 'venue',
                'location': 'venue',
                'status': 'status',
                'division': 'division',
                'competition': 'competition',
            }

            for json_key, match_key in key_mappings.items():
                if json_key in data:
                    value = data[json_key]
                    # Extraire le nom si c'est un dict avec une clé 'name'
                    if isinstance(value, dict) and 'name' in value:
                        value = value['name']
                    setattr(match, match_key, value)

            return match if match.home_team or match.away_team else None

        except Exception as e:
            logger.debug(f"Erreur parsing match dict: {e}")
            return None

    def _assign_field_by_header(self, match: Match, header: str, value: str):
        """Assigne une valeur à un champ du match selon le header"""
        header = header.lower()

        if any(word in header for word in ['date', 'jour', 'day']):
            match.date = value
        elif any(word in header for word in ['time', 'heure', 'hour']):
            match.time = value
        elif any(word in header for word in ['home', 'domicile', 'local']):
            match.home_team = value
        elif any(word in header for word in ['away', 'visitor', 'exterieur', 'visiteur']):
            match.away_team = value
        elif 'score' in header:
            self._parse_score(match, value)
        elif any(word in header for word in ['venue', 'lieu', 'location', 'stadium']):
            match.venue = value
        elif any(word in header for word in ['division', 'league', 'ligue']):
            match.division = value
        elif any(word in header for word in ['status', 'statut', 'state']):
            match.status = value

    def _guess_and_assign_field(self, match: Match, text: str):
        """Devine le type de champ et l'assigne"""
        # Essayer les patterns de date
        for pattern in self.match_patterns['date']:
            if re.search(pattern, text):
                match.date = text
                return

        # Essayer les patterns d'heure
        for pattern in self.match_patterns['time']:
            if re.search(pattern, text):
                match.time = text
                return

        # Essayer les patterns de score
        for pattern in self.match_patterns['score']:
            if re.search(pattern, text):
                self._parse_score(match, text)
                return

        # Si c'est un texte simple, l'ajouter en info additionnelle
        if text and not match.additional_info.get('extra_info'):
            match.additional_info['extra_info'] = text

    def _extract_metadata_from_text(self, match: Match, text: str):
        """Extrait date, heure, score d'un texte libre"""
        # Date
        for pattern in self.match_patterns['date']:
            date_match = re.search(pattern, text)
            if date_match:
                match.date = date_match.group()
                break

        # Heure
        for pattern in self.match_patterns['time']:
            time_match = re.search(pattern, text)
            if time_match:
                match.time = time_match.group()
                break

        # Score
        for pattern in self.match_patterns['score']:
            score_match = re.search(pattern, text)
            if score_match:
                self._parse_score(match, score_match.group())
                break

    def _parse_score(self, match: Match, score_text: str):
        """Parse un score au format "X-Y" ou "X:Y" """
        score_match = re.search(r'(\d+)\s*[-:vs]\s*(\d+)', score_text)
        if score_match:
            try:
                match.home_score = int(score_match.group(1))
                match.away_score = int(score_match.group(2))
            except ValueError:
                pass

    def _deduplicate_matches(self, matches: List[Match]) -> List[Match]:
        """Élimine les doublons de matchs"""
        unique_matches = []
        seen = set()

        for match in matches:
            # Créer une clé unique basée sur les infos principales
            key = (
                match.date,
                match.time,
                match.home_team,
                match.away_team,
                match.venue
            )

            if key not in seen:
                seen.add(key)
                unique_matches.append(match)

        return unique_matches

    def scrape_all_calendars(self, base_url: str, max_depth: int = 3) -> Dict[str, List[Match]]:
        """
        Découvre et scrape tous les calendriers depuis une URL

        Args:
            base_url: URL de départ
            max_depth: Profondeur maximale de crawling

        Returns:
            Dictionnaire {calendar_url: [matches]}
        """
        logger.info(f"Scraping complet depuis {base_url}")

        # Découvrir tous les calendriers
        calendars = self.discover_calendars(base_url, max_depth)

        # Scraper chaque calendrier
        results = {}
        for calendar in calendars:
            logger.info(f"Scraping du calendrier: {calendar.name}")
            matches = self.scrape_matches_from_url(calendar.url)
            calendar.matches = matches
            results[calendar.url] = matches

        return results

    def export_to_csv(self, matches: List[Match], filename: str,
                      include_metadata: bool = True):
        """
        Export les matchs vers un fichier CSV

        Args:
            matches: Liste des matchs à exporter
            filename: Nom du fichier de sortie
            include_metadata: Inclure les métadonnées (source_url, scraped_at)
        """
        if not matches:
            logger.warning("Aucun match à exporter")
            return

        # Créer le répertoire de sortie si nécessaire
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Convertir les matchs en dictionnaires
        data = [match.to_dict() for match in matches]

        # Déterminer les champs à inclure
        fieldnames = [
            'match_id', 'sport', 'date', 'time', 'datetime_iso',
            'home_team', 'away_team', 'home_team_id', 'away_team_id',
            'home_score', 'away_score', 'status',
            'venue', 'venue_id', 'city', 'state', 'address',
            'competition', 'competition_id', 'division', 'division_id',
            'round', 'week', 'season', 'additional_info'
        ]

        if include_metadata:
            fieldnames.extend(['source_url', 'scraped_at'])

        # Écrire le CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"✓ {len(matches)} matchs exportés vers {filename}")

        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")

    def export_calendars_to_csv(self, calendars: List[Calendar], output_dir: str = 'output'):
        """
        Export chaque calendrier dans un fichier CSV séparé

        Args:
            calendars: Liste des calendriers à exporter
            output_dir: Répertoire de sortie
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, calendar in enumerate(calendars):
            if not calendar.matches:
                continue

            # Créer un nom de fichier basé sur le nom du calendrier
            safe_name = re.sub(r'[^\w\s-]', '', calendar.name)
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            filename = os.path.join(output_dir, f"{safe_name}_{i+1}.csv")

            self.export_to_csv(calendar.matches, filename)

        logger.info(f"✓ Tous les calendriers exportés dans {output_dir}/")


def main():
    """Fonction principale pour utilisation en CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generic Sports Match Scraper - Scrape les matchs depuis n\'importe quel site'
    )
    parser.add_argument('url', help='URL du site à scraper')
    parser.add_argument('-o', '--output', default='output',
                        help='Répertoire de sortie (défaut: output)')
    parser.add_argument('-d', '--depth', type=int, default=3,
                        help='Profondeur maximale de crawling (défaut: 3)')
    parser.add_argument('-r', '--rate-limit', type=float, default=1.5,
                        help='Délai entre requêtes en secondes (défaut: 1.5)')
    parser.add_argument('--single-page', action='store_true',
                        help='Scraper uniquement la page donnée (pas de découverte)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Mode verbose (debug)')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = GenericSportsMatchScraper(rate_limit=args.rate_limit)

    if args.single_page:
        # Mode simple: scraper uniquement l'URL donnée
        matches = scraper.scrape_matches_from_url(args.url)

        if matches:
            filename = os.path.join(args.output, 'matches.csv')
            scraper.export_to_csv(matches, filename)
        else:
            logger.warning("Aucun match trouvé")
    else:
        # Mode complet: découvrir et scraper tous les calendriers
        calendars = scraper.discover_calendars(args.url, max_depth=args.depth)

        # Scraper chaque calendrier
        for calendar in calendars:
            matches = scraper.scrape_matches_from_url(calendar.url)
            calendar.matches = matches

        # Exporter
        scraper.export_calendars_to_csv(calendars, args.output)

        # Export récapitulatif
        all_matches = []
        for calendar in calendars:
            all_matches.extend(calendar.matches)

        if all_matches:
            summary_file = os.path.join(args.output, 'all_matches.csv')
            scraper.export_to_csv(all_matches, summary_file)
            logger.info(f"✓ Récapitulatif: {len(all_matches)} matchs au total")


if __name__ == '__main__':
    main()
