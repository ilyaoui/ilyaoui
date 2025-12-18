/**
 * ExposureEvents Plugin
 *
 * Specialized scraper for basketball.exposureevents.com
 */

import { ScraperPlugin, APIDiscovery, RawMatch, CalendarView } from '../types';
import { Page } from '@playwright/test';

export const ExposureEventsPlugin: ScraperPlugin = {
  name: 'exposure-events',
  domains: ['exposureevents.com', 'basketball.exposureevents.com'],

  async detect(page: Page): Promise<boolean> {
    const url = page.url();
    return url.includes('exposureevents.com');
  },

  async extractAPI(page: Page): Promise<APIDiscovery | null> {
    // ExposureEvents might have API endpoints
    const apiEndpoints: any[] = [];

    // Wait for potential API calls
    await page.waitForTimeout(3000);

    // Check for data attributes or embedded JSON
    try {
      const dataScripts = await page.$$('script[type="application/json"]');
      for (const script of dataScripts) {
        const content = await script.textContent();
        if (content) {
          apiEndpoints.push({
            url: page.url(),
            method: 'GET',
            headers: {},
            sampleResponse: JSON.parse(content),
            detected_by: 'embedded-json',
          });
        }
      }
    } catch {
      // No embedded JSON
    }

    if (apiEndpoints.length > 0) {
      return {
        found: true,
        endpoints: apiEndpoints,
        dataFormat: 'json',
        confidence: 0.8,
      };
    }

    return null;
  },

  async navigateFilters(page: Page): Promise<CalendarView[]> {
    const views: CalendarView[] = [];

    console.log('[ExposureEvents] Looking for schedule buttons...');

    // Wait for page to load (use domcontentloaded to avoid timeout)
    await page.waitForLoadState('domcontentloaded');

    // Look for common schedule/bracket buttons on ExposureEvents
    const scheduleSelectors = [
      'a:has-text("Schedule")',
      'button:has-text("Schedule")',
      'a:has-text("Schedules")',
      'button:has-text("Schedules")',
      '[href*="schedule"]',
      '[class*="schedule"]',
      '[class*="Schedule"]',
      'a[class*="nav"]',
      'button[class*="tab"]',
      '.nav-link',
      '.tab-link',
    ];

    for (const selector of scheduleSelectors) {
      try {
        const buttons = await page.$$(selector);
        console.log(`[ExposureEvents] Found ${buttons.length} elements with selector: ${selector}`);

        for (const button of buttons) {
          const text = await button.textContent();
          const isVisible = await button.isVisible();

          if (isVisible && text && text.toLowerCase().includes('schedule')) {
            console.log(`[ExposureEvents] Clicking on: "${text}"`);

            // Click and wait for navigation
            await button.click();
            await page.waitForLoadState('domcontentloaded');
            await page.waitForTimeout(3000);

            // Capture this view
            views.push({
              id: `schedule-${views.length}`,
              signature: page.url(),
              url: page.url(),
              controls: [],
              matchCount: await countMatches(page),
              timestamp: Date.now(),
            });

            console.log(`[ExposureEvents] Captured view: ${page.url()}`);
          }
        }
      } catch (error) {
        console.log(`[ExposureEvents] Error with selector ${selector}:`, error);
      }
    }

    return views;
  },

  async extractMatches(page: Page): Promise<RawMatch[]> {
    const matches: RawMatch[] = [];

    console.log('[ExposureEvents] Extracting matches...');

    // Wait for content to load
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // ExposureEvents specific selectors
    const gameSelectors = [
      'div[class*="game"]',
      'div[class*="Game"]',
      'tr[class*="game"]',
      'div[class*="match"]',
      'div[class*="schedule-item"]',
      '.game-row',
      '.schedule-row',
    ];

    for (const gameSelector of gameSelectors) {
      try {
        const gameElements = await page.$$(gameSelector);
        console.log(`[ExposureEvents] Found ${gameElements.length} games with selector: ${gameSelector}`);

        for (const game of gameElements) {
          try {
            const html = await game.innerHTML();

            // Try to extract team names
            const teamSelectors = [
              '[class*="team"]',
              '[class*="Team"]',
              'span',
              'div',
            ];

            let teams: string[] = [];
            for (const teamSel of teamSelectors) {
              const teamElements = await game.$$(teamSel);
              for (const team of teamElements) {
                const text = await team.textContent();
                if (text && text.trim().length > 2 && !text.includes(':')) {
                  teams.push(text.trim());
                }
              }
              if (teams.length >= 2) break;
            }

            // Extract date/time
            const timeSelectors = [
              '[class*="time"]',
              '[class*="Time"]',
              '[class*="date"]',
              '[class*="Date"]',
              'time',
            ];

            let dateText = '';
            for (const timeSel of timeSelectors) {
              const timeEl = await game.$(timeSel);
              if (timeEl) {
                dateText = await timeEl.textContent() || '';
                if (dateText) break;
              }
            }

            // Extract location
            const locationSelectors = [
              '[class*="court"]',
              '[class*="Court"]',
              '[class*="venue"]',
              '[class*="Venue"]',
              '[class*="location"]',
            ];

            let location = '';
            for (const locSel of locationSelectors) {
              const locEl = await game.$(locSel);
              if (locEl) {
                location = await locEl.textContent() || '';
                if (location) break;
              }
            }

            if (teams.length >= 2 || dateText) {
              matches.push({
                home: teams[0] || '',
                away: teams[1] || '',
                date: dateText,
                location: location || undefined,
                metadata: {
                  selector: gameSelector,
                  rawHTML: html,
                  confidence: teams.length >= 2 ? 0.8 : 0.5,
                },
              });
            }
          } catch (error) {
            console.log('[ExposureEvents] Error extracting game:', error);
          }
        }

        if (matches.length > 0) {
          console.log(`[ExposureEvents] Extracted ${matches.length} matches`);
          break; // Found matches, no need to try other selectors
        }
      } catch (error) {
        console.log(`[ExposureEvents] Error with selector ${gameSelector}:`, error);
      }
    }

    return matches;
  },
};

// Helper function to count matches
async function countMatches(page: Page): Promise<number> {
  const selectors = [
    'div[class*="game"]',
    'tr[class*="game"]',
    '.game-row',
    '.schedule-row',
  ];

  for (const selector of selectors) {
    try {
      const count = await page.$$eval(selector, (els) => els.length);
      if (count > 0) return count;
    } catch {
      continue;
    }
  }

  return 0;
}
