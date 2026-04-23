'use client';

import { useEffect, useRef } from 'react';
import styles from './CircularHUD.module.css';

interface CircularHUDProps {
  state: 'idle' | 'listening' | 'processing' | 'responding';
  isActive: boolean;
}

export default function CircularHUD({ state, isActive }: CircularHUDProps) {
  const coreRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    if (isActive && coreRef.current) {
      // Add activation ripple effect
      coreRef.current.classList.add(styles.activating);
      setTimeout(() => {
        coreRef.current?.classList.remove(styles.activating);
      }, 600);
    }
  }, [isActive]);

  return (
    <div className={styles.container}>
      <svg
        className={styles.svg}
        viewBox="0 0 2000 2000"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="geometricPrecision"
      >
        {/* Glowing Core */}
        <defs>
          {/* Core Glow Filter */}
          <filter id="coreGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="25" result="blur" />
            <feFlood floodColor="#EBFA1D" floodOpacity="0.8" />
            <feComposite in2="blur" operator="in" />
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Ring Glow Filter */}
          <filter id="ringGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feFlood floodColor="#EBFA1D" floodOpacity="0.5" />
            <feComposite in2="blur" operator="in" />
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Gradient for core */}
          <radialGradient id="coreGradient">
            <stop offset="0%" stopColor="#EBFA1D" stopOpacity="1" />
            <stop offset="50%" stopColor="#00FF88" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#00FFF2" stopOpacity="0.3" />
          </radialGradient>
        </defs>

        {/* Central Glowing Core */}
        <circle
          ref={coreRef}
          cx="1000"
          cy="1000"
          r="100"
          fill="url(#coreGradient)"
          filter="url(#coreGlow)"
          className={`${styles.core} ${isActive ? styles.coreActive : ''}`}
        />

        {/* Inner Core Detail */}
        <circle
          cx="1000"
          cy="1000"
          r="75"
          fill="none"
          stroke="#EBFA1D"
          strokeWidth="4"
          opacity="0.6"
          className={styles.corePulse}
        />

        {/* Ring 1 - Innermost rotating ring */}
        <circle
          cx="1000"
          cy="1000"
          r="200"
          fill="none"
          stroke="#EBFA1D"
          strokeWidth="3"
          opacity="0.7"
          filter="url(#ringGlow)"
          className={styles.ring1}
          strokeDasharray="25 12"
        />

        {/* Ring 2 - Second ring with segments */}
        <circle
          cx="1000"
          cy="1000"
          r="300"
          fill="none"
          stroke="#00FF88"
          strokeWidth="4"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.ring2}
          strokeDasharray="50 25"
        />

        {/* Ring 3 - Larger ring */}
        <circle
          cx="1000"
          cy="1000"
          r="425"
          fill="none"
          stroke="#00FFF2"
          strokeWidth="2"
          opacity="0.5"
          filter="url(#ringGlow)"
          className={styles.ring3}
          strokeDasharray="12 38"
        />

        {/* Ring 4 - Outermost ring */}
        <circle
          cx="1000"
          cy="1000"
          r="550"
          fill="none"
          stroke="#EBFA1D"
          strokeWidth="3"
          opacity="0.4"
          filter="url(#ringGlow)"
          className={styles.ring4}
          strokeDasharray="75 50"
        />

        {/* Diagnostic Arcs - Top */}
        <path
          d="M 750 500 A 300 300 0 0 1 1250 500"
          fill="none"
          stroke="#00FF88"
          strokeWidth="4"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.arcTop}
        />

        {/* Diagnostic Arcs - Bottom */}
        <path
          d="M 750 1500 A 300 300 0 0 0 1250 1500"
          fill="none"
          stroke="#00FF88"
          strokeWidth="4"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.arcBottom}
        />

        {/* Targeting Lines */}
        <line x1="1000" y1="450" x2="1000" y2="550" stroke="#EBFA1D" strokeWidth="2" opacity="0.5" />
        <line x1="1000" y1="1450" x2="1000" y2="1550" stroke="#EBFA1D" strokeWidth="2" opacity="0.5" />
        <line x1="450" y1="1000" x2="550" y2="1000" stroke="#EBFA1D" strokeWidth="2" opacity="0.5" />
        <line x1="1450" y1="1000" x2="1550" y2="1000" stroke="#EBFA1D" strokeWidth="2" opacity="0.5" />

        {/* Corner Brackets */}
        <g className={styles.corners}>
          {/* Top Left */}
          <path d="M 625 625 L 625 700" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />
          <path d="M 625 625 L 700 625" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />

          {/* Top Right */}
          <path d="M 1375 625 L 1375 700" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />
          <path d="M 1375 625 L 1300 625" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />

          {/* Bottom Left */}
          <path d="M 625 1375 L 625 1300" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />
          <path d="M 625 1375 L 700 1375" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />

          {/* Bottom Right */}
          <path d="M 1375 1375 L 1375 1300" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />
          <path d="M 1375 1375 L 1300 1375" stroke="#00FFF2" strokeWidth="4" opacity="0.7" />
        </g>

        {/* Data Points */}
        <g className={styles.dataPoints}>
          <circle cx="750" cy="750" r="8" fill="#EBFA1D" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="1250" cy="750" r="8" fill="#00FF88" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="750" cy="1250" r="8" fill="#00FFF2" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite" />
          </circle>
          <circle cx="1250" cy="1250" r="8" fill="#EBFA1D" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2.2s" repeatCount="indefinite" />
          </circle>
        </g>
      </svg>

      {/* Floating Info Panels */}
      <div className={styles.infoPanel} style={{ top: '10%', left: '5%' }}>
        <div className={styles.panelTitle}>SYSTEM</div>
        <div className={styles.panelValue}>ONLINE</div>
      </div>

      <div className={styles.infoPanel} style={{ top: '10%', right: '5%' }}>
        <div className={styles.panelTitle}>STATUS</div>
        <div className={styles.panelValue}>{state.toUpperCase()}</div>
      </div>

      <div className={styles.infoPanel} style={{ bottom: '10%', left: '5%' }}>
        <div className={styles.panelTitle}>CORE</div>
        <div className={styles.panelValue}>{isActive ? '100%' : '0%'}</div>
      </div>

      <div className={styles.infoPanel} style={{ bottom: '10%', right: '5%' }}>
        <div className={styles.panelTitle}>MODE</div>
        <div className={styles.panelValue}>STANDBY</div>
      </div>
    </div>
  );
}
