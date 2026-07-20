'use client';

import { useMemo } from 'react';
import styles from './Hexagon.module.css';

interface HexagonProps {
  size: number;
  color: string;
  agentCount: number;
  status: 'active' | 'dead' | 'dormant';
  name: string;
  culture: string;
  cx: number;
  cy: number;
}

export default function Hexagon({
  size,
  color,
  agentCount,
  status,
  name,
  culture,
  cx,
  cy,
}: HexagonProps) {
  // Calculate hexagon points
  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 2; // Start from top
      const x = cx + size * Math.cos(angle);
      const y = cy + size * Math.sin(angle);
      pts.push(`${x},${y}`);
    }
    return pts.join(' ');
  }, [cx, cy, size]);

  // Generate random dot positions inside hexagon
  const dots = useMemo(() => {
    if (agentCount === 0) return [];

    const dotPositions = [];
    const innerRadius = size * 0.4; // Smaller radius to keep dots well within bounds

    for (let i = 0; i < agentCount; i++) {
      // Random position within circle (rough approximation of hexagon interior)
      const angle = Math.random() * Math.PI * 2;
      const r = Math.sqrt(Math.random()) * innerRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);

      dotPositions.push({
        x,
        y,
        delay: Math.random() * 3, // Random animation delay for staggered movement
        amplitude: 3 + Math.random() * 4, // Random vertical movement range (3-7px)
      });
    }

    return dotPositions;
  }, [agentCount, cx, cy, size]);

  return (
    <g className={styles.hexagonGroup}>
      {/* Hexagon border */}
      <polygon
        points={points}
        className={`${styles.hexagon} ${styles[status]}`}
        style={{
          stroke: color,
          fill: status === 'active' ? `${color}10` : 'transparent',
        }}
      />

      {/* Inner glow for active landscapes */}
      {status === 'active' && (
        <polygon
          points={points}
          className={styles.hexagonGlow}
          style={{
            stroke: color,
            fill: `${color}08`,
          }}
        />
      )}

      {/* Agent dots */}
      {dots.map((dot, i) => (
        <circle
          key={i}
          cx={dot.x}
          cy={dot.y}
          r={status === 'active' ? 1.5 : 1}
          className={`${styles.dot} ${styles[status]}`}
          style={{
            fill: color,
            animationDelay: `${dot.delay}s`,
            // CSS variable for vertical movement amplitude
            ['--float-distance' as any]: `${dot.amplitude}px`,
          }}
        />
      ))}

      {/* Landscape label */}
      <text
        x={cx}
        y={cy - size * 0.05}
        className={styles.label}
        style={{ fill: color }}
      >
        {name}
      </text>

      {/* Agent count */}
      <text
        x={cx}
        y={cy + size * 0.2}
        className={styles.count}
        style={{ fill: color, opacity: 0.6 }}
      >
        {agentCount > 0 ? `${agentCount} agents` : 'dormant'}
      </text>

      {/* Tooltip on hover */}
      <title>{`${name}\n${culture}\n${agentCount} active agents`}</title>
    </g>
  );
}
