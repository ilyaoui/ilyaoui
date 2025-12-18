/**
 * Tests for ValidatorAgent
 */

import { ValidatorAgent } from '../agents/ValidatorAgent';
import { createLogger } from '../core/Logger';
import { DEFAULT_CONFIG } from '../core/Config';
import { AgentContext, RawMatch } from '../types';

describe('ValidatorAgent', () => {
  let agent: ValidatorAgent;
  let context: AgentContext;

  beforeEach(() => {
    const logger = createLogger('./test-logs');
    agent = new ValidatorAgent(logger);

    context = {
      url: 'https://example.com',
      config: DEFAULT_CONFIG,
      logger,
      state: new Map(),
    };
  });

  it('should validate a complete match', async () => {
    const rawMatches: RawMatch[] = [
      {
        home: 'Team A',
        away: 'Team B',
        date: '2025-12-25',
        time: '14:30',
        location: 'Stadium 1',
        metadata: {
          selector: 'tr.match',
          rawHTML: '<tr>...</tr>',
          confidence: 0.8,
        },
      },
    ];

    const result = await agent.run({ rawMatches }, context);

    expect(result.success).toBe(true);
    expect(result.data).toHaveLength(1);
    expect(result.data![0].home).toBe('Team A');
    expect(result.data![0].away).toBe('Team B');
    expect(result.data![0].date_utc).toContain('2025-12-25');
  });

  it('should reject match with no home team', async () => {
    const rawMatches: RawMatch[] = [
      {
        away: 'Team B',
        date: '2025-12-25',
        metadata: {
          selector: 'tr.match',
          rawHTML: '<tr>...</tr>',
          confidence: 0.8,
        },
      },
    ];

    const result = await agent.run({ rawMatches }, context);

    expect(result.success).toBe(true);
    expect(result.data).toHaveLength(0); // Invalid match filtered out
  });

  it('should normalize team names', async () => {
    const rawMatches: RawMatch[] = [
      {
        home: '  Team A  ',
        away: 'Team-B!',
        date: '2025-12-25',
        metadata: {
          selector: 'tr.match',
          rawHTML: '<tr>...</tr>',
          confidence: 0.8,
        },
      },
    ];

    const result = await agent.run({ rawMatches }, context);

    expect(result.success).toBe(true);
    expect(result.data![0].home).toBe('Team A');
    expect(result.data![0].away).toBe('TeamB');
  });

  it('should parse multiple date formats', async () => {
    const rawMatches: RawMatch[] = [
      {
        home: 'Team A',
        away: 'Team B',
        date: '12/25/2025 2:30 PM',
        metadata: {
          selector: 'tr.match',
          rawHTML: '<tr>...</tr>',
          confidence: 0.8,
        },
      },
    ];

    const result = await agent.run({ rawMatches }, context);

    expect(result.success).toBe(true);
    expect(result.data![0].date_utc).toContain('2025-12-25');
  });
});
