#!/bin/bash
# Script pour configurer l'environnement local et tester le scraper Squadi

echo "========================================"
echo "SETUP LOCAL - SCRAPER SQUADI"
echo "========================================"
echo ""

# Étape 1 : Vérifier l'état actuel
echo "📍 Étape 1/5 : Vérification de l'état Git..."
echo ""
echo "Branche actuelle :"
git branch --show-current
echo ""
echo "Status :"
git status --short
echo ""

# Étape 2 : Sauvegarder les changements locaux (si nécessaire)
read -p "Voulez-vous sauvegarder vos changements locaux ? (o/N) : " save_changes
if [ "$save_changes" = "o" ] || [ "$save_changes" = "O" ]; then
    echo ""
    echo "💾 Sauvegarde des changements locaux..."
    git stash save "Sauvegarde avant pull $(date +%Y%m%d_%H%M%S)"
    echo "✅ Changements sauvegardés (utilisez 'git stash pop' pour les restaurer)"
fi

echo ""
echo "📥 Étape 2/5 : Récupération des dernières modifications..."

# Vérifier si on est sur la bonne branche
current_branch=$(git branch --show-current)
target_branch="claude/fetch-upcoming-schedules-fHJTo"

if [ "$current_branch" != "$target_branch" ]; then
    echo ""
    echo "⚠️  Vous êtes sur la branche : $current_branch"
    echo "   La branche cible est : $target_branch"
    echo ""
    read -p "Voulez-vous changer de branche ? (o/N) : " switch_branch

    if [ "$switch_branch" = "o" ] || [ "$switch_branch" = "O" ]; then
        echo ""
        echo "🔄 Changement vers $target_branch..."

        # Fetch d'abord pour avoir la branche
        git fetch origin $target_branch

        # Checkout
        git checkout $target_branch

        if [ $? -eq 0 ]; then
            echo "✅ Changement de branche réussi"
        else
            echo "❌ Erreur lors du changement de branche"
            exit 1
        fi
    else
        echo "⏭️  Reste sur la branche $current_branch"
    fi
fi

echo ""
echo "⬇️  Pull des dernières modifications..."
git pull origin $(git branch --show-current)

if [ $? -eq 0 ]; then
    echo "✅ Pull réussi"
else
    echo "❌ Erreur lors du pull"
    exit 1
fi

echo ""
echo "📂 Étape 3/5 : Vérification des fichiers Squadi..."
echo ""

# Vérifier que tous les fichiers sont présents
files=(
    "squadi_schedules_scraper.py"
    "squadi_manual_explorer.py"
    "squadi_browser_script.js"
    "test_squadi_simple.py"
    "install_and_test.sh"
    "requirements_squadi.txt"
    "README_SQUADI.md"
    "QUICK_START_SQUADI.md"
    "GUIDE_TEST_LOCAL.md"
)

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (manquant)"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo ""
    echo "⚠️  Certains fichiers sont manquants"
    echo "   Vérifiez que vous êtes sur la bonne branche"
    exit 1
fi

echo ""
echo "🔍 Étape 4/5 : Vérification de Python et pip..."
python3 --version
pip --version || pip3 --version

echo ""
echo "📦 Étape 5/5 : Prêt pour l'installation des dépendances"
echo ""
echo "========================================"
echo "✅ SETUP TERMINÉ"
echo "========================================"
echo ""
echo "🎯 Prochaines étapes :"
echo ""
echo "Option A - Installation et test automatique :"
echo "  ./install_and_test.sh"
echo ""
echo "Option B - Installation manuelle :"
echo "  pip install beautifulsoup4 requests lxml cloudscraper"
echo "  python3 test_squadi_simple.py"
echo ""
echo "Option C - Installation complète :"
echo "  pip install -r requirements_squadi.txt"
echo "  python3 squadi_schedules_scraper.py"
echo ""
echo "📖 Documentation :"
echo "  - Guide rapide : cat QUICK_START_SQUADI.md"
echo "  - Guide complet : cat GUIDE_TEST_LOCAL.md"
echo "  - README : cat README_SQUADI.md"
echo ""
