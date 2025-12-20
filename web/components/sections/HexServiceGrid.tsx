'use client';

import React from 'react';
import { services, Service } from '@/data/services'; // Assuming '@/data/services' is the correct path and structure
import ServiceCard from './ServiceCard'; // Reusing the existing ServiceCard component
import styles from './HexServiceGrid.module.css';

interface HexServiceGridProps {
  // Any props specific to the grid container can go here
}

// Map service IDs to an icon (placeholder for now, could be dynamic)
const serviceIcons: { [key: string]: string } = {
  openwebui: '💬',
  comfyui: '🎨',
  ollama: '🧠',
  letta: '📚',
  surrealdb: '🗄️',
  // Add other service icons here
  engine: '⚙️',
  library: '📖',
  incubator: '🧪',
};

export default function HexServiceGrid({}: HexServiceGridProps) {
  return (
    <div className={styles.grid}>
      {services.map((service, index) => (
        <div
          key={service.id}
          className={`${styles.hexWrapper} cursor-hover`}
          style={
            {
              '--hex-color': service.color,
              // Offset every other row for a honeycomb effect
              // This is a basic approach and might need refinement for perfect alignment
              // using complex grid-template-areas or absolute positioning for a perfect hex grid
            } as React.CSSProperties
          }
        >
          {/* Base Hexagon - always visible */}
          <div className={styles.hexagon}>
            <div className={styles.hexContent}>
              <span className={styles.hexPrefix}>{service.prefix}</span>
              <span className={styles.hexIcon}>
                {serviceIcons[service.id] || '✨'}
              </span>
              <span
                className={styles.hexStatus}
                style={{
                  backgroundColor: service.status === 'online' ? '#00FF88' : service.status === 'configuring' ? '#FFB800' : '#FF3366',
                  boxShadow: `0 0 10px ${service.status === 'online' ? '#00FF88' : service.status === 'configuring' ? '#FFB800' : '#FF3366'}`,
                }}
              ></span>
            </div>
          </div>

          {/* Info Card - appears on hover */}
          <div className={styles.infoCard}>
            <ServiceCard service={service} index={index} />
          </div>
        </div>
      ))}
    </div>
  );
}
