/**
 * Validator Agent
 *
 * Validates and normalizes match data
 */

import { Agent } from '../core/Agent';
import {
  RawMatch,
  ValidatedMatch,
  ValidationIssue,
  AgentContext,
  AgentResult,
} from '../types';
import { Logger } from 'winston';
import { parseISO, parse, isValid } from 'date-fns';
import { zonedTimeToUtc } from 'date-fns-tz';

interface ValidatorInput {
  rawMatches: RawMatch[];
  timezone?: string;
}

export class ValidatorAgent extends Agent<ValidatorInput, ValidatedMatch[]> {
  constructor(logger: Logger) {
    super('ValidatorAgent', logger);
  }

  async execute(
    input: ValidatorInput,
    context: AgentContext
  ): Promise<AgentResult<ValidatedMatch[]>> {
    const { rawMatches, timezone = 'America/New_York' } = input;

    this.logger.info(`Validating ${rawMatches.length} raw matches...`);

    const validated: ValidatedMatch[] = [];

    for (const raw of rawMatches) {
      try {
        const match = this.validateMatch(raw, timezone);
        if (match) {
          validated.push(match);
        }
      } catch (error) {
        this.logger.warn('Failed to validate match', { raw, error });
      }
    }

    this.logger.info(
      `Validation complete. ${validated.length}/${rawMatches.length} matches valid`
    );

    // Store evidence
    this.storeEvidence(context, 'validated_matches', validated);

    return {
      success: true,
      data: validated,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private validateMatch(
    raw: RawMatch,
    timezone: string
  ): ValidatedMatch | null {
    const issues: ValidationIssue[] = [];

    // Validate home team
    let home = this.normalizeTeamName(raw.home);
    if (!home) {
      issues.push({
        field: 'home',
        severity: 'error',
        message: 'Home team is empty',
      });
      return null;
    }

    // Validate away team
    let away = this.normalizeTeamName(raw.away);
    if (!away) {
      issues.push({
        field: 'away',
        severity: 'warning',
        message: 'Away team is empty',
      });
      // Allow missing away team (might be a time slot)
    }

    // Validate date
    let date_utc: string;
    try {
      date_utc = this.parseDate(raw.date, raw.time, timezone);
    } catch (error) {
      issues.push({
        field: 'date',
        severity: 'error',
        message: `Invalid date: ${raw.date}`,
      });
      return null;
    }

    // Check for same team
    if (home === away) {
      issues.push({
        field: 'teams',
        severity: 'warning',
        message: 'Home and away teams are the same',
      });
    }

    // Normalize location
    const location = this.normalizeLocation(raw.location);

    // Normalize competition
    const competition = this.normalizeText(raw.competition);

    // Calculate confidence
    const confidence = this.calculateConfidence(raw, issues);

    return {
      home,
      away: away || '',
      date_utc,
      location,
      competition,
      metadata: {
        raw: raw.metadata.rawHTML,
        confidence,
        issues,
      },
    };
  }

  private normalizeTeamName(team?: string): string {
    if (!team) return '';

    return team
      .trim()
      .replace(/\s+/g, ' ') // Collapse whitespace
      .replace(/[^\w\s-]/g, ''); // Remove special chars
  }

  private normalizeLocation(location?: string): string | undefined {
    if (!location) return undefined;

    return this.normalizeText(location);
  }

  private normalizeText(text?: string): string | undefined {
    if (!text) return undefined;

    return text.trim().replace(/\s+/g, ' ');
  }

  private parseDate(
    dateStr?: string,
    timeStr?: string,
    timezone: string = 'America/New_York'
  ): string {
    if (!dateStr) {
      throw new Error('Date is required');
    }

    // Combine date and time if both provided
    const fullDateStr = timeStr ? `${dateStr} ${timeStr}` : dateStr;

    // Try multiple date formats
    const formats = [
      // ISO 8601
      'yyyy-MM-dd HH:mm:ss',
      'yyyy-MM-dd HH:mm',
      "yyyy-MM-dd'T'HH:mm:ss",
      "yyyy-MM-dd'T'HH:mm:ssXXX",

      // US formats
      'MM/dd/yyyy HH:mm',
      'MM/dd/yyyy h:mm a',
      'MMM dd, yyyy h:mm a',
      'MMM dd, yyyy',

      // European formats
      'dd/MM/yyyy HH:mm',
      'dd-MM-yyyy HH:mm',
    ];

    // Try parsing with each format
    for (const format of formats) {
      try {
        const parsed = parse(fullDateStr, format, new Date());
        if (isValid(parsed)) {
          // Convert to UTC
          const utc = zonedTimeToUtc(parsed, timezone);
          return utc.toISOString();
        }
      } catch {
        // Try next format
      }
    }

    // Try ISO parse as fallback
    try {
      const parsed = parseISO(fullDateStr);
      if (isValid(parsed)) {
        return parsed.toISOString();
      }
    } catch {
      // Ignore
    }

    throw new Error(`Could not parse date: ${fullDateStr}`);
  }

  private calculateConfidence(
    raw: RawMatch,
    issues: ValidationIssue[]
  ): number {
    let confidence = raw.metadata.confidence;

    // Penalize for missing fields
    if (!raw.home) confidence -= 0.3;
    if (!raw.away) confidence -= 0.1;
    if (!raw.date) confidence -= 0.3;
    if (!raw.location) confidence -= 0.1;

    // Penalize for validation issues
    const errors = issues.filter((i) => i.severity === 'error').length;
    const warnings = issues.filter((i) => i.severity === 'warning').length;

    confidence -= errors * 0.2;
    confidence -= warnings * 0.05;

    return Math.max(0, Math.min(1, confidence));
  }
}
