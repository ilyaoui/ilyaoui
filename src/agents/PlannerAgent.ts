/**
 * Planner Agent
 *
 * Analyzes URL and proposes extraction strategy
 */

import { Agent } from '../core/Agent';
import { Plan, PlanStep, AgentContext, AgentResult } from '../types';
import { Logger } from 'winston';

interface PlannerInput {
  url: string;
}

export class PlannerAgent extends Agent<PlannerInput, Plan> {
  constructor(logger: Logger) {
    super('PlannerAgent', logger);
  }

  async execute(
    input: PlannerInput,
    context: AgentContext
  ): Promise<AgentResult<Plan>> {
    const { url } = input;

    this.logger.info(`Analyzing URL: ${url}`);

    // Parse URL
    const urlObj = new URL(url);
    const domain = urlObj.hostname;

    // Detect known patterns
    const patterns = this.detectPatterns(domain);
    const risks = this.identifyRisks(urlObj);

    // Propose strategy
    const strategy = this.proposeStrategy(patterns);

    // Build execution steps
    const steps = this.buildSteps(strategy);

    const plan: Plan = {
      url,
      strategy,
      detectedPatterns: patterns,
      estimatedCalendarCount: this.estimateCalendarCount(patterns),
      risks,
      steps,
    };

    // Store plan in context
    this.storeEvidence(context, 'plan', plan);

    return {
      success: true,
      data: plan,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private detectPatterns(domain: string): string[] {
    const patterns: string[] = [];

    if (domain.includes('teamsnap')) {
      patterns.push('teamsnap');
    }
    if (domain.includes('bluesombrero')) {
      patterns.push('bluesombrero');
    }
    if (domain.includes('sportsengine')) {
      patterns.push('sportsengine');
    }
    if (domain.includes('squadi')) {
      patterns.push('squadi');
    }
    if (domain.includes('nflflag')) {
      patterns.push('nflflag');
    }

    return patterns;
  }

  private identifyRisks(url: URL): string[] {
    const risks: string[] = [];

    // Check if requires auth
    if (url.pathname.includes('/login') || url.pathname.includes('/auth')) {
      risks.push('authentication_required');
    }

    // Check if dynamic content
    if (url.hostname.includes('app.') || url.hostname.includes('dashboard.')) {
      risks.push('spa_dynamic_content');
    }

    // Check query params (might be filter state)
    if (url.search) {
      risks.push('stateful_filters');
    }

    return risks;
  }

  private proposeStrategy(patterns: string[]): 'api' | 'scrape' | 'hybrid' {
    // Known platforms with APIs
    const apiPlatforms = ['teamsnap', 'sportsengine', 'squadi'];

    if (patterns.some((p) => apiPlatforms.includes(p))) {
      return 'api';
    }

    // Default to scraping
    return 'scrape';
  }

  private buildSteps(strategy: 'api' | 'scrape' | 'hybrid'): PlanStep[] {
    const steps: PlanStep[] = [];

    // Always start with API scout
    steps.push({
      agent: 'APIScoutAgent',
      action: 'detect_api',
      dependencies: [],
      estimated_duration_ms: 5000,
    });

    if (strategy === 'api' || strategy === 'hybrid') {
      steps.push({
        agent: 'APIScoutAgent',
        action: 'extract_via_api',
        dependencies: ['APIScoutAgent:detect_api'],
        estimated_duration_ms: 10000,
      });
    }

    if (strategy === 'scrape' || strategy === 'hybrid') {
      steps.push({
        agent: 'UINavigatorAgent',
        action: 'explore_controls',
        dependencies: ['APIScoutAgent:detect_api'],
        estimated_duration_ms: 15000,
      });

      steps.push({
        agent: 'ScraperAgent',
        action: 'extract_matches',
        dependencies: ['UINavigatorAgent:explore_controls'],
        estimated_duration_ms: 20000,
      });
    }

    // Validation and deduplication
    steps.push({
      agent: 'ValidatorAgent',
      action: 'validate_matches',
      dependencies: ['ScraperAgent:extract_matches'],
      estimated_duration_ms: 3000,
    });

    steps.push({
      agent: 'DeduperAgent',
      action: 'deduplicate',
      dependencies: ['ValidatorAgent:validate_matches'],
      estimated_duration_ms: 2000,
    });

    // Final report
    steps.push({
      agent: 'ReporterAgent',
      action: 'generate_report',
      dependencies: ['DeduperAgent:deduplicate'],
      estimated_duration_ms: 1000,
    });

    return steps;
  }

  private estimateCalendarCount(patterns: string[]): number {
    // Heuristic based on platform
    if (patterns.includes('teamsnap')) return 5;
    if (patterns.includes('bluesombrero')) return 3;
    return 1;
  }
}
