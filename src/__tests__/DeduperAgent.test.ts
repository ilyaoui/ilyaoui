/**
 * Tests for DeduperAgent
 */

import { DeduperAgent } from '../agents/DeduperAgent';
import { createLogger } from '../core/Logger';
import { DEFAULT_CONFIG } from '../core/Config';
import { AgentContext, ValidatedMatch } from '../types';

describe('DeduperAgent', () => {
  let agent: DeduperAgent;
  let context: AgentContext;

  beforeEach(() => {
    const logger = createLogger('./test-logs');
    agent = new DeduperAgent(logger);

    context = {
      url: 'https://example.com',
      config: DEFAULT_CONFIG,
      logger,
      state: new Map(),
    };
  });

  it('should remove exact duplicates', async () => {
    const matches: ValidatedMatch[] = [
      {
        home: 'Team A',
        away: 'Team B',
        date_utc: '2025-12-25T14:30:00Z',
        location: 'Stadium 1',
        metadata: {
          raw: '<tr>...</tr>',
          confidence: 0.8,
          issues: [],
        },
      },
      {
        home: 'Team A',
        away: 'Team B',
        date_utc: '2025-12-25T14:30:00Z',
        location: 'Stadium 1',
        metadata: {
          raw: '<tr>...</tr>',
          confidence: 0.8,
          issues: [],
        },
      },
    ];

    const result = await agent.run(
      { matches, calendarId: 'calendar-1' },
      context
    );

    expect(result.success).toBe(true);
    expect(result.data).toHaveLength(1);
  });

  it('should handle reversed home/away teams', async () => {
    const matches: ValidatedMatch[] = [
      {
        home: 'Team A',
        away: 'Team B',
        date_utc: '2025-12-25T14:30:00Z',
        metadata: {
          raw: '<tr>...</tr>',
          confidence: 0.8,
          issues: [],
        },
      },
      {
        home: 'Team B',
        away: 'Team A',
        date_utc: '2025-12-25T14:30:00Z',
        metadata: {
          raw: '<tr>...</tr>',
          confidence: 0.8,
          issues: [],
        },
      },
    ];

    const result = await agent.run(
      { matches, calendarId: 'calendar-1' },
      context
    );

    expect(result.success).toBe(true);
    expect(result.data).toHaveLength(1); // Should deduplicate
  });

  it('should merge sources from multiple calendars', async () => {
    const matches1: ValidatedMatch[] = [
      {
        home: 'Team A',
        away: 'Team B',
        date_utc: '2025-12-25T14:30:00Z',
        metadata: {
          raw: '<tr>...</tr>',
          confidence: 0.8,
          issues: [],
        },
      },
    ];

    // First calendar
    const result1 = await agent.run(
      { matches: matches1, calendarId: 'calendar-1' },
      context
    );

    expect(result1.data![0].sources).toEqual(['calendar-1']);

    // Second calendar with same match
    const result2 = await agent.run(
      { matches: matches1, calendarId: 'calendar-2' },
      context
    );

    expect(result2.data).toHaveLength(1);
    expect(result2.data![0].sources).toContain('calendar-1');
    expect(result2.data![0].sources).toContain('calendar-2');
  });
});
