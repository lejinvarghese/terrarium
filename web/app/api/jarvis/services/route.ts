import { NextResponse } from 'next/server';
import { SERVICE_CONFIG } from '@/config/services.config';

interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'unknown';
  port?: number;
}

async function checkService(url: string, timeout = 2000): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

export async function GET() {
  try {
    // Check various Terrarium services
    const services: ServiceStatus[] = [
      { name: 'Open WebUI', port: SERVICE_CONFIG.dome.targetPort },
      { name: 'Ollama', port: SERVICE_CONFIG.ollama.port },
    ];

    // Check each service
    const serviceStatuses = await Promise.all(
      services.map(async (service) => {
        const isOnline = await checkService(`http://localhost:${service.port}`);
        return {
          ...service,
          status: isOnline ? 'online' : 'offline',
        };
      })
    );

    return NextResponse.json({
      services: serviceStatuses,
      timestamp: Date.now(),
    });
  } catch (error) {
    console.error('Error checking service status:', error);
    return NextResponse.json(
      { error: 'Failed to check service status' },
      { status: 500 }
    );
  }
}
