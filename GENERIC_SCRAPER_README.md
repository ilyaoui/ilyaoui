# Generic Sports Match Scraper 🏆⚽🏀🏈

Un système de scraping **universel et adaptatif** pour extraire des matchs sportifs depuis **n'importe quel site web** et les enregistrer dans des fichiers CSV bien organisés, structurés et riches d'informations.

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Installation](#installation)
- [Utilisation Rapide](#utilisation-rapide)
- [Guide Complet](#guide-complet)
- [Architecture](#architecture)
- [Stratégies de Scraping](#stratégies-de-scraping)
- [Format des Données](#format-des-données)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Configuration Avancée](#configuration-avancée)
- [API Programmatique](#api-programmatique)
- [Troubleshooting](#troubleshooting)
- [Bonnes Pratiques](#bonnes-pratiques)

---

## 🎯 Vue d'ensemble

Le **Generic Sports Match Scraper** est un système intelligent qui peut:
- ✅ Scraper **n'importe quel site web** de sports
- ✅ Détecter **automatiquement** la structure des pages
- ✅ Découvrir **tous les calendriers** disponibles
- ✅ Extraire des **matchs complets** avec métadonnées riches
- ✅ Exporter vers des **fichiers CSV structurés**
- ✅ Gérer **plusieurs formats** (tables, listes, divs, JSON, JSON-LD)

### Cas d'utilisation

- 🏈 **Football américain**: NFL Flag, NCAA, NFL
- ⚽ **Soccer**: Ligues locales, compétitions
- 🏀 **Basketball**: Tournois, ligues
- ⚾ **Baseball**: Calendriers de saison
- 🏐 **Volleyball**: Championnats
- 🎾 **Tennis**: Tournois
- ... et **tout autre sport** !

---

## ✨ Fonctionnalités Principales

### 🔍 Scraping Adaptatif

Le scraper **détecte automatiquement** la structure des pages et adapte sa stratégie:

1. **Extraction depuis tables HTML** (`<table>`)
2. **Extraction depuis listes** (`<ul>`, `<ol>`)
3. **Extraction depuis divs structurées** (classes CSS)
4. **Extraction depuis JSON-LD** (structured data / schema.org)
5. **Extraction depuis JSON embedded** dans JavaScript

### 🗺️ Découverte Automatique de Calendriers

- **Crawling intelligent** avec profondeur configurable
- **Identification automatique** des pages contenant des matchs
- **Détection de patterns** (dates, heures, scores, équipes)
- **Filtrage par mots-clés** (schedule, calendar, matches, etc.)

### 📊 Extraction Complète

Le scraper extrait **toutes les informations disponibles**:

#### Informations sur les Matchs
- 🆔 **ID du match**
- 🏆 **Sport** (si identifiable)
- 📅 **Date** et **Heure**
- 🕐 **DateTime ISO** (format standardisé)

#### Équipes
- 🏠 **Équipe domicile** (nom + ID)
- ✈️ **Équipe extérieur** (nom + ID)
- 🔢 **Scores** (domicile et extérieur)
- ⚡ **Status** (scheduled, live, finished, cancelled)

#### Lieu
- 📍 **Lieu/Stade** (nom + ID)
- 🌆 **Ville**
- 🗺️ **État/Région**
- 📮 **Adresse complète**

#### Compétition
- 🏅 **Compétition** (nom + ID)
- 🔰 **Division** (nom + ID)
- 🔄 **Round/Tour**
- 📅 **Semaine**
- 🗓️ **Saison**

#### Métadonnées
- 🔗 **URL source**
- ⏰ **Date de scraping**
- 📝 **Informations additionnelles** (JSON)

### 💾 Export Structuré

- **CSV enrichi** avec toutes les métadonnées
- **Organisation automatique** par calendrier
- **Fichier récapitulatif** (`all_matches.csv`)
- **Encodage UTF-8** (support international)
- **Headers explicites** pour faciliter l'analyse

### 🛡️ Robustesse

- ✅ **Rate limiting** configurable
- ✅ **Retry automatique** avec exponential backoff
- ✅ **Gestion des erreurs** gracieuse
- ✅ **Logging détaillé** pour debugging
- ✅ **Déduplication** des matchs
- ✅ **Headers réalistes** pour éviter les blocages

---

## 📦 Installation

### Prérequis

- Python 3.7+
- pip

### Installation Simple

```bash
# Cloner le repository
git clone <repo-url>
cd ilyaoui

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances

Le scraper utilise uniquement des bibliothèques standard et éprouvées:

```
requests>=2.31.0        # Client HTTP
beautifulsoup4>=4.12.0  # Parser HTML/XML
lxml>=4.9.0             # Backend rapide pour BeautifulSoup
python-dotenv>=1.0.0    # Gestion des variables d'environnement
```

---

## 🚀 Utilisation Rapide

### Option 1: Interface Interactive (Recommandé)

```bash
python interactive_scraper.py
```

Menu convivial avec 5 options:
1. **Scraper une page unique** - URL directe vers une page de matchs
2. **Découvrir tous les calendriers** - Crawling automatique
3. **Mode avancé** - Configuration personnalisée
4. **Exemples** - Voir des cas d'utilisation
5. **Aide** - Documentation complète

### Option 2: Ligne de Commande

#### Scraper une page unique

```bash
python generic_sports_scraper.py "https://example.com/matches" --single-page
```

#### Découvrir et scraper tous les calendriers

```bash
python generic_sports_scraper.py "https://example.com/sports"
```

#### Avec options personnalisées

```bash
python generic_sports_scraper.py "https://example.com/sports" \
  --depth 4 \
  --rate-limit 2.0 \
  --output mes_matchs \
  --verbose
```

### Option 3: Import Python

```python
from generic_sports_scraper import GenericSportsMatchScraper

# Créer le scraper
scraper = GenericSportsMatchScraper(rate_limit=1.5)

# Scraper une page
matches = scraper.scrape_matches_from_url('https://example.com/matches')

# Exporter
scraper.export_to_csv(matches, 'output/matches.csv')
```

---

## 📖 Guide Complet

### Mode 1: Page Unique

Utilisez ce mode quand vous avez **une URL directe** vers une page contenant des matchs.

#### Ligne de commande

```bash
python generic_sports_scraper.py "https://nflflag.com/events/patriots-tournament" --single-page
```

#### Python

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper()
matches = scraper.scrape_matches_from_url('https://nflflag.com/events/patriots')

# Afficher les résultats
print(f"{len(matches)} matchs trouvés")
for match in matches:
    print(f"{match.home_team} vs {match.away_team} - {match.date}")

# Exporter
scraper.export_to_csv(matches, 'patriots_matches.csv')
```

### Mode 2: Découverte de Calendriers

Utilisez ce mode pour **crawler un site** et découvrir automatiquement tous les calendriers.

#### Ligne de commande

```bash
python generic_sports_scraper.py "https://example.com/sports" --depth 3 --rate-limit 1.5
```

#### Python

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper(rate_limit=1.5)

# Découvrir les calendriers
calendars = scraper.discover_calendars('https://example.com/sports', max_depth=3)

print(f"{len(calendars)} calendriers découverts:")
for cal in calendars:
    print(f"  - {cal.name}: {cal.url}")

# Scraper chaque calendrier
for calendar in calendars:
    matches = scraper.scrape_matches_from_url(calendar.url)
    calendar.matches = matches
    print(f"    {len(matches)} matchs extraits")

# Exporter tout
scraper.export_calendars_to_csv(calendars, 'output/')
```

### Mode 3: Scraping Complet (Tout-en-un)

```python
scraper = GenericSportsMatchScraper(rate_limit=1.5)

# Découvrir + Scraper + Exporter en une seule opération
results = scraper.scrape_all_calendars('https://example.com/sports', max_depth=3)

# results est un dict: {calendar_url: [matches]}
total = sum(len(matches) for matches in results.values())
print(f"Total: {total} matchs extraits depuis {len(results)} calendriers")
```

---

## 🏗️ Architecture

### Composants Principaux

```
generic_sports_scraper.py
│
├── Match (dataclass)
│   └── Modèle de données pour un match
│
├── Calendar (dataclass)
│   └── Modèle de données pour un calendrier
│
└── GenericSportsMatchScraper (class)
    ├── discover_calendars()           # Découverte de calendriers
    ├── scrape_matches_from_url()      # Extraction de matchs
    ├── export_to_csv()                # Export CSV
    └── export_calendars_to_csv()      # Export multiple
```

### Flux de Données

```
URL d'entrée
    ↓
Découverte de calendriers (optionnel)
    ↓
Pour chaque calendrier:
    ↓
Requête HTTP + Rate Limiting
    ↓
Parse HTML avec BeautifulSoup
    ↓
Essai de 5 stratégies d'extraction
    ↓
Consolidation des résultats
    ↓
Déduplication
    ↓
Export CSV
```

---

## 🎯 Stratégies de Scraping

Le scraper utilise **5 stratégies** qui s'exécutent en parallèle. Toutes les stratégies qui trouvent des matchs contribuent au résultat final.

### Stratégie 1: Tables HTML

**Quand:** La page contient des `<table>` avec des matchs

**Comment:**
- Identifie les headers de colonnes
- Map les colonnes aux champs (date, équipe, score, etc.)
- Parse chaque ligne comme un match

**Exemple de structure détectée:**
```html
<table>
  <tr>
    <th>Date</th><th>Home Team</th><th>Away Team</th><th>Score</th>
  </tr>
  <tr>
    <td>2025-01-15</td><td>Patriots</td><td>Eagles</td><td>24-17</td>
  </tr>
</table>
```

### Stratégie 2: Listes HTML

**Quand:** La page utilise `<ul>` ou `<ol>` pour afficher les matchs

**Comment:**
- Cherche des patterns "Team A vs Team B"
- Extrait date/heure/score avec regex
- Parse chaque `<li>` comme un match potentiel

**Exemple de structure détectée:**
```html
<ul>
  <li>Patriots vs Eagles - Jan 15, 2025 at 7:00 PM (24-17)</li>
  <li>Cowboys vs Giants - Jan 16, 2025 at 1:00 PM</li>
</ul>
```

### Stratégie 3: Divs Structurées

**Quand:** La page utilise des `<div>` avec des classes CSS spécifiques

**Comment:**
- Cherche des divs avec classes contenant "match", "game", "fixture"
- Extrait les sous-éléments (teams, scores, dates)
- Analyse les classes CSS pour identifier le rôle

**Exemple de structure détectée:**
```html
<div class="match-card">
  <div class="team home">Patriots</div>
  <div class="score">24 - 17</div>
  <div class="team away">Eagles</div>
  <div class="match-date">Jan 15, 2025</div>
</div>
```

### Stratégie 4: JSON-LD (Structured Data)

**Quand:** La page inclut des `<script type="application/ld+json">`

**Comment:**
- Parse le JSON-LD (schema.org)
- Identifie les objets de type "SportsEvent"
- Extrait les propriétés structurées

**Exemple de structure détectée:**
```html
<script type="application/ld+json">
{
  "@type": "SportsEvent",
  "name": "Patriots vs Eagles",
  "startDate": "2025-01-15T19:00:00",
  "location": {
    "@type": "Place",
    "name": "Gillette Stadium",
    "address": {
      "addressLocality": "Foxborough",
      "addressRegion": "MA"
    }
  },
  "competitor": [
    {"name": "Patriots"},
    {"name": "Eagles"}
  ]
}
</script>
```

### Stratégie 5: JSON Embedded

**Quand:** La page inclut du JSON dans des balises `<script>`

**Comment:**
- Cherche des patterns JavaScript contenant du JSON
- Extrait les objets "matches", "games", "fixtures"
- Parse récursivement les structures JSON

**Exemple de structure détectée:**
```html
<script>
  var matchData = {
    "matches": [
      {
        "id": 12345,
        "homeTeam": "Patriots",
        "awayTeam": "Eagles",
        "date": "2025-01-15",
        "homeScore": 24,
        "awayScore": 17
      }
    ]
  };
</script>
```

---

## 📊 Format des Données

### Modèle de Données: Match

```python
@dataclass
class Match:
    # Identification
    match_id: Optional[str] = None
    sport: Optional[str] = None

    # Timing
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
    status: Optional[str] = None

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
```

### Format CSV

Le fichier CSV exporté contient **toutes les colonnes** avec headers explicites:

```csv
match_id,sport,date,time,datetime_iso,home_team,away_team,home_team_id,away_team_id,home_score,away_score,status,venue,venue_id,city,state,address,competition,competition_id,division,division_id,round,week,season,source_url,scraped_at,additional_info
12345,Football,2025-01-15,19:00,2025-01-15T19:00:00,Patriots,Eagles,101,102,24,17,finished,Gillette Stadium,201,Foxborough,MA,"1 Patriot Place",NFL,1,AFC East,10,Wild Card,18,2024-2025,https://example.com/match/12345,2025-01-15T20:30:00,"{""weather"":""Clear""}"
```

### Organisation des Fichiers

Après un scraping complet avec découverte de calendriers:

```
output/
├── Division_U12_1.csv           # Calendrier 1
├── Division_U14_2.csv           # Calendrier 2
├── Championship_Tournament_3.csv # Calendrier 3
└── all_matches.csv              # Récapitulatif de TOUS les matchs
```

---

## 💡 Exemples d'Utilisation

### Exemple 1: Scraper les matchs de la NFL

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper(rate_limit=2.0)

# Scraper la page de schedule NFL
matches = scraper.scrape_matches_from_url('https://www.nfl.com/schedules/')

print(f"{len(matches)} matchs NFL trouvés")

# Filtrer par équipe
patriots_matches = [m for m in matches if 'Patriots' in (m.home_team or '') or 'Patriots' in (m.away_team or '')]
print(f"{len(patriots_matches)} matchs des Patriots")

# Exporter
scraper.export_to_csv(patriots_matches, 'patriots_schedule.csv')
```

### Exemple 2: Scraper tous les tournois d'une ligue

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper(rate_limit=1.5)

# Découvrir tous les calendriers
base_url = 'https://example-league.com/tournaments'
calendars = scraper.discover_calendars(base_url, max_depth=4)

print(f"Calendriers découverts: {len(calendars)}")

# Scraper et exporter
all_matches = []
for cal in calendars:
    matches = scraper.scrape_matches_from_url(cal.url)
    cal.matches = matches
    all_matches.extend(matches)

# Stats
print(f"Total: {len(all_matches)} matchs")
print(f"Équipes uniques: {len(set(m.home_team for m in all_matches if m.home_team))}")

# Export
scraper.export_calendars_to_csv(calendars, 'output/')
```

### Exemple 3: Analyser les résultats

```python
from generic_sports_scraper import GenericSportsMatchScraper
import csv
from collections import Counter

scraper = GenericSportsMatchScraper()
matches = scraper.scrape_matches_from_url('https://example.com/results')

# Statistiques
print(f"Total matchs: {len(matches)}")

# Matchs par status
statuses = Counter(m.status for m in matches if m.status)
print("\nMatchs par status:")
for status, count in statuses.items():
    print(f"  {status}: {count}")

# Lieux les plus utilisés
venues = Counter(m.venue for m in matches if m.venue)
print("\nTop 5 lieux:")
for venue, count in venues.most_common(5):
    print(f"  {venue}: {count} matchs")

# Matchs avec scores élevés
high_scoring = [m for m in matches
                if m.home_score and m.away_score
                and (m.home_score + m.away_score) > 50]
print(f"\nMatchs avec +50 points: {len(high_scoring)}")
```

### Exemple 4: Export personnalisé

```python
from generic_sports_scraper import GenericSportsMatchScraper
import csv
from datetime import datetime

scraper = GenericSportsMatchScraper()
matches = scraper.scrape_matches_from_url('https://example.com/schedule')

# Filtrer les matchs à venir
today = datetime.now().date()
upcoming = []
for match in matches:
    if match.date:
        try:
            match_date = datetime.strptime(match.date, '%Y-%m-%d').date()
            if match_date >= today:
                upcoming.append(match)
        except:
            pass

print(f"{len(upcoming)} matchs à venir")

# Export personnalisé avec seulement certains champs
with open('upcoming_matches.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Date', 'Heure', 'Domicile', 'Extérieur', 'Lieu'])

    for match in upcoming:
        writer.writerow([
            match.date,
            match.time,
            match.home_team,
            match.away_team,
            match.venue
        ])

print("Export personnalisé terminé!")
```

### Exemple 5: Monitoring automatique

```python
from generic_sports_scraper import GenericSportsMatchScraper
import time
from datetime import datetime

def monitor_matches(url, interval_minutes=60):
    """
    Monitore une page et détecte les nouveaux matchs
    """
    scraper = GenericSportsMatchScraper()
    seen_matches = set()

    while True:
        print(f"\n[{datetime.now()}] Checking for new matches...")

        matches = scraper.scrape_matches_from_url(url)

        # Identifier les nouveaux matchs
        new_matches = []
        for match in matches:
            match_key = (match.date, match.home_team, match.away_team)
            if match_key not in seen_matches:
                seen_matches.add(match_key)
                new_matches.append(match)

        if new_matches:
            print(f"🆕 {len(new_matches)} nouveau(x) match(s) détecté(s)!")
            for match in new_matches:
                print(f"  - {match.home_team} vs {match.away_team} ({match.date})")

            # Export des nouveaux matchs
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scraper.export_to_csv(new_matches, f'new_matches_{timestamp}.csv')
        else:
            print("Aucun nouveau match")

        # Attendre avant le prochain check
        print(f"Prochain check dans {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

# Lancer le monitoring
monitor_matches('https://example.com/live-schedule', interval_minutes=30)
```

---

## ⚙️ Configuration Avancée

### Paramètres du Scraper

```python
scraper = GenericSportsMatchScraper(
    rate_limit=1.5,      # Délai minimum entre requêtes (secondes)
    max_retries=3        # Nombre de tentatives en cas d'échec
)
```

### Rate Limiting Personnalisé

```python
# Rate limiting agressif (scraping rapide - risqué)
scraper = GenericSportsMatchScraper(rate_limit=0.5)

# Rate limiting conservateur (scraping lent - sûr)
scraper = GenericSportsMatchScraper(rate_limit=3.0)

# Rate limiting adaptatif
import random
scraper = GenericSportsMatchScraper(
    rate_limit=random.uniform(1.0, 2.5)  # Variable entre 1 et 2.5s
)
```

### Headers Personnalisés

```python
scraper = GenericSportsMatchScraper()

# Modifier les headers
scraper.headers['User-Agent'] = 'Mon Bot Personnalisé/1.0'
scraper.headers['Accept-Language'] = 'fr-FR'
```

### Ajouter des Patterns Personnalisés

```python
scraper = GenericSportsMatchScraper()

# Ajouter un pattern de date personnalisé
scraper.match_patterns['date'].append(r'\d{2}\.\d{2}\.\d{4}')  # Format DD.MM.YYYY

# Ajouter des mots-clés pour la découverte de calendriers
scraper.calendar_keywords.extend(['planning', 'horaires', 'rencontres'])
```

### Logging Avancé

```python
import logging

# Mode debug complet
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Ou mode silencieux
logging.getLogger('generic_sports_scraper').setLevel(logging.ERROR)
```

---

## 🔧 API Programmatique

### Classes Principales

#### GenericSportsMatchScraper

```python
class GenericSportsMatchScraper:
    def __init__(self, rate_limit: float = 1.5, max_retries: int = 3):
        """Initialise le scraper"""

    def discover_calendars(self, base_url: str, max_depth: int = 3) -> List[Calendar]:
        """Découvre tous les calendriers depuis une URL"""

    def scrape_matches_from_url(self, url: str) -> List[Match]:
        """Scrape tous les matchs depuis une URL"""

    def scrape_all_calendars(self, base_url: str, max_depth: int = 3) -> Dict[str, List[Match]]:
        """Découvre et scrape tous les calendriers (tout-en-un)"""

    def export_to_csv(self, matches: List[Match], filename: str, include_metadata: bool = True):
        """Exporte les matchs vers un fichier CSV"""

    def export_calendars_to_csv(self, calendars: List[Calendar], output_dir: str = 'output'):
        """Exporte chaque calendrier dans un fichier CSV séparé"""
```

#### Match (Dataclass)

```python
@dataclass
class Match:
    # Voir section "Format des Données" pour tous les champs

    def to_dict(self) -> Dict:
        """Convertit le match en dictionnaire pour export CSV"""
```

#### Calendar (Dataclass)

```python
@dataclass
class Calendar:
    calendar_id: Optional[str]
    name: Optional[str]
    url: str
    sport: Optional[str]
    season: Optional[str]
    division: Optional[str]
    matches: List[Match]
    discovered_at: Optional[str]
```

### Méthodes Internes (Avancé)

Si vous voulez étendre le scraper:

```python
# Ajouter une stratégie d'extraction personnalisée
def my_custom_extraction(soup: BeautifulSoup, url: str) -> List[Match]:
    matches = []
    # Votre logique ici
    return matches

# Injecter dans le scraper
scraper._extract_from_custom = my_custom_extraction
```

---

## 🐛 Troubleshooting

### Problème: Aucun match trouvé

**Causes possibles:**
1. La structure de la page n'est pas reconnue
2. Les matchs sont chargés dynamiquement (JavaScript)
3. L'URL ne contient pas de matchs

**Solutions:**
```python
# 1. Activer le mode debug
import logging
logging.getLogger().setLevel(logging.DEBUG)

# 2. Inspecter la page manuellement
import requests
from bs4 import BeautifulSoup

response = requests.get('https://example.com')
soup = BeautifulSoup(response.content, 'lxml')
print(soup.prettify())  # Voir la structure HTML

# 3. Essayer une URL plus spécifique
# Au lieu de /sports, essayer /sports/schedule ou /sports/matches
```

### Problème: Blocage par le site (403, 429)

**Causes:**
- Rate limiting trop agressif
- Headers suspects
- IP bloquée

**Solutions:**
```python
# 1. Augmenter le rate limit
scraper = GenericSportsMatchScraper(rate_limit=3.0)

# 2. Modifier le User-Agent
scraper.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'

# 3. Ajouter des délais aléatoires
import random
import time
scraper.rate_limit = random.uniform(2.0, 4.0)

# 4. Utiliser un proxy (nécessite configuration requests)
proxies = {'http': 'http://proxy:port', 'https': 'http://proxy:port'}
# Modifier _make_request pour utiliser proxies=proxies
```

### Problème: Données incomplètes ou erronées

**Causes:**
- Structure HTML complexe
- Données dans un format non standard
- Caractères spéciaux mal encodés

**Solutions:**
```python
# 1. Vérifier l'encodage
scraper = GenericSportsMatchScraper()
response = scraper._make_request('https://example.com')
print(response.encoding)  # Doit être 'utf-8'

# 2. Inspecter les matchs extraits
matches = scraper.scrape_matches_from_url('https://example.com')
for match in matches[:5]:  # Premiers matchs seulement
    print(f"Match: {match}")
    print(f"  Home: {match.home_team}")
    print(f"  Away: {match.away_team}")
    print(f"  Date: {match.date}")
    print()

# 3. Ajouter des patterns personnalisés (voir Configuration Avancée)
```

### Problème: Trop de calendriers découverts

**Cause:** La profondeur de crawling est trop élevée

**Solution:**
```python
# Réduire max_depth
calendars = scraper.discover_calendars('https://example.com', max_depth=2)

# Ou filtrer manuellement
calendars = scraper.discover_calendars('https://example.com', max_depth=3)
filtered = [cal for cal in calendars if 'schedule' in cal.url.lower()]
```

### Problème: Erreur "Connection timeout"

**Causes:**
- Site lent
- Problème réseau
- Site down

**Solutions:**
```python
# 1. Augmenter le timeout
import requests

# Modifier la méthode _make_request
scraper = GenericSportsMatchScraper()
# Dans le code source, changer timeout=30 à timeout=60

# 2. Augmenter max_retries
scraper = GenericSportsMatchScraper(max_retries=5)

# 3. Vérifier la connectivité
import requests
try:
    response = requests.get('https://example.com', timeout=10)
    print(f"Status: {response.status_code}")
except requests.exceptions.Timeout:
    print("Timeout - le site est trop lent")
except requests.exceptions.ConnectionError:
    print("Connection error - vérifier votre réseau")
```

---

## ✅ Bonnes Pratiques

### 1. Respecter les Sites Web

```python
# ✅ BON: Rate limiting approprié
scraper = GenericSportsMatchScraper(rate_limit=1.5)

# ❌ MAUVAIS: Pas de rate limiting
scraper = GenericSportsMatchScraper(rate_limit=0.1)
```

### 2. Vérifier robots.txt

```python
import requests
from urllib.parse import urljoin, urlparse

def check_robots_txt(url):
    """Vérifie si le scraping est autorisé"""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    response = requests.get(robots_url)
    print(response.text)

check_robots_txt('https://example.com')
```

### 3. Gérer les Erreurs Gracieusement

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper()

urls = [
    'https://example.com/matches1',
    'https://example.com/matches2',
    'https://example.com/matches3',
]

all_matches = []
for url in urls:
    try:
        matches = scraper.scrape_matches_from_url(url)
        all_matches.extend(matches)
        print(f"✓ {url}: {len(matches)} matchs")
    except Exception as e:
        print(f"✗ {url}: Erreur - {e}")
        continue  # Continuer avec les autres URLs

print(f"\nTotal: {len(all_matches)} matchs extraits")
```

### 4. Logger les Activités

```python
import logging
from datetime import datetime

# Créer un log file avec timestamp
log_filename = f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Début du scraping")

# Votre code ici

logger.info("Fin du scraping")
```

### 5. Valider les Données

```python
def validate_match(match):
    """Vérifie qu'un match a des données minimales"""
    if not match.home_team and not match.away_team:
        return False
    if not match.date and not match.datetime_iso:
        return False
    return True

# Utilisation
matches = scraper.scrape_matches_from_url('https://example.com')
valid_matches = [m for m in matches if validate_match(m)]

print(f"Matchs extraits: {len(matches)}")
print(f"Matchs valides: {len(valid_matches)}")
print(f"Matchs rejetés: {len(matches) - len(valid_matches)}")
```

### 6. Sauvegarder Régulièrement

```python
from generic_sports_scraper import GenericSportsMatchScraper
import os
from datetime import datetime

scraper = GenericSportsMatchScraper(rate_limit=1.5)
calendars = scraper.discover_calendars('https://example.com', max_depth=3)

# Créer un répertoire avec timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = f'output_{timestamp}'
os.makedirs(output_dir, exist_ok=True)

# Scraper et sauvegarder après chaque calendrier
for i, calendar in enumerate(calendars):
    print(f"Scraping {i+1}/{len(calendars)}: {calendar.name}")

    matches = scraper.scrape_matches_from_url(calendar.url)
    calendar.matches = matches

    # Sauvegarder immédiatement
    filename = f"{output_dir}/calendar_{i+1}.csv"
    scraper.export_to_csv(matches, filename)
    print(f"  ✓ Sauvegardé: {filename}")

print(f"\n✓ Tous les calendriers sauvegardés dans {output_dir}/")
```

---

## 📜 Avertissements Légaux

### Conformité et Éthique

⚠️ **IMPORTANT**: L'utilisation de ce scraper est soumise aux conditions suivantes:

1. **Respectez les Terms of Service** des sites web
2. **Vérifiez robots.txt** avant de scraper
3. **Utilisez un rate limiting approprié** (minimum 1 seconde entre requêtes)
4. **Ne revendez pas** les données scrappées sans autorisation
5. **Respectez la vie privée** et les lois sur les données personnelles (RGPD, CCPA, etc.)
6. **Identifiez votre scraper** avec un User-Agent approprié
7. **Ne surchargez pas** les serveurs cibles

### Utilisation Recommandée

✅ **Autorisé:**
- Usage personnel et éducatif
- Recherche et analyse
- Agrégation de données publiques
- Tests et développement

❌ **Non recommandé:**
- Scraping agressif (< 1 req/sec)
- Contourner des protections anti-bot
- Revente de données
- Usage commercial sans autorisation
- Extraction de données personnelles

### Disclaimer

Ce logiciel est fourni **"tel quel"** sans garantie d'aucune sorte. Les auteurs ne sont pas responsables:
- Des dommages causés par l'utilisation du scraper
- Des violations de Terms of Service
- De la précision ou complétude des données extraites
- Des conséquences légales liées à un usage inapproprié

**Utilisez ce scraper de manière responsable et éthique.**

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer:

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Idées de Contributions

- 🌍 Support de sites web spécifiques
- 🔍 Nouvelles stratégies d'extraction
- 🧪 Tests unitaires
- 📖 Traductions de la documentation
- 🐛 Corrections de bugs
- ⚡ Optimisations de performance

---

## 📞 Support

Pour obtenir de l'aide:
- 📖 Consultez cette documentation
- 🐛 Ouvrez une issue sur GitHub
- 💬 Posez des questions dans les discussions

---

## 📝 License

Ce projet est fourni sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

## 🎉 Remerciements

Merci d'utiliser Generic Sports Match Scraper !

**Made with ❤️ for the sports data community**

---

**Version:** 1.0.0
**Date:** 2025-01-27
**Auteur:** Generic Sports Scraper Team
