/**
 * Basic Usage Example
 *
 * Shows how to use the scraper as a library
 */

import { Orchestrator, createLogger, DEFAULT_CONFIG } from '../src';

async function main() {
  // Create logger
  const logger = createLogger('./logs');

  // Create orchestrator with default config
  const orchestrator = new Orchestrator(logger, DEFAULT_CONFIG);

  // Scrape a calendar
  const url = 'https://example.com/sports/calendar';

  console.log(`\n🚀 Scraping calendar from: ${url}\n`);

  try {
    const report = await orchestrator.scrape(url);

    // Print summary
    console.log('\n✅ Scraping complete!\n');
    console.log(`📊 Total matches: ${report.total_matches}`);
    console.log(`📅 Calendars found: ${report.calendars.length}`);
    console.log(`🔄 Duplicates removed: ${report.duplicates_removed}`);
    console.log(`⏱️  Duration: ${report.performance.duration_ms}ms`);

    // Print first 5 matches
    console.log('\n📋 First 5 matches:\n');

    const matches = report.calendars.flatMap((c) => c.matches).slice(0, 5);

    for (const match of matches) {
      console.log(
        `  ${match.date_utc.split('T')[0]} | ${match.home} vs ${match.away}`
      );
      if (match.location) {
        console.log(`    📍 ${match.location}`);
      }
    }

    // Print API endpoints if found
    if (report.api_endpoints && report.api_endpoints.length > 0) {
      console.log('\n🎯 API Endpoints discovered:\n');
      for (const endpoint of report.api_endpoints) {
        console.log(`  ${endpoint.method} ${endpoint.url}`);
      }
    }
  } catch (error: any) {
    console.error('\n❌ Scraping failed:', error.message);
    process.exit(1);
  }
}

main();
