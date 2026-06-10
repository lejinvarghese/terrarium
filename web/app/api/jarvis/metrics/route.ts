import { NextResponse } from 'next/server';
import si from 'systeminformation';

export async function GET() {
  try {
    // Fetch CPU, memory, and temperature data
    const [cpu, mem, temp] = await Promise.all([
      si.currentLoad(),
      si.mem(),
      si.cpuTemperature(),
    ]);

    // Calculate percentages
    const cpuUsage = cpu.currentLoad;
    const memoryUsage = (mem.used / mem.total) * 100;
    const temperature = temp.main || temp.max || 0;

    return NextResponse.json({
      cpu: Math.round(cpuUsage * 10) / 10,
      memory: Math.round(memoryUsage * 10) / 10,
      temperature: Math.round(temperature * 10) / 10,
      timestamp: Date.now(),
    });
  } catch (error) {
    console.error('Error fetching system metrics:', error);
    return NextResponse.json(
      { error: 'Failed to fetch system metrics' },
      { status: 500 }
    );
  }
}
