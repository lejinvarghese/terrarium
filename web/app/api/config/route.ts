import { NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

interface ServiceConfig {
  port: number;
  targetUrl: string;
  title: string;
  serviceName: string;
}

interface Config {
  dome: ServiceConfig;
  archive: ServiceConfig;
  jarvis: ServiceConfig;
  accessCodes: string[];
  cookieSecret: string;
  cookieMaxAge: number;
}

// Read config from centralized location
function getConfig(): Config | null {
  try {
    const configPath = path.join(process.cwd(), '..', 'src', 'authentication', 'config.json');
    const configData = fs.readFileSync(configPath, 'utf-8');
    return JSON.parse(configData);
  } catch (error) {
    console.error('Failed to read config:', error);
    return null;
  }
}

export async function GET() {
  const config = getConfig();

  if (!config) {
    return NextResponse.json(
      { error: 'Configuration not found' },
      { status: 500 }
    );
  }

  // Return public config (exclude sensitive data like accessCodes and cookieSecret)
  return NextResponse.json({
    services: {
      dome: {
        port: config.dome.port,
        targetPort: parseInt(config.dome.targetUrl.split(':').pop() || '8080'),
      },
      archive: {
        port: config.archive.port,
        targetPort: parseInt(config.archive.targetUrl.split(':').pop() || '8502'),
      },
      jarvis: {
        port: config.jarvis.port,
        targetPort: parseInt(config.jarvis.targetUrl.split(':').pop() || '3000'),
      },
    },
  });
}
