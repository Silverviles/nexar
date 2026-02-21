import winston from 'winston';

// Configure Winston logger
export const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.errors({ stack: true }),
        winston.format.splat(),
        winston.format.json()
    ),
    defaultMeta: { service: 'api-server' },
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.printf(({ level, message, timestamp, service, error, ...meta }) => {
                    let log = `${timestamp} [${service}] ${level}: ${message}`;
                    if (error instanceof Error) {
                        log += `\n  ${error.stack || error.message}`;
                    } else if (error) {
                        const errMsg = typeof error === 'object' && error !== null
                            ? (error as Record<string, unknown>).message || JSON.stringify(error)
                            : String(error);
                        log += `\n  ${errMsg}`;
                    }
                    if (Object.keys(meta).length > 0) {
                        log += ` ${JSON.stringify(meta)}`;
                    }
                    return log;
                })
            )
        })
    ]
});
