/**
 * TeamSnap Plugin
 *
 * Specialized scraper for TeamSnap calendars
 */

import { ScraperPlugin, APIDiscovery, RawMatch } from '../types';
import { Page } from '@playwright/test';

export const TeamSnapPlugin: ScraperPlugin = {
  name: 'teamsnap',
  domains: ['teamsnap.com', 'tournaments.teamsnap.com'],

  async detect(page: Page): Promise<boolean> {
    const url = page.url();
    return (
      url.includes('teamsnap.com') ||
      (await page.evaluate(() =>
        document.body.innerHTML.includes('teamsnap')
      ))
    );
  },

  async extractAPI(page: Page): Promise<APIDiscovery | null> {
    // TeamSnap uses api.teamsnap.com/v3
    const apiEndpoints: any[] = [];

    // Listen for API calls
    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('api.teamsnap.com')) {
        try {
          const data = await response.json();
          apiEndpoints.push({
            url,
            method: 'GET',
            headers: response.request().headers(),
            sampleResponse: data,
            detected_by: 'network',
          });
        } catch {
          // Not JSON
        }
      }
    });

    // Wait for page to load
    await page.waitForTimeout(2000);

    if (apiEndpoints.length > 0) {
      return {
        found: true,
        endpoints: apiEndpoints,
        dataFormat: 'json',
        confidence: 1.0,
      };
    }

    return null;
  },

  async extractMatches(page: Page): Promise<RawMatch[]> {
    const matches: RawMatch[] = [];

    try {
      // TeamSnap specific selectors
      const gameRows = await page.$$('.game-row, tr[data-game-id]');

      for (const row of gameRows) {
        const home = await row.$eval(
          '.home-team, .team-name:first-child',
          (el) => el.textContent?.trim()
        );
        const away = await row.$eval(
          '.away-team, .team-name:last-child',
          (el) => el.textContent?.trim()
        );
        const date = await row.$eval(
          '.game-time, time[datetime]',
          (el) =>
            (el as HTMLElement).getAttribute('datetime') ||
            el.textContent?.trim()
        );
        const location = await row.$eval('.location, .venue', (el) =>
          el.textContent?.trim()
        );

        matches.push({
          home,
          away,
          date,
          location,
          metadata: {
            selector: '.game-row',
            rawHTML: await row.innerHTML(),
            confidence: 0.9,
          },
        });
      }
    } catch (error) {
      console.warn('TeamSnap extraction failed', error);
    }

    return matches;
  },
};
