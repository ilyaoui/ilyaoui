# Squadi Schedules Scraper

Scraper pour récupérer tous les schedules (calendriers) à venir depuis le site **registration.us.squadi.com**.

## 🚀 Installation

### 1. Installer les dépendances Python

```bash
pip install -r requirements_squadi.txt
```

### 2. Dépendances système (pour Selenium)

**Linux/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
- Téléchargez et installez Google Chrome depuis le site officiel

## 📖 Utilisation

### Mode interactif

```bash
python squadi_schedules_scraper.py
```

Le script vous proposera 4 méthodes :

1. **Auto** (recommandé) - Essaie toutes les méthodes automatiquement
2. **API directe** - Tente d'accéder directement aux endpoints API
3. **Requests/Cloudscraper** - Utilise cloudscraper pour contourner les protections
4. **Selenium** - Utilise un navigateur headless (plus lent mais plus fiable)

### Utilisation dans votre code Python

```python
from squadi_schedules_scraper import SquadiSchedulesScraper

# Créer le scraper
scraper = SquadiSchedulesScraper()

# Récupérer tous les schedules
schedules = scraper.run(method='auto')

# Afficher les résultats
for schedule in schedules:
    print(f"Titre: {schedule.get('title')}")
    print(f"Date: {schedule.get('date')}")
    print(f"Lieu: {schedule.get('location')}")
    print("---")

# Exporter en JSON
scraper.export_to_json(schedules, 'mes_schedules.json')

# Exporter en CSV
scraper.export_to_csv(schedules, 'mes_schedules.csv')
```

## 🔧 Méthodes de scraping

### 1. API Directe
Le scraper tente de découvrir et accéder directement aux endpoints API de Squadi :
- `https://registration.us.squadi.com/api/schedules`
- `https://api.squadi.com/schedules`
- Et autres variations possibles

### 2. Cloudscraper
Utilise `cloudscraper` pour contourner les protections Cloudflare et autres systèmes anti-bot.

### 3. Selenium
Utilise un navigateur Chrome headless pour :
- Exécuter le JavaScript de la page
- Intercepter les requêtes réseau
- Naviguer sur les liens de schedules
- Extraire les données dynamiques

## 📊 Format des données exportées

### JSON
```json
{
  "metadata": {
    "scraped_at": "2025-12-16T10:30:00",
    "source": "https://registration.us.squadi.com",
    "total_schedules": 42
  },
  "schedules": [
    {
      "title": "Championship Game",
      "date": "2025-12-20",
      "location": "Main Stadium",
      "url": "https://registration.us.squadi.com/schedule/123",
      "id": "123"
    }
  ]
}
```

### CSV
```csv
title,date,location,url,id
Championship Game,2025-12-20,Main Stadium,https://...,123
```

## 🛠️ Dépannage

### Erreur 403 (Forbidden)

Le site bloque l'accès. Solutions :

1. **Utilisez Selenium** (méthode 4) - Le navigateur headless est plus difficile à détecter
2. **VPN/Proxy** - Le site peut bloquer certaines régions
3. **Attendez** - Vous avez peut-être été temporairement bloqué

### Selenium ne fonctionne pas

```bash
# Réinstaller webdriver-manager
pip uninstall webdriver-manager -y
pip install webdriver-manager

# Ou spécifier manuellement le chemin de ChromeDriver
export CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### Aucun schedule trouvé

Plusieurs raisons possibles :

1. **Le site est protégé** - Utilisez Selenium
2. **Structure différente** - Le site a peut-être changé sa structure HTML
3. **API privée** - Les endpoints API nécessitent peut-être une authentification
4. **Pas de schedules disponibles** - Vérifiez manuellement sur le site

## 🔍 Debug

Pour plus de détails sur l'exécution :

```python
import logging

# Activer les logs debug
logging.basicConfig(level=logging.DEBUG)

scraper = SquadiSchedulesScraper()
schedules = scraper.run(method='auto')
```

## 📝 Exemples de commandes

### Test rapide avec API uniquement
```bash
python -c "from squadi_schedules_scraper import SquadiSchedulesScraper; s = SquadiSchedulesScraper(); print(s.run(method='api'))"
```

### Export direct
```python
from squadi_schedules_scraper import SquadiSchedulesScraper
from datetime import datetime

scraper = SquadiSchedulesScraper()
schedules = scraper.run(method='auto')

if schedules:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.export_to_json(schedules, f'squadi_{timestamp}.json')
    print(f"✓ {len(schedules)} schedules exportés")
else:
    print("✗ Aucun schedule trouvé")
```

## ⚖️ Considérations légales

- Respectez les conditions d'utilisation du site
- Ne surchargez pas le serveur avec trop de requêtes
- Le scraper inclut un rate limiting pour respecter le site
- Utilisez ces données de manière responsable

## 🤝 Contribution

Ce scraper utilise plusieurs techniques pour s'adapter aux différentes protections :
- Détection automatique de la meilleure méthode
- Multiple fallbacks
- Extraction intelligente des données JSON et HTML

N'hésitez pas à améliorer le code !

## 📄 Licence

Code généré pour un usage personnel et éducatif.
