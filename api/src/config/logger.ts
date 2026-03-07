import winston from "winston";

// ──────────────────────────────────────────────────────────────────────────────
// Google Cloud Logging–compatible Winston logger
//
// Cloud Run captures stdout/stderr. When the output is a JSON object with a
// "severity" field, Cloud Logging parses it as a structured log entry and
// displays it with the correct severity in Logs Explorer.
//
// Reference:
//   https://cloud.google.com/run/docs/logging#writing_structured_logs
//   https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
// ──────────────────────────────────────────────────────────────────────────────

// K_SERVICE is set automatically by Cloud Run
const isCloudRun = !!process.env.K_SERVICE;

// Map Winston levels → Cloud Logging severity strings
const CLOUD_SEVERITY: Record<string, string> = {
  error: "ERROR",
  warn: "WARNING",
  info: "INFO",
  http: "INFO",
  verbose: "DEBUG",
  debug: "DEBUG",
  silly: "DEBUG",
};

/**
 * Structured JSON format for Google Cloud Logging.
 *
 * Each log line is a JSON object with:
 *   { "severity": "INFO", "message": "…", "timestamp": "…" }
 *
 * Extra metadata (error stacks, request context, etc.) appears in the
 * log entry's jsonPayload in Logs Explorer.
 */
const cloudFormat = winston.format.printf(
  ({ level, message, timestamp, stack, error, service, ...meta }) => {
    const entry: Record<string, unknown> = {
      severity: CLOUD_SEVERITY[level] ?? "DEFAULT",
      message,
      timestamp,
      "logging.googleapis.com/labels": { service: service ?? "api-server" },
    };

    // Attach stack trace (Cloud Error Reporting picks this up)
    if (stack) {
      entry.stack_trace = stack;
    }

    // Attach error details
    if (error) {
      if (error instanceof Error) {
        entry.error = { message: error.message, stack: error.stack };
      } else if (typeof error === "object") {
        entry.error = error;
      } else {
        entry.error = String(error);
      }
    }

    // Spread remaining metadata into the entry
    for (const key of Object.keys(meta)) {
      entry[key] = meta[key];
    }

    return JSON.stringify(entry);
  },
);

/**
 * Pretty, colorized format for local development.
 */
const localFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.printf(
    ({ level, message, timestamp, service, error, ...meta }) => {
      let log = `${timestamp} [${service}] ${level}: ${message}`;
      if (error instanceof Error) {
        log += `\n  ${error.stack || error.message}`;
      } else if (error) {
        const errMsg =
          typeof error === "object" && error !== null
            ? (error as Record<string, unknown>).message ||
              JSON.stringify(error)
            : String(error);
        log += `\n  ${errMsg}`;
      }
      if (Object.keys(meta).length > 0) {
        log += ` ${JSON.stringify(meta)}`;
      }
      return log;
    },
  ),
);

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.combine(
    winston.format.timestamp({ format: "YYYY-MM-DDTHH:mm:ss.SSSZ" }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
  ),
  defaultMeta: { service: "api-server" },
  transports: [
    new winston.transports.Console({
      format: isCloudRun ? cloudFormat : localFormat,
    }),
  ],
});
