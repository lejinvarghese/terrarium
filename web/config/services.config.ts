/**
 * Service configuration - centralized source of truth
 *
 * This file should mirror the configuration in src/authentication/config.json
 * Update both files when making changes to service ports or URLs.
 */

export const SERVICE_CONFIG = {
  dome: {
    authPort: 8081,      // Authentication proxy port
    targetPort: 8080,    // Actual service port (Open WebUI)
    publicUrl: 'https://dome.mutatedterrarium.com',
  },
  archive: {
    authPort: 8503,      // Authentication proxy port
    targetPort: 8502,    // Actual service port (Open Notebook)
    publicUrl: 'https://archive.mutatedterrarium.com',
  },
  jarvis: {
    authPort: 3002,      // Authentication proxy port (not currently used)
    targetPort: 3000,    // Actual Next.js app port
  },
  scheduler: {
    port: 5000,
  },
  telegram: {
    botUsername: 'casper_whispers_bot',
    url: 'https://t.me/casper_whispers_bot',
  },
  ollama: {
    port: 11434,
  },
} as const;

export type ServiceName = keyof typeof SERVICE_CONFIG;
