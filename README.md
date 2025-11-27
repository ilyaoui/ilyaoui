# Sports Match Scrapers 🏆⚽🏀🏈

Collection complète de scrapers pour extraire les données sportives depuis différentes sources.

## 🎯 Outils Disponibles

### 1. **Generic Sports Match Scraper** (⭐ Nouveau!)
Un scraper **universel** qui peut extraire des matchs depuis **n'importe quel site web** de sports.
- ✅ Détection automatique de la structure des pages
- ✅ Support multi-sports (tous les sports)
- ✅ Découverte automatique des calendriers
- ✅ 5 stratégies d'extraction intelligentes
- ✅ Export CSV enrichi et organisé

👉 **[Documentation complète du Generic Scraper](./GENERIC_SCRAPER_README.md)**

**Démarrage rapide:**
```bash
# Interface interactive
python interactive_scraper.py

# Ligne de commande
python generic_sports_scraper.py "https://example.com/matches" --single-page
```

---

### 2. **NFL Flag Tournaments Scraper**
Un scraper spécialisé pour extraire les données des équipes et organisations de l'application **NFL Flag Tournaments** (powered by TeamSnap).
- ✅ Mode API TeamSnap (authentification OAuth2)
- ✅ Mode Web Scraping (sans authentification)
- ✅ Support BlueSombrero
- ✅ Export CSV et JSON

---

## 📋 Table des Matières (NFL Flag Scraper)

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Modes de Scraping](#modes-de-scraping)
- [Structure des Données](#structure-des-données)
- [Exemples](#exemples)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Avertissements Légaux](#avertissements-légaux)

## ✨ Fonctionnalités

### Mode API TeamSnap
- ✅ Authentification OAuth2 complète
- ✅ Récupération des équipes
- ✅ Accès aux divisions
- ✅ Extraction des membres d'équipe
- ✅ Informations sur les emplacements
- ✅ Export CSV et JSON

### Mode Web Scraping
- ✅ Découverte automatique d'événements NFL Flag
- ✅ Scraping de pages de tournois
- ✅ Support BlueSombrero
- ✅ Extraction de tables HTML
- ✅ Découverte d'APIs non documentées
- ✅ Rate limiting configurable
- ✅ Export enrichi en CSV

## 🏗️ Architecture

```
NFL Flag Tournaments App
    ↓
TeamSnap Infrastructure
    ↓
    ├── API TeamSnap v3 (api.teamsnap.com)
    ├── TeamSnap Tournaments (tournaments.teamsnap.com)
    └── BlueSombrero (leagues.bluesombrero.com)
```

### Fichiers du Projet

```
ilyaoui/
# Scraper Générique (Nouveau!)
├── generic_sports_scraper.py    # Scraper universel pour tous les sports
├── interactive_scraper.py       # Interface interactive conviviale
├── GENERIC_SCRAPER_README.md    # Documentation complète du scraper générique

# Scraper NFL Flag
├── nfl_flag_scraper.py          # Scraper principal (API + Web)
├── advanced_scraper.py          # Scraper avancé avec BeautifulSoup
├── oauth_helper.py              # Utilitaire OAuth2 pour TeamSnap
├── quick_start.py               # Menu de démarrage rapide

# Documentation et Configuration
├── README.md                    # Cette documentation
├── requirements.txt             # Dépendances Python
├── config.example.json          # Template de configuration OAuth
├── .env.example                 # Template variables d'environnement
├── config.json                  # Configuration (généré après OAuth)
└── .env                         # Variables d'environnement (optionnel)
```

## 📦 Installation

### 1. Cloner le Repository

```bash
git clone <repo-url>
cd ilyaoui
```

### 2. Créer un Environnement Virtuel (Recommandé)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### Dépendances

- `requests>=2.31.0` - Requêtes HTTP
- `beautifulsoup4>=4.12.0` - Parsing HTML
- `lxml>=4.9.0` - Parser XML/HTML rapide
- `python-dotenv>=1.0.0` - Gestion des variables d'environnement

## ⚙️ Configuration

### Option 1: API TeamSnap (Authentification Requise)

#### Étape 1: Obtenir des Credentials

1. Contactez TeamSnap Developer Support:
   - Email: api@teamsnap.com
   - Site: https://www.teamsnap.com/documentation/apiv3

2. Demandez:
   - Client ID
   - Client Secret

#### Étape 2: Obtenir un Access Token

```bash
python oauth_helper.py
```

Suivez le processus interactif:
1. Entrez votre Client ID et Client Secret
2. Ouvrez l'URL d'autorisation dans votre navigateur
3. Connectez-vous et autorisez l'application
4. Copiez le code d'autorisation
5. Le script l'échangera contre un Access Token

Le fichier `config.json` sera créé automatiquement:

```json
{
  "client_id": "votre_client_id",
  "client_secret": "votre_client_secret",
  "access_token": "votre_access_token",
  "refresh_token": "votre_refresh_token",
  "expires_in": 7200
}
```

#### Étape 3: Tester le Token

```bash
python oauth_helper.py test
```

### Option 2: Web Scraping (Sans Authentification)

Aucune configuration requise ! Le scraper web fonctionne sans authentification.

## 🚀 Utilisation

### Mode 1: Scraper Principal

```bash
python nfl_flag_scraper.py
```

Menu interactif:
- **Mode 1**: API TeamSnap (nécessite token)
- **Mode 2**: Web Scraping (pas d'auth)

### Mode 2: Scraper Avancé

```bash
python advanced_scraper.py
```

Options:
1. **Découvrir les événements NFL Flag**
   - Scrape https://nflflag.com/events
   - Trouve tous les tournois disponibles

2. **Scraper un tournoi spécifique**
   - Entrez une URL de tournoi
   - Extrait équipes, divisions, horaires

3. **Scraper BlueSombrero**
   - Entrez un ID de tournoi (tabid)
   - Format: `https://leagues.bluesombrero.com/Default.aspx?tabid=XXXXX`

## 🔍 Modes de Scraping

### API TeamSnap

**Avantages:**
- ✅ Données structurées et complètes
- ✅ Accès à toutes les ressources
- ✅ Mises à jour en temps réel
- ✅ Support officiel

**Inconvénients:**
- ❌ Nécessite authentification OAuth2
- ❌ Limites de rate limiting
- ❌ Accès limité selon les permissions

**Exemple:**

```python
from nfl_flag_scraper import TeamSnapAPIClient

client = TeamSnapAPIClient(access_token="votre_token")

# Récupérer les équipes
teams = client.get_teams()

# Récupérer les divisions
divisions = client.get_divisions()

# Membres d'une équipe
members = client.get_team_members(team_id=12345)
```

### Web Scraping

**Avantages:**
- ✅ Pas d'authentification requise
- ✅ Accès aux données publiques
- ✅ Flexible et adaptable

**Inconvénients:**
- ❌ Données potentiellement incomplètes
- ❌ Fragile (dépend de la structure HTML)
- ❌ Plus lent

**Exemple:**

```python
from advanced_scraper import AdvancedNFLFlagScraper

scraper = AdvancedNFLFlagScraper(rate_limit=1.5)

# Découvrir les événements
events = scraper.discover_nfl_flag_events()

# Scraper un tournoi
tournament = scraper.scrape_tournament_page("https://nflflag.com/events/patriots")

# Export CSV
scraper.export_enriched_csv(tournament['teams'], "teams.csv")
```

## 📊 Structure des Données

### Format des Équipes (CSV)

```csv
team_name,team_id,organization,coach,division,division_id,location,city,state,roster_size,wins,losses,url,scraped_at
Patriots U12,12345,Boston Youth Sports,John Doe,U12 Division,67,Gillette Stadium,Foxborough,MA,10,5,2,https://...,2025-01-15T10:30:00
```

### Format JSON (API)

```json
{
  "collection": {
    "items": [
      {
        "data": [
          {"name": "id", "value": 12345},
          {"name": "name", "value": "Patriots U12"},
          {"name": "division_id", "value": 67},
          {"name": "division_name", "value": "U12 Division"}
        ],
        "links": [
          {"rel": "self", "href": "https://api.teamsnap.com/v3/teams/12345"}
        ]
      }
    ]
  }
}
```

## 💡 Exemples

### Exemple 1: Scraper tous les tournois de 2025

```python
from advanced_scraper import AdvancedNFLFlagScraper
import json

scraper = AdvancedNFLFlagScraper()

# Découvrir les événements
events = scraper.discover_nfl_flag_events()

all_tournaments = []
for event in events:
    if 'url' in event:
        tournament = scraper.scrape_tournament_page(event['url'])
        all_tournaments.append(tournament)

# Sauvegarder
with open('all_tournaments_2025.json', 'w') as f:
    json.dump(all_tournaments, f, indent=2)
```

### Exemple 2: Exporter toutes les équipes d'une division

```python
from nfl_flag_scraper import TeamSnapAPIClient, NFLFlagDataExporter

client = TeamSnapAPIClient(access_token="votre_token")

# Récupérer les équipes d'une division spécifique
divisions = client.get_divisions()

for division in divisions:
    division_id = division['data'][0]['value']  # ID de la division
    teams = client.get_teams()  # Filtrer par division

    # Export CSV
    filename = f"division_{division_id}_teams.csv"
    NFLFlagDataExporter.export_to_csv(teams, filename)
```

### Exemple 3: Statistiques par organisation

```python
from advanced_scraper import AdvancedNFLFlagScraper
import csv
from collections import Counter

scraper = AdvancedNFLFlagScraper()
tournament = scraper.scrape_tournament_page("https://nflflag.com/events/patriots")

# Compter les équipes par organisation
orgs = Counter(team.get('organization', 'Unknown') for team in tournament['teams'])

print("Équipes par organisation:")
for org, count in orgs.most_common():
    print(f"  {org}: {count} équipes")
```

## 📚 API Documentation

### TeamSnap API v3

**Base URL:** `https://api.teamsnap.com/v3`

**Format:** Collection+JSON

**Endpoints Principaux:**

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/me` | GET | Utilisateur actuel |
| `/teams` | GET | Liste des équipes |
| `/teams/{id}` | GET | Détails d'une équipe |
| `/teams/{id}/members` | GET | Membres d'une équipe |
| `/divisions` | GET | Liste des divisions |
| `/divisions/{id}` | GET | Détails d'une division |
| `/divisions/{id}/locations` | GET | Emplacements d'une division |

**Headers Requis:**

```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
```

### Rate Limiting

- **API TeamSnap:** Non documenté officiellement, recommandé 1-2 req/sec
- **Web Scraping:** 1-2 secondes entre requêtes (configurable)

## 🐛 Troubleshooting

### Erreur: "403 Forbidden"

**Cause:** Le site bloque les requêtes automatisées

**Solutions:**
1. Utilisez le mode API avec authentification
2. Ajoutez un délai entre les requêtes (rate limiting)
3. Modifiez le User-Agent
4. Utilisez un proxy

### Erreur: "Invalid token"

**Cause:** Le token OAuth2 a expiré

**Solution:**
```bash
python oauth_helper.py test
```
Le script tentera de rafraîchir le token automatiquement.

### Aucune donnée extraite

**Cause:** La structure HTML a changé

**Solution:**
1. Inspectez manuellement la page web
2. Mettez à jour les sélecteurs CSS/XPath dans `advanced_scraper.py`
3. Utilisez le mode API si disponible

### Erreur de dépendances

```bash
pip install --upgrade -r requirements.txt
```

## ⚖️ Avertissements Légaux

### Conformité

- ✅ **Respectez les Terms of Service** de TeamSnap et NFL Flag
- ✅ **Rate Limiting:** Utilisez des délais entre les requêtes
- ✅ **Données personnelles:** Respectez le RGPD et les lois sur la vie privée
- ❌ **Ne pas:** Revendre les données scrappées
- ❌ **Ne pas:** Surcharger les serveurs

### Utilisation Responsable

Ce scraper est fourni **à des fins éducatives et de recherche uniquement**.

**Recommandations:**
1. Contactez TeamSnap pour un accès API officiel
2. Limitez le scraping aux données publiques
3. Respectez le fichier `robots.txt`
4. Utilisez un User-Agent identifiable

### Robots.txt

Vérifiez toujours:
- https://nflflag.com/robots.txt
- https://teamsnap.com/robots.txt
- https://leagues.bluesombrero.com/robots.txt

## 📞 Support

### TeamSnap API Support

- **Email:** api@teamsnap.com
- **Documentation:** https://www.teamsnap.com/documentation/apiv3
- **GitHub:** https://github.com/teamsnap

### NFL Flag

- **Site Web:** https://nflflag.com
- **Email:** info@nflflag.com
- **Téléphone:** 1-844-940-1005

## 📝 License

Ce projet est fourni "tel quel" sans garantie. Utilisez-le à vos propres risques.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📋 TODO

- [ ] Support pour les tournois en temps réel
- [ ] Cache des requêtes API
- [ ] Interface web (Flask/FastAPI)
- [ ] Support pour d'autres sports
- [ ] Base de données SQLite intégrée
- [ ] Monitoring et alertes
- [ ] Docker containerization

## 📈 Changelog

### Version 1.0.0 (2025-01-15)

- ✨ Scraper initial avec support API et Web
- ✨ OAuth2 helper pour TeamSnap
- ✨ Export CSV et JSON
- ✨ Documentation complète

---

**Made with 🏈 for NFL Flag Community**
