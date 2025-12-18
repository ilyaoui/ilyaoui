/**
 * UI Navigator Agent
 *
 * Explores UI controls (filters, tabs, buttons, dropdowns) to discover all calendar views
 */

import { Agent } from '../core/Agent';
import {
  CalendarGraph,
  CalendarView,
  UIControl,
  ViewTransition,
  AgentContext,
  AgentResult,
} from '../types';
import { Logger } from 'winston';
import { Page } from '@playwright/test';
import crypto from 'crypto';

interface UINavigatorInput {
  page: Page;
}

export class UINavigatorAgent extends Agent<UINavigatorInput, CalendarGraph> {
  private visited: Set<string> = new Set();
  private views: CalendarView[] = [];
  private edges: ViewTransition[] = [];

  constructor(logger: Logger) {
    super('UINavigatorAgent', logger);
  }

  async execute(
    input: UINavigatorInput,
    context: AgentContext
  ): Promise<AgentResult<CalendarGraph>> {
    const { page } = input;
    const { limits, selectors } = context.config;

    this.logger.info('Starting UI navigation exploration...');

    // Reset state
    this.visited.clear();
    this.views = [];
    this.edges = [];

    // Start BFS exploration
    await this.exploreBFS(page, limits.maxDepth, limits.maxInteractions, selectors.calendar);

    const graph: CalendarGraph = {
      views: this.views,
      edges: this.edges,
    };

    // Store evidence
    this.storeEvidence(context, 'calendar_graph', graph);

    this.logger.info(
      `UI exploration complete. Found ${this.views.length} views, ${this.edges.length} transitions`
    );

    return {
      success: true,
      data: graph,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private async exploreBFS(
    page: Page,
    maxDepth: number,
    maxInteractions: number,
    calendarSelectors: string[]
  ): Promise<void> {
    const queue: Array<{ depth: number }> = [{ depth: 0 }];
    let interactionCount = 0;

    while (queue.length > 0 && interactionCount < maxInteractions) {
      const { depth } = queue.shift()!;

      if (depth > maxDepth) continue;

      // Capture current view
      const view = await this.captureView(page, calendarSelectors);

      // Skip if already visited
      if (this.visited.has(view.signature)) {
        continue;
      }

      this.visited.add(view.signature);
      this.views.push(view);

      this.logger.debug(`Discovered view: ${view.id} (${view.matchCount} matches)`);

      // Find controls to interact with
      const controls = await this.findControls(page);

      // Explore each control
      for (const control of controls) {
        if (interactionCount >= maxInteractions) break;

        try {
          // Save current state
          const beforeSignature = view.signature;

          // Interact with control
          await this.interactWithControl(page, control);
          interactionCount++;

          // Wait for changes
          await page.waitForTimeout(1000);

          // Capture new view
          const newView = await this.captureView(page, calendarSelectors);

          // If view changed, record transition
          if (newView.signature !== beforeSignature) {
            this.edges.push({
              from: view.id,
              to: newView.id,
              control,
              cost: 1,
            });

            // Add to queue for further exploration
            queue.push({ depth: depth + 1 });
          }

          // Navigate back
          await page.goBack();
          await page.waitForTimeout(500);
        } catch (error) {
          this.logger.warn(`Failed to interact with control`, { control, error });
        }
      }
    }
  }

  private async captureView(
    page: Page,
    calendarSelectors: string[]
  ): Promise<CalendarView> {
    const url = page.url();

    // Try to find calendar container
    let calendarHTML = '';
    for (const selector of calendarSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          calendarHTML = await element.innerHTML();
          break;
        }
      } catch {
        // Try next selector
      }
    }

    // If no calendar found, use full page
    if (!calendarHTML) {
      calendarHTML = await page.content();
    }

    // Compute signature
    const signature = this.computeSignature(url, calendarHTML);

    // Count matches (heuristic)
    const matchCount = await this.countMatches(page);

    // Find controls
    const controls = await this.findControls(page);

    return {
      id: `view-${this.views.length + 1}`,
      signature,
      url,
      controls,
      matchCount,
      timestamp: Date.now(),
    };
  }

  private computeSignature(url: string, html: string): string {
    // Remove dynamic content (timestamps, session IDs, etc.)
    const normalized = html
      .replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/g, 'DATE')
      .replace(/[a-f0-9]{32,}/g, 'ID');

    return crypto
      .createHash('sha256')
      .update(url + normalized)
      .digest('hex')
      .substring(0, 16);
  }

  private async countMatches(page: Page): Promise<number> {
    // Try common match patterns
    const patterns = [
      'tr[class*="match"]',
      'tr[class*="game"]',
      'div[class*="match-card"]',
      'div[class*="game-card"]',
    ];

    for (const pattern of patterns) {
      try {
        const count = await page.$$eval(pattern, (els) => els.length);
        if (count > 0) return count;
      } catch {
        // Try next pattern
      }
    }

    return 0;
  }

  private async findControls(page: Page): Promise<UIControl[]> {
    const controls: UIControl[] = [];

    // Find filters/dropdowns
    try {
      const selects = await page.$$('select');
      for (const select of selects) {
        const label =
          (await select.getAttribute('name')) ||
          (await select.getAttribute('id')) ||
          'unknown';

        controls.push({
          type: 'select',
          selector: await this.getSelector(page, select),
          label,
          action: 'select',
        });
      }
    } catch {
      // Ignore
    }

    // Find tabs
    try {
      const tabs = await page.$$('[role="tab"], .tab, [class*="tab-"]');
      for (const tab of tabs) {
        const label = (await tab.textContent())?.trim() || 'tab';

        controls.push({
          type: 'tab',
          selector: await this.getSelector(page, tab),
          label,
          action: 'click',
        });
      }
    } catch {
      // Ignore
    }

    // Find filter buttons
    try {
      const buttons = await page.$$(
        'button[class*="filter"], button[class*="season"], button[class*="division"]'
      );
      for (const button of buttons) {
        const label = (await button.textContent())?.trim() || 'button';

        controls.push({
          type: 'filter',
          selector: await this.getSelector(page, button),
          label,
          action: 'click',
        });
      }
    } catch {
      // Ignore
    }

    return controls;
  }

  private async getSelector(page: Page, element: any): Promise<string> {
    // Try to get a stable selector
    const id = await element.getAttribute('id');
    if (id) return `#${id}`;

    const className = await element.getAttribute('class');
    if (className) {
      const firstClass = className.split(' ')[0];
      return `.${firstClass}`;
    }

    return 'unknown';
  }

  private async interactWithControl(page: Page, control: UIControl): Promise<void> {
    if (control.action === 'click') {
      await page.click(control.selector);
    } else if (control.action === 'select' && control.value) {
      await page.selectOption(control.selector, control.value);
    }
  }
}
