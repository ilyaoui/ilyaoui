/**
 * Base Agent Interface
 *
 * All agents inherit from this base class and follow evidence-based principles
 */

import { AgentContext, AgentResult } from '../types';
import { Logger } from 'winston';

export abstract class Agent<TInput, TOutput> {
  protected name: string;
  protected logger: Logger;

  constructor(name: string, logger: Logger) {
    this.name = name;
    this.logger = logger;
  }

  /**
   * Execute the agent's main task
   * Must be implemented by subclasses
   */
  abstract execute(
    input: TInput,
    context: AgentContext
  ): Promise<AgentResult<TOutput>>;

  /**
   * Validate input before execution
   */
  protected validateInput(input: TInput): void {
    if (!input) {
      throw new Error(`${this.name}: Invalid input`);
    }
  }

  /**
   * Wrap execution with timing and error handling
   */
  async run(
    input: TInput,
    context: AgentContext
  ): Promise<AgentResult<TOutput>> {
    const startTime = Date.now();

    this.logger.info(`[${this.name}] Starting execution`);

    try {
      this.validateInput(input);

      const result = await this.execute(input, context);

      const duration = Date.now() - startTime;
      this.logger.info(`[${this.name}] Completed in ${duration}ms`);

      return {
        ...result,
        metadata: {
          ...result.metadata,
          duration_ms: duration,
          timestamp: Date.now(),
          agent: this.name,
        },
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error(`[${this.name}] Failed after ${duration}ms`, { error });

      return {
        success: false,
        error: error as Error,
        metadata: {
          duration_ms: duration,
          timestamp: Date.now(),
          agent: this.name,
        },
      };
    }
  }

  /**
   * Store evidence in context
   */
  protected storeEvidence(
    context: AgentContext,
    key: string,
    value: any
  ): void {
    context.state.set(`${this.name}:${key}`, value);
  }

  /**
   * Retrieve evidence from context
   */
  protected getEvidence(context: AgentContext, key: string): any {
    return context.state.get(`${this.name}:${key}`);
  }
}
