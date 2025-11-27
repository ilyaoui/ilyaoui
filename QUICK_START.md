# 🚀 Quick Start - Sports Match Scrapers

Démarrage rapide pour scraper des matchs sportifs depuis n'importe quel site web.

---

## 📋 Fichiers Disponibles

### 🎯 Scraper Universel (Tous les Sports)

| Fichier | Description | Usage |
|---------|-------------|-------|
| **`generic_sports_scraper.py`** | Scraper universel avec 5 stratégies | Ligne de commande |
| **`interactive_scraper.py`** | Interface interactive conviviale | **⭐ Recommandé pour débuter** |
| **`GENERIC_SCRAPER_README.md`** | Documentation complète (1200 lignes) | Référence |

### ⚽ Scraper ECNL Spécialisé

| Fichier | Description | Usage |
|---------|-------------|-------|
| **`scrape_ecnl.py`** | Scraper optimisé pour theecnl.com | Simple et direct |
| **`test_ecnl_demo.py`** | Démonstration avec données simulées | Test sans connexion |
| **`GUIDE_ECNL_SCRAPING.md`** | Guide complet pour ECNL | Référence ECNL |

### 🏈 Scraper NFL Flag

| Fichier | Description | Usage |
|---------|-------------|-------|
| `nfl_flag_scraper.py` | API TeamSnap + Web scraping | NFL Flag |
| `advanced_scraper.py` | Scraper avancé BeautifulSoup | NFL Flag |
| `oauth_helper.py` | OAuth2 pour TeamSnap API | Configuration |

---

## ⚡ Démarrage Rapide (30 secondes)

### Option 1 : Interface Interactive (Recommandé 🌟)

```bash
python interactive_scraper.py
```

**Interface conviviale avec menu** :
1. Scraper une page unique
2. Découvrir tous les calendriers
3. Mode avancé
4. Exemples
5. Aide

### Option 2 : Ligne de Commande

**Scraper une page :**
```bash
python generic_sports_scraper.py "https://example.com/matches" --single-page
```

**Découvrir tous les calendriers :**
```bash
python generic_sports_scraper.py "https://example.com/sports" --depth 3
```

### Option 3 : Script Python

```python
from generic_sports_scraper import GenericSportsMatchScraper

scraper = GenericSportsMatchScraper()
matches = scraper.scrape_matches_from_url('https://example.com/matches')
scraper.export_to_csv(matches, 'output/matches.csv')

print(f"{len(matches)} matchs extraits !")
```

---

## 🏆 Cas d'Usage Spécifiques

### Pour Scraper ECNL (theecnl.com)

```bash
# Méthode 1 : Script spécialisé
python scrape_ecnl.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"

# Méthode 2 : Scraper générique
python generic_sports_scraper.py "https://theecnl.com/..." --single-page

# Méthode 3 : Démonstration (sans connexion)
python test_ecnl_demo.py
```

👉 **Voir le guide complet** : `GUIDE_ECNL_SCRAPING.md`

### Pour Scraper NFL Flag

```bash
# Interface interactive
python quick_start.py

# Mode API (nécessite OAuth2)
python nfl_flag_scraper.py

# Mode Web (sans authentification)
python advanced_scraper.py
```

### Pour Scraper N'importe Quel Site

```bash
# Automatique avec découverte de calendriers
python generic_sports_scraper.py "https://votre-site.com" --depth 3 --rate-limit 2.0

# Page unique
python generic_sports_scraper.py "https://votre-site.com/matches" --single-page
```

---

## 📊 Exemples de Sites Supportés

Le scraper universel fonctionne avec :

- ⚽ **Soccer** : ECNL, MLS, Ligue 1, etc.
- 🏀 **Basketball** : NCAA, NBA calendars
- 🏈 **Football** : NFL Flag, NCAA, NFL
- ⚾ **Baseball** : MLB, ligues locales
- 🏐 **Volleyball** : Championnats, tournois
- 🎾 **Tennis** : Tournois
- ... **et plus encore** !

---

## 🎯 Que Fait le Scraper ?

### Extraction Automatique

Le scraper extrait **automatiquement** :

✅ Équipes (domicile/extérieur)
✅ Scores
✅ Dates et heures
✅ Lieux (stades, villes, états)
✅ Compétitions et divisions
✅ Status des matchs
✅ Métadonnées enrichies

### 5 Stratégies Intelligentes

Le scraper essaye **automatiquement** 5 stratégies :

1. **Tables HTML** - Parse les `<table>` avec headers
2. **Listes HTML** - Extrait depuis `<ul>`, `<ol>`
3. **Divs Structurées** - Cherche des divs avec classes "match", "game"
4. **JSON-LD** - Parse les structured data (schema.org)
5. **JSON Embedded** - Extrait le JSON dans JavaScript

### Format de Sortie

**Fichiers CSV enrichis** avec jusqu'à **27 colonnes** :

```csv
match_id,sport,date,time,home_team,away_team,home_score,away_score,status,venue,city,state,competition,division,season,source_url,scraped_at,...
```

---

## ⚙️ Installation

### Prérequis

```bash
# Python 3.7+
python3 --version

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances

- `requests` - Client HTTP
- `beautifulsoup4` - Parser HTML
- `lxml` - Backend rapide
- `python-dotenv` - Variables d'environnement

---

## 🔧 Configuration

### Rate Limiting (Recommandé)

Pour éviter d'être bloqué :

```python
# Recommandé : 1.5 - 2.5 secondes entre requêtes
scraper = GenericSportsMatchScraper(rate_limit=2.0)
```

### Headers Personnalisés

Si un site bloque :

```python
scraper = GenericSportsMatchScraper()
scraper.headers['User-Agent'] = 'Mozilla/5.0 ...'
scraper.headers['Referer'] = 'https://example.com'
```

### Désactiver le Proxy

Si vous avez des erreurs de proxy :

```python
import os
os.environ['NO_PROXY'] = '*'
```

---

## 📖 Documentation Complète

| Document | Description | Taille |
|----------|-------------|--------|
| **`GENERIC_SCRAPER_README.md`** | Guide complet du scraper universel | 1200 lignes |
| **`GUIDE_ECNL_SCRAPING.md`** | Guide spécifique ECNL | 400 lignes |
| **`README.md`** | Documentation du projet | 500 lignes |
| **`QUICK_START.md`** | Ce guide (démarrage rapide) | Vous êtes ici |

---

## 💡 Tips & Astuces

### 1. Commencer Simple

```bash
# Test rapide avec interface
python interactive_scraper.py
```

### 2. Vérifier avant de Scraper

```bash
# Voir les options disponibles
python generic_sports_scraper.py --help
```

### 3. Tester avec Verbose

```bash
# Mode debug pour voir ce qui se passe
python generic_sports_scraper.py "URL" --verbose
```

### 4. Sauvegarder Régulièrement

```python
# Sauvegarder après chaque calendrier
for calendar in calendars:
    matches = scraper.scrape_matches_from_url(calendar.url)
    scraper.export_to_csv(matches, f'output/calendar_{i}.csv')
```

### 5. Gérer les Erreurs

```python
try:
    matches = scraper.scrape_matches_from_url(url)
except Exception as e:
    print(f"Erreur: {e}")
    # Continuer avec la prochaine URL
```

---

## 🐛 Troubleshooting Rapide

### Problème : Aucun match trouvé

**Cause** : La structure de la page n'est pas reconnue

**Solution** :
```bash
# Mode verbose pour voir les détails
python generic_sports_scraper.py "URL" --verbose
```

### Problème : 403 Forbidden / Proxy Error

**Cause** : Site bloque ou problème de proxy

**Solution** :
```python
import os
os.environ['NO_PROXY'] = '*'
# Puis lancer le scraper
```

### Problème : Trop lent

**Cause** : Rate limiting trop élevé

**Solution** :
```python
# Réduire le rate limit (attention aux blocages)
scraper = GenericSportsMatchScraper(rate_limit=1.0)
```

### Problème : Données incomplètes

**Cause** : Structure HTML complexe

**Solution** : Consulter `GENERIC_SCRAPER_README.md` section "Configuration Avancée"

---

## ✅ Checklist de Démarrage

- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Testé l'interface interactive (`python interactive_scraper.py`)
- [ ] Testé un scraping simple (`python generic_sports_scraper.py "URL" --single-page`)
- [ ] Lu la documentation (`GENERIC_SCRAPER_README.md`)
- [ ] Configuré le rate limiting (≥ 1.5s)
- [ ] Vérifié les fichiers CSV générés

---

## 🎉 Prêt à Commencer !

### 3 Commandes pour Démarrer

```bash
# 1. Interface interactive (recommandé)
python interactive_scraper.py

# 2. Test ECNL avec démo
python test_ecnl_demo.py

# 3. Scraping réel d'une page
python generic_sports_scraper.py "https://votre-url.com/matches" --single-page
```

---

## 📞 Besoin d'Aide ?

- 📖 **Documentation complète** : `GENERIC_SCRAPER_README.md`
- 🏆 **Guide ECNL** : `GUIDE_ECNL_SCRAPING.md`
- 💻 **Interface interactive** : `python interactive_scraper.py` → Option 5 (Aide)
- 🐛 **Troubleshooting** : Voir section correspondante dans les docs

---

**Bon scraping ! 🚀**

---

*Dernière mise à jour : 2025-11-27*
