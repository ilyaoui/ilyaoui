/**
 * Structured logging setup with Winston
 */

import winston from 'winston';
import path from 'path';

export function createLogger(logDir: string = './logs'): winston.Logger {
  const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      winston.format.errors({ stack: true }),
      winston.format.splat(),
      winston.format.json()
    ),
    defaultMeta: { service: 'sports-calendar-scraper' },
    transports: [
      // Console output (pretty)
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.printf(({ level, message, timestamp, ...meta }) => {
            const metaStr = Object.keys(meta).length
              ? '\n' + JSON.stringify(meta, null, 2)
              : '';
            return `${timestamp} [${level}]: ${message}${metaStr}`;
          })
        ),
      }),

      // File output (JSON)
      new winston.transports.File({
        filename: path.join(logDir, 'error.log'),
        level: 'error',
      }),
      new winston.transports.File({
        filename: path.join(logDir, 'combined.log'),
      }),
    ],
  });

  return logger;
}
