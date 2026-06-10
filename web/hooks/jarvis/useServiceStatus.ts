import { useEffect, useState } from 'react';

interface Service {
  name: string;
  status: 'online' | 'offline' | 'unknown';
  port?: number;
}

interface ServiceStatusData {
  services: Service[];
  timestamp: number;
}

export function useServiceStatus(isActive: boolean, pollInterval = 5000) {
  const [data, setData] = useState<ServiceStatusData>({
    services: [],
    timestamp: 0,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isActive) {
      setData({ services: [], timestamp: 0 });
      return;
    }

    const fetchServices = async () => {
      try {
        const response = await fetch('/api/jarvis/services');
        if (!response.ok) {
          throw new Error('Failed to fetch service status');
        }
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching service status:', err);
      }
    };

    // Fetch immediately
    fetchServices();

    // Then poll at interval
    const interval = setInterval(fetchServices, pollInterval);

    return () => clearInterval(interval);
  }, [isActive, pollInterval]);

  return { data, error };
}
