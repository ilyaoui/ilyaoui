# Architecture - Sports Calendar Scraper 🏗️

## Vue d'ensemble

Système robuste et maintenable pour scraper des calendriers sportifs avec approche **API-First** et architecture **multi-agents**.

## Principes de Design

### 1. API-First
- Toujours chercher une API avant de scraper le HTML
- Détecter : XHR, Fetch, GraphQL, JSON-LD, iCal, RSS, endpoints privés
- Fallback intelligent sur scraping si pas d'API

### 2. Multi-Agents
- Agents spécialisés avec responsabilités claires
- Communication via interfaces typées
- Évidence-based : pas d'hallucination de données

### 3. État et Signature
- Signature de "vue" : `hash(DOM_calendar + URL + params)`
- Exploration BFS/DFS des filtres UI
- Détection de boucles infinies

### 4. Observabilité
- Logs structurés (winston)
- Traces Playwright
- Screenshots en cas d'échec
- HAR files pour network debugging

## Architecture des Agents

### 📋 Planner Agent
**Rôle :** Analyse initiale et planification

**Input :**
- URL cible
- Configuration utilisateur

**Output :**
```typescript
interface Plan {
  url: string;
  strategy: 'api' | 'scrape' | 'hybrid';
  detectedPatterns: string[];
  estimatedCalendarCount: number;
  risks: string[];
  steps: PlanStep[];
}
```

**Responsabilités :**
- Analyser l'URL (domaine, path, query params)
- Détecter des patterns connus (TeamSnap, BlueSombrero, etc.)
- Proposer une stratégie d'extraction
- Identifier les risques (rate limiting, auth, dynamic content)

---

### 🔍 API Scout Agent
**Rôle :** Détection et exploitation d'APIs

**Input :**
- URL de la page
- HAR network logs

**Output :**
```typescript
interface APIDiscovery {
  found: boolean;
  endpoints: APIEndpoint[];
  authentication?: AuthMethod;
  dataFormat: 'json' | 'xml' | 'ical' | 'rss' | 'graphql';
  confidence: number;
}
```

**Stratégies de détection :**
1. **Network Interception** : Écouter XHR/Fetch pendant le chargement
2. **Script Analysis** : Parser les `<script>` pour trouver des endpoints
3. **JSON-LD** : Extraire schema.org Event data
4. **HTML Comments** : Chercher des URLs commentées
5. **GraphQL Introspection** : Tester `/graphql` avec introspection query
6. **iCal/RSS Links** : Détecter `<link rel="alternate">`

**Exemples d'APIs détectées :**
```typescript
{
  url: 'https://api.teamsnap.com/v3/teams',
  method: 'GET',
  headers: { 'Authorization': 'Bearer ...' },
  samplePayload: { ... }
}
```

---

### 🧭 UI Navigator Agent
**Rôle :** Explorer les contrôles UI pour découvrir tous les calendriers

**Input :**
- Page Playwright
- Liste des selectors à explorer

**Output :**
```typescript
interface CalendarGraph {
  views: CalendarView[];
  edges: ViewTransition[];
}

interface CalendarView {
  id: string;
  signature: string; // hash(DOM + URL + params)
  url: string;
  controls: UIControl[];
  matchCount: number;
}

interface UIControl {
  type: 'button' | 'select' | 'tab' | 'filter' | 'pagination';
  selector: string;
  label: string;
  action: 'click' | 'select' | 'navigate';
}
```

**Stratégies d'exploration :**
1. **BFS** : Explorer tous les contrôles niveau par niveau
2. **Signature de vue** : Éviter les boucles avec hash DOM
3. **Limites** : Max interactions, max profondeur
4. **State tracking** : Sauvegarder l'état pour revenir en arrière

**Exemple de graphe :**
```
View A (All Teams)
  ├─ [Select: Season] → View B (2024)
  │   ├─ [Select: Division] → View C (U12)
  │   └─ [Select: Division] → View D (U14)
  └─ [Select: Season] → View E (2025)
      └─ ...
```

---

### 📥 Scraper Agent
**Rôle :** Extraction des matchs depuis DOM/HTML

**Input :**
- Page HTML (statique ou Playwright page)
- Selectors candidats

**Output :**
```typescript
interface RawMatch {
  home?: string;
  away?: string;
  date?: string;
  time?: string;
  location?: string;
  competition?: string;
  metadata: {
    selector: string;
    rawHTML: string;
    confidence: number;
  }
}
```

**Stratégies d'extraction :**
1. **Table Detection** : Détecter `<table>` avec headers (Date, Home, Away)
2. **Card Layout** : Détecter pattern de cards répétées
3. **Schema.org** : Extraire JSON-LD SportsEvent
4. **iFrame** : Détecter et scraper iframes récursivement
5. **Dynamic Load** : Scroll infini / pagination

**Selectors intelligents :**
```typescript
const MATCH_PATTERNS = {
  table: 'table[class*="schedule"], table[class*="calendar"]',
  row: 'tr[class*="match"], tr[class*="game"]',
  card: 'div[class*="match-card"], article[class*="game"]',
  home: '[class*="home"], [class*="team-1"]',
  away: '[class*="away"], [class*="team-2"]',
  date: '[class*="date"], time[datetime]',
};
```

---

### ✅ Validator Agent
**Rôle :** Validation et normalisation des données

**Input :**
- Liste de matchs bruts

**Output :**
```typescript
interface ValidatedMatch {
  home: string;
  away: string;
  date_utc: string; // ISO 8601
  location?: string;
  competition?: string;
  metadata: {
    raw: string;
    confidence: number; // 0.0 - 1.0
    issues: ValidationIssue[];
  }
}
```

**Règles de validation :**
1. **Équipes** : Non vides, trim, normalisation casse
2. **Dates** : Parser formats multiples, convertir en UTC
3. **Duplicates** : Détecter doublons au sein d'un calendrier
4. **Incohérences** : Date passée, équipe = opponent, etc.

**Parser de dates :**
```typescript
// Formats supportés
"2025-12-25 14:30"
"Dec 25, 2025 at 2:30 PM"
"25/12/2025 14h30"
"2025-12-25T14:30:00Z"
```

---

### 🔗 Deduper Agent
**Rôle :** Déduplication cross-calendriers

**Input :**
- Matchs validés de plusieurs calendriers

**Output :**
```typescript
interface DeduplicatedMatch extends ValidatedMatch {
  sources: string[]; // Liste des calendar_ids
  duplicateKey: string; // hash stable
}
```

**Stratégie de clé stable :**
```typescript
function computeMatchKey(match: ValidatedMatch): string {
  const parts = [
    normalizeTeamName(match.home),
    normalizeTeamName(match.away),
    match.date_utc.split('T')[0], // Date only
    normalizeLocation(match.location),
  ];
  return crypto.createHash('sha256')
    .update(parts.join('|'))
    .digest('hex');
}
```

**Fusion de métadonnées :**
- Garder le match avec confidence la plus haute
- Merger les sources
- Logger les conflits (dates différentes, etc.)

---

### 📊 Reporter Agent
**Rôle :** Génération du rapport final

**Input :**
- Matchs dédupliqués
- Métadonnées de scraping

**Output :**
```typescript
interface ScrapingReport {
  source_url: string;
  scraped_at: string;
  strategy_used: 'api' | 'scrape' | 'hybrid';

  calendars: Calendar[];
  total_matches: number;
  duplicates_removed: number;

  api_endpoints?: APIEndpoint[];
  selectors_used?: string[];
  errors: ScrapingError[];

  performance: {
    duration_ms: number;
    pages_visited: number;
    requests_made: number;
  };

  artifacts: {
    har_file?: string;
    screenshots?: string[];
    trace_file?: string;
  };
}

interface Calendar {
  id: string;
  name: string;
  url: string;
  method: 'api' | 'scrape';
  matches: DeduplicatedMatch[];
  evidence: Evidence;
}

interface Evidence {
  api_endpoint?: string;
  selectors?: string[];
  network_calls?: NetworkCall[];
  dom_snapshot?: string;
}
```

---

## Playwright Integration

### Network Interception
```typescript
// Enregistrer toutes les requêtes
await page.route('**/*', (route) => {
  const request = route.request();
  networkLog.push({
    url: request.url(),
    method: request.method(),
    headers: request.headers(),
    postData: request.postData(),
  });
  route.continue();
});

// Capturer les réponses JSON
page.on('response', async (response) => {
  const contentType = response.headers()['content-type'];
  if (contentType?.includes('application/json')) {
    const json = await response.json();
    jsonResponses.push({ url: response.url(), data: json });
  }
});
```

### State Management
```typescript
interface ViewState {
  url: string;
  domSignature: string;
  filterState: Record<string, string>;
  timestamp: number;
}

async function captureViewState(page: Page): Promise<ViewState> {
  const calendarDOM = await page.$eval(
    CALENDAR_SELECTOR,
    (el) => el.innerHTML
  );

  return {
    url: page.url(),
    domSignature: hashString(calendarDOM),
    filterState: await extractFilterState(page),
    timestamp: Date.now(),
  };
}
```

### Error Recovery
```typescript
// Auto-retry avec backoff
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(2 ** i * 1000); // Exponential backoff
    }
  }
}

// Screenshot on failure
try {
  await page.click(selector);
} catch (error) {
  const screenshot = await page.screenshot({
    path: `error-${Date.now()}.png`,
    fullPage: true,
  });
  logger.error('Click failed', { selector, screenshot });
  throw error;
}
```

---

## Configuration

### config.json
```json
{
  "scraping": {
    "headless": true,
    "timeout": 30000,
    "userAgent": "Mozilla/5.0 ...",
    "viewport": { "width": 1920, "height": 1080 }
  },

  "limits": {
    "maxInteractions": 50,
    "maxPages": 20,
    "maxDepth": 5,
    "requestDelay": 1000
  },

  "selectors": {
    "calendar": [
      "table[class*='schedule']",
      "div[class*='calendar']",
      "[data-testid='calendar']"
    ],
    "match": [
      "tr[class*='match']",
      "div[class*='game-card']"
    ]
  },

  "output": {
    "directory": "./output",
    "formats": ["json", "csv"],
    "saveHAR": true,
    "saveScreenshots": true,
    "saveTraces": true
  },

  "plugins": {
    "enabled": ["teamsnap", "bluesombrero"],
    "directory": "./plugins"
  }
}
```

---

## Plugin System

Permet d'ajouter des stratégies spécifiques par site.

### Plugin Interface
```typescript
interface ScraperPlugin {
  name: string;
  domains: string[];

  detect(page: Page): Promise<boolean>;
  extractAPI?(page: Page): Promise<APIDiscovery>;
  extractMatches?(page: Page): Promise<RawMatch[]>;
  navigateFilters?(page: Page): Promise<CalendarView[]>;
}
```

### Example Plugin - TeamSnap
```typescript
export const TeamSnapPlugin: ScraperPlugin = {
  name: 'teamsnap',
  domains: ['teamsnap.com', 'tournaments.teamsnap.com'],

  async detect(page) {
    return await page.evaluate(() =>
      window.location.hostname.includes('teamsnap')
    );
  },

  async extractAPI(page) {
    // Intercepter les calls à api.teamsnap.com
    const endpoints = await interceptTeamSnapAPI(page);
    return {
      found: endpoints.length > 0,
      endpoints,
      dataFormat: 'json',
      confidence: 1.0,
    };
  },

  async extractMatches(page) {
    // Sélecteurs spécifiques TeamSnap
    return await page.$$eval('.game-row', (rows) =>
      rows.map((row) => ({
        home: row.querySelector('.home-team')?.textContent,
        away: row.querySelector('.away-team')?.textContent,
        date: row.querySelector('.game-time')?.getAttribute('datetime'),
      }))
    );
  },
};
```

---

## Tests Strategy

### Unit Tests
```typescript
describe('Validator Agent', () => {
  it('should parse multiple date formats', () => {
    expect(parseDate('2025-12-25 14:30')).toEqual(
      new Date('2025-12-25T14:30:00Z')
    );
  });

  it('should normalize team names', () => {
    expect(normalizeTeamName('  Patriots U12 ')).toBe('Patriots U12');
  });
});
```

### Integration Tests
```typescript
describe('Scraper End-to-End', () => {
  it('should scrape a static HTML calendar', async () => {
    const result = await scrapeCalendar({
      url: 'http://localhost:3000/test-calendar.html',
      config: testConfig,
    });

    expect(result.matches).toHaveLength(10);
    expect(result.matches[0].home).toBe('Team A');
  });
});
```

### Snapshot Tests
```typescript
it('should match output format snapshot', () => {
  expect(report).toMatchSnapshot();
});
```

---

## Roadmap

### Phase 1: Core (MVP)
- [x] Architecture multi-agents
- [ ] Planner + API Scout + Scraper
- [ ] Playwright integration
- [ ] Output format standard
- [ ] CLI basique

### Phase 2: Robustesse
- [ ] UI Navigator (exploration filtres)
- [ ] Validator + Deduper
- [ ] Error recovery + retry
- [ ] HAR export + screenshots

### Phase 3: Extensibilité
- [ ] Plugin system
- [ ] Plugins TeamSnap + BlueSombrero
- [ ] Configuration avancée
- [ ] Tests complets

### Phase 4: Production
- [ ] Logging structuré
- [ ] Métriques/monitoring
- [ ] Rate limiting intelligent
- [ ] Docker image
- [ ] CI/CD

---

## Comparaison avec l'existant

| Feature | Python (existant) | TypeScript (nouveau) |
|---------|-------------------|----------------------|
| Browser automation | ❌ | ✅ Playwright |
| API detection | ⚠️ Manuel | ✅ Automatique |
| Multi-calendriers | ❌ | ✅ UI Navigator |
| Déduplication | ❌ | ✅ Deduper Agent |
| Network logs | ❌ | ✅ HAR export |
| Type safety | ❌ | ✅ TypeScript |
| Plugin system | ❌ | ✅ Extensible |
| Tests | ❌ | ✅ Jest |

---

## Références

- **Playwright** : https://playwright.dev/
- **Collection+JSON** : http://amundsen.com/media-types/collection/
- **Schema.org SportsEvent** : https://schema.org/SportsEvent
- **iCalendar RFC** : https://datatracker.ietf.org/doc/html/rfc5545
