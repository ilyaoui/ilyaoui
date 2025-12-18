#!/usr/bin/env node

/**
 * CLI Entry Point for Sports Calendar Scraper
 */

import { Command } from 'commander';
import { Orchestrator } from './core/Orchestrator';
import { createLogger } from './core/Logger';
import { loadConfig } from './core/Config';
import path from 'path';
import fs from 'fs';

const program = new Command();

program
  .name('scrape-calendar')
  .description('API-first sports calendar scraper with multi-agent architecture')
  .version('1.0.0');

program
  .command('scrape')
  .description('Scrape a sports calendar from URL')
  .argument('<url>', 'URL of the calendar to scrape')
  .option('-o, --output <dir>', 'Output directory', './output')
  .option('-c, --config <file>', 'Configuration file')
  .option('--headless <boolean>', 'Run browser in headless mode', 'true')
  .option('--format <formats>', 'Output formats (json,csv)', 'json,csv')
  .option('--save-har', 'Save network HAR file', false)
  .option('--save-screenshots', 'Save screenshots on error', false)
  .option('--save-traces', 'Save Playwright traces', false)
  .option('--log-level <level>', 'Log level (debug, info, warn, error)', 'info')
  .action(async (url: string, options: any) => {
    try {
      // Setup logging
      const logDir = path.join(options.output, 'logs');
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }

      process.env.LOG_LEVEL = options.logLevel;
      const logger = createLogger(logDir);

      logger.info('Sports Calendar Scraper starting...');
      logger.info(`URL: ${url}`);

      // Load config
      let config = loadConfig(options.config);

      // Override with CLI options
      config.output.directory = options.output;
      config.scraping.headless = options.headless === 'true';
      config.output.formats = options.format.split(',');
      config.output.saveHAR = options.saveHar;
      config.output.saveScreenshots = options.saveScreenshots;
      config.output.saveTraces = options.saveTraces;

      logger.info('Configuration loaded', { config });

      // Create orchestrator
      const orchestrator = new Orchestrator(logger, config);

      // Run scraper
      const report = await orchestrator.scrape(url);

      // Print summary
      console.log('\n✅ Scraping complete!');
      console.log(`📊 Total matches: ${report.total_matches}`);
      console.log(`📅 Calendars found: ${report.calendars.length}`);
      console.log(`🔄 Duplicates removed: ${report.duplicates_removed}`);
      console.log(`⏱️  Duration: ${report.performance.duration_ms}ms`);
      console.log(`📄 Output: ${options.output}/report.json`);

      if (report.api_endpoints && report.api_endpoints.length > 0) {
        console.log(`\n🎯 API Endpoints discovered:`);
        for (const endpoint of report.api_endpoints) {
          console.log(`  - ${endpoint.method} ${endpoint.url}`);
        }
      }

      if (report.errors.length > 0) {
        console.log(`\n⚠️  Errors: ${report.errors.length}`);
        for (const error of report.errors.slice(0, 5)) {
          console.log(`  - ${error.message}`);
        }
      }

      process.exit(0);
    } catch (error: any) {
      console.error('❌ Scraping failed:', error.message);
      console.error(error.stack);
      process.exit(1);
    }
  });

program
  .command('config')
  .description('Generate default configuration file')
  .option('-o, --output <file>', 'Output file', './scraper.config.json')
  .action((options: any) => {
    const { DEFAULT_CONFIG, saveConfig } = require('./core/Config');

    saveConfig(DEFAULT_CONFIG, options.output);
    console.log(`✅ Configuration saved to ${options.output}`);
  });

program
  .command('validate')
  .description('Validate a configuration file')
  .argument('<file>', 'Configuration file to validate')
  .action((file: string) => {
    try {
      const config = loadConfig(file);
      console.log('✅ Configuration is valid');
      console.log(JSON.stringify(config, null, 2));
    } catch (error: any) {
      console.error('❌ Invalid configuration:', error.message);
      process.exit(1);
    }
  });

program.parse();
