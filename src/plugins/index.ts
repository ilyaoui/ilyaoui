/**
 * Plugin Registry
 *
 * Central registry for all scraper plugins
 */

import { ScraperPlugin } from '../types';
import { TeamSnapPlugin } from './TeamSnapPlugin';
import { ExposureEventsPlugin } from './ExposureEventsPlugin';

export const PLUGIN_REGISTRY: Record<string, ScraperPlugin> = {
  teamsnap: TeamSnapPlugin,
  'exposure-events': ExposureEventsPlugin,
};

export function getPlugin(name: string): ScraperPlugin | undefined {
  return PLUGIN_REGISTRY[name];
}

export function detectPlugin(url: string): ScraperPlugin | undefined {
  const hostname = new URL(url).hostname;

  for (const plugin of Object.values(PLUGIN_REGISTRY)) {
    if (plugin.domains.some((domain) => hostname.includes(domain))) {
      return plugin;
    }
  }

  return undefined;
}
