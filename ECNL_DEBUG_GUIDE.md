# 🔍 Guide de Débogage ECNL - Aucun Match Trouvé

## ❌ Problème Rencontré

Vous avez exécuté :
```bash
python generic_sports_scraper.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx" --single-page
```

Et obtenu :
```
INFO - Total: 0 matchs uniques extraits
WARNING - Aucun match trouvé
```

**Cela signifie** : La connexion fonctionne ✓, mais la structure de la page n'est pas reconnue par les stratégies génériques.

---

## ✅ Solution : Scraper Spécifique ECNL

J'ai créé un **scraper spécialisé** pour les pages ECNL (qui utilisent Sidearm Sports).

### Étape 1 : Utiliser le Scraper Spécialisé

```bash
python ecnl_specific_scraper.py "https://theecnl.com/sports/2023/8/8/ECNLRLG_0808235356.aspx"
```

Ce script va :
- ✅ Essayer plusieurs stratégies spécifiques à Sidearm Sports
- ✅ Sauvegarder automatiquement des fichiers de debug
- ✅ Afficher les matchs trouvés
- ✅ Exporter en CSV

### Étape 2 : Analyser les Fichiers de Debug

Si aucun match n'est trouvé, 3 fichiers seront créés automatiquement :

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `ecnl_page_debug.html` | HTML complet de la page | Ouvrir dans un navigateur pour voir la structure |
| `ecnl_page_debug.txt` | Texte brut extrait | Chercher les patterns de matchs |
| `ecnl_tables_debug.txt` | Toutes les tables HTML | Identifier les tables de matchs |

### Étape 3 : Identifier la Structure

Ouvrez `ecnl_page_debug.html` dans un navigateur et cherchez :

#### A. Tables HTML

Cherchez une table contenant les matchs. Exemple :

```html
<table class="sidearm-schedule-games">
  <tr>
    <td>8/8/2023</td>
    <td>10:00 AM</td>
    <td>Team A vs Team B</td>
    <td>2-1</td>
  </tr>
</table>
```

**Notez** :
- La classe de la table (`class="..."`)
- Les colonnes (date, heure, équipes, score)
- Le format des données

#### B. Divs Structurées

Cherchez des divs avec les matchs. Exemple :

```html
<div class="game-item" data-game-id="12345">
  <div class="game-date">August 8, 2023</div>
  <div class="team-home">Team A</div>
  <div class="team-away">Team B</div>
  <div class="score">2-1</div>
</div>
```

**Notez** :
- Les classes CSS (`game-item`, `game-date`, etc.)
- La structure des données

#### C. JavaScript/JSON

Cherchez dans le code source (Ctrl+U) des variables JavaScript :

```javascript
var schedule = [
  {
    "date": "2023-08-08",
    "homeTeam": "Team A",
    "awayTeam": "Team B",
    "score": "2-1"
  }
];
```

#### D. IFrames

Si la page contient un iframe :

```html
<iframe src="https://example.com/schedule.php?id=123"></iframe>
```

Les matchs sont dans l'iframe, pas dans la page principale. Il faudra scraper l'URL de l'iframe.

---

## 🛠️ Adapter le Scraper

Une fois la structure identifiée, vous avez **3 options** :

### Option 1 : Me Fournir la Structure

Copiez un extrait de `ecnl_page_debug.html` montrant comment les matchs sont affichés, et je peux adapter le scraper.

### Option 2 : Modifier `ecnl_specific_scraper.py`

Si vous êtes à l'aise avec Python, modifiez la méthode `_parse_table_row` ou `_parse_game_div` selon la structure trouvée.

**Exemple** : Si les matchs sont dans une table avec classe `schedule-table` :

```python
# Dans _parse_table_row, ajouter :
schedule_table = soup.find('table', class_='schedule-table')
if schedule_table:
    rows = schedule_table.find_all('tr')[1:]  # Skip header
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            match = {
                'date': cells[0].get_text().strip(),
                'time': cells[1].get_text().strip(),
                'home_team': cells[2].get_text().strip(),
                'away_team': cells[3].get_text().strip(),
                # ... etc
            }
```

### Option 3 : Scraper l'IFrame

Si les matchs sont dans un iframe :

```python
# Récupérer l'URL de l'iframe
iframe = soup.find('iframe', src=re.compile(r'schedule'))
if iframe:
    iframe_url = iframe['src']
    # Scraper l'iframe
    matches = scraper.scrape_matches_from_url(iframe_url)
```

---

## 📊 Cas Typiques de Pages ECNL

### Cas 1 : Page avec Table Simple

**Structure** :
```html
<table class="schedule">
  <tr><th>Date</th><th>Time</th><th>Opponent</th><th>Result</th></tr>
  <tr><td>8/8/23</td><td>10:00 AM</td><td>vs Team A</td><td>W 2-1</td></tr>
</table>
```

**Solution** : Parser les headers pour identifier les colonnes, puis extraire les données ligne par ligne.

### Cas 2 : Page avec Divs et Classes

**Structure** :
```html
<div class="games-list">
  <div class="game">
    <span class="date">8/8/23</span>
    <span class="opponent">Team A</span>
    <span class="result">W 2-1</span>
  </div>
</div>
```

**Solution** : Trouver tous les divs `.game`, puis extraire les spans à l'intérieur.

### Cas 3 : Page avec JSON Embedded

**Structure** :
```html
<script>
var scheduleData = {
  "games": [
    {"date": "2023-08-08", "home": "Team A", "away": "Team B", "score": "2-1"}
  ]
};
</script>
```

**Solution** : Extraire le JSON avec regex, le parser, et créer les matchs.

### Cas 4 : Page avec IFrame

**Structure** :
```html
<iframe src="https://example.com/widget/schedule?team=123"></iframe>
```

**Solution** : Scraper l'URL de l'iframe au lieu de la page principale.

---

## 🔧 Commandes de Débogage

### 1. Voir le Contenu Texte de la Page

```bash
python ecnl_specific_scraper.py "URL"
# Puis :
cat ecnl_page_debug.txt | grep -i "vs\|team\|game"
```

### 2. Voir Toutes les Tables

```bash
cat ecnl_tables_debug.txt
```

### 3. Chercher des Patterns Spécifiques

```bash
# Chercher des dates
cat ecnl_page_debug.txt | grep -E '\d{1,2}/\d{1,2}/\d{2,4}'

# Chercher des scores
cat ecnl_page_debug.txt | grep -E '\d+-\d+'

# Chercher "vs"
cat ecnl_page_debug.txt | grep -i " vs "
```

### 4. Analyser le HTML Directement

```bash
# Ouvrir dans un navigateur
firefox ecnl_page_debug.html
# ou
chrome ecnl_page_debug.html

# Puis utiliser les DevTools (F12) pour inspecter la structure
```

---

## 💡 Workflow Recommandé

```bash
# Étape 1 : Scraper avec le script spécialisé
python ecnl_specific_scraper.py "https://theecnl.com/..."

# Étape 2 : Si aucun match trouvé, analyser les fichiers de debug
firefox ecnl_page_debug.html  # Inspecter visuellement
cat ecnl_tables_debug.txt     # Voir les tables

# Étape 3 : Identifier la structure
# Note: Chercher les patterns de dates, équipes, scores

# Étape 4 : Adapter le scraper selon la structure trouvée
# Ou me fournir un extrait pour que j'adapte le scraper
```

---

## 🚀 Test Rapide

Pour vérifier que le scraper fonctionne (avec données simulées) :

```bash
python test_ecnl_demo.py
```

Cela montre comment le scraper **devrait** fonctionner avec des données réelles.

---

## 📝 Exemples de Structures ECNL Réelles

### Structure Type 1 : Sidearm Sports Standard

```html
<div id="schedule" class="sidearm-schedule">
  <article class="sidearm-schedule-game">
    <div class="sidearm-schedule-game-opponent-name">
      <span>vs</span> Team Name
    </div>
    <div class="sidearm-schedule-game-result">
      <time>Aug 8, 2023 - 10:00 AM</time>
    </div>
    <div class="sidearm-schedule-game-result-score">
      W 2-1
    </div>
  </article>
</div>
```

**Classes clés** : `sidearm-schedule-game`, `sidearm-schedule-game-opponent-name`

### Structure Type 2 : Legacy ECNL

```html
<table class="schedule-table">
  <tbody>
    <tr class="game-row">
      <td class="date-cell">8/8/2023</td>
      <td class="time-cell">10:00 AM</td>
      <td class="opponent-cell">
        <a href="/team/123">Team Name</a>
      </td>
      <td class="result-cell">W, 2-1</td>
      <td class="location-cell">Stadium Name</td>
    </tr>
  </tbody>
</table>
```

**Classes clés** : `schedule-table`, `game-row`, `date-cell`

### Structure Type 3 : JSON Feed

```javascript
// Dans un <script> tag
window.scheduleData = {
  "items": [
    {
      "id": "12345",
      "date": "2023-08-08T10:00:00",
      "teams": {
        "home": {"name": "Team A", "score": 2},
        "away": {"name": "Team B", "score": 1}
      },
      "venue": "Stadium Name"
    }
  ]
};
```

**Variable clé** : `scheduleData`, `items`

---

## ❓ FAQ

### Q: Le scraper ne trouve toujours rien après avoir utilisé `ecnl_specific_scraper.py`

**R:** Cela signifie que la structure est unique. Options :
1. Envoyez-moi un extrait de `ecnl_page_debug.html`
2. Vérifiez si les matchs sont dans un iframe
3. Le site peut charger les matchs avec JavaScript (requiert Selenium)

### Q: Les fichiers de debug ne contiennent pas de matchs

**R:** Possible que :
- La page ne contienne vraiment pas de matchs (vérifiez dans un navigateur)
- Les matchs sont chargés dynamiquement (JavaScript)
- L'URL pointe vers une page différente (redirect)

### Q: Comment scraper si les matchs sont chargés en JavaScript ?

**R:** Il faudrait utiliser Selenium ou Playwright. Exemple :

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)  # Attendre le chargement
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
# Continuer le parsing...
```

### Q: Le site bloque mon IP

**R:**
- Augmentez le rate limiting (3-5 secondes)
- Changez le User-Agent
- Utilisez un VPN
- Utilisez des proxies résidentiels

---

## 📞 Besoin d'Aide ?

Si vous êtes bloqué :

1. **Exécutez** le scraper spécialisé :
   ```bash
   python ecnl_specific_scraper.py "URL"
   ```

2. **Partagez** un extrait de `ecnl_page_debug.html` montrant :
   - La structure d'un match
   - Les classes CSS utilisées
   - Le format des données

3. **Ou partagez** une capture d'écran de la page dans un navigateur

Je pourrai alors adapter le scraper précisément pour cette structure !

---

## ✅ Checklist

- [ ] Exécuté `python ecnl_specific_scraper.py "URL"`
- [ ] Vérifié les fichiers de debug créés
- [ ] Ouvert `ecnl_page_debug.html` dans un navigateur
- [ ] Identifié où sont les matchs dans la page
- [ ] Noté les classes CSS ou structure utilisée
- [ ] Essayé de modifier le scraper ou demandé de l'aide

---

**Bon débogage ! 🔍**
