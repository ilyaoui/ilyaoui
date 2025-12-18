/**
 * API Scout Agent
 *
 * Detects and exploits available APIs (XHR, GraphQL, JSON, iCal, RSS)
 */

import { Agent } from '../core/Agent';
import {
  APIDiscovery,
  APIEndpoint,
  AgentContext,
  AgentResult,
  NetworkCall,
} from '../types';
import { Logger } from 'winston';
import { Page } from '@playwright/test';

interface APIScoutInput {
  page: Page;
  url: string;
}

export class APIScoutAgent extends Agent<APIScoutInput, APIDiscovery> {
  private networkCalls: NetworkCall[] = [];

  constructor(logger: Logger) {
    super('APIScoutAgent', logger);
  }

  async execute(
    input: APIScoutInput,
    context: AgentContext
  ): Promise<AgentResult<APIDiscovery>> {
    const { page, url } = input;

    this.logger.info('Starting API detection...');

    // Setup network interception
    await this.setupNetworkInterception(page);

    // Navigate to page (use domcontentloaded instead of networkidle to avoid timeout on busy sites)
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // Wait for initial page load
    await page.waitForTimeout(3000);

    // Record current network calls count (baseline)
    const baselineCallsCount = this.networkCalls.length;
    this.logger.info(`Baseline: ${baselineCallsCount} network calls captured`);

    // Try clicking on schedule/navigation elements to trigger API calls
    const navSelectors = [
      'a:has-text("Schedule")',
      'button:has-text("Schedule")',
      'a:has-text("Schedules")',
      'button:has-text("Schedules")',
      '[href*="schedule"]',
      '[class*="tab"]',
      '[class*="nav-link"]',
    ];

    for (const selector of navSelectors) {
      try {
        const elements = await page.$$(selector);

        for (let i = 0; i < Math.min(elements.length, 3); i++) {
          const element = elements[i];
          const isVisible = await element.isVisible();

          if (isVisible) {
            const text = await element.textContent();
            this.logger.info(`Clicking on: "${text?.trim()}" (${selector})`);

            // Record calls before click
            const beforeClick = this.networkCalls.length;

            // Click and wait for network activity
            await element.click();
            await page.waitForTimeout(3000);

            // Check if new API calls were triggered
            const afterClick = this.networkCalls.length;
            const newCalls = afterClick - beforeClick;

            if (newCalls > 0) {
              this.logger.info(`✅ Click triggered ${newCalls} new network calls`);

              // Log the new calls
              const recentCalls = this.networkCalls.slice(beforeClick);
              for (const call of recentCalls) {
                if (this.isAPICall(call)) {
                  this.logger.info(`   📡 API call: ${call.method} ${call.url}`);
                }
              }
            }
          }
        }
      } catch (error) {
        this.logger.debug(`Could not interact with ${selector}: ${error}`);
      }
    }

    // Final wait to capture any delayed responses
    await page.waitForTimeout(2000);

    // Analyze collected network calls
    const endpoints = this.analyzeNetworkCalls();

    // Search for JSON-LD
    const jsonLdEndpoints = await this.extractJSONLD(page);
    endpoints.push(...jsonLdEndpoints);

    // Search for iCal/RSS links
    const feedEndpoints = await this.extractFeeds(page);
    endpoints.push(...feedEndpoints);

    // Check for GraphQL
    const graphqlEndpoints = await this.detectGraphQL(page);
    endpoints.push(...graphqlEndpoints);

    const discovery: APIDiscovery = {
      found: endpoints.length > 0,
      endpoints,
      dataFormat: this.inferDataFormat(endpoints),
      confidence: this.calculateConfidence(endpoints),
    };

    // Store evidence
    this.storeEvidence(context, 'api_discovery', discovery);
    this.storeEvidence(context, 'network_calls', this.networkCalls);

    this.logger.info(`API detection complete. Found ${endpoints.length} endpoints`);

    return {
      success: true,
      data: discovery,
      metadata: {
        duration_ms: 0,
        timestamp: Date.now(),
        agent: this.name,
      },
    };
  }

  private async setupNetworkInterception(page: Page): Promise<void> {
    page.on('request', (request) => {
      const url = request.url();
      const method = request.method();

      // Capture API-like requests
      if (
        url.includes('/api/') ||
        url.includes('/graphql') ||
        method === 'POST' ||
        request.resourceType() === 'xhr' ||
        request.resourceType() === 'fetch'
      ) {
        this.networkCalls.push({
          url,
          method,
          headers: request.headers(),
          body: request.postData() || undefined,
          timestamp: Date.now(),
        });
      }
    });

    page.on('response', async (response) => {
      const request = response.request();
      const url = request.url();

      // Find matching call
      const call = this.networkCalls.find((c) => c.url === url);
      if (call) {
        const contentType = response.headers()['content-type'];
        if (contentType?.includes('application/json')) {
          try {
            call.response = await response.json();
          } catch {
            // Ignore parse errors
          }
        }
      }
    });
  }

  private analyzeNetworkCalls(): APIEndpoint[] {
    const endpoints: APIEndpoint[] = [];
    const uniqueUrls = new Set<string>();

    for (const call of this.networkCalls) {
      // Filter out non-API calls and duplicates
      if (this.isAPICall(call) && !uniqueUrls.has(call.url)) {
        uniqueUrls.add(call.url);

        // Calculate confidence based on response
        let confidence = 0.5;
        if (call.response) {
          const responseStr = JSON.stringify(call.response).toLowerCase();

          // Higher confidence if response contains schedule-related data
          if (responseStr.includes('game') || responseStr.includes('match')) {
            confidence += 0.3;
          }
          if (responseStr.includes('team')) {
            confidence += 0.1;
          }
          if (responseStr.includes('schedule') || responseStr.includes('event')) {
            confidence += 0.1;
          }
        }

        endpoints.push({
          url: call.url,
          method: call.method as any,
          headers: call.headers,
          body: call.body,
          sampleResponse: call.response,
          detected_by: 'network',
        });

        // Log high-confidence endpoints
        if (confidence > 0.7) {
          this.logger.info(`🎯 High-confidence API found: ${call.url}`);
        }
      }
    }

    // Sort by confidence (endpoints with responses first)
    endpoints.sort((a, b) => {
      const aHasResponse = a.sampleResponse ? 1 : 0;
      const bHasResponse = b.sampleResponse ? 1 : 0;
      return bHasResponse - aHasResponse;
    });

    return endpoints;
  }

  private isAPICall(call: NetworkCall): boolean {
    const url = call.url.toLowerCase();

    // Check for common API patterns
    const apiPatterns = [
      '/api/',
      '/v1/',
      '/v2/',
      '/v3/',
      '/graphql',
      '/rest/',
      '.json',
      '/schedules',
      '/games',
      '/events',
      '/matches',
      '/calendar',
    ];

    // Also check content-type
    const contentType = call.headers['content-type'] || '';
    const isJSON = contentType.includes('application/json');

    return apiPatterns.some((pattern) => url.includes(pattern)) || isJSON;
  }

  private async extractJSONLD(page: Page): Promise<APIEndpoint[]> {
    const endpoints: APIEndpoint[] = [];

    try {
      const jsonLdScripts = await page.$$('script[type="application/ld+json"]');

      for (const script of jsonLdScripts) {
        const content = await script.textContent();
        if (content) {
          try {
            const data = JSON.parse(content);

            // Check if it's a SportsEvent schema
            if (
              data['@type'] === 'SportsEvent' ||
              (Array.isArray(data) &&
                data.some((item) => item['@type'] === 'SportsEvent'))
            ) {
              endpoints.push({
                url: page.url(),
                method: 'GET',
                headers: {},
                sampleResponse: data,
                detected_by: 'json-ld',
              });
            }
          } catch {
            // Ignore parse errors
          }
        }
      }
    } catch (error) {
      this.logger.warn('Failed to extract JSON-LD', { error });
    }

    return endpoints;
  }

  private async extractFeeds(page: Page): Promise<APIEndpoint[]> {
    const endpoints: APIEndpoint[] = [];

    try {
      // Look for iCal, RSS, Atom links
      const links = await page.$$eval(
        'link[rel="alternate"], a[href*=".ics"], a[href*="calendar"]',
        (elements) =>
          elements.map((el) => ({
            href: (el as HTMLElement).getAttribute('href') || '',
            type: (el as HTMLElement).getAttribute('type') || '',
          }))
      );

      for (const link of links) {
        if (
          link.type.includes('calendar') ||
          link.type.includes('ics') ||
          link.href.endsWith('.ics')
        ) {
          endpoints.push({
            url: link.href,
            method: 'GET',
            headers: {},
            detected_by: 'link',
          });
        }
      }
    } catch (error) {
      this.logger.warn('Failed to extract feeds', { error });
    }

    return endpoints;
  }

  private async detectGraphQL(page: Page): Promise<APIEndpoint[]> {
    const endpoints: APIEndpoint[] = [];

    // Check if any network call went to /graphql
    const graphqlCalls = this.networkCalls.filter((call) =>
      call.url.includes('/graphql')
    );

    if (graphqlCalls.length > 0) {
      // Add GraphQL endpoint
      endpoints.push({
        url: graphqlCalls[0].url,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: graphqlCalls[0].body,
        sampleResponse: graphqlCalls[0].response,
        detected_by: 'network',
      });
    }

    return endpoints;
  }

  private inferDataFormat(
    endpoints: APIEndpoint[]
  ): 'json' | 'xml' | 'ical' | 'rss' | 'graphql' {
    if (endpoints.some((e) => e.url.includes('/graphql'))) {
      return 'graphql';
    }
    if (endpoints.some((e) => e.url.endsWith('.ics'))) {
      return 'ical';
    }
    if (endpoints.some((e) => e.url.includes('rss'))) {
      return 'rss';
    }
    return 'json';
  }

  private calculateConfidence(endpoints: APIEndpoint[]): number {
    if (endpoints.length === 0) return 0;

    // Higher confidence if we have sample responses
    const withResponses = endpoints.filter((e) => e.sampleResponse).length;
    return Math.min(0.5 + withResponses * 0.25, 1.0);
  }
}
