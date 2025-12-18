/**
 * Deduper Agent
 *
 * Deduplicates matches across calendars using stable keys
 */

import { Agent } from '../core/Agent';
import {
  ValidatedMatch,
  DeduplicatedMatch,
  AgentContext,
  AgentResult,
} from '../types';
import { Logger } from 'winston';
import crypto from 'crypto';

interface DeduperInput {
  matches: ValidatedMatch[];
  calendarId: string;
}

export class DeduperAgent extends Agent<DeduperInput, DeduplicatedMatch[]> {
  private matchMap: Map<string, DeduplicatedMatch> = new Map();

  constructor(logger: Logger) {
    super('DeduperAgent', logger);
  }

  async execute(
    input: DeduperInput,
    context: AgentContext
  ): Promise<AgentResult<DeduplicatedMatch[]>> {
    const { matches, calendarId } = input;

    this.logger.info(`Deduplicating ${matches.length} matches for calendar ${calendarId}`);

    // Get existing matches from context (cross-calendar deduplication)
    const existingMatches =
      this.getEvidence(context, 'deduplicated_matches') || [];

    // Initialize map with existing matches
    for (const match of existingMatches) {
      this.matchMap.set(match.duplicateKey, match);
    }

    // Process new matches
    for (const match of matches) {
      const key = this.computeMatchKey(match);

      if (this.matchMap.has(key)) {
        // Merge with existing match
        const existing = this.matchMap.get(key)!;
        existing.sources.push(calendarId);

        // Keep match with higher confidence
        if (match.metadata.confidence > existing.metadata.confidence) {
          this.matchMap.set(key, {
            ...match,
            sources: existing.sources,
            duplicateKey: key,
          });
        }
      } else {
        // Add new match
        this.matchMap.set(key, {
          ...match,
          sources: [calendarId],
          duplicateKey: key,
        });
      }
    }

    const deduplicated = Array.from(this.matchMap.values());

    // Store evidence
    this.storeEvidence(context, 'deduplicated_matches', deduplicated);

    this.logger.info(
      `Deduplication complete. ${deduplicated.length} unique matches (removed ${matches.length - deduplicated.length} duplicates)`
    );

    return {
      success: true,
      data: deduplicated,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private computeMatchKey(match: ValidatedMatch): string {
    // Normalize team names for comparison
    const homeNorm = this.normalizeForKey(match.home);
    const awayNorm = this.normalizeForKey(match.away);

    // Sort teams to handle reversed home/away
    const [team1, team2] = [homeNorm, awayNorm].sort();

    // Extract date only (ignore time for fuzzy matching)
    const dateOnly = match.date_utc.split('T')[0];

    // Normalize location
    const locationNorm = this.normalizeForKey(match.location || '');

    // Create key
    const parts = [team1, team2, dateOnly, locationNorm].filter((p) => p);

    return crypto.createHash('sha256').update(parts.join('|')).digest('hex');
  }

  private normalizeForKey(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, '') // Remove punctuation
      .replace(/\s+/g, ' ') // Collapse whitespace
      .trim();
  }
}
