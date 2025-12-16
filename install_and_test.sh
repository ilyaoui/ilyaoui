#!/bin/bash
# Installation et test en une commande

echo "🚀 Installation et test du scraper Squadi"
echo "=========================================="
echo ""

# Demander quelle méthode
echo "Choisissez votre méthode de test :"
echo ""
echo "1. Test rapide (uniquement dépendances de base)"
echo "2. Installation complète (avec cloudscraper)"
echo "3. Installation complète + Selenium (tout)"
echo ""
read -p "Votre choix (1-3) : " choice

case $choice in
    1)
        echo ""
        echo "📦 Installation des dépendances de base..."
        pip install beautifulsoup4 requests lxml
        echo ""
        echo "✅ Installation terminée"
        echo ""
        echo "🧪 Lancement du test..."
        python3 test_squadi_simple.py
        ;;
    2)
        echo ""
        echo "📦 Installation avec cloudscraper..."
        pip install beautifulsoup4 requests lxml cloudscraper
        echo ""
        echo "✅ Installation terminée"
        echo ""
        echo "🧪 Lancement du scraper complet..."
        python3 squadi_schedules_scraper.py
        ;;
    3)
        echo ""
        echo "📦 Installation complète (avec Selenium)..."
        pip install -r requirements_squadi.txt
        echo ""
        echo "✅ Installation terminée"
        echo ""
        echo "🧪 Lancement du scraper complet..."
        python3 squadi_schedules_scraper.py
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Terminé !"
echo "=========================================="
