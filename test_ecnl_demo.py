#!/usr/bin/env python3
"""
Démonstration du scraper avec une page ECNL simulée
"""

from generic_sports_scraper import GenericSportsMatchScraper, Match
from datetime import datetime
import json

def simulate_ecnl_scraping():
    """
    Simule le scraping d'une page ECNL avec données d'exemple
    pour montrer les capacités du scraper
    """
    print("=" * 70)
    print("DÉMONSTRATION: Generic Sports Match Scraper")
    print("Site: ECNL (Elite Clubs National League)")
    print("=" * 70)
    print()

    # Créer le scraper
    scraper = GenericSportsMatchScraper(rate_limit=1.5)
    print("✓ Scraper initialisé")
    print(f"  - Rate limit: {scraper.rate_limit}s")
    print(f"  - Max retries: {scraper.max_retries}")
    print(f"  - Stratégies disponibles: 5")
    print()

    # Simuler des matchs extraits (comme si on avait scraped la page)
    print("📊 Simulation de l'extraction...")
    print()

    # Exemple de matchs qui seraient extraits d'une page ECNL
    sample_matches = [
        Match(
            match_id="ECNL001",
            sport="Soccer",
            date="2023-08-08",
            time="10:00",
            datetime_iso="2023-08-08T10:00:00",
            home_team="FC Dallas",
            away_team="Solar SC",
            home_score=2,
            away_score=1,
            status="finished",
            venue="Toyota Soccer Center",
            city="Frisco",
            state="TX",
            competition="ECNL Regional League",
            division="U15 Girls",
            season="2023-2024",
            source_url="https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx",
            scraped_at=datetime.now().isoformat()
        ),
        Match(
            match_id="ECNL002",
            sport="Soccer",
            date="2023-08-08",
            time="12:00",
            datetime_iso="2023-08-08T12:00:00",
            home_team="Sting Dallas",
            away_team="Dallas Texans",
            home_score=1,
            away_score=1,
            status="finished",
            venue="Toyota Soccer Center",
            city="Frisco",
            state="TX",
            competition="ECNL Regional League",
            division="U15 Girls",
            season="2023-2024",
            source_url="https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx",
            scraped_at=datetime.now().isoformat()
        ),
        Match(
            match_id="ECNL003",
            sport="Soccer",
            date="2023-08-08",
            time="14:00",
            datetime_iso="2023-08-08T14:00:00",
            home_team="Tulsa SC",
            away_team="Oklahoma Energy",
            home_score=3,
            away_score=2,
            status="finished",
            venue="Toyota Soccer Center",
            city="Frisco",
            state="TX",
            competition="ECNL Regional League",
            division="U15 Girls",
            season="2023-2024",
            source_url="https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx",
            scraped_at=datetime.now().isoformat()
        ),
        Match(
            match_id="ECNL004",
            sport="Soccer",
            date="2023-08-08",
            time="16:00",
            datetime_iso="2023-08-08T16:00:00",
            home_team="Classics Elite",
            away_team="Houston Dash Youth",
            home_team_id="CLA001",
            away_team_id="HOU001",
            status="scheduled",
            venue="Toyota Soccer Center",
            venue_id="TSC001",
            city="Frisco",
            state="TX",
            competition="ECNL Regional League",
            competition_id="ECNLRL",
            division="U15 Girls",
            division_id="U15G",
            week="1",
            season="2023-2024",
            source_url="https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx",
            scraped_at=datetime.now().isoformat(),
            additional_info={"weather": "Sunny", "temperature": "95°F"}
        ),
        Match(
            match_id="ECNL005",
            sport="Soccer",
            date="2023-08-08",
            time="18:00",
            datetime_iso="2023-08-08T18:00:00",
            home_team="Lonestar SC",
            away_team="San Antonio FC Youth",
            status="scheduled",
            venue="Toyota Soccer Center",
            city="Frisco",
            state="TX",
            competition="ECNL Regional League",
            division="U15 Girls",
            season="2023-2024",
            source_url="https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx",
            scraped_at=datetime.now().isoformat()
        ),
    ]

    print(f"✓ {len(sample_matches)} matchs extraits\n")

    # Afficher les détails
    print("=" * 70)
    print("MATCHS EXTRAITS")
    print("=" * 70)
    print()

    for i, match in enumerate(sample_matches, 1):
        print(f"Match #{i}")
        print("-" * 40)
        print(f"  🆔 ID: {match.match_id}")
        print(f"  ⚽ Sport: {match.sport}")
        print(f"  📅 Date: {match.date} à {match.time}")
        print(f"  🏠 Domicile: {match.home_team}", end="")
        if match.home_score is not None:
            print(f" ({match.home_score})", end="")
        print()
        print(f"  ✈️  Extérieur: {match.away_team}", end="")
        if match.away_score is not None:
            print(f" ({match.away_score})", end="")
        print()

        if match.home_score is not None and match.away_score is not None:
            print(f"  📊 Score Final: {match.home_score} - {match.away_score}")

        print(f"  ⚡ Status: {match.status}")
        print(f"  📍 Lieu: {match.venue}, {match.city}, {match.state}")
        print(f"  🏆 Compétition: {match.competition}")
        print(f"  🔰 Division: {match.division}")
        print(f"  🗓️  Saison: {match.season}")

        if match.additional_info:
            print(f"  ℹ️  Info: {match.additional_info}")

        print()

    # Statistiques
    print("=" * 70)
    print("STATISTIQUES")
    print("=" * 70)
    print()

    finished_matches = [m for m in sample_matches if m.status == "finished"]
    scheduled_matches = [m for m in sample_matches if m.status == "scheduled"]

    print(f"Total matchs: {len(sample_matches)}")
    print(f"  - Terminés: {len(finished_matches)}")
    print(f"  - À venir: {len(scheduled_matches)}")
    print()

    # Équipes uniques
    teams = set()
    for match in sample_matches:
        if match.home_team:
            teams.add(match.home_team)
        if match.away_team:
            teams.add(match.away_team)

    print(f"Équipes uniques: {len(teams)}")
    for team in sorted(teams):
        print(f"  - {team}")
    print()

    # Lieux uniques
    venues = set(m.venue for m in sample_matches if m.venue)
    print(f"Lieux: {len(venues)}")
    for venue in venues:
        print(f"  - {venue}")
    print()

    # Export CSV
    print("=" * 70)
    print("EXPORT CSV")
    print("=" * 70)
    print()

    output_file = "test_ecnl/ecnl_matches_demo.csv"
    scraper.export_to_csv(sample_matches, output_file)
    print(f"✓ Export réussi: {output_file}")
    print()

    # Afficher le contenu du CSV
    print("Aperçu du fichier CSV:")
    print("-" * 70)

    import csv
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)

        # Header
        print(" | ".join(lines[0][:6]) + " | ...")
        print("-" * 70)

        # Premières lignes
        for line in lines[1:4]:
            print(" | ".join(line[:6]) + " | ...")

    print(f"\n... et {len(lines) - 4} lignes supplémentaires")
    print()

    # Démonstration des stratégies
    print("=" * 70)
    print("STRATÉGIES D'EXTRACTION UTILISÉES")
    print("=" * 70)
    print()

    strategies = [
        ("1. Tables HTML", "Extrait les matchs depuis des <table> avec headers"),
        ("2. Listes HTML", "Parse les <ul>/<ol> avec patterns 'Team A vs Team B'"),
        ("3. Divs Structurées", "Cherche des divs avec classes 'match', 'game', etc."),
        ("4. JSON-LD", "Parse les <script type='application/ld+json'> (schema.org)"),
        ("5. JSON Embedded", "Extrait le JSON embedded dans les scripts JavaScript"),
    ]

    print("Le scraper essaye automatiquement ces 5 stratégies:")
    print()
    for name, desc in strategies:
        print(f"{name}")
        print(f"  → {desc}")
        print()

    # Champs extraits
    print("=" * 70)
    print("CHAMPS DE DONNÉES DISPONIBLES")
    print("=" * 70)
    print()

    fields = [
        ("Identification", ["match_id", "sport"]),
        ("Timing", ["date", "time", "datetime_iso"]),
        ("Équipes", ["home_team", "away_team", "home_team_id", "away_team_id"]),
        ("Scores", ["home_score", "away_score", "status"]),
        ("Lieu", ["venue", "venue_id", "city", "state", "address"]),
        ("Compétition", ["competition", "competition_id", "division", "division_id", "round", "week", "season"]),
        ("Métadonnées", ["source_url", "scraped_at", "additional_info"]),
    ]

    print("Le scraper extrait jusqu'à 27 champs par match:")
    print()
    for category, field_list in fields:
        print(f"{category}:")
        print(f"  {', '.join(field_list)}")
        print()

    # Conclusion
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    print("✅ Le Generic Sports Match Scraper peut extraire:")
    print("  • Des matchs depuis n'importe quel site web de sports")
    print("  • Toutes les informations disponibles (27 champs)")
    print("  • Export CSV organisé et structuré")
    print("  • Métadonnées complètes pour chaque match")
    print()

    print("🚀 Utilisation réelle:")
    print("  python generic_sports_scraper.py \"https://theecnl.com/...\" --single-page")
    print()

    print("💡 Pour contourner les restrictions réseau:")
    print("  • Utiliser un VPN")
    print("  • Modifier les headers du scraper")
    print("  • Utiliser un proxy")
    print("  • Exécuter depuis un environnement différent")
    print()


def show_ecnl_page_structure():
    """Affiche la structure typique d'une page ECNL"""
    print("\n" + "=" * 70)
    print("STRUCTURE TYPIQUE D'UNE PAGE ECNL")
    print("=" * 70)
    print()

    print("Les pages ECNL contiennent généralement:")
    print()

    structures = [
        ("Tables de calendrier", """
<table class="schedule-table">
  <thead>
    <tr><th>Date</th><th>Time</th><th>Home</th><th>Away</th><th>Score</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>08/08/2023</td>
      <td>10:00 AM</td>
      <td>FC Dallas</td>
      <td>Solar SC</td>
      <td>2-1</td>
    </tr>
  </tbody>
</table>
        """),
        ("Divs de matchs", """
<div class="match-item">
  <div class="match-date">08/08/2023</div>
  <div class="match-time">10:00 AM</div>
  <div class="team home">FC Dallas</div>
  <div class="score">2 - 1</div>
  <div class="team away">Solar SC</div>
  <div class="venue">Toyota Soccer Center</div>
</div>
        """),
        ("JSON-LD (structured data)", """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SportsEvent",
  "name": "FC Dallas vs Solar SC",
  "startDate": "2023-08-08T10:00:00",
  "location": {
    "@type": "Place",
    "name": "Toyota Soccer Center",
    "address": {
      "addressLocality": "Frisco",
      "addressRegion": "TX"
    }
  },
  "homeTeam": {"name": "FC Dallas"},
  "awayTeam": {"name": "Solar SC"}
}
</script>
        """)
    ]

    for title, code in structures:
        print(f"📄 {title}:")
        print(code)
        print()

    print("✅ Le scraper détecte et parse automatiquement ces structures!")
    print()


if __name__ == '__main__':
    simulate_ecnl_scraping()
    show_ecnl_page_structure()

    print("=" * 70)
    print("FIN DE LA DÉMONSTRATION")
    print("=" * 70)
    print()
    print("Pour tester avec le vrai site ECNL:")
    print("  1. Vérifier la connectivité réseau")
    print("  2. Utiliser python generic_sports_scraper.py <URL>")
    print("  3. Ou utiliser l'interface interactive: python interactive_scraper.py")
    print()
