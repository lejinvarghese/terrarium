'use client';

/**
 * LandscapeHexGrid - Hexagonal visualization of Terrarium landscapes
 *
 * MODULAR DESIGN - Easy to remove or customize:
 * 1. To remove: Comment out the import and section in app/page.tsx
 * 2. To customize layout: Adjust hexSize, gap, or layout array below
 * 3. To add more landscapes: Update data/landscapes.ts
 * 4. To change colors: Update landscape colors in data/landscapes.ts
 *
 * Data source: /web/data/landscapes.ts
 * Components: Hexagon.tsx (individual hexagon), this file (grid layout)
 */

import { useMemo } from 'react';
import Hexagon from './Hexagon';
import { landscapes } from '@/data/landscapes';
import styles from './LandscapeHexGrid.module.css';

interface HexPosition {
  row: number;
  col: number;
}

export default function LandscapeHexGrid() {
  const hexSize = 60; // Radius of each hexagon
  const gap = 8; // Gap between hexagons

  // Calculate hexagon centers in a honeycomb pattern
  const hexPositions = useMemo(() => {
    // Manual layout for 4 landscapes in a compact cluster
    // Row 0: 2 hexagons (offset)
    // Row 1: 2 hexagons
    const layout: HexPosition[] = [
      { row: 0, col: 0 }, // Undergrowth
      { row: 0, col: 1 }, // Canopy
      { row: 1, col: 0 }, // Mycelium
      { row: 1, col: 1 }, // Reef
    ];

    const hexWidth = hexSize * 2;
    const hexHeight = Math.sqrt(3) * hexSize;
    const horizontalSpacing = hexWidth * 0.75 + gap;
    const verticalSpacing = hexHeight + gap;

    return layout.map((pos) => {
      // Offset odd rows
      const xOffset = pos.row % 2 === 1 ? horizontalSpacing / 2 : 0;

      return {
        cx: pos.col * horizontalSpacing + hexSize + xOffset,
        cy: pos.row * verticalSpacing + hexSize,
      };
    });
  }, [hexSize, gap]);

  // Calculate SVG viewBox to fit all hexagons
  const viewBox = useMemo(() => {
    const padding = 20;
    const maxX = Math.max(...hexPositions.map(p => p.cx)) + hexSize + padding;
    const maxY = Math.max(...hexPositions.map(p => p.cy)) + hexSize + padding;
    return `0 0 ${maxX} ${maxY}`;
  }, [hexPositions, hexSize]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          <span className={styles.titlePrefix}>{'//'}</span>
          landscapes
        </h2>
        <p className={styles.subtitle}>
          Distinct ecosystems where synthetic minds emerge, evolve, and interact
        </p>
      </div>

      <svg
        className={styles.svg}
        viewBox={viewBox}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Grid background pattern (optional) */}
        <defs>
          <pattern
            id="gridPattern"
            width="20"
            height="20"
            patternUnits="userSpaceOnUse"
          >
            <circle cx="10" cy="10" r="0.5" fill="#EBFA1D" opacity="0.1" />
          </pattern>
        </defs>

        {/* Render hexagons */}
        {landscapes.slice(0, 4).map((landscape, i) => (
          <Hexagon
            key={landscape.id}
            size={hexSize}
            color={landscape.color}
            agentCount={landscape.agentCount}
            status={landscape.status}
            name={landscape.name}
            culture={landscape.culture}
            cx={hexPositions[i].cx}
            cy={hexPositions[i].cy}
          />
        ))}
      </svg>

      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <div className={styles.legendDot} style={{ background: '#EBFA1D' }} />
          <span>Active</span>
        </div>
        <div className={styles.legendItem}>
          <div className={styles.legendDot} style={{ background: '#4A4A4A' }} />
          <span>Dead</span>
        </div>
        <div className={styles.legendItem}>
          <div className={styles.legendDot} style={{ background: '#2A2A2A' }} />
          <span>Dormant</span>
        </div>
      </div>
    </div>
  );
}
