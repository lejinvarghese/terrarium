'use client';

import { useEffect, useState } from 'react';
import styles from './DataPanel.module.css';

interface DataPanelProps {
  title: string;
  position: 'left' | 'right';
  isActive: boolean;
}

interface DataItem {
  label: string;
  value: string;
  status?: 'normal' | 'warning' | 'success';
}

export default function DataPanel({ title, position, isActive }: DataPanelProps) {
  const [data, setData] = useState<DataItem[]>([]);

  console.log('DataPanel render -', title, 'isActive:', isActive, 'data items:', data.length);

  // Simulate data updates
  useEffect(() => {
    console.log('DataPanel useEffect -', title, 'isActive:', isActive);
    if (!isActive) {
      setData([]);
      return;
    }

    const systemStatusData: DataItem[] = [
      { label: 'POWER CORE', value: '99.8%', status: 'success' },
      { label: 'SHIELD STATUS', value: 'ACTIVE', status: 'success' },
      { label: 'REPULSOR CHARGE', value: '100%', status: 'success' },
      { label: 'FLIGHT SYSTEMS', value: 'ONLINE', status: 'success' },
      { label: 'WEAPON SYSTEMS', value: 'STANDBY', status: 'normal' },
      { label: 'AI CORE', value: 'ACTIVE', status: 'success' },
    ];

    const diagnosticsData: DataItem[] = [
      { label: 'CPU TEMP', value: '42°C', status: 'success' },
      { label: 'GPU LOAD', value: '34%', status: 'success' },
      { label: 'NETWORK', value: '1.2 GB/s', status: 'success' },
      { label: 'DISK I/O', value: 'OPTIMAL', status: 'success' },
      { label: 'MEMORY', value: '64.3 GB', status: 'success' },
      { label: 'UPTIME', value: '127 DAYS', status: 'success' },
      { label: 'PROCESSES', value: '342', status: 'normal' },
      { label: 'CONNECTIONS', value: '28', status: 'normal' },
    ];

    const sampleData = title === 'SYSTEM STATUS' ? systemStatusData : diagnosticsData;
    setData(sampleData);

    // Randomly update values
    const interval = setInterval(() => {
      setData((prev) =>
        prev.map((item) => {
          if (Math.random() > 0.7) {
            const newValue =
              item.label === 'POWER CORE'
                ? `${(Math.random() * 5 + 95).toFixed(1)}%`
                : item.value;
            return { ...item, value: newValue };
          }
          return item;
        })
      );
    }, 2000);

    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className={`${styles.container} ${styles[position]}`}>
      <div className={styles.header}>
        <div className={styles.title}>{title}</div>
        <div className={styles.indicator} />
      </div>

      <div className={styles.content}>
        {data.map((item, index) => (
          <div key={index} className={styles.dataRow} style={{ animationDelay: `${index * 0.1}s` }}>
            <div className={styles.label}>{item.label}</div>
            <div
              className={`${styles.value} ${styles[item.status || 'normal']}`}
            >
              {item.value}
            </div>
          </div>
        ))}
      </div>

      {/* Decorative edge */}
      <div className={styles.edge} />
    </div>
  );
}
