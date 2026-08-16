import { NextResponse } from "next/server";
import si from "systeminformation";

export async function GET() {
  try {
    // Fetch CPU, memory, temperature, and GPU data
    const [cpu, mem, temp, graphics] = await Promise.all([
      si.currentLoad(),
      si.mem(),
      si.cpuTemperature(),
      si.graphics(),
    ]);

    // Calculate percentages
    const cpuUsage = cpu.currentLoad;
    const memoryUsage = (mem.used / mem.total) * 100;
    const temperature = temp.main || temp.max || 0;

    // GPU metrics (use first GPU if multiple)
    const gpu = graphics.controllers[0];
    const gpuUtilization = gpu?.utilizationGpu || 0;
    const gpuMemoryUsage =
      gpu?.memoryUsed && gpu?.memoryTotal
        ? (gpu.memoryUsed / gpu.memoryTotal) * 100
        : 0;

    return NextResponse.json({
      cpu: Math.round(cpuUsage * 10) / 10,
      memory: Math.round(memoryUsage * 10) / 10,
      temperature: Math.round(temperature * 10) / 10,
      gpuUtilization: Math.round(gpuUtilization * 10) / 10,
      gpuMemory: Math.round(gpuMemoryUsage * 10) / 10,
      timestamp: Date.now(),
    });
  } catch (error) {
    console.error("Error fetching system metrics:", error);
    return NextResponse.json(
      { error: "Failed to fetch system metrics" },
      { status: 500 },
    );
  }
}
