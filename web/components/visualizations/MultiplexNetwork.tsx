'use client';

import { useMemo } from 'react';
import { landscapes } from '@/data/landscapes';
import styles from './MultiplexNetwork.module.css';

export default function MultiplexNetwork() {
  const hexSize = 110; // Bottom hexagon size
  const topHexSize = 110; // Top hexagon size - matching bottom for true cylinder
  const layerGap = 120;

  // Layer 1 positions
  const layer1Positions = useMemo(() => {
    const layout = [
      { row: 0, col: 0 },
      { row: 0, col: 1 },
      { row: 1, col: 0 },
      { row: 1, col: 1 },
    ];

    const hexWidth = hexSize * 2;
    const hexHeight = Math.sqrt(3) * hexSize;
    const horizontalSpacing = hexWidth * 0.75 + 15;
    const verticalSpacing = hexHeight + 15;

    return layout.map((pos) => {
      const xOffset = pos.row % 2 === 1 ? horizontalSpacing / 2 : 0;
      return {
        cx: pos.col * horizontalSpacing + hexSize + xOffset + 250,
        cy: pos.row * verticalSpacing + hexSize + 140,
      };
    });
  }, [hexSize]);

  // H1 position (centered below layer 1)
  const h1 = {
    cx: layer1Positions[0].cx + (layer1Positions[1].cx - layer1Positions[0].cx) / 2,
    cy: layer1Positions[2].cy + layerGap,
  };

  const getHexVertices = (cx: number, cy: number, size: number) => {
    const vertices = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      vertices.push({
        x: cx + size * Math.cos(angle),
        y: cy + size * Math.sin(angle),
      });
    }
    return vertices;
  };

  const getHexPoints = (cx: number, cy: number, size: number) => {
    return getHexVertices(cx, cy, size)
      .map(v => `${v.x},${v.y}`)
      .join(' ');
  };

  const h1Vertices = getHexVertices(h1.cx, h1.cy, hexSize);
  const undergrowthVertices = getHexVertices(layer1Positions[0].cx, layer1Positions[0].cy, topHexSize);

  // H1 dots
  const h1Dots = useMemo(() => {
    const dots = [];
    const innerRadius = hexSize * 0.5;

    dots.push({ color: '#0099FF', size: 4, type: 'human' });
    dots.push({ color: '#FF3366', size: 3.5, type: 'dog' });
    for (let i = 0; i < 30; i++) {
      dots.push({ color: '#00FF88', size: 2, type: 'plant' });
    }

    return dots.map((dot, i) => {
      const angle = (i / dots.length) * Math.PI * 2 + Math.random() * 0.3;
      const r = Math.sqrt(Math.random()) * innerRadius;
      return {
        x: h1.cx + r * Math.cos(angle),
        y: h1.cy + r * Math.sin(angle),
        ...dot,
      };
    });
  }, [h1]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          <span className={styles.titlePrefix}>{'//'}</span>landscapes
        </h2>
      </div>

      <div className={styles.networkContainer}>
        <svg className={styles.svg} viewBox="0 0 800 650" preserveAspectRatio="xMidYMid meet">
          {/* Hexagonal cylinder edges - only from Undergrowth to H1 */}
          <g className={styles.cylinderEdges}>
            {h1Vertices.map((v0, i) => {
              const v1 = undergrowthVertices[i];
              return (
                <line
                  key={i}
                  x1={v0.x}
                  y1={v0.y}
                  x2={v1.x}
                  y2={v1.y}
                  stroke="#0099FF"
                  strokeWidth={1.5}
                  opacity={0.5}
                />
              );
            })}
          </g>

          {/* Layer 0 - H1 */}
          <g className={styles.layer0}>
            <polygon
              points={getHexPoints(h1.cx, h1.cy, hexSize)}
              fill="transparent"
              stroke="#0099FF"
              strokeWidth={0.8}
              opacity={0.7}
            />
            <text
              x={h1.cx}
              y={h1.cy - 8}
              className={styles.hexLabel}
              fill="#0099FF"
            >
              H1
            </text>

            {h1Dots.map((dot, i) => (
              <circle
                key={i}
                cx={dot.x}
                cy={dot.y}
                r={dot.size}
                fill={dot.color}
                opacity={0.8}
                className={styles.physicalDot}
              />
            ))}
          </g>

          {/* Layer 1 - All landscapes */}
          <g className={styles.layer1}>
            {landscapes.slice(0, 4).map((landscape, i) => {
              const pos = layer1Positions[i];
              const dots = [];
              const innerRadius = topHexSize * 0.45;

              for (let j = 0; j < landscape.agentCount; j++) {
                const angle = (j / landscape.agentCount) * Math.PI * 2 + Math.random() * 0.3;
                const r = Math.sqrt(Math.random()) * innerRadius;
                dots.push({
                  x: pos.cx + r * Math.cos(angle),
                  y: pos.cy + r * Math.sin(angle),
                });
              }

              return (
                <g key={landscape.id}>
                  <polygon
                    points={getHexPoints(pos.cx, pos.cy, topHexSize)}
                    fill={landscape.status === 'active' ? `${landscape.color}10` : 'transparent'}
                    stroke={landscape.color}
                    strokeWidth={landscape.status === 'active' ? 0.8 : 0.5}
                    opacity={landscape.status === 'active' ? 1 : 0.5}
                    strokeDasharray={landscape.status === 'dead' ? '5,5' : 'none'}
                  />
                  <text
                    x={pos.cx}
                    y={pos.cy - 5}
                    className={styles.hexLabel}
                    fill={landscape.color}
                  >
                    {landscape.name}
                  </text>
                  <text
                    x={pos.cx}
                    y={pos.cy + 18}
                    className={styles.hexCount}
                    fill={landscape.color}
                    opacity={0.6}
                  >
                    {landscape.agentCount > 0 ? `${landscape.agentCount} agents` : 'dormant'}
                  </text>
                  {dots.map((dot, j) => (
                    <circle
                      key={j}
                      cx={dot.x}
                      cy={dot.y}
                      r={2}
                      fill={landscape.color}
                      className={styles.digitalDot}
                      style={{ animationDelay: `${j * 0.1}s` }}
                    />
                  ))}
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      <div className={styles.legend}>
        <div className={styles.legendSection}>
          <span className={styles.legendTitle}>Layer 0</span>
          <div className={styles.legendItems}>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#0099FF' }} />
              <span>Human (1)</span>
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#FF3366' }} />
              <span>Dog (1)</span>
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#00FF88' }} />
              <span>Plants (30)</span>
            </div>
          </div>
        </div>
        <div className={styles.legendSection}>
          <span className={styles.legendTitle}>Layer 1</span>
          <div className={styles.legendItems}>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#EBFA1D' }} />
              <span>Active</span>
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#4A4A4A' }} />
              <span>Dead/Dormant</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
