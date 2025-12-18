/**
 * Custom Configuration Example
 *
 * Shows how to use custom configuration
 */

import { Orchestrator, createLogger, ScraperConfig } from '../src';

async function main() {
  const logger = createLogger('./logs');

  // Custom configuration
  const config: ScraperConfig = {
    scraping: {
      headless: false, // Run in non-headless mode for debugging
      timeout: 60000, // Longer timeout
      userAgent:
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      viewport: { width: 1920, height: 1080 },
    },

    limits: {
      maxInteractions: 100, // More interactions allowed
      maxPages: 50,
      maxDepth: 10,
      requestDelay: 2000, // Slower rate limiting
    },

    selectors: {
      calendar: ['#my-calendar', '.schedule-table'],
      match: ['.match-row', '.game-item'],
      home: ['.team-home', '.home'],
      away: ['.team-away', '.away'],
      date: ['.match-date', 'time'],
      location: ['.venue', '.location'],
    },

    output: {
      directory: './custom-output',
      formats: ['json', 'csv'],
      saveHAR: true,
      saveScreenshots: true,
      saveTraces: true, // Enable traces
    },

    plugins: {
      enabled: ['teamsnap'],
      directory: './src/plugins',
    },
  };

  const orchestrator = new Orchestrator(logger, config);

  const url = process.argv[2] || 'https://example.com/calendar';

  console.log(`\n🚀 Scraping with custom config: ${url}\n`);

  try {
    const report = await orchestrator.scrape(url);

    console.log('\n✅ Complete!');
    console.log(`📊 Found ${report.total_matches} matches`);
    console.log(`📁 Output: ${config.output.directory}/`);
  } catch (error: any) {
    console.error('\n❌ Failed:', error.message);
    process.exit(1);
  }
}

main();
