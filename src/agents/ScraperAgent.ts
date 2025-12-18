/**
 * Scraper Agent
 *
 * Extracts matches from DOM/HTML using intelligent selectors
 */

import { Agent } from '../core/Agent';
import { RawMatch, AgentContext, AgentResult } from '../types';
import { Logger } from 'winston';
import { Page } from '@playwright/test';
import * as cheerio from 'cheerio';

interface ScraperInput {
  page: Page;
}

export class ScraperAgent extends Agent<ScraperInput, RawMatch[]> {
  constructor(logger: Logger) {
    super('ScraperAgent', logger);
  }

  async execute(
    input: ScraperInput,
    context: AgentContext
  ): Promise<AgentResult<RawMatch[]>> {
    const { page } = input;
    const { selectors } = context.config;

    this.logger.info('Starting match extraction...');

    // Get page HTML
    const html = await page.content();
    const $ = cheerio.load(html);

    let matches: RawMatch[] = [];

    // Try table extraction
    const tableMatches = this.extractFromTable($, selectors);
    if (tableMatches.length > 0) {
      this.logger.info(`Extracted ${tableMatches.length} matches from table`);
      matches.push(...tableMatches);
    }

    // Try card layout extraction
    const cardMatches = this.extractFromCards($, selectors);
    if (cardMatches.length > 0) {
      this.logger.info(`Extracted ${cardMatches.length} matches from cards`);
      matches.push(...cardMatches);
    }

    // Try JSON-LD extraction
    const jsonLdMatches = await this.extractFromJSONLD(page);
    if (jsonLdMatches.length > 0) {
      this.logger.info(`Extracted ${jsonLdMatches.length} matches from JSON-LD`);
      matches.push(...jsonLdMatches);
    }

    // Deduplicate by raw HTML
    matches = this.deduplicateRaw(matches);

    // Store evidence
    this.storeEvidence(context, 'raw_matches', matches);

    this.logger.info(`Match extraction complete. Found ${matches.length} matches`);

    return {
      success: true,
      data: matches,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private extractFromTable(
    $: cheerio.CheerioAPI,
    selectors: any
  ): RawMatch[] {
    const matches: RawMatch[] = [];

    // Find table
    const tables = $('table[class*="schedule"], table[class*="calendar"]');

    tables.each((_, table) => {
      const rows = $(table).find('tr').slice(1); // Skip header

      rows.each((_, row) => {
        const cells = $(row).find('td');

        if (cells.length < 2) return;

        // Try to find home, away, date
        const match: RawMatch = {
          metadata: {
            selector: 'table > tr',
            rawHTML: $(row).html() || '',
            confidence: 0.7,
          },
        };

        // Heuristic extraction
        cells.each((i, cell) => {
          const text = $(cell).text().trim();

          // Date detection
          if (this.isDate(text)) {
            match.date = text;
          }

          // Team detection (usually columns 1 and 2)
          if (i === 0 || $(cell).hasClass('home')) {
            match.home = text;
          }
          if (i === 1 || $(cell).hasClass('away')) {
            match.away = text;
          }

          // Location detection
          if ($(cell).hasClass('location') || $(cell).hasClass('venue')) {
            match.location = text;
          }
        });

        if (match.home || match.away) {
          matches.push(match);
        }
      });
    });

    return matches;
  }

  private extractFromCards(
    $: cheerio.CheerioAPI,
    selectors: any
  ): RawMatch[] {
    const matches: RawMatch[] = [];

    // Find cards
    const cards = $('div[class*="match-card"], div[class*="game-card"]');

    cards.each((_, card) => {
      const match: RawMatch = {
        metadata: {
          selector: 'div.match-card',
          rawHTML: $(card).html() || '',
          confidence: 0.6,
        },
      };

      // Try to extract teams
      const homeEl = $(card).find(
        '[class*="home"], [class*="team-1"], .home-team'
      );
      if (homeEl.length) {
        match.home = homeEl.text().trim();
      }

      const awayEl = $(card).find(
        '[class*="away"], [class*="team-2"], .away-team'
      );
      if (awayEl.length) {
        match.away = awayEl.text().trim();
      }

      // Try to extract date
      const dateEl = $(card).find(
        '[class*="date"], [class*="time"], time[datetime]'
      );
      if (dateEl.length) {
        match.date =
          dateEl.attr('datetime') || dateEl.text().trim();
      }

      // Try to extract location
      const locationEl = $(card).find('[class*="location"], [class*="venue"]');
      if (locationEl.length) {
        match.location = locationEl.text().trim();
      }

      if (match.home || match.away) {
        matches.push(match);
      }
    });

    return matches;
  }

  private async extractFromJSONLD(page: Page): Promise<RawMatch[]> {
    const matches: RawMatch[] = [];

    try {
      const jsonLdScripts = await page.$$('script[type="application/ld+json"]');

      for (const script of jsonLdScripts) {
        const content = await script.textContent();
        if (!content) continue;

        try {
          const data = JSON.parse(content);

          // Handle single event or array
          const events = Array.isArray(data) ? data : [data];

          for (const event of events) {
            if (event['@type'] === 'SportsEvent') {
              matches.push({
                home:
                  event.homeTeam?.name ||
                  event.competitor?.[0]?.name,
                away:
                  event.awayTeam?.name ||
                  event.competitor?.[1]?.name,
                date: event.startDate,
                location:
                  event.location?.name || event.location?.address?.addressLocality,
                competition: event.name,
                metadata: {
                  selector: 'script[type="application/ld+json"]',
                  rawHTML: JSON.stringify(event),
                  confidence: 1.0,
                },
              });
            }
          }
        } catch {
          // Ignore parse errors
        }
      }
    } catch (error) {
      this.logger.warn('Failed to extract JSON-LD', { error });
    }

    return matches;
  }

  private isDate(text: string): boolean {
    // Simple date detection
    const datePatterns = [
      /\d{4}-\d{2}-\d{2}/, // 2025-12-25
      /\d{2}\/\d{2}\/\d{4}/, // 12/25/2025
      /\w{3}\s+\d{1,2},?\s+\d{4}/, // Dec 25, 2025
    ];

    return datePatterns.some((pattern) => pattern.test(text));
  }

  private deduplicateRaw(matches: RawMatch[]): RawMatch[] {
    const seen = new Set<string>();
    return matches.filter((match) => {
      const key = match.metadata.rawHTML;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }
}
