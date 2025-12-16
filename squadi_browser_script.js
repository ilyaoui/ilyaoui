
// ==================================================================
// Script à exécuter dans la console du navigateur (F12 -> Console)
// ==================================================================

// 1. Intercepter toutes les requêtes fetch
(function() {
    const originalFetch = window.fetch;
    const capturedRequests = [];

    window.fetch = function(...args) {
        const url = args[0];

        // Capturer l'URL
        if (url && (url.includes('api') || url.includes('schedule'))) {
            console.log('🔍 API Request:', url);
            capturedRequests.push(url);
        }

        return originalFetch.apply(this, args);
    };

    // Fonction pour afficher toutes les URLs capturées
    window.getCapturedRequests = () => {
        console.log('📋 Captured Requests:', capturedRequests);
        return capturedRequests;
    };

    console.log('✓ Fetch interceptor installé!');
    console.log('  Utilisez getCapturedRequests() pour voir les URLs');
})();

// 2. Chercher des données de schedules dans le DOM
function findScheduleData() {
    // Chercher dans tous les scripts JSON
    const scripts = document.querySelectorAll('script[type="application/json"]');
    const jsonData = [];

    scripts.forEach((script, index) => {
        try {
            const data = JSON.parse(script.textContent);
            console.log(`📄 JSON Script ${index + 1}:`, data);
            jsonData.push(data);
        } catch (e) {
            // Pas du JSON valide
        }
    });

    return jsonData;
}

// 3. Chercher dans window/global scope
function findGlobalScheduleData() {
    const matches = [];

    for (let key in window) {
        const lowerKey = key.toLowerCase();
        if (lowerKey.includes('schedule') || lowerKey.includes('event') || lowerKey.includes('api')) {
            try {
                const value = window[key];
                console.log(`🔑 window.${key}:`, value);
                matches.push({ key, value });
            } catch (e) {
                // Propriété non accessible
            }
        }
    }

    return matches;
}

// 4. Exporter les données
function exportSchedules() {
    const jsonData = findScheduleData();
    const globalData = findGlobalScheduleData();

    const exportData = {
        timestamp: new Date().toISOString(),
        jsonScripts: jsonData,
        globalData: globalData,
        capturedRequests: window.getCapturedRequests ? window.getCapturedRequests() : []
    };

    // Télécharger en JSON
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'squadi_export_' + Date.now() + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✓ Données exportées!');
}

console.log('');
console.log('='.repeat(60));
console.log('SQUADI SCHEDULE EXTRACTOR - Ready!');
console.log('='.repeat(60));
console.log('');
console.log('Commandes disponibles:');
console.log('  findScheduleData()      - Chercher JSON dans le DOM');
console.log('  findGlobalScheduleData() - Chercher dans window');
console.log('  getCapturedRequests()   - Voir les requêtes capturées');
console.log('  exportSchedules()       - Télécharger toutes les données');
console.log('');
console.log('Naviguez sur le site, puis utilisez exportSchedules()');
console.log('');
