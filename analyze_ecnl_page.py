#!/usr/bin/env python3
"""
Script pour analyser la structure d'une page ECNL
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_ecnl_page(url):
    """Analyse la structure d'une page ECNL"""
    print(f"Analyse de: {url}\n")
    print("=" * 70)

    # Récupérer la page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.content)} bytes")
    print("=" * 70)

    soup = BeautifulSoup(response.content, 'lxml')

    # 1. Analyser les tables
    print("\n1. TABLES HTML")
    print("-" * 70)
    tables = soup.find_all('table')
    print(f"Nombre de tables: {len(tables)}")

    for i, table in enumerate(tables[:3], 1):
        print(f"\nTable #{i}:")
        # Classes
        classes = table.get('class', [])
        print(f"  Classes: {classes}")

        # Headers
        headers = table.find_all('th')
        if headers:
            print(f"  Headers: {[h.get_text().strip() for h in headers[:10]]}")

        # Rows
        rows = table.find_all('tr')
        print(f"  Rows: {len(rows)}")

        # Premier row comme exemple
        if len(rows) > 1:
            first_row = rows[1]
            cells = first_row.find_all(['td', 'th'])
            print(f"  Exemple (première ligne): {[c.get_text().strip()[:30] for c in cells[:5]]}")

    # 2. Analyser les divs avec classes "match", "game", etc.
    print("\n\n2. DIVS STRUCTURÉES")
    print("-" * 70)

    match_keywords = ['match', 'game', 'fixture', 'event', 'contest', 'schedule']
    for keyword in match_keywords:
        divs = soup.find_all('div', class_=re.compile(keyword, re.I))
        if divs:
            print(f"\nDivs avec '{keyword}' dans class: {len(divs)}")
            if divs:
                first_div = divs[0]
                print(f"  Classes: {first_div.get('class')}")
                print(f"  Contenu (extrait): {first_div.get_text().strip()[:100]}")

    # 3. Chercher les scripts avec JSON
    print("\n\n3. SCRIPTS JAVASCRIPT / JSON")
    print("-" * 70)

    scripts = soup.find_all('script')
    print(f"Nombre de scripts: {len(scripts)}")

    # JSON-LD
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    print(f"\nScripts JSON-LD: {len(json_ld_scripts)}")

    for i, script in enumerate(json_ld_scripts[:2], 1):
        print(f"\nJSON-LD #{i}:")
        try:
            data = json.loads(script.string)
            print(f"  Type: {data.get('@type', 'N/A')}")
            print(f"  Keys: {list(data.keys())[:10]}")
        except:
            print("  Erreur de parsing")

    # Scripts avec variables JavaScript
    print(f"\nRecherche de patterns JSON dans les scripts...")
    json_patterns = [
        r'var\s+\w+\s*=\s*\{',
        r'const\s+\w+\s*=\s*\{',
        r'let\s+\w+\s*=\s*\{',
        r'window\.\w+\s*=\s*\{',
        r'\{["\']games["\']\s*:',
        r'\{["\']matches["\']\s*:',
        r'\{["\']schedule["\']\s*:',
    ]

    found_json = []
    for script in scripts:
        if script.string:
            for pattern in json_patterns:
                if re.search(pattern, script.string):
                    found_json.append((pattern, script.string[:200]))
                    break

    print(f"Scripts avec JSON potentiel: {len(found_json)}")
    for i, (pattern, snippet) in enumerate(found_json[:3], 1):
        print(f"\n  Pattern #{i}: {pattern}")
        print(f"  Snippet: {snippet}...")

    # 4. Analyser les listes
    print("\n\n4. LISTES (UL/OL)")
    print("-" * 70)

    lists = soup.find_all(['ul', 'ol'])
    print(f"Nombre de listes: {len(lists)}")

    # Chercher des listes avec pattern "vs" ou "vs."
    for i, list_elem in enumerate(lists[:5], 1):
        items = list_elem.find_all('li')
        if items:
            text = ' '.join([item.get_text() for item in items[:3]])
            if 'vs' in text.lower() or ' - ' in text:
                print(f"\nListe #{i} (potentiel):")
                print(f"  Items: {len(items)}")
                print(f"  Exemple: {items[0].get_text().strip()[:100]}")

    # 5. Chercher des patterns de texte
    print("\n\n5. ANALYSE DE CONTENU")
    print("-" * 70)

    text_content = soup.get_text()

    # Patterns de matchs
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
    ]

    time_patterns = [
        r'\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm))?',
    ]

    score_patterns = [
        r'\d{1,3}\s*[-:]\s*\d{1,3}',
    ]

    print("\nPatterns trouvés dans le texte:")

    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text_content)
        dates.extend(matches[:5])
    if dates:
        print(f"  Dates: {dates[:5]}")

    times = []
    for pattern in time_patterns:
        matches = re.findall(pattern, text_content)
        times.extend(matches[:5])
    if times:
        print(f"  Heures: {times[:5]}")

    scores = []
    for pattern in score_patterns:
        matches = re.findall(pattern, text_content)
        scores.extend(matches[:5])
    if scores:
        print(f"  Scores: {scores[:5]}")

    # 6. Sauvegarder le HTML pour inspection
    print("\n\n6. SAUVEGARDE")
    print("-" * 70)

    with open('ecnl_page_analysis.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("HTML sauvegardé dans: ecnl_page_analysis.html")

    # Sauvegarder un extrait du texte
    with open('ecnl_page_text.txt', 'w', encoding='utf-8') as f:
        f.write(text_content)
    print("Texte sauvegardé dans: ecnl_page_text.txt")

    # 7. Recommandations
    print("\n\n7. RECOMMANDATIONS")
    print("-" * 70)

    print("\nPour implémenter le scraping:")

    if tables:
        print("  ✓ Analyser les tables dans ecnl_page_analysis.html")
        print("    Chercher les classes/IDs spécifiques des tables de matchs")

    if found_json:
        print("  ✓ Examiner les scripts JavaScript pour données JSON")
        print("    Chercher les structures 'games', 'matches', 'schedule'")

    if dates or times:
        print("  ✓ Le contenu contient des dates/heures")
        print("    Implémenter une stratégie de parsing de texte")

    print("\n  → Inspectez ecnl_page_analysis.html pour identifier")
    print("    la structure exacte des matchs")


if __name__ == '__main__':
    url = "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"
    analyze_ecnl_page(url)
