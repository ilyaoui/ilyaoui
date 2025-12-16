# 🚀 Quick Start - Scraper Squadi

## Objectif
Récupérer tous les schedules à venir depuis **https://registration.us.squadi.com/**

## 📦 Fichiers créés

1. **squadi_schedules_scraper.py** - Scraper automatique principal
2. **squadi_manual_explorer.py** - Outil d'exploration et diagnostic
3. **squadi_browser_script.js** - Script à exécuter dans le navigateur
4. **requirements_squadi.txt** - Dépendances Python
5. **README_SQUADI.md** - Documentation complète

## ⚡ Utilisation rapide

### Méthode 1 : Script automatique (Recommandé)

```bash
# Installer les dépendances
pip install -r requirements_squadi.txt

# Lancer le scraper
python squadi_schedules_scraper.py

# Choisir l'option 1 (Auto) pour essayer toutes les méthodes
```

### Méthode 2 : Script navigateur (Plus simple)

1. Ouvrir https://registration.us.squadi.com dans Chrome
2. Ouvrir la console (F12 → Console)
3. Copier-coller le contenu de `squadi_browser_script.js`
4. Naviguer sur le site
5. Dans la console, taper : `exportSchedules()`
6. Un fichier JSON sera téléchargé automatiquement

### Méthode 3 : Exploration manuelle

```bash
python squadi_manual_explorer.py
```

Ce script va :
- Tester l'accès au site
- Découvrir les endpoints API
- Créer des fichiers d'aide
- Générer un guide pas à pas

## 🔧 Résolution de problèmes

### Erreur 403 (Forbidden)

Le site est protégé par Cloudflare/anti-bot. Solutions :

1. **Utiliser le script navigateur** (squadi_browser_script.js) ← PLUS SIMPLE
2. Installer cloudscraper : `pip install cloudscraper`
3. Utiliser Selenium : `pip install selenium webdriver-manager`

### Aucune donnée trouvée

1. Vérifiez que le site est accessible manuellement
2. Utilisez la méthode du script navigateur
3. Inspectez manuellement avec DevTools (F12 → Network)
4. Contactez-moi pour adapter le scraper

## 📊 Format de sortie

Les schedules seront exportés en deux formats :

**JSON** : `squadi_schedules_YYYYMMDD_HHMMSS.json`
```json
{
  "metadata": {
    "scraped_at": "2025-12-16T10:30:00",
    "total_schedules": 42
  },
  "schedules": [...]
}
```

**CSV** : `squadi_schedules_YYYYMMDD_HHMMSS.csv`

## 🎯 Prochaines étapes

1. Essayez d'abord le script navigateur (le plus simple)
2. Si ça ne fonctionne pas, utilisez le scraper automatique
3. Pour des besoins spécifiques, modifiez `squadi_schedules_scraper.py`

## 💡 Exemple de code Python

```python
from squadi_schedules_scraper import SquadiSchedulesScraper

# Créer le scraper
scraper = SquadiSchedulesScraper()

# Récupérer tous les schedules
schedules = scraper.run(method='auto')

# Traiter les données
for schedule in schedules:
    print(f"{schedule.get('title')} - {schedule.get('date')}")

# Exporter
scraper.export_to_json(schedules, 'mes_schedules.json')
scraper.export_to_csv(schedules, 'mes_schedules.csv')
```

## 📚 Documentation complète

Voir **README_SQUADI.md** pour la documentation complète et les exemples avancés.

---

**Note** : Le site Squadi utilise des protections anti-bot. Si les méthodes automatiques échouent, le script navigateur (JavaScript dans la console) est la solution la plus fiable car il utilise votre navigateur authentique.
