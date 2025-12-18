/**
 * Core Types for Sports Calendar Scraper
 *
 * Evidence-based system: all data must be traceable to source
 */

// ============================================================================
// Match Data Types
// ============================================================================

export interface RawMatch {
  home?: string;
  away?: string;
  date?: string;
  time?: string;
  location?: string;
  competition?: string;
  metadata: {
    selector: string;
    rawHTML: string;
    confidence: number; // 0.0 - 1.0
  };
}

export interface ValidatedMatch {
  home: string;
  away: string;
  date_utc: string; // ISO 8601
  location?: string;
  competition?: string;
  metadata: {
    raw: string;
    confidence: number;
    issues: ValidationIssue[];
  };
}

export interface DeduplicatedMatch extends ValidatedMatch {
  sources: string[]; // calendar_ids
  duplicateKey: string;
}

export interface ValidationIssue {
  field: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
}

// ============================================================================
// Calendar Types
// ============================================================================

export interface Calendar {
  id: string;
  name: string;
  url: string;
  method: 'api' | 'scrape';
  matches: DeduplicatedMatch[];
  evidence: Evidence;
}

export interface Evidence {
  api_endpoint?: string;
  selectors?: string[];
  network_calls?: NetworkCall[];
  dom_snapshot?: string;
}

export interface NetworkCall {
  url: string;
  method: string;
  headers: Record<string, string>;
  body?: string;
  response?: any;
  timestamp: number;
}

// ============================================================================
// UI Navigation Types
// ============================================================================

export interface CalendarView {
  id: string;
  signature: string; // hash(DOM + URL + params)
  url: string;
  controls: UIControl[];
  matchCount: number;
  timestamp: number;
}

export interface UIControl {
  type: 'button' | 'select' | 'tab' | 'filter' | 'pagination';
  selector: string;
  label: string;
  value?: string;
  action: 'click' | 'select' | 'navigate';
}

export interface CalendarGraph {
  views: CalendarView[];
  edges: ViewTransition[];
}

export interface ViewTransition {
  from: string; // view id
  to: string;
  control: UIControl;
  cost: number; // interaction cost
}

export interface ViewState {
  url: string;
  domSignature: string;
  filterState: Record<string, string>;
  timestamp: number;
}

// ============================================================================
// API Detection Types
// ============================================================================

export interface APIDiscovery {
  found: boolean;
  endpoints: APIEndpoint[];
  authentication?: AuthMethod;
  dataFormat: 'json' | 'xml' | 'ical' | 'rss' | 'graphql';
  confidence: number;
}

export interface APIEndpoint {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers: Record<string, string>;
  params?: Record<string, string>;
  body?: string;
  sampleResponse?: any;
  detected_by: string; // 'network' | 'script' | 'json-ld' | 'link'
}

export interface AuthMethod {
  type: 'bearer' | 'oauth2' | 'api_key' | 'session' | 'none';
  details: Record<string, string>;
}

// ============================================================================
// Planning Types
// ============================================================================

export interface Plan {
  url: string;
  strategy: 'api' | 'scrape' | 'hybrid';
  detectedPatterns: string[];
  estimatedCalendarCount: number;
  risks: string[];
  steps: PlanStep[];
}

export interface PlanStep {
  agent: string;
  action: string;
  dependencies: string[];
  estimated_duration_ms: number;
}

// ============================================================================
// Agent Base Types
// ============================================================================

export interface AgentContext {
  url: string;
  page?: any; // Playwright Page
  config: ScraperConfig;
  logger: any; // Winston Logger
  state: Map<string, any>;
}

export interface AgentResult<T> {
  success: boolean;
  data?: T;
  error?: Error;
  metadata: {
    duration_ms: number;
    timestamp: number;
    agent: string;
  };
}

// ============================================================================
// Configuration Types
// ============================================================================

export interface ScraperConfig {
  scraping: {
    headless: boolean;
    timeout: number;
    userAgent: string;
    viewport: { width: number; height: number };
  };

  limits: {
    maxInteractions: number;
    maxPages: number;
    maxDepth: number;
    requestDelay: number;
  };

  selectors: {
    calendar: string[];
    match: string[];
    home: string[];
    away: string[];
    date: string[];
    location: string[];
  };

  output: {
    directory: string;
    formats: ('json' | 'csv')[];
    saveHAR: boolean;
    saveScreenshots: boolean;
    saveTraces: boolean;
  };

  plugins: {
    enabled: string[];
    directory: string;
  };
}

// ============================================================================
// Output Types
// ============================================================================

export interface ScrapingReport {
  source_url: string;
  scraped_at: string;
  strategy_used: 'api' | 'scrape' | 'hybrid';

  calendars: Calendar[];
  total_matches: number;
  duplicates_removed: number;

  api_endpoints?: APIEndpoint[];
  selectors_used?: string[];
  errors: ScrapingError[];

  performance: {
    duration_ms: number;
    pages_visited: number;
    requests_made: number;
  };

  artifacts: {
    har_file?: string;
    screenshots?: string[];
    trace_file?: string;
  };
}

export interface ScrapingError {
  timestamp: number;
  severity: 'error' | 'warning';
  message: string;
  agent?: string;
  stack?: string;
  screenshot?: string;
}

// ============================================================================
// Plugin Types
// ============================================================================

export interface ScraperPlugin {
  name: string;
  domains: string[];

  detect(page: any): Promise<boolean>;
  extractAPI?(page: any): Promise<APIDiscovery | null>;
  extractMatches?(page: any): Promise<RawMatch[]>;
  navigateFilters?(page: any): Promise<CalendarView[]>;
}

// ============================================================================
// Utility Types
// ============================================================================

export type Strategy = 'api' | 'scrape' | 'hybrid';
export type Severity = 'error' | 'warning' | 'info';
export type DataFormat = 'json' | 'xml' | 'ical' | 'rss' | 'graphql';
