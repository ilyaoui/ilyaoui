# 🧪 Guide de Test Local - Scraper Squadi

## Prérequis

- Python 3.7+
- pip
- Accès Internet

## Option 1 : Test Rapide avec Script Automatique ⚡

### Étape 1 : Lancer le test
```bash
python3 test_squadi_simple.py
```

Le script va :
- Vérifier toutes les dépendances
- Tester chaque méthode disponible
- Vous indiquer ce qui manque

---

## Option 2 : Installation Manuelle Complète 🔧

### Étape 1 : Installer les dépendances de base
```bash
pip install beautifulsoup4 requests lxml
```

### Étape 2 : Installer cloudscraper (pour contourner Cloudflare)
```bash
pip install cloudscraper
```

### Étape 3 : (Optionnel) Installer Selenium
```bash
pip install selenium webdriver-manager
```

### Étape 4 : Tester avec le scraper complet
```bash
python3 squadi_schedules_scraper.py
```

Puis choisir :
- **Option 1** : Auto (teste toutes les méthodes)
- **Option 2** : API uniquement
- **Option 3** : Requests/Cloudscraper
- **Option 4** : Selenium (navigateur headless)

---

## Option 3 : Test avec le Navigateur (La plus simple) 🌐

Si les méthodes automatiques échouent (erreur 403), utilisez cette méthode :

### Étape 1 : Ouvrir le site
```
https://registration.us.squadi.com
```

### Étape 2 : Ouvrir DevTools
- Appuyez sur **F12**
- Allez dans l'onglet **Console**

### Étape 3 : Charger le script
```bash
# Dans votre terminal, afficher le script :
cat squadi_browser_script.js
```

- Copiez tout le contenu
- Collez dans la Console Chrome
- Appuyez sur Entrée

### Étape 4 : Exporter les données
Dans la Console, tapez :
```javascript
exportSchedules()
```

Un fichier JSON sera automatiquement téléchargé avec tous les schedules !

---

## Tests Disponibles

### Test 1 : Vérification des dépendances
```bash
python3 test_squadi_simple.py
```

### Test 2 : Exploration manuelle du site
```bash
python3 squadi_manual_explorer.py
```

Ce script va :
- Tester l'accès au site
- Découvrir les endpoints API
- Sauvegarder les pages HTML pour analyse
- Générer un script navigateur

### Test 3 : Scraper complet interactif
```bash
python3 squadi_schedules_scraper.py
```

### Test 4 : Utilisation dans votre propre code
```python
from squadi_schedules_scraper import SquadiSchedulesScraper

# Créer le scraper
scraper = SquadiSchedulesScraper()

# Méthode 1 : Auto (essaie toutes les méthodes)
schedules = scraper.run(method='auto')

# Méthode 2 : API uniquement
schedules = scraper.scrape_api_directly()

# Méthode 3 : Cloudscraper
schedules = scraper.scrape_with_requests()

# Afficher les résultats
print(f"{len(schedules)} schedules trouvés")
for schedule in schedules:
    print(schedule)

# Exporter
scraper.export_to_json(schedules, 'mes_schedules.json')
scraper.export_to_csv(schedules, 'mes_schedules.csv')
```

---

## Résolution de Problèmes

### Erreur 403 (Forbidden)

**Problème** : Le site bloque l'accès

**Solutions** :
1. ✅ Utilisez la méthode navigateur (Option 3)
2. ✅ Installez cloudscraper : `pip install cloudscraper`
3. ✅ Utilisez Selenium : `pip install selenium webdriver-manager`

### Import Error

**Problème** : `ModuleNotFoundError: No module named 'xxx'`

**Solution** :
```bash
pip install beautifulsoup4 requests lxml
```

### Selenium ne fonctionne pas

**Problème** : Erreur avec ChromeDriver

**Solutions** :
```bash
# Option 1 : Réinstaller
pip uninstall selenium webdriver-manager -y
pip install selenium webdriver-manager

# Option 2 : Installer Chrome/Chromium
# Ubuntu/Debian
sudo apt-get install chromium-browser

# macOS
brew install --cask google-chrome
```

### Aucun schedule trouvé

**Causes possibles** :
1. Le site est protégé (erreur 403)
2. Pas de schedules disponibles actuellement
3. Structure du site a changé

**Solutions** :
1. ✅ Vérifiez manuellement sur https://registration.us.squadi.com
2. ✅ Utilisez la méthode navigateur (script JS)
3. ✅ Lancez `python3 squadi_manual_explorer.py` pour diagnostiquer

---

## Commandes Utiles

### Vérifier que tout fonctionne
```bash
# Test rapide
python3 -c "from squadi_schedules_scraper import SquadiSchedulesScraper; print('✅ Import OK')"
```

### Lister les dépendances installées
```bash
pip list | grep -E "(beautifulsoup4|requests|lxml|cloudscraper|selenium)"
```

### Nettoyer et réinstaller
```bash
pip uninstall beautifulsoup4 requests lxml cloudscraper selenium -y
pip install -r requirements_squadi.txt
```

---

## Fichiers Générés Après les Tests

Après avoir lancé les scripts, vous aurez :

- `squadi_schedules_YYYYMMDD_HHMMSS.json` - Schedules en JSON
- `squadi_schedules_YYYYMMDD_HHMMSS.csv` - Schedules en CSV
- `squadi_homepage_YYYYMMDD_HHMMSS.html` - Page d'accueil sauvegardée
- `squadi_apis.json` - Endpoints API découverts
- `squadi_json_data_*.json` - Données JSON extraites
- `squadi_browser_script.js` - Script pour le navigateur

---

## Exemples d'Utilisation

### Exemple 1 : Récupérer tous les schedules
```bash
python3 squadi_schedules_scraper.py
# Choisir option 1 (Auto)
```

### Exemple 2 : Script Python personnalisé
```python
from squadi_schedules_scraper import SquadiSchedulesScraper
from datetime import datetime

scraper = SquadiSchedulesScraper()
schedules = scraper.run(method='auto')

if schedules:
    print(f"✅ {len(schedules)} schedules trouvés")

    # Filtrer par date (exemple)
    upcoming = [s for s in schedules if 'date' in s]

    # Exporter avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scraper.export_to_json(schedules, f'squadi_{timestamp}.json')
else:
    print("❌ Aucun schedule trouvé")
    print("💡 Essayez la méthode navigateur")
```

### Exemple 3 : Avec gestion d'erreurs
```python
from squadi_schedules_scraper import SquadiSchedulesScraper
import logging

# Activer le logging détaillé
logging.basicConfig(level=logging.DEBUG)

scraper = SquadiSchedulesScraper()

# Essayer chaque méthode
methods = ['api', 'requests', 'selenium']
all_schedules = []

for method in methods:
    try:
        print(f"\n🔄 Test méthode: {method}")
        schedules = scraper.run(method=method)
        if schedules:
            all_schedules.extend(schedules)
            print(f"✅ {len(schedules)} trouvés avec {method}")
            break
    except Exception as e:
        print(f"❌ Erreur avec {method}: {e}")
        continue

# Dédupliquer et exporter
if all_schedules:
    unique = scraper._deduplicate_schedules(all_schedules)
    scraper.export_to_json(unique, 'final_schedules.json')
```

---

## Checklist de Test

- [ ] Python 3 installé et fonctionnel
- [ ] Dépendances de base installées (beautifulsoup4, requests, lxml)
- [ ] Test du script simple réussi (`python3 test_squadi_simple.py`)
- [ ] cloudscraper installé (optionnel mais recommandé)
- [ ] Selenium installé (optionnel)
- [ ] Test du scraper complet (`python3 squadi_schedules_scraper.py`)
- [ ] Script navigateur testé (si méthodes auto échouent)
- [ ] Fichiers JSON/CSV générés avec succès

---

## Support

Si vous rencontrez des problèmes :

1. Lancez le diagnostic : `python3 squadi_manual_explorer.py`
2. Vérifiez les logs pour les erreurs détaillées
3. Essayez la méthode navigateur (la plus fiable)
4. Consultez README_SQUADI.md pour plus d'informations

---

**Bonne chance avec vos tests ! 🚀**
