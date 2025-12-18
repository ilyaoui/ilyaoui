# Sports Calendar Scraper 🏆

> Robust, maintainable, and API-first sports calendar scraper with multi-agent architecture

[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.41-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

### API-First Approach
- ✅ Automatic API detection (XHR, GraphQL, JSON-LD, iCal, RSS)
- ✅ Network interception and analysis
- ✅ Intelligent fallback to scraping
- ✅ Evidence-based extraction (no hallucination)

### Multi-Agent Architecture
- 🤖 **Planner Agent**: Analyzes URL and proposes strategy
- 🔍 **API Scout Agent**: Detects and exploits APIs
- 🧭 **UI Navigator Agent**: Explores UI controls (filters, tabs, dropdowns)
- 📥 **Scraper Agent**: Extracts matches from DOM/HTML
- ✅ **Validator Agent**: Validates and normalizes data
- 🔗 **Deduper Agent**: Cross-calendar deduplication
- 📊 **Reporter Agent**: Generates comprehensive reports

### Robust Features
- ⚡ Playwright-based browser automation
- 🔄 Automatic retry with exponential backoff
- 📸 Screenshots on error
- 📊 HAR network logs
- 🎬 Playwright traces
- 🔌 Plugin system for site-specific scrapers
- 📝 Structured logging
- ✅ Full TypeScript type safety

## 📦 Installation

```bash
# Clone the repository
git clone <repo-url>
cd ilyaoui

# Install dependencies
npm install

# Build TypeScript
npm run build
```

## 🚀 Quick Start

### Basic Usage

```bash
# Scrape a calendar
npx scrape-calendar scrape "https://example.com/calendar"

# With custom output directory
npx scrape-calendar scrape "https://example.com/calendar" --output ./my-output

# Save HAR and screenshots
npx scrape-calendar scrape "https://example.com/calendar" --save-har --save-screenshots

# Use custom config
npx scrape-calendar scrape "https://example.com/calendar" --config ./my-config.json
```

### Generate Config

```bash
# Generate default configuration
npx scrape-calendar config --output ./scraper.config.json

# Validate configuration
npx scrape-calendar validate ./scraper.config.json
```

## 📊 Output Format

### JSON Report

```json
{
  "source_url": "https://example.com/calendar",
  "scraped_at": "2025-12-18T10:30:00Z",
  "strategy_used": "scrape",

  "calendars": [
    {
      "id": "main",
      "name": "2025 Season",
      "url": "https://example.com/calendar",
      "method": "scrape",
      "matches": [
        {
          "home": "Team A",
          "away": "Team B",
          "date_utc": "2025-12-25T14:30:00Z",
          "location": "Stadium 1",
          "competition": "League Championship",
          "sources": ["calendar-1"],
          "metadata": {
            "confidence": 0.85,
            "issues": []
          }
        }
      ]
    }
  ],

  "total_matches": 42,
  "duplicates_removed": 5,

  "performance": {
    "duration_ms": 12500,
    "pages_visited": 3,
    "requests_made": 47
  },

  "artifacts": {
    "har_file": "./output/network.har",
    "screenshots": ["./output/error-1234.png"]
  }
}
```

### CSV Export

```csv
Home,Away,Date (UTC),Location,Competition,Confidence,Sources
Team A,Team B,2025-12-25T14:30:00Z,Stadium 1,League Championship,0.85,calendar-1
```

## ⚙️ Configuration

### scraper.config.json

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
      "div[class*='calendar']"
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
    "saveTraces": false
  },

  "plugins": {
    "enabled": ["teamsnap"],
    "directory": "./plugins"
  }
}
```

## 🏗️ Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLI Entry Point                              │
└────────────────────────┬────────────────────────────────────────────┘
                         ▼
                  ┌──────────────┐
                  │ Orchestrator │
                  └──────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼───┐     ┌────▼────┐    ┌────▼─────┐
    │Planner │     │API Scout│    │Scraper   │
    └────────┘     └─────────┘    └──────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌──────────────┐
                  │  Validator   │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │   Deduper    │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │   Reporter   │
                  └──────────────┘
```

## 🔌 Plugin System

Create custom plugins for site-specific scrapers:

```typescript
// src/plugins/MyPlugin.ts
import { ScraperPlugin } from '../types';

export const MyPlugin: ScraperPlugin = {
  name: 'my-plugin',
  domains: ['example.com'],

  async detect(page) {
    return page.url().includes('example.com');
  },

  async extractAPI(page) {
    // Detect and return API endpoints
    return {
      found: true,
      endpoints: [...],
      dataFormat: 'json',
      confidence: 1.0,
    };
  },

  async extractMatches(page) {
    // Extract matches using site-specific selectors
    return [...];
  },
};
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm test -- --coverage
```

## 📝 Examples

### Example 1: Scrape TeamSnap Calendar

```bash
npx scrape-calendar scrape "https://tournaments.teamsnap.com/event/12345" \
  --output ./teamsnap-output \
  --save-har \
  --format json,csv
```

### Example 2: Use as Library

```typescript
import { Orchestrator, createLogger, DEFAULT_CONFIG } from 'sports-calendar-scraper';

const logger = createLogger('./logs');
const orchestrator = new Orchestrator(logger, DEFAULT_CONFIG);

const report = await orchestrator.scrape('https://example.com/calendar');

console.log(`Found ${report.total_matches} matches`);
```

### Example 3: Custom Agent Pipeline

```typescript
import { PlannerAgent, APIScoutAgent, createLogger } from 'sports-calendar-scraper';

const logger = createLogger('./logs');
const planner = new PlannerAgent(logger);
const apiScout = new APIScoutAgent(logger);

const context = {
  url: 'https://example.com/calendar',
  config: DEFAULT_CONFIG,
  logger,
  state: new Map(),
};

const plan = await planner.run({ url: context.url }, context);
const apiDiscovery = await apiScout.run({ page, url: context.url }, context);

console.log('Strategy:', plan.data?.strategy);
console.log('API found:', apiDiscovery.data?.found);
```

## 🐛 Troubleshooting

### Issue: Browser launch fails

**Solution:**
```bash
# Install Playwright browsers
npx playwright install
```

### Issue: No matches extracted

**Solution:**
1. Check selectors in config
2. Enable screenshots to debug: `--save-screenshots`
3. Check HAR file for network activity: `--save-har`

### Issue: Date parsing fails

**Solution:**
Add custom date format in ValidatorAgent or create a plugin for the site.

## 🔒 Rate Limiting & Best Practices

- ✅ Default delay: 1000ms between requests
- ✅ Respect robots.txt
- ✅ Use identifiable user-agent
- ✅ Limit concurrent requests
- ❌ Do not overload servers
- ❌ Do not scrape personal data without consent

## 📚 API Reference

See [TypeScript types](./src/types/index.ts) for complete API reference.

### Main Classes

- **Orchestrator**: Main coordinator for scraping pipeline
- **Agent**: Base class for all agents
- **PlannerAgent**: Strategy planning
- **APIScoutAgent**: API detection
- **ScraperAgent**: DOM extraction
- **ValidatorAgent**: Data validation
- **DeduperAgent**: Deduplication

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Run `npm test` and `npm run lint`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 🙏 Acknowledgments

- **Playwright** for robust browser automation
- **TypeScript** for type safety
- **Winston** for structured logging

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: https://github.com/yourrepo/issues
- 📖 Docs: https://docs.example.com

---

**Made with 🏆 for the sports community**
