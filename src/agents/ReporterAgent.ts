/**
 * Reporter Agent
 *
 * Generates final scraping report with all evidence
 */

import { Agent } from '../core/Agent';
import {
  ScrapingReport,
  Calendar,
  DeduplicatedMatch,
  ScrapingError,
  APIDiscovery,
  Plan,
  AgentContext,
  AgentResult,
} from '../types';
import { Logger } from 'winston';

interface ReporterInput {
  url: string;
  startTime: number;
}

export class ReporterAgent extends Agent<ReporterInput, ScrapingReport> {
  constructor(logger: Logger) {
    super('ReporterAgent', logger);
  }

  async execute(
    input: ReporterInput,
    context: AgentContext
  ): Promise<AgentResult<ScrapingReport>> {
    const { url, startTime } = input;

    this.logger.info('Generating final report...');

    // Gather evidence from context
    const plan: Plan = this.getEvidence(context, 'plan');
    const apiDiscovery: APIDiscovery = this.getEvidence(context, 'api_discovery');
    const matches: DeduplicatedMatch[] =
      this.getEvidence(context, 'deduplicated_matches') || [];

    // Build calendars
    const calendars: Calendar[] = this.buildCalendars(context, matches);

    // Count duplicates
    const totalRawMatches = this.countRawMatches(context);
    const duplicatesRemoved = totalRawMatches - matches.length;

    // Gather errors
    const errors: ScrapingError[] = this.getEvidence(context, 'errors') || [];

    // Build report
    const report: ScrapingReport = {
      source_url: url,
      scraped_at: new Date().toISOString(),
      strategy_used: plan?.strategy || 'scrape',

      calendars,
      total_matches: matches.length,
      duplicates_removed: duplicatesRemoved,

      api_endpoints: apiDiscovery?.endpoints,
      selectors_used: this.getSelectorsUsed(context),
      errors,

      performance: {
        duration_ms: Date.now() - startTime,
        pages_visited: this.countPagesVisited(context),
        requests_made: this.countRequestsMade(context),
      },

      artifacts: {
        har_file: this.getEvidence(context, 'har_file'),
        screenshots: this.getEvidence(context, 'screenshots') || [],
        trace_file: this.getEvidence(context, 'trace_file'),
      },
    };

    // Store report
    this.storeEvidence(context, 'report', report);

    this.logger.info('Report generation complete');

    return {
      success: true,
      data: report,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private buildCalendars(
    context: AgentContext,
    matches: DeduplicatedMatch[]
  ): Calendar[] {
    const calendars: Calendar[] = [];

    // Group matches by source calendar
    const matchesByCalendar = new Map<string, DeduplicatedMatch[]>();

    for (const match of matches) {
      for (const source of match.sources) {
        if (!matchesByCalendar.has(source)) {
          matchesByCalendar.set(source, []);
        }
        matchesByCalendar.get(source)!.push(match);
      }
    }

    // Build calendar objects
    for (const [calendarId, calendarMatches] of matchesByCalendar) {
      calendars.push({
        id: calendarId,
        name: calendarId, // TODO: extract actual name
        url: context.url,
        method: 'scrape', // TODO: determine method
        matches: calendarMatches,
        evidence: {
          selectors: this.getSelectorsUsed(context),
          network_calls: this.getEvidence(context, 'network_calls'),
        },
      });
    }

    return calendars;
  }

  private countRawMatches(context: AgentContext): number {
    const rawMatches = this.getEvidence(context, 'raw_matches') || [];
    return rawMatches.length;
  }

  private getSelectorsUsed(context: AgentContext): string[] {
    const selectors = new Set<string>();

    const rawMatches = this.getEvidence(context, 'raw_matches') || [];
    for (const match of rawMatches) {
      if (match.metadata?.selector) {
        selectors.add(match.metadata.selector);
      }
    }

    return Array.from(selectors);
  }

  private countPagesVisited(context: AgentContext): number {
    const graph = this.getEvidence(context, 'calendar_graph');
    return graph?.views?.length || 1;
  }

  private countRequestsMade(context: AgentContext): number {
    const networkCalls = this.getEvidence(context, 'network_calls') || [];
    return networkCalls.length;
  }
}
