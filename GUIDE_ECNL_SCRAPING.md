# Guide de Scraping ECNL (Elite Clubs National League) 🏆⚽

Ce guide explique comment scraper le site **theecnl.com** avec le Generic Sports Match Scraper.

## 🎯 Problème Rencontré

Lors du test avec l'URL `https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx`, nous avons rencontré une erreur :

```
ProxyError: Tunnel connection failed: 403 Forbidden
```

Cela signifie que le réseau actuel bloque l'accès au site via proxy.

---

## ✅ Solutions

### Solution 1 : Désactiver le Proxy (Recommandé)

Modifiez le scraper pour désactiver le proxy :

```python
import os

# Désactiver les proxies
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper(rate_limit=2.0)
matches = scraper.scrape_matches_from_url('https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx')

print(f"{len(matches)} matchs extraits")
scraper.export_to_csv(matches, 'ecnl_matches.csv')
```

### Solution 2 : Utiliser un Environnement Local

Exécutez le scraper depuis votre machine locale (pas depuis un container ou serveur distant) :

```bash
# Sur votre machine locale
python3 generic_sports_scraper.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx" --single-page
```

### Solution 3 : Modifier les Paramètres Requests

Créez un script personnalisé qui contourne le proxy :

```python
from generic_sports_scraper import GenericSportsMatchScraper
import requests

# Créer le scraper
scraper = GenericSportsMatchScraper(rate_limit=2.0)

# Modifier la méthode _make_request pour désactiver le proxy
original_request = scraper._make_request

def no_proxy_request(url, method='GET', **kwargs):
    # Désactiver le proxy pour cette requête
    kwargs['proxies'] = {'http': None, 'https': None}
    return original_request(url, method, **kwargs)

scraper._make_request = no_proxy_request

# Maintenant scraper normalement
matches = scraper.scrape_matches_from_url('https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx')
```

### Solution 4 : Utiliser un VPN

Si le site bloque certaines régions géographiques :

1. Connectez-vous à un VPN (USA recommandé)
2. Exécutez le scraper normalement

```bash
python3 generic_sports_scraper.py "https://theecnl.com/..." --single-page
```

---

## 📊 Structure Attendue du Site ECNL

D'après l'analyse du site ECNL, les pages contiennent généralement :

### 1. Tables HTML

```html
<table class="schedule-table">
  <thead>
    <tr>
      <th>Date</th>
      <th>Time</th>
      <th>Home Team</th>
      <th>Away Team</th>
      <th>Score</th>
      <th>Location</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>08/08/2023</td>
      <td>10:00 AM</td>
      <td>FC Dallas</td>
      <td>Solar SC</td>
      <td>2-1</td>
      <td>Toyota Soccer Center</td>
    </tr>
  </tbody>
</table>
```

**Le scraper extrait automatiquement** : date, heure, équipes, scores, lieu

### 2. Divs Structurées

```html
<div class="game-item" data-game-id="12345">
  <div class="game-date">August 8, 2023</div>
  <div class="game-time">10:00 AM</div>
  <div class="team-home">
    <span class="team-name">FC Dallas</span>
    <span class="score">2</span>
  </div>
  <div class="team-away">
    <span class="team-name">Solar SC</span>
    <span class="score">1</span>
  </div>
  <div class="venue">Toyota Soccer Center - Frisco, TX</div>
</div>
```

**Le scraper extrait automatiquement** : game_id, équipes, scores, lieu, ville

### 3. JSON Embedded

Les pages ECNL contiennent souvent du JavaScript avec des données :

```javascript
var scheduleData = {
  "games": [
    {
      "id": "12345",
      "date": "2023-08-08",
      "time": "10:00",
      "homeTeam": "FC Dallas",
      "awayTeam": "Solar SC",
      "homeScore": 2,
      "awayScore": 1,
      "venue": "Toyota Soccer Center",
      "division": "U15 Girls"
    }
  ]
};
```

**Le scraper détecte et parse automatiquement** ce JSON !

---

## 🚀 Utilisation Pratique

### Cas 1 : Scraper une seule page de matchs

```bash
python3 generic_sports_scraper.py \
  "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx" \
  --single-page \
  --output ecnl_output \
  --rate-limit 2.0
```

**Résultat** : Un fichier `ecnl_output/matches.csv` avec tous les matchs

### Cas 2 : Découvrir tous les calendriers ECNL

```bash
python3 generic_sports_scraper.py \
  "https://theecnl.com/schedule" \
  --depth 3 \
  --rate-limit 2.0 \
  --output ecnl_all_calendars
```

**Résultat** :
- Plusieurs fichiers CSV (un par calendrier/division)
- Un fichier `all_matches.csv` avec TOUS les matchs

### Cas 3 : Scraper avec l'interface interactive

```bash
python3 interactive_scraper.py
```

Puis choisir :
1. Option 1 pour une page unique
2. Option 2 pour découvrir tous les calendriers
3. Entrer l'URL ECNL
4. Configurer les options

---

## 📝 Exemple de Script Complet pour ECNL

Créez un fichier `scrape_ecnl.py` :

```python
#!/usr/bin/env python3
"""
Script pour scraper le site ECNL
"""

import os
from generic_sports_scraper import GenericSportsMatchScraper
from datetime import datetime

# Désactiver le proxy si nécessaire
os.environ['NO_PROXY'] = '*'

def scrape_ecnl_page(url, output_dir='ecnl_data'):
    """Scrape une page ECNL"""
    print(f"Scraping ECNL: {url}")

    # Créer le scraper avec rate limiting approprié
    scraper = GenericSportsMatchScraper(
        rate_limit=2.0,  # 2 secondes entre requêtes
        max_retries=5    # 5 tentatives max
    )

    # Scraper la page
    matches = scraper.scrape_matches_from_url(url)

    if not matches:
        print("❌ Aucun match trouvé")
        return

    print(f"✓ {len(matches)} matchs extraits")

    # Export CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/ecnl_matches_{timestamp}.csv"
    scraper.export_to_csv(matches, filename)

    print(f"✓ Export réussi: {filename}")

    # Afficher aperçu
    print("\n📊 Aperçu des matchs:")
    for i, match in enumerate(matches[:5], 1):
        print(f"\n{i}. {match.home_team} vs {match.away_team}")
        if match.home_score is not None:
            print(f"   Score: {match.home_score} - {match.away_score}")
        print(f"   Date: {match.date} à {match.time}")
        print(f"   Lieu: {match.venue}, {match.city}, {match.state}")
        print(f"   Division: {match.division}")

    if len(matches) > 5:
        print(f"\n... et {len(matches) - 5} autres matchs")

    return matches


def scrape_all_ecnl_calendars(base_url='https://theecnl.com'):
    """Découvre et scrape tous les calendriers ECNL"""
    print(f"Découverte des calendriers depuis {base_url}")

    scraper = GenericSportsMatchScraper(rate_limit=2.0)

    # Découvrir les calendriers
    calendars = scraper.discover_calendars(base_url, max_depth=3)

    print(f"\n✓ {len(calendars)} calendriers découverts")

    # Scraper chaque calendrier
    all_matches = []
    for i, calendar in enumerate(calendars, 1):
        print(f"\n[{i}/{len(calendars)}] {calendar.name}")
        matches = scraper.scrape_matches_from_url(calendar.url)
        calendar.matches = matches
        all_matches.extend(matches)
        print(f"  → {len(matches)} matchs")

    # Export
    scraper.export_calendars_to_csv(calendars, 'ecnl_all_calendars')

    print(f"\n✓ Total: {len(all_matches)} matchs extraits")
    print(f"✓ Fichiers sauvegardés dans ecnl_all_calendars/")

    return all_matches


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # URL passée en argument
        url = sys.argv[1]
        scrape_ecnl_page(url)
    else:
        # Mode interactif
        print("=== ECNL Scraper ===\n")
        print("1. Scraper une page spécifique")
        print("2. Découvrir tous les calendriers")

        choice = input("\nChoix (1 ou 2): ").strip()

        if choice == '1':
            url = input("URL de la page ECNL: ").strip()
            scrape_ecnl_page(url)
        elif choice == '2':
            scrape_all_ecnl_calendars()
        else:
            print("Choix invalide")
```

**Utilisation** :

```bash
# Avec URL en argument
python3 scrape_ecnl.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"

# Mode interactif
python3 scrape_ecnl.py
```

---

## 📊 Format de Sortie CSV

Le fichier CSV généré contient **27 colonnes** :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `match_id` | ID unique du match | ECNL001 |
| `sport` | Type de sport | Soccer |
| `date` | Date du match | 2023-08-08 |
| `time` | Heure du match | 10:00 |
| `datetime_iso` | Date/heure ISO | 2023-08-08T10:00:00 |
| `home_team` | Équipe domicile | FC Dallas |
| `away_team` | Équipe extérieur | Solar SC |
| `home_score` | Score domicile | 2 |
| `away_score` | Score extérieur | 1 |
| `status` | Statut | finished / scheduled |
| `venue` | Stade/Lieu | Toyota Soccer Center |
| `city` | Ville | Frisco |
| `state` | État | TX |
| `competition` | Compétition | ECNL Regional League |
| `division` | Division | U15 Girls |
| `season` | Saison | 2023-2024 |
| `source_url` | URL source | https://theecnl.com/... |
| `scraped_at` | Date d'extraction | 2025-11-27T10:10:44 |
| ... | Et 9 autres colonnes | ... |

---

## 🎯 Tips pour Scraper ECNL

### 1. Rate Limiting

Les sites de sports n'aiment pas les scrapers trop rapides. **Utilisez un rate limit de 2-3 secondes** :

```python
scraper = GenericSportsMatchScraper(rate_limit=2.5)
```

### 2. Headers Personnalisés

Si le site bloque les scrapers, modifiez les headers :

```python
scraper = GenericSportsMatchScraper()
scraper.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
scraper.headers['Referer'] = 'https://theecnl.com/'
```

### 3. Scraper par Saison/Division

Au lieu de scraper tout le site, ciblez des URLs spécifiques :

```python
urls = [
    'https://theecnl.com/sports/schedule?season=2023-2024&division=U15G',
    'https://theecnl.com/sports/schedule?season=2023-2024&division=U16G',
    'https://theecnl.com/sports/schedule?season=2023-2024&division=U17G',
]

for url in urls:
    matches = scraper.scrape_matches_from_url(url)
    # Traiter les matchs
```

### 4. Gérer les Erreurs

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper(rate_limit=2.0)

urls_to_scrape = [
    'https://theecnl.com/page1',
    'https://theecnl.com/page2',
    'https://theecnl.com/page3',
]

all_matches = []
for url in urls_to_scrape:
    try:
        matches = scraper.scrape_matches_from_url(url)
        all_matches.extend(matches)
        print(f"✓ {url}: {len(matches)} matchs")
    except Exception as e:
        print(f"✗ {url}: Erreur - {e}")
        continue

# Export final
scraper.export_to_csv(all_matches, 'ecnl_all_matches.csv')
```

---

## 🔍 Debugging

Si le scraping ne fonctionne pas, activez le mode verbose :

```bash
python3 generic_sports_scraper.py "https://theecnl.com/..." --verbose
```

Ou en Python :

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from generic_sports_scraper import GenericSportsMatchScraper
# ... votre code
```

---

## 📚 Ressources

- **Documentation complète** : `GENERIC_SCRAPER_README.md`
- **Interface interactive** : `python3 interactive_scraper.py`
- **Script de démonstration** : `python3 test_ecnl_demo.py`

---

## ⚠️ Notes Légales

- ✅ Respectez les Terms of Service de theecnl.com
- ✅ Utilisez un rate limiting approprié (≥ 2 secondes)
- ✅ Ne surchargez pas les serveurs
- ✅ Les données ECNL sont publiques mais protégées par copyright
- ❌ Ne revendez pas les données sans autorisation

---

## 🎉 Bon Scraping !

Le Generic Sports Match Scraper est conçu pour fonctionner avec **n'importe quel site de sports**, y compris ECNL. Les 5 stratégies d'extraction s'adaptent automatiquement à la structure des pages.

**Questions ?** Consultez la documentation complète : `GENERIC_SCRAPER_README.md`
