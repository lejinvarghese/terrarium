'use client';

import { useEffect, useState } from 'react';
import styles from './RadarDisplay.module.css';

interface RadarDisplayProps {
  isActive: boolean;
}

interface RadarDot {
  id: number;
  angle: number;
  distance: number;
  opacity: number;
}

export default function RadarDisplay({ isActive }: RadarDisplayProps) {
  const [sweepAngle, setSweepAngle] = useState(0);
  const [dots, setDots] = useState<RadarDot[]>([]);

  // Animate sweep
  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setSweepAngle((prev) => (prev + 2) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, [isActive]);

  // Generate random radar dots
  useEffect(() => {
    if (!isActive) {
      setDots([]);
      return;
    }

    const interval = setInterval(() => {
      const newDot: RadarDot = {
        id: Date.now(),
        angle: Math.random() * 360,
        distance: Math.random() * 80 + 20,
        opacity: 1,
      };

      setDots((prev) => [...prev.slice(-10), newDot]);
    }, 1500);

    return () => clearInterval(interval);
  }, [isActive]);

  // Fade out old dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) =>
        prev
          .map((dot) => ({
            ...dot,
            opacity: dot.opacity - 0.02,
          }))
          .filter((dot) => dot.opacity > 0)
      );
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.container}>
      <svg
        className={styles.svg}
        viewBox="0 0 400 400"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="geometricPrecision"
      >
        <defs>
          {/* Radar sweep gradient */}
          <radialGradient id="radarSweep">
            <stop offset="0%" stopColor="#EBFA1D" stopOpacity="0" />
            <stop offset="50%" stopColor="#EBFA1D" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#EBFA1D" stopOpacity="0" />
          </radialGradient>

          {/* Glow filter */}
          <filter id="radarGlow">
            <feGaussianBlur stdDeviation="2" />
          </filter>
        </defs>

        {/* Background circle */}
        <circle
          cx="200"
          cy="200"
          r="100"
          fill="rgba(0, 0, 0, 0.5)"
          stroke="#EBFA1D"
          strokeWidth="1"
          opacity="0.3"
        />

        {/* Concentric circles */}
        <circle cx="200" cy="200" r="25" fill="none" stroke="#00FF88" strokeWidth="0.5" opacity="0.4" />
        <circle cx="200" cy="200" r="50" fill="none" stroke="#00FF88" strokeWidth="0.5" opacity="0.4" />
        <circle cx="200" cy="200" r="75" fill="none" stroke="#00FF88" strokeWidth="0.5" opacity="0.4" />
        <circle cx="200" cy="200" r="100" fill="none" stroke="#EBFA1D" strokeWidth="1.5" opacity="0.6" />

        {/* Cross lines */}
        <line x1="200" y1="100" x2="200" y2="300" stroke="#00FFF2" strokeWidth="0.5" opacity="0.3" />
        <line x1="100" y1="200" x2="300" y2="200" stroke="#00FFF2" strokeWidth="0.5" opacity="0.3" />

        {/* Diagonal guides */}
        <line
          x1="129.3"
          y1="129.3"
          x2="270.7"
          y2="270.7"
          stroke="#00FFF2"
          strokeWidth="0.5"
          opacity="0.2"
        />
        <line
          x1="270.7"
          y1="129.3"
          x2="129.3"
          y2="270.7"
          stroke="#00FFF2"
          strokeWidth="0.5"
          opacity="0.2"
        />

        {/* Radar sweep */}
        {isActive && (
          <line
            x1="200"
            y1="200"
            x2={200 + 100 * Math.cos((sweepAngle * Math.PI) / 180)}
            y2={200 + 100 * Math.sin((sweepAngle * Math.PI) / 180)}
            stroke="#EBFA1D"
            strokeWidth="2"
            opacity="0.8"
            filter="url(#radarGlow)"
            className={styles.sweep}
          />
        )}

        {/* Sweep trail */}
        {isActive && (
          <path
            d={`M 200 200 L ${200 + 100 * Math.cos((sweepAngle * Math.PI) / 180)} ${
              200 + 100 * Math.sin((sweepAngle * Math.PI) / 180)
            } A 100 100 0 0 0 ${200 + 100 * Math.cos(((sweepAngle - 60) * Math.PI) / 180)} ${
              200 + 100 * Math.sin(((sweepAngle - 60) * Math.PI) / 180)
            } Z`}
            fill="url(#radarSweep)"
            opacity="0.5"
          />
        )}

        {/* Radar dots */}
        {dots.map((dot) => {
          const x = 200 + dot.distance * Math.cos((dot.angle * Math.PI) / 180);
          const y = 200 + dot.distance * Math.sin((dot.angle * Math.PI) / 180);
          return (
            <circle
              key={dot.id}
              cx={x}
              cy={y}
              r="3"
              fill="#00FF88"
              opacity={dot.opacity}
              filter="url(#radarGlow)"
            >
              <animate
                attributeName="r"
                from="3"
                to="5"
                dur="1s"
                repeatCount="indefinite"
              />
            </circle>
          );
        })}

        {/* Center dot */}
        <circle cx="200" cy="200" r="2" fill="#EBFA1D" opacity="0.8" />
      </svg>

      {/* Label */}
      <div className={styles.label}>RADAR</div>
    </div>
  );
}
