import { useEffect, useState } from "react";

interface SystemMetrics {
  cpu: number;
  memory: number;
  temperature: number;
  gpuUtilization: number;
  gpuMemory: number;
  timestamp: number;
}

export function useSystemMetrics(isActive: boolean, pollInterval = 2000) {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    temperature: 0,
    gpuUtilization: 0,
    gpuMemory: 0,
    timestamp: 0,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isActive) {
      setMetrics({
        cpu: 0,
        memory: 0,
        temperature: 0,
        gpuUtilization: 0,
        gpuMemory: 0,
        timestamp: 0,
      });
      return;
    }

    const fetchMetrics = async () => {
      try {
        const response = await fetch("/api/jarvis/metrics");
        if (!response.ok) {
          throw new Error("Failed to fetch metrics");
        }
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        console.error("Error fetching system metrics:", err);
      }
    };

    // Fetch immediately
    fetchMetrics();

    // Then poll at interval
    const interval = setInterval(fetchMetrics, pollInterval);

    return () => clearInterval(interval);
  }, [isActive, pollInterval]);

  return { metrics, error };
}
