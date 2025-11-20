#!/usr/bin/env python3
"""
NFL Flag Tournaments Scraper
-----------------------------
Ce scraper permet d'extraire les données des équipes et organisations
de l'application NFL Flag Tournaments (powered by TeamSnap).

Deux modes disponibles:
1. API TeamSnap (nécessite OAuth2)
2. Web Scraping des pages publiques

Author: Generated for NFL Flag Data Collection
"""

import requests
import csv
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import re

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TeamSnapAPIClient:
    """
    Client pour l'API TeamSnap v3
    Requiert une authentification OAuth2
    """

    BASE_URL = "https://api.teamsnap.com/v3"

    def __init__(self, access_token: str):
        """
        Initialise le client API avec un token d'accès

        Args:
            access_token: Token OAuth2 obtenu via le processus d'authentification
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def get_current_user(self) -> Dict:
        """Récupère les informations de l'utilisateur actuel"""
        try:
            response = self.session.get(f"{self.BASE_URL}/me")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return {}

    def get_teams(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Récupère la liste des équipes

        Args:
            user_id: ID de l'utilisateur (optionnel)

        Returns:
            Liste des équipes
        """
        try:
            url = f"{self.BASE_URL}/teams"
            params = {}
            if user_id:
                params['user_id'] = user_id

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # TeamSnap utilise Collection+JSON format
            if 'collection' in data and 'items' in data['collection']:
                return data['collection']['items']
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des équipes: {e}")
            return []

    def get_divisions(self, division_id: Optional[int] = None) -> List[Dict]:
        """
        Récupère les informations des divisions

        Args:
            division_id: ID de la division (optionnel)

        Returns:
            Liste des divisions
        """
        try:
            url = f"{self.BASE_URL}/divisions"
            if division_id:
                url = f"{url}/{division_id}"

            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if 'collection' in data and 'items' in data['collection']:
                return data['collection']['items']
            elif 'data' in data:
                return [data['data']]
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des divisions: {e}")
            return []

    def get_team_members(self, team_id: int) -> List[Dict]:
        """
        Récupère les membres d'une équipe

        Args:
            team_id: ID de l'équipe

        Returns:
            Liste des membres
        """
        try:
            url = f"{self.BASE_URL}/teams/{team_id}/members"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if 'collection' in data and 'items' in data['collection']:
                return data['collection']['items']
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des membres: {e}")
            return []

    def get_division_locations(self, division_id: int) -> List[Dict]:
        """
        Récupère les emplacements d'une division

        Args:
            division_id: ID de la division

        Returns:
            Liste des emplacements
        """
        try:
            url = f"{self.BASE_URL}/divisions/{division_id}/locations"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            if 'collection' in data and 'items' in data['collection']:
                return data['collection']['items']
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des emplacements: {e}")
            return []


class NFLFlagWebScraper:
    """
    Scraper web pour les pages publiques des tournois NFL Flag
    Ne nécessite pas d'authentification
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_tournament_data(self, tournament_url: str) -> Dict:
        """
        Récupère les données d'un tournoi depuis son URL publique

        Args:
            tournament_url: URL du tournoi

        Returns:
            Dictionnaire contenant les données du tournoi
        """
        try:
            response = self.session.get(tournament_url)
            response.raise_for_status()

            # Chercher des données JSON embarquées dans la page
            json_data = self._extract_json_data(response.text)

            if json_data:
                return json_data

            # Si pas de JSON, parser le HTML
            return self._parse_html(response.text)

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération du tournoi: {e}")
            return {}

    def _extract_json_data(self, html: str) -> Optional[Dict]:
        """
        Extrait les données JSON embarquées dans le HTML

        Args:
            html: Contenu HTML de la page

        Returns:
            Dictionnaire des données JSON ou None
        """
        # Chercher des patterns JSON courants dans le HTML
        patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'window\.__PRELOADED_STATE__\s*=\s*({.+?});',
            r'var\s+tournamentData\s*=\s*({.+?});',
            r'data-props="({.+?})"',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    # Décoder les entités HTML si nécessaire
                    json_str = json_str.replace('&quot;', '"')
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        return None

    def _parse_html(self, html: str) -> Dict:
        """
        Parse le HTML pour extraire les informations
        Note: Cette méthode nécessiterait BeautifulSoup pour un parsing complet

        Args:
            html: Contenu HTML

        Returns:
            Dictionnaire des données extraites
        """
        # Implémentation basique - à améliorer avec BeautifulSoup
        data = {
            'teams': [],
            'divisions': [],
            'tournament_info': {}
        }

        # Extraction basique avec regex
        team_pattern = r'<div[^>]*class="[^"]*team[^"]*"[^>]*>(.+?)</div>'
        teams = re.findall(team_pattern, html, re.DOTALL)

        logger.info(f"Trouvé {len(teams)} équipes potentielles dans le HTML")

        return data

    def search_tournaments_api(self) -> List[Dict]:
        """
        Tente de découvrir l'API des tournois en testant des endpoints communs

        Returns:
            Liste des tournois trouvés
        """
        potential_apis = [
            "https://api.teamsnap.com/v3/tournaments",
            "https://tournaments.teamsnap.com/api/tournaments",
            "https://api.nflflag.com/tournaments",
            "https://api.nflflag.com/v1/tournaments",
        ]

        tournaments = []
        for api_url in potential_apis:
            try:
                logger.info(f"Test de l'endpoint: {api_url}")
                response = self.session.get(api_url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✓ Endpoint actif: {api_url}")
                    tournaments.append({
                        'endpoint': api_url,
                        'data': data
                    })

            except Exception as e:
                logger.debug(f"✗ Endpoint non accessible: {api_url} - {e}")
                continue

        return tournaments


class NFLFlagDataExporter:
    """
    Exporte les données collectées vers différents formats
    """

    @staticmethod
    def flatten_team_data(team: Dict) -> Dict:
        """
        Aplatit les données d'une équipe pour l'export CSV

        Args:
            team: Dictionnaire des données de l'équipe

        Returns:
            Dictionnaire aplati
        """
        # Extraire les données selon le format Collection+JSON de TeamSnap
        flattened = {}

        if 'data' in team:
            for item in team['data']:
                if 'name' in item and 'value' in item:
                    flattened[item['name']] = item['value']
        else:
            # Format simple
            flattened = team.copy()

        return flattened

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str, fieldnames: Optional[List[str]] = None):
        """
        Exporte les données vers un fichier CSV

        Args:
            data: Liste des dictionnaires à exporter
            filename: Nom du fichier de sortie
            fieldnames: Liste des champs à inclure (optionnel)
        """
        if not data:
            logger.warning("Aucune donnée à exporter")
            return

        # Aplatir les données
        flattened_data = [NFLFlagDataExporter.flatten_team_data(item) for item in data]

        # Déterminer les colonnes
        if not fieldnames:
            fieldnames = set()
            for item in flattened_data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))

        # Écrire le CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(flattened_data)

            logger.info(f"✓ Données exportées vers {filename} ({len(data)} entrées)")
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")

    @staticmethod
    def export_to_json(data: List[Dict], filename: str):
        """
        Exporte les données vers un fichier JSON

        Args:
            data: Liste des dictionnaires à exporter
            filename: Nom du fichier de sortie
        """
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

            logger.info(f"✓ Données exportées vers {filename} ({len(data)} entrées)")
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {e}")


def main():
    """
    Fonction principale pour démontrer l'utilisation du scraper
    """
    print("=" * 70)
    print("NFL FLAG TOURNAMENTS SCRAPER")
    print("=" * 70)
    print()

    print("Ce scraper permet de collecter les données des équipes et organisations")
    print("de l'application NFL Flag Tournaments (powered by TeamSnap).")
    print()
    print("Deux modes disponibles:")
    print("  1. API TeamSnap (nécessite OAuth2 token)")
    print("  2. Web Scraping (pages publiques)")
    print()

    mode = input("Choisissez le mode (1 ou 2): ").strip()

    if mode == "1":
        print("\n--- MODE API TEAMSNAP ---")
        print("\nPour utiliser l'API TeamSnap, vous devez:")
        print("1. Créer un compte développeur sur TeamSnap")
        print("2. Obtenir un Client ID et Client Secret")
        print("3. Compléter le flux OAuth2 pour obtenir un Access Token")
        print("\nVoir: https://www.teamsnap.com/documentation/apiv3")
        print()

        access_token = input("Entrez votre Access Token (ou 'skip' pour passer): ").strip()

        if access_token and access_token.lower() != 'skip':
            client = TeamSnapAPIClient(access_token)

            print("\nRécupération des données...")
            user = client.get_current_user()

            if user:
                print(f"✓ Connecté en tant que: {user.get('email', 'Unknown')}")

                teams = client.get_teams()
                print(f"✓ {len(teams)} équipes trouvées")

                if teams:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"nfl_flag_teams_{timestamp}.csv"
                    NFLFlagDataExporter.export_to_csv(teams, filename)

                    # Export JSON aussi
                    json_filename = f"nfl_flag_teams_{timestamp}.json"
                    NFLFlagDataExporter.export_to_json(teams, json_filename)
            else:
                print("✗ Erreur d'authentification. Vérifiez votre token.")

    elif mode == "2":
        print("\n--- MODE WEB SCRAPING ---")
        print("\nCe mode tente de découvrir et scraper les endpoints publics.")
        print()

        scraper = NFLFlagWebScraper()

        print("Recherche d'APIs publiques...")
        tournaments = scraper.search_tournaments_api()

        if tournaments:
            print(f"\n✓ {len(tournaments)} endpoint(s) découvert(s)")
            for idx, t in enumerate(tournaments, 1):
                print(f"  {idx}. {t['endpoint']}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nfl_flag_discovered_data_{timestamp}.json"
            NFLFlagDataExporter.export_to_json(tournaments, filename)
        else:
            print("\n✗ Aucun endpoint public découvert automatiquement.")
            print("\nVous pouvez:")
            print("1. Utiliser le mode API avec authentification")
            print("2. Fournir une URL spécifique de tournoi à scraper")

            tournament_url = input("\nEntrez une URL de tournoi (ou 'skip'): ").strip()

            if tournament_url and tournament_url.lower() != 'skip':
                print(f"\nScraping de: {tournament_url}")
                data = scraper.get_tournament_data(tournament_url)

                if data:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"nfl_flag_tournament_{timestamp}.json"
                    NFLFlagDataExporter.export_to_json([data], filename)

    print("\n" + "=" * 70)
    print("Scraping terminé!")
    print("=" * 70)


if __name__ == "__main__":
    main()
