# Quick Start Guide 🚀

## Installation

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Install Playwright browsers
npx playwright install chromium
```

## Basic Usage

### 1. Scrape a calendar (CLI)

```bash
# Basic scraping
npx scrape-calendar scrape "https://example.com/sports/calendar"

# With options
npx scrape-calendar scrape "https://example.com/calendar" \
  --output ./my-results \
  --save-har \
  --save-screenshots \
  --format json,csv
```

### 2. Use as a library

```typescript
import { Orchestrator, createLogger, DEFAULT_CONFIG } from './src';

const logger = createLogger('./logs');
const orchestrator = new Orchestrator(logger, DEFAULT_CONFIG);

const report = await orchestrator.scrape('https://example.com/calendar');

console.log(`Found ${report.total_matches} matches`);
```

### 3. Run the examples

```bash
# Basic example
npx tsx examples/basic-usage.ts

# Custom config example
npx tsx examples/custom-config.ts "https://example.com/calendar"
```

## Configuration

### Generate default config

```bash
npx scrape-calendar config --output ./my-config.json
```

### Edit configuration

```json
{
  "scraping": {
    "headless": true,
    "timeout": 30000
  },
  "limits": {
    "maxInteractions": 50,
    "maxPages": 20
  },
  "output": {
    "directory": "./output",
    "formats": ["json", "csv"],
    "saveHAR": true
  }
}
```

### Use custom config

```bash
npx scrape-calendar scrape "https://example.com/calendar" \
  --config ./my-config.json
```

## Output

The scraper creates:

```
output/
├── report.json          # Full scraping report
├── matches.csv          # Matches in CSV format
├── network.har          # Network activity log (if enabled)
├── screenshots/         # Error screenshots (if enabled)
├── videos/             # Session recordings (if enabled)
└── logs/
    ├── combined.log
    └── error.log
```

## Common Use Cases

### Scrape TeamSnap Calendar

```bash
npx scrape-calendar scrape \
  "https://tournaments.teamsnap.com/event/12345" \
  --output ./teamsnap-results
```

### Debug Scraping Issues

```bash
# Run in non-headless mode with screenshots
npx scrape-calendar scrape "https://example.com/calendar" \
  --headless false \
  --save-screenshots \
  --save-har \
  --log-level debug
```

### Extract API Endpoints

```bash
# The scraper will automatically detect APIs
npx scrape-calendar scrape "https://example.com/calendar" \
  --save-har

# Check report.json for discovered endpoints
cat output/report.json | jq '.api_endpoints'
```

## Troubleshooting

### Issue: Browser won't launch

```bash
# Install Playwright browsers
npx playwright install
```

### Issue: No matches found

1. Check if the page loads correctly
2. Run with `--headless false` to see what's happening
3. Use `--save-screenshots` to capture the page state
4. Adjust selectors in config

### Issue: Rate limiting

```bash
# Increase delay between requests
# Edit config.json:
{
  "limits": {
    "requestDelay": 2000  // 2 seconds
  }
}
```

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Read [README_SCRAPER.md](./README_SCRAPER.md) for complete documentation
- Create custom plugins for specific sites (see `src/plugins/`)
- Run tests: `npm test`

## Support

- 📖 Documentation: [README_SCRAPER.md](./README_SCRAPER.md)
- 🏗️ Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 🐛 Issues: Create an issue on GitHub
