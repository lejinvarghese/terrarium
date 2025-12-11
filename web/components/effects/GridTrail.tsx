'use client';

import { useEffect, useRef } from 'react';
import styles from './GridTrail.module.css';

interface GridTrailProps {
  cellSize?: number;
  trailColor?: string;
  fadeSpeed?: number;
  trailRadius?: number;
}

export default function GridTrail({
  cellSize = 40,
  trailColor = '#EBFA1D',
  fadeSpeed = 0.05,
  trailRadius = 2,
}: GridTrailProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const p5Instance = useRef<any>(null);

  useEffect(() => {
    if (!containerRef.current || typeof window === 'undefined') return;

    // Dynamically import p5 on client side only
    const loadP5 = async () => {
      const p5Module = await import('p5');
      const p5 = p5Module.default;

      // Grid state
      let cols: number;
      let rows: number;
      let grid: number[][];
      let mouseXGrid = 0;
      let mouseYGrid = 0;

      const sketch = (p: any) => {
        p.setup = () => {
          const canvas = p.createCanvas(p.windowWidth, p.windowHeight);
          canvas.parent(containerRef.current!);

          // Initialize grid
          cols = Math.ceil(p.width / cellSize);
          rows = Math.ceil(p.height / cellSize);
          grid = Array(cols).fill(0).map(() => Array(rows).fill(0));

          p.noStroke();
        };

        p.draw = () => {
          // Clear background (transparent)
          p.clear();

          // Update mouse grid position
          mouseXGrid = Math.floor(p.mouseX / cellSize);
          mouseYGrid = Math.floor(p.mouseY / cellSize);

          // Activate cells around mouse
          for (let dx = -trailRadius; dx <= trailRadius; dx++) {
            for (let dy = -trailRadius; dy <= trailRadius; dy++) {
              const x = mouseXGrid + dx;
              const y = mouseYGrid + dy;

              if (x >= 0 && x < cols && y >= 0 && y < rows) {
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance <= trailRadius) {
                  // Intensity based on distance from mouse
                  const intensity = 1 - (distance / trailRadius);
                  grid[x][y] = Math.max(grid[x][y], intensity);
                }
              }
            }
          }

          // Draw grid and fade cells
          for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
              if (grid[i][j] > 0) {
                // Parse hex color to RGB
                const r = parseInt(trailColor.slice(1, 3), 16);
                const g = parseInt(trailColor.slice(3, 5), 16);
                const b = parseInt(trailColor.slice(5, 7), 16);

                // Set fill with current intensity
                p.fill(r, g, b, grid[i][j] * 255);
                p.rect(i * cellSize, j * cellSize, cellSize, cellSize);

                // Fade out
                grid[i][j] -= fadeSpeed;
                if (grid[i][j] < 0) grid[i][j] = 0;
              }
            }
          }

          // Draw grid lines (subtle)
          p.stroke(197, 182, 175, 30);
          p.strokeWeight(1);

          // Vertical lines
          for (let i = 0; i <= cols; i++) {
            p.line(i * cellSize, 0, i * cellSize, p.height);
          }

          // Horizontal lines
          for (let j = 0; j <= rows; j++) {
            p.line(0, j * cellSize, p.width, j * cellSize);
          }
        };

        p.windowResized = () => {
          p.resizeCanvas(p.windowWidth, p.windowHeight);
          cols = Math.ceil(p.width / cellSize);
          rows = Math.ceil(p.height / cellSize);
          grid = Array(cols).fill(0).map(() => Array(rows).fill(0));
        };
      };

      p5Instance.current = new p5(sketch);
    };

    loadP5();

    return () => {
      if (p5Instance.current) {
        p5Instance.current.remove();
      }
    };
  }, [cellSize, trailColor, fadeSpeed, trailRadius]);

  return <div ref={containerRef} className={styles.gridTrail} />;
}
