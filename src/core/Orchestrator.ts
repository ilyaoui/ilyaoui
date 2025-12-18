/**
 * Orchestrator
 *
 * Coordinates all agents and manages Playwright lifecycle
 */

import { chromium, Browser, BrowserContext, Page } from '@playwright/test';
import { AgentContext, ScraperConfig, ScrapingReport } from '../types';
import { Logger } from 'winston';
import { PlannerAgent } from '../agents/PlannerAgent';
import { APIScoutAgent } from '../agents/APIScoutAgent';
import { UINavigatorAgent } from '../agents/UINavigatorAgent';
import { ScraperAgent } from '../agents/ScraperAgent';
import { ValidatorAgent } from '../agents/ValidatorAgent';
import { DeduperAgent } from '../agents/DeduperAgent';
import { ReporterAgent } from '../agents/ReporterAgent';
import { detectPlugin } from '../plugins';
import path from 'path';
import fs from 'fs';

export class Orchestrator {
  private logger: Logger;
  private config: ScraperConfig;
  private browser?: Browser;
  private context?: BrowserContext;
  private page?: Page;

  // Agents
  private plannerAgent: PlannerAgent;
  private apiScoutAgent: APIScoutAgent;
  private uiNavigatorAgent: UINavigatorAgent;
  private scraperAgent: ScraperAgent;
  private validatorAgent: ValidatorAgent;
  private deduperAgent: DeduperAgent;
  private reporterAgent: ReporterAgent;

  constructor(logger: Logger, config: ScraperConfig) {
    this.logger = logger;
    this.config = config;

    // Initialize agents
    this.plannerAgent = new PlannerAgent(logger);
    this.apiScoutAgent = new APIScoutAgent(logger);
    this.uiNavigatorAgent = new UINavigatorAgent(logger);
    this.scraperAgent = new ScraperAgent(logger);
    this.validatorAgent = new ValidatorAgent(logger);
    this.deduperAgent = new DeduperAgent(logger);
    this.reporterAgent = new ReporterAgent(logger);
  }

  async scrape(url: string): Promise<ScrapingReport> {
    const startTime = Date.now();

    try {
      // Setup Playwright
      await this.setupPlaywright();

      // Create agent context
      const agentContext: AgentContext = {
        url,
        page: this.page,
        config: this.config,
        logger: this.logger,
        state: new Map(),
      };

      // Execute agent pipeline
      this.logger.info('Starting scraping pipeline...');

      // 1. Planning
      const planResult = await this.plannerAgent.run({ url }, agentContext);
      if (!planResult.success) {
        throw planResult.error || new Error('Planning failed');
      }

      const plan = planResult.data!;
      this.logger.info(`Strategy: ${plan.strategy}`);

      // 2. API Detection
      const apiResult = await this.apiScoutAgent.run(
        { page: this.page!, url },
        agentContext
      );

      if (!apiResult.success) {
        this.logger.warn('API detection failed, falling back to scraping');
      }

      const apiDiscovery = apiResult.data;

      // Check for site-specific plugin
      const plugin = detectPlugin(url);
      if (plugin) {
        this.logger.info(`Using plugin: ${plugin.name}`);
      }

      // 3. Extraction based on strategy
      let rawMatches: any[] = [];

      if (plan.strategy === 'api' && apiDiscovery?.found) {
        this.logger.info('Using API extraction...');
        // TODO: Implement API extraction
        rawMatches = [];
      } else {
        this.logger.info('Using scraping extraction...');

        // Use plugin if available
        if (plugin && plugin.navigateFilters) {
          this.logger.info(`Using plugin navigation: ${plugin.name}`);

          try {
            const views = await plugin.navigateFilters(this.page!);
            this.logger.info(`Plugin discovered ${views.length} calendar views`);

            // Scrape each view
            for (const view of views) {
              // Use plugin extraction if available
              if (plugin.extractMatches) {
                const pluginMatches = await plugin.extractMatches(this.page!);
                rawMatches.push(...pluginMatches);
              } else {
                // Fallback to default scraper
                const scrapeResult = await this.scraperAgent.run(
                  { page: this.page! },
                  agentContext
                );
                if (scrapeResult.success) {
                  rawMatches.push(...scrapeResult.data!);
                }
              }
            }
          } catch (error) {
            this.logger.warn(`Plugin navigation failed: ${error}. Falling back to default.`);
          }
        }

        // Fallback to default navigation if no plugin or plugin failed
        if (rawMatches.length === 0) {
          // 3a. UI Navigation (discover all calendar views)
          if (plan.strategy === 'scrape' || plan.strategy === 'hybrid') {
            const navResult = await this.uiNavigatorAgent.run(
              { page: this.page! },
              agentContext
            );

            if (navResult.success) {
              const graph = navResult.data!;
              this.logger.info(`Discovered ${graph.views.length} calendar views`);

              // 3b. Scrape each view
              for (const view of graph.views) {
                // Navigate to view
                await this.page!.goto(view.url, { waitUntil: 'domcontentloaded', timeout: 60000 });

                // Scrape matches
                const scrapeResult = await this.scraperAgent.run(
                  { page: this.page! },
                  agentContext
                );

                if (scrapeResult.success) {
                  rawMatches.push(...scrapeResult.data!);
                }
              }
            }
          } else {
            // Single page scrape
            const scrapeResult = await this.scraperAgent.run(
              { page: this.page! },
              agentContext
            );

            if (scrapeResult.success) {
              rawMatches = scrapeResult.data!;
            }
          }
        }
      }

      this.logger.info(`Extracted ${rawMatches.length} raw matches`);

      // 4. Validation
      const validationResult = await this.validatorAgent.run(
        { rawMatches },
        agentContext
      );

      if (!validationResult.success) {
        throw validationResult.error || new Error('Validation failed');
      }

      const validatedMatches = validationResult.data!;
      this.logger.info(`Validated ${validatedMatches.length} matches`);

      // 5. Deduplication
      const dedupResult = await this.deduperAgent.run(
        { matches: validatedMatches, calendarId: 'main' },
        agentContext
      );

      if (!dedupResult.success) {
        throw dedupResult.error || new Error('Deduplication failed');
      }

      const dedupedMatches = dedupResult.data!;
      this.logger.info(`Deduplicated to ${dedupedMatches.length} unique matches`);

      // 6. Report Generation
      const reportResult = await this.reporterAgent.run(
        { url, startTime },
        agentContext
      );

      if (!reportResult.success) {
        throw reportResult.error || new Error('Report generation failed');
      }

      const report = reportResult.data!;

      // Save artifacts
      await this.saveArtifacts(report);

      this.logger.info('Scraping pipeline complete!');

      return report;
    } catch (error) {
      this.logger.error('Scraping failed', { error });
      throw error;
    } finally {
      await this.cleanup();
    }
  }

  private async setupPlaywright(): Promise<void> {
    this.logger.info('Setting up Playwright...');

    const { scraping, output } = this.config;

    // Launch browser
    this.browser = await chromium.launch({
      headless: scraping.headless,
      timeout: scraping.timeout,
    });

    // Create context
    this.context = await this.browser.newContext({
      userAgent: scraping.userAgent,
      viewport: scraping.viewport,
      // Record HAR if enabled
      ...(output.saveHAR && {
        recordHar: {
          path: path.join(output.directory, 'network.har'),
        },
      }),
      // Record traces if enabled
      ...(output.saveTraces && {
        recordVideo: {
          dir: path.join(output.directory, 'videos'),
        },
      }),
    });

    // Create page
    this.page = await this.context.newPage();

    // Enable screenshots on error
    if (output.saveScreenshots) {
      this.page.on('pageerror', async (error) => {
        const screenshot = await this.page!.screenshot({
          path: path.join(
            output.directory,
            `error-${Date.now()}.png`
          ),
          fullPage: true,
        });
        this.logger.error('Page error captured', { error, screenshot });
      });
    }
  }

  private async saveArtifacts(report: ScrapingReport): Promise<void> {
    const { output } = this.config;

    // Ensure output directory exists
    if (!fs.existsSync(output.directory)) {
      fs.mkdirSync(output.directory, { recursive: true });
    }

    // Save JSON report
    if (output.formats.includes('json')) {
      const jsonPath = path.join(output.directory, 'report.json');
      fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
      this.logger.info(`Report saved to ${jsonPath}`);
    }

    // Save CSV (matches only)
    if (output.formats.includes('csv')) {
      const csvPath = path.join(output.directory, 'matches.csv');
      await this.saveCSV(report, csvPath);
      this.logger.info(`Matches saved to ${csvPath}`);
    }

    // Save HAR if available
    if (output.saveHAR && this.context) {
      await this.context.close(); // HAR is written on context close
      report.artifacts.har_file = path.join(output.directory, 'network.har');
    }

    // Save traces if enabled
    if (output.saveTraces && this.context) {
      const tracePath = path.join(output.directory, 'trace.zip');
      await this.context.tracing.stop({ path: tracePath });
      report.artifacts.trace_file = tracePath;
    }
  }

  private async saveCSV(report: ScrapingReport, filePath: string): Promise<void> {
    const { createObjectCsvWriter } = await import('csv-writer');

    const csvWriter = createObjectCsvWriter({
      path: filePath,
      header: [
        { id: 'home', title: 'Home' },
        { id: 'away', title: 'Away' },
        { id: 'date_utc', title: 'Date (UTC)' },
        { id: 'location', title: 'Location' },
        { id: 'competition', title: 'Competition' },
        { id: 'confidence', title: 'Confidence' },
        { id: 'sources', title: 'Sources' },
      ],
    });

    const records = report.calendars.flatMap((calendar) =>
      calendar.matches.map((match) => ({
        home: match.home,
        away: match.away,
        date_utc: match.date_utc,
        location: match.location || '',
        competition: match.competition || '',
        confidence: match.metadata.confidence,
        sources: match.sources.join(', '),
      }))
    );

    await csvWriter.writeRecords(records);
  }

  private async cleanup(): Promise<void> {
    this.logger.info('Cleaning up...');

    try {
      if (this.page) {
        await this.page.close();
      }
      if (this.context) {
        await this.context.close();
      }
      if (this.browser) {
        await this.browser.close();
      }
    } catch (error) {
      this.logger.warn('Cleanup error', { error });
    }
  }
}
