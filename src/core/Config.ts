/**
 * Configuration management
 */

import { ScraperConfig } from '../types';
import fs from 'fs';
import path from 'path';

export const DEFAULT_CONFIG: ScraperConfig = {
  scraping: {
    headless: true,
    timeout: 30000,
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
  },

  limits: {
    maxInteractions: 50,
    maxPages: 20,
    maxDepth: 5,
    requestDelay: 1000,
  },

  selectors: {
    calendar: [
      'table[class*="schedule"]',
      'table[class*="calendar"]',
      'div[class*="calendar"]',
      '[data-testid="calendar"]',
    ],
    match: [
      'tr[class*="match"]',
      'tr[class*="game"]',
      'div[class*="match-card"]',
      'div[class*="game-card"]',
      'article[class*="game"]',
    ],
    home: [
      '[class*="home"]',
      '[class*="team-1"]',
      '[class*="team-a"]',
      '.home-team',
    ],
    away: [
      '[class*="away"]',
      '[class*="team-2"]',
      '[class*="team-b"]',
      '.away-team',
    ],
    date: [
      '[class*="date"]',
      '[class*="time"]',
      'time[datetime]',
      '[datetime]',
    ],
    location: [
      '[class*="location"]',
      '[class*="venue"]',
      '[class*="field"]',
    ],
  },

  output: {
    directory: './output',
    formats: ['json', 'csv'],
    saveHAR: true,
    saveScreenshots: true,
    saveTraces: true,
  },

  plugins: {
    enabled: [],
    directory: './plugins',
  },
};

export function loadConfig(configPath?: string): ScraperConfig {
  if (!configPath) {
    return DEFAULT_CONFIG;
  }

  try {
    const configFile = fs.readFileSync(configPath, 'utf-8');
    const userConfig = JSON.parse(configFile);

    // Deep merge with defaults
    return mergeConfig(DEFAULT_CONFIG, userConfig);
  } catch (error) {
    console.warn(`Failed to load config from ${configPath}, using defaults`);
    return DEFAULT_CONFIG;
  }
}

function mergeConfig(
  defaults: ScraperConfig,
  overrides: Partial<ScraperConfig>
): ScraperConfig {
  return {
    scraping: { ...defaults.scraping, ...overrides.scraping },
    limits: { ...defaults.limits, ...overrides.limits },
    selectors: { ...defaults.selectors, ...overrides.selectors },
    output: { ...defaults.output, ...overrides.output },
    plugins: { ...defaults.plugins, ...overrides.plugins },
  };
}

export function saveConfig(config: ScraperConfig, outputPath: string): void {
  fs.writeFileSync(outputPath, JSON.stringify(config, null, 2));
}
