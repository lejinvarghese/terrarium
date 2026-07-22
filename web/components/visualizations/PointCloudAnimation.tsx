'use client';

import { useEffect, useRef } from 'react';
import styles from './PointCloudAnimation.module.css';

export default function PointCloudAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size responsively
    const updateCanvasSize = () => {
      const container = canvas.parentElement;
      if (!container) return;

      const containerWidth = container.clientWidth;
      // Maintain aspect ratio, but make it taller on mobile
      const aspectRatio = window.innerWidth < 768 ? 1.2 : 0.64;
      const width = Math.min(containerWidth, 1200);
      const height = width * aspectRatio;

      canvas.width = width;
      canvas.height = height;

      return { width, height };
    };

    const size = updateCanvasSize();
    if (!size) return;
    let { width, height } = size;

    // Generate 10,000 points following the parametric equations from Wolfram code
    const numPoints = 10000;
    const x = Array.from({ length: numPoints }, (_, i) => i);
    const y = x.map(val => val / 235.0);

    const generatePoints = (t: number) => {
      const points: Array<{ x: number; y: number; inWave: boolean }> = [];

      // Parameters for wave animation
      const waveLength = 4 * Math.PI;
      const speed = 6;
      const waveWidth = waveLength / 2;
      const yFirst = y[0];
      const ySpan = y[y.length - 1] - yFirst;
      const wavePosition = ((speed * t) / (2 * Math.PI)) % ySpan;

      for (let i = 0; i < numPoints; i++) {
        // Parametric equations from Wolfram code
        const k = (4 + 3 * Math.sin(2 * y[i] - t)) * Math.cos(x[i] / 29.0);
        const e = y[i] / 8.0 - 13.0;
        const d = Math.sqrt(k * k + e * e);
        const c = d - t;
        const q = 3 * Math.sin(2 * k) + 0.3 / k + Math.sin(y[i] / 25.0) * k * (9 + 4 * Math.sin(9 * e - 3 * d + 2 * t));

        // Scale points to canvas size and center properly
        const scaleX = width / 550;
        const scaleY = height / 350;
        // Center the x-coordinate: original was offset by 200 in a 550px canvas
        // Now center it relative to current canvas width
        const px = (q + 30 * Math.cos(c)) * scaleX + width / 2;
        const py = (400 - (q * Math.sin(c) + 39 * d - 220.0)) * scaleY;

        // Determine if point is in the scanning wave
        const distanceFromWave = Math.abs(((y[i] - yFirst) - wavePosition + ySpan / 2) % ySpan - ySpan / 2);
        const inWave = distanceFromWave <= waveWidth;

        points.push({ x: px, y: py, inWave });
      }

      return points;
    };

    // Animation loop
    let t = 0;
    const animate = () => {
      // Clear canvas with black background
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, width, height);

      // Generate points for current time
      const points = generatePoints(t);

      // Draw white points (background)
      points.forEach(point => {
        if (!point.inWave) {
          ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
          ctx.beginPath();
          ctx.arc(point.x, point.y, 1, 0, 2 * Math.PI);
          ctx.fill();
        }
      });

      // Draw yellow glowing points (wave)
      points.forEach(point => {
        if (point.inWave) {
          // Create radial gradient for glow effect
          const gradient = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, 3);
          gradient.addColorStop(0, 'rgba(235, 250, 29, 1)'); // Bright yellow (#EBFA1D)
          gradient.addColorStop(0.5, 'rgba(235, 250, 29, 0.6)');
          gradient.addColorStop(1, 'rgba(235, 250, 29, 0)');

          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(point.x, point.y, 3, 0, 2 * Math.PI);
          ctx.fill();

          // Add extra bright core
          ctx.fillStyle = 'rgba(235, 250, 29, 0.9)';
          ctx.beginPath();
          ctx.arc(point.x, point.y, 1.5, 0, 2 * Math.PI);
          ctx.fill();
        }
      });

      // Increment time (slower animation for smoothness)
      t += 0.03;
      if (t > 2 * Math.PI) t = 0;

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Handle window resize
    const handleResize = () => {
      const size = updateCanvasSize();
      if (size) {
        width = size.width;
        height = size.height;
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <div className={styles.container}>
      <canvas ref={canvasRef} className={styles.canvas} />
    </div>
  );
}
