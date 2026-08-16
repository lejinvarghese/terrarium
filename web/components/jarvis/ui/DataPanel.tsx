"use client";

import { useEffect, useState } from "react";
import { useServiceStatus } from "@/hooks/jarvis/useServiceStatus";
import { useSystemMetrics } from "@/hooks/jarvis/useSystemMetrics";
import styles from "./DataPanel.module.css";

interface DataPanelProps {
  title: string;
  position: "left" | "right";
  isActive: boolean;
}

interface DataItem {
  label: string;
  value: string;
  status?: "normal" | "warning" | "success" | "error";
}

export default function DataPanel({
  title,
  position,
  isActive,
}: DataPanelProps) {
  const [data, setData] = useState<DataItem[]>([]);
  const { data: serviceData } = useServiceStatus(isActive);
  const { metrics } = useSystemMetrics(isActive);

  useEffect(() => {
    if (!isActive) {
      setData([]);
      return;
    }

    if (title === "SYSTEM STATUS") {
      // Left panel - Terrarium services status
      const statusData: DataItem[] = serviceData.services.map((service) => ({
        label: service.name.toUpperCase(),
        value: service.status.toUpperCase(),
        status:
          service.status === "online"
            ? "success"
            : service.status === "offline"
              ? "error"
              : "normal",
      }));

      // Add system health indicator
      const allOnline = serviceData.services.every(
        (s) => s.status === "online",
      );
      statusData.unshift({
        label: "TERRARIUM STATUS",
        value: allOnline ? "OPTIMAL" : "DEGRADED",
        status: allOnline ? "success" : "warning",
      });

      setData(statusData);
    } else {
      // Right panel - System diagnostics
      const diagnosticsData: DataItem[] = [
        {
          label: "CPU USAGE",
          value: `${metrics.cpu.toFixed(1)}%`,
          status:
            metrics.cpu > 80
              ? "error"
              : metrics.cpu > 60
                ? "warning"
                : "success",
        },
        {
          label: "MEMORY USAGE",
          value: `${metrics.memory.toFixed(1)}%`,
          status:
            metrics.memory > 80
              ? "error"
              : metrics.memory > 60
                ? "warning"
                : "success",
        },
        {
          label: "CPU TEMP",
          value: `${metrics.temperature.toFixed(1)}°C`,
          status:
            metrics.temperature > 80
              ? "error"
              : metrics.temperature > 70
                ? "warning"
                : "success",
        },
        { label: "NETWORK", value: "CONNECTED", status: "success" },
        { label: "DISK I/O", value: "OPTIMAL", status: "success" },
      ];

      setData(diagnosticsData);
    }
  }, [isActive, title, serviceData, metrics]);

  return (
    <div className={`${styles.container} ${styles[position]}`}>
      <div className={styles.header}>
        <div className={styles.title}>{title}</div>
        <div className={styles.indicator} />
      </div>

      <div className={styles.content}>
        {data.map((item, index) => (
          <div
            key={index}
            className={styles.dataRow}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className={styles.label}>{item.label}</div>
            <div
              className={`${styles.value} ${styles[item.status || "normal"]}`}
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
