'use client';

import { useEffect, useState } from 'react';
import styles from './CircularGauge.module.css';

interface CircularGaugeProps {
  label: string;
  value: number;
  max: number;
  unit?: string;
  color?: 'yellow' | 'green' | 'cyan';
  isActive: boolean;
}

export default function CircularGauge({
  label,
  value,
  max,
  unit = '',
  color = 'yellow',
  isActive,
}: CircularGaugeProps) {
  const [displayValue, setDisplayValue] = useState(0);

  // Animate value changes
  useEffect(() => {
    if (!isActive) {
      setDisplayValue(0);
      return;
    }

    const increment = (value - displayValue) / 20;
    const interval = setInterval(() => {
      setDisplayValue((prev) => {
        const next = prev + increment;
        if (Math.abs(next - value) < 0.1) {
          clearInterval(interval);
          return value;
        }
        return next;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [value, isActive]);

  const percentage = (displayValue / max) * 100;
  const arcLength = (percentage / 100) * 283; // Circumference of circle with r=45
  const rotation = -90; // Start from top

  const colorMap = {
    yellow: '#EBFA1D',
    green: '#00FF88',
    cyan: '#00FFF2',
  };

  const strokeColor = colorMap[color];

  return (
    <div className={styles.container}>
      <svg
        className={styles.svg}
        viewBox="0 0 120 120"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="geometricPrecision"
      >
        <defs>
          <filter id={`gaugeGlow-${label}`}>
            <feGaussianBlur stdDeviation="2" />
          </filter>
        </defs>

        {/* Background circle */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth="3"
        />

        {/* Progress arc */}
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke={strokeColor}
          strokeWidth="3"
          strokeDasharray={`${arcLength} 283`}
          strokeDashoffset="0"
          transform={`rotate(${rotation} 60 60)`}
          className={styles.progressArc}
          filter={`url(#gaugeGlow-${label})`}
          opacity="0.8"
        />

        {/* Inner glow circle */}
        <circle
          cx="60"
          cy="60"
          r="35"
          fill="none"
          stroke={strokeColor}
          strokeWidth="0.5"
          opacity="0.3"
        />

        {/* Tick marks */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => {
          const rad = ((angle - 90) * Math.PI) / 180;
          const x1 = 60 + 42 * Math.cos(rad);
          const y1 = 60 + 42 * Math.sin(rad);
          const x2 = 60 + 45 * Math.cos(rad);
          const y2 = 60 + 45 * Math.sin(rad);

          return (
            <line
              key={angle}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={strokeColor}
              strokeWidth="0.5"
              opacity="0.4"
            />
          );
        })}
      </svg>

      {/* Value display */}
      <div className={styles.value} style={{ color: strokeColor }}>
        {displayValue.toFixed(0)}
        {unit && <span className={styles.unit}>{unit}</span>}
      </div>

      {/* Label */}
      <div className={styles.label}>{label}</div>
    </div>
  );
}
