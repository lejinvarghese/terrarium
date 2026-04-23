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
      <svg className={styles.svg} viewBox="0 0 800 800">
        {/* Glowing Core */}
        <defs>
          {/* Core Glow Filter */}
          <filter id="coreGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feFlood floodColor="#00F0FF" floodOpacity="0.8" />
            <feComposite in2="blur" operator="in" />
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Ring Glow Filter */}
          <filter id="ringGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feFlood floodColor="#00F0FF" floodOpacity="0.5" />
            <feComposite in2="blur" operator="in" />
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Gradient for core */}
          <radialGradient id="coreGradient">
            <stop offset="0%" stopColor="#00FFFF" stopOpacity="1" />
            <stop offset="50%" stopColor="#00F0FF" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#0084FF" stopOpacity="0.3" />
          </radialGradient>
        </defs>

        {/* Central Glowing Core */}
        <circle
          ref={coreRef}
          cx="400"
          cy="400"
          r="40"
          fill="url(#coreGradient)"
          filter="url(#coreGlow)"
          className={`${styles.core} ${isActive ? styles.coreActive : ''}`}
        />

        {/* Inner Core Detail */}
        <circle
          cx="400"
          cy="400"
          r="30"
          fill="none"
          stroke="#00FFFF"
          strokeWidth="2"
          opacity="0.6"
          className={styles.corePulse}
        />

        {/* Ring 1 - Innermost rotating ring */}
        <circle
          cx="400"
          cy="400"
          r="80"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="1.5"
          opacity="0.7"
          filter="url(#ringGlow)"
          className={styles.ring1}
          strokeDasharray="10 5"
        />

        {/* Ring 2 - Second ring with segments */}
        <circle
          cx="400"
          cy="400"
          r="120"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="2"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.ring2}
          strokeDasharray="20 10"
        />

        {/* Ring 3 - Larger ring */}
        <circle
          cx="400"
          cy="400"
          r="170"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="1"
          opacity="0.5"
          filter="url(#ringGlow)"
          className={styles.ring3}
          strokeDasharray="5 15"
        />

        {/* Ring 4 - Outermost ring */}
        <circle
          cx="400"
          cy="400"
          r="220"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="1.5"
          opacity="0.4"
          filter="url(#ringGlow)"
          className={styles.ring4}
          strokeDasharray="30 20"
        />

        {/* Diagnostic Arcs - Top */}
        <path
          d="M 300 200 A 120 120 0 0 1 500 200"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="2"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.arcTop}
        />

        {/* Diagnostic Arcs - Bottom */}
        <path
          d="M 300 600 A 120 120 0 0 0 500 600"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="2"
          opacity="0.6"
          filter="url(#ringGlow)"
          className={styles.arcBottom}
        />

        {/* Targeting Lines */}
        <line x1="400" y1="180" x2="400" y2="220" stroke="#00F0FF" strokeWidth="1" opacity="0.5" />
        <line x1="400" y1="580" x2="400" y2="620" stroke="#00F0FF" strokeWidth="1" opacity="0.5" />
        <line x1="180" y1="400" x2="220" y2="400" stroke="#00F0FF" strokeWidth="1" opacity="0.5" />
        <line x1="580" y1="400" x2="620" y2="400" stroke="#00F0FF" strokeWidth="1" opacity="0.5" />

        {/* Corner Brackets */}
        <g className={styles.corners}>
          {/* Top Left */}
          <path d="M 250 250 L 250 280" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />
          <path d="M 250 250 L 280 250" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />

          {/* Top Right */}
          <path d="M 550 250 L 550 280" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />
          <path d="M 550 250 L 520 250" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />

          {/* Bottom Left */}
          <path d="M 250 550 L 250 520" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />
          <path d="M 250 550 L 280 550" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />

          {/* Bottom Right */}
          <path d="M 550 550 L 550 520" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />
          <path d="M 550 550 L 520 550" stroke="#00F0FF" strokeWidth="2" opacity="0.7" />
        </g>

        {/* Data Points */}
        <g className={styles.dataPoints}>
          <circle cx="300" cy="300" r="3" fill="#00F0FF" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="500" cy="300" r="3" fill="#00F0FF" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="300" cy="500" r="3" fill="#00F0FF" opacity="0.8">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite" />
          </circle>
          <circle cx="500" cy="500" r="3" fill="#00F0FF" opacity="0.8">
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
