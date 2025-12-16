#!/bin/bash
# Script de test local pour le scraper Squadi

echo "=========================================="
echo "TEST LOCAL - SCRAPER SQUADI"
echo "=========================================="
echo ""

# Étape 1 : Vérifier Python
echo "1️⃣  Vérification de Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi
echo "✅ Python OK"
echo ""

# Étape 2 : Créer un environnement virtuel (optionnel mais recommandé)
echo "2️⃣  Création d'un environnement virtuel (optionnel)..."
read -p "Créer un venv ? (o/N): " create_venv
if [ "$create_venv" = "o" ] || [ "$create_venv" = "O" ]; then
    python3 -m venv venv_squadi
    source venv_squadi/bin/activate
    echo "✅ Environnement virtuel activé"
else
    echo "⏭️  Pas de venv, installation globale"
fi
echo ""

# Étape 3 : Installer les dépendances de base
echo "3️⃣  Installation des dépendances de base..."
echo "   (beautifulsoup4, requests, lxml)"
pip install beautifulsoup4 requests lxml --quiet
echo "✅ Dépendances de base installées"
echo ""

# Étape 4 : Test de l'outil d'exploration
echo "4️⃣  Test de l'outil d'exploration..."
echo "   Lancement de squadi_manual_explorer.py..."
echo ""
python3 squadi_manual_explorer.py
echo ""

# Étape 5 : Vérifier les fichiers générés
echo "5️⃣  Vérification des fichiers générés..."
if [ -f "squadi_browser_script.js" ]; then
    echo "✅ squadi_browser_script.js généré"
fi

echo ""
echo "=========================================="
echo "INSTALLATION DE BASE TERMINÉE"
echo "=========================================="
echo ""
echo "🎯 Prochaines étapes pour tester :"
echo ""
echo "OPTION A - Test avec cloudscraper (recommandé) :"
echo "  pip install cloudscraper"
echo "  python3 squadi_schedules_scraper.py"
echo ""
echo "OPTION B - Test avec Selenium (si A échoue) :"
echo "  pip install selenium webdriver-manager"
echo "  python3 squadi_schedules_scraper.py"
echo ""
echo "OPTION C - Méthode navigateur (la plus fiable) :"
echo "  1. Ouvrir Chrome → https://registration.us.squadi.com"
echo "  2. F12 → Console"
echo "  3. Copier-coller le contenu de squadi_browser_script.js"
echo "  4. Taper: exportSchedules()"
echo ""
