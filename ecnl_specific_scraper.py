#!/usr/bin/env python3
"""
Extracteur spécifique pour les pages ECNL (Sidearm Sports)
Les pages ECNL utilisent une structure spécifique qu'il faut parser différemment
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional


class ECNLSidearmExtractor:
    """Extracteur spécialisé pour les pages ECNL basées sur Sidearm Sports"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère et parse une page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"❌ Erreur lors de la récupération: {e}")
            return None

    def extract_from_sidearm_schedule(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """
        Extrait les matchs depuis une page schedule Sidearm Sports
        Les pages ECNL utilisent généralement des tables ou divs avec classes spécifiques
        """
        matches = []

        # Stratégie 1: Chercher les tables de schedule Sidearm
        # Patterns communs: .sidearm-schedule-games, .sidearm-table-schedule
        schedule_tables = soup.find_all('table', class_=re.compile(r'schedule|sidearm', re.I))

        for table in schedule_tables:
            print(f"  → Table trouvée: {table.get('class')}")
            rows = table.find_all('tr')

            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue

                match = self._parse_table_row(cells, url)
                if match:
                    matches.append(match)

        # Stratégie 2: Divs avec data-game ou data-event
        game_divs = soup.find_all(['div', 'article'], attrs={'data-game': True})
        game_divs += soup.find_all(['div', 'article'], class_=re.compile(r'game|event|match', re.I))

        for div in game_divs:
            match = self._parse_game_div(div, url)
            if match:
                matches.append(match)

        # Stratégie 3: Chercher dans les scripts pour JSON/JavaScript
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_matches = self._extract_from_script(script.string, url)
                matches.extend(script_matches)

        # Stratégie 4: iFrame avec schedule embedded
        iframes = soup.find_all('iframe', src=re.compile(r'schedule|calendar', re.I))
        if iframes:
            print(f"  ℹ️  {len(iframes)} iframe(s) détecté(s) - peut contenir des matchs")
            # Note: Les iframes nécessitent un traitement séparé

        return self._deduplicate_matches(matches)

    def _parse_table_row(self, cells, url: str) -> Optional[Dict]:
        """Parse une ligne de table"""
        try:
            match = {
                'source_url': url,
                'scraped_at': datetime.now().isoformat()
            }

            # Extraire le texte de chaque cellule
            cell_texts = [cell.get_text().strip() for cell in cells]

            # Identifier les colonnes par contenu
            for i, text in enumerate(cell_texts):
                # Date pattern
                if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text):
                    match['date'] = text

                # Time pattern
                elif re.search(r'\d{1,2}:\d{2}', text):
                    match['time'] = text

                # Score pattern
                elif re.search(r'^\d+\s*-\s*\d+$', text):
                    scores = re.findall(r'\d+', text)
                    if len(scores) == 2:
                        match['home_score'] = int(scores[0])
                        match['away_score'] = int(scores[1])
                        match['status'] = 'finished'

                # vs pattern (équipes)
                elif ' vs ' in text.lower() or ' vs. ' in text.lower():
                    teams = re.split(r'\s+vs\.?\s+', text, flags=re.I)
                    if len(teams) == 2:
                        match['home_team'] = teams[0].strip()
                        match['away_team'] = teams[1].strip()

                # @ pattern (away @ home)
                elif ' @ ' in text or ' at ' in text.lower():
                    parts = re.split(r'\s+(?:@|at)\s+', text, flags=re.I)
                    if len(parts) == 2:
                        match['away_team'] = parts[0].strip()
                        match['home_team'] = parts[1].strip()

                # Liens vers équipes
                links = cells[i].find_all('a')
                if links:
                    for link in links[:2]:  # Max 2 équipes
                        team_name = link.get_text().strip()
                        if team_name and 'home_team' not in match:
                            match['home_team'] = team_name
                        elif team_name and 'away_team' not in match:
                            match['away_team'] = team_name

            # Vérifier si on a au moins des équipes
            if 'home_team' in match or 'away_team' in match:
                return match

        except Exception as e:
            print(f"  ⚠️  Erreur parsing row: {e}")

        return None

    def _parse_game_div(self, div, url: str) -> Optional[Dict]:
        """Parse un div de match"""
        try:
            match = {
                'source_url': url,
                'scraped_at': datetime.now().isoformat()
            }

            # Chercher les classes et data attributes
            match_id = div.get('data-game') or div.get('data-event-id')
            if match_id:
                match['match_id'] = match_id

            # Chercher des sous-éléments spécifiques
            text = div.get_text()

            # Date
            date_elem = div.find(class_=re.compile(r'date', re.I))
            if date_elem:
                match['date'] = date_elem.get_text().strip()

            # Time
            time_elem = div.find(class_=re.compile(r'time', re.I))
            if time_elem:
                match['time'] = time_elem.get_text().strip()

            # Teams
            team_elems = div.find_all(class_=re.compile(r'team', re.I))
            if len(team_elems) >= 2:
                match['home_team'] = team_elems[0].get_text().strip()
                match['away_team'] = team_elems[1].get_text().strip()

            # Score
            score_elems = div.find_all(class_=re.compile(r'score', re.I))
            if len(score_elems) >= 2:
                try:
                    match['home_score'] = int(re.search(r'\d+', score_elems[0].get_text()).group())
                    match['away_score'] = int(re.search(r'\d+', score_elems[1].get_text()).group())
                    match['status'] = 'finished'
                except:
                    pass

            # Venue
            venue_elem = div.find(class_=re.compile(r'location|venue', re.I))
            if venue_elem:
                match['venue'] = venue_elem.get_text().strip()

            if 'home_team' in match or 'away_team' in match:
                return match

        except Exception as e:
            print(f"  ⚠️  Erreur parsing div: {e}")

        return None

    def _extract_from_script(self, script_text: str, url: str) -> List[Dict]:
        """Extrait les matchs depuis du JavaScript/JSON"""
        matches = []

        # Chercher des patterns JSON
        json_patterns = [
            r'var\s+schedule\s*=\s*(\[.*?\]);',
            r'const\s+games\s*=\s*(\[.*?\]);',
            r'"games"\s*:\s*(\[.*?\])',
            r'"schedule"\s*:\s*(\[.*?\])',
        ]

        for pattern in json_patterns:
            try:
                match = re.search(pattern, script_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    data = json.loads(json_str)

                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                match_data = {
                                    'source_url': url,
                                    'scraped_at': datetime.now().isoformat()
                                }

                                # Mapper les clés communes
                                key_mapping = {
                                    'id': 'match_id',
                                    'gameId': 'match_id',
                                    'date': 'date',
                                    'time': 'time',
                                    'homeTeam': 'home_team',
                                    'awayTeam': 'away_team',
                                    'opponent': 'away_team',
                                    'homeScore': 'home_score',
                                    'awayScore': 'away_score',
                                    'location': 'venue',
                                    'venue': 'venue',
                                }

                                for json_key, match_key in key_mapping.items():
                                    if json_key in item:
                                        match_data[match_key] = item[json_key]

                                if 'home_team' in match_data or 'away_team' in match_data:
                                    matches.append(match_data)
            except:
                continue

        return matches

    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        """Élimine les doublons"""
        seen = set()
        unique = []

        for match in matches:
            key = (
                match.get('date'),
                match.get('time'),
                match.get('home_team'),
                match.get('away_team')
            )

            if key not in seen:
                seen.add(key)
                unique.append(match)

        return unique

    def save_debug_info(self, soup: BeautifulSoup):
        """Sauvegarde des infos de debug"""
        # Sauvegarder le HTML
        with open('ecnl_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        # Sauvegarder le texte brut
        with open('ecnl_page_debug.txt', 'w', encoding='utf-8') as f:
            f.write(soup.get_text())

        # Sauvegarder la structure des tables
        tables = soup.find_all('table')
        with open('ecnl_tables_debug.txt', 'w', encoding='utf-8') as f:
            for i, table in enumerate(tables, 1):
                f.write(f"\n{'='*70}\n")
                f.write(f"TABLE #{i}\n")
                f.write(f"Classes: {table.get('class')}\n")
                f.write(f"ID: {table.get('id')}\n")
                f.write(f"{'='*70}\n")
                f.write(table.prettify())
                f.write("\n\n")

        print("\n💾 Fichiers de debug sauvegardés:")
        print("   - ecnl_page_debug.html")
        print("   - ecnl_page_debug.txt")
        print("   - ecnl_tables_debug.txt")

    def export_to_csv(self, matches: List[Dict], filename: str):
        """Exporte les matchs en CSV"""
        if not matches:
            print("❌ Aucun match à exporter")
            return

        fieldnames = [
            'match_id', 'date', 'time', 'home_team', 'away_team',
            'home_score', 'away_score', 'status', 'venue',
            'source_url', 'scraped_at'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(matches)

        print(f"✓ {len(matches)} matchs exportés vers {filename}")


def main():
    """Fonction principale"""
    import sys

    print("=" * 70)
    print("ECNL SPECIFIC SCRAPER (Sidearm Sports)")
    print("=" * 70)
    print()

    # URL par défaut
    url = "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"

    if len(sys.argv) > 1:
        url = sys.argv[1]

    print(f"URL: {url}\n")

    # Créer l'extracteur
    extractor = ECNLSidearmExtractor()

    # Récupérer la page
    print("⏳ Récupération de la page...")
    soup = extractor.fetch_page(url)

    if not soup:
        print("\n❌ Impossible de récupérer la page")
        print("\n💡 Suggestions:")
        print("   1. Vérifiez votre connexion internet")
        print("   2. Vérifiez que l'URL est accessible")
        print("   3. Le site peut bloquer les scrapers")
        return

    print("✓ Page récupérée\n")

    # Sauvegarder pour debug
    print("💾 Sauvegarde des infos de debug...")
    extractor.save_debug_info(soup)

    # Extraire les matchs
    print("\n🔍 Extraction des matchs...\n")
    matches = extractor.extract_from_sidearm_schedule(soup, url)

    # Afficher les résultats
    print("\n" + "=" * 70)
    print("RÉSULTATS")
    print("=" * 70)
    print()

    if not matches:
        print("❌ Aucun match trouvé\n")
        print("💡 Actions à faire:")
        print("   1. Ouvrez ecnl_page_debug.html dans un navigateur")
        print("   2. Identifiez la structure des matchs")
        print("   3. Consultez ecnl_tables_debug.txt pour voir les tables")
        print()
        print("   Puis adaptez le script selon la structure trouvée.")
        return

    print(f"✓ {len(matches)} matchs extraits\n")

    # Aperçu
    print("APERÇU DES MATCHS:\n")
    for i, match in enumerate(matches[:5], 1):
        print(f"Match #{i}")
        print("-" * 40)
        if match.get('date'):
            print(f"  📅 Date: {match['date']}")
        if match.get('time'):
            print(f"  🕐 Heure: {match['time']}")
        if match.get('home_team'):
            score_str = f" ({match['home_score']})" if match.get('home_score') is not None else ""
            print(f"  🏠 Domicile: {match['home_team']}{score_str}")
        if match.get('away_team'):
            score_str = f" ({match['away_score']})" if match.get('away_score') is not None else ""
            print(f"  ✈️  Extérieur: {match['away_team']}{score_str}")
        if match.get('venue'):
            print(f"  📍 Lieu: {match['venue']}")
        if match.get('status'):
            print(f"  ⚡ Status: {match['status']}")
        print()

    if len(matches) > 5:
        print(f"... et {len(matches) - 5} autres matchs\n")

    # Export CSV
    output_file = 'ecnl_matches_extracted.csv'
    extractor.export_to_csv(matches, output_file)

    print("\n" + "=" * 70)
    print("✓ TERMINÉ")
    print("=" * 70)


if __name__ == '__main__':
    main()
