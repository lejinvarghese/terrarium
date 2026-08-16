"use client";

import { useEffect, useState } from "react";
import styles from "./TargetingReticle.module.css";

interface TargetingReticleProps {
  isActive: boolean;
}

export default function TargetingReticle({ isActive }: TargetingReticleProps) {
  const [locked, setLocked] = useState(false);

  useEffect(() => {
    if (!isActive) {
      setLocked(false);
      return;
    }

    // Simulate lock-on after 2 seconds
    const timeout = setTimeout(() => {
      setLocked(true);
    }, 2000);

    return () => clearTimeout(timeout);
  }, [isActive]);

  return (
    <div className={`${styles.container} ${locked ? styles.locked : ""}`}>
      <svg
        className={styles.svg}
        viewBox="0 0 300 300"
        xmlns="http://www.w3.org/2000/svg"
        shapeRendering="geometricPrecision"
      >
        <defs>
          <filter id="reticleGlow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feFlood floodColor={locked ? "#00FF88" : "#EBFA1D"} />
            <feComposite in2="blur" operator="in" />
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Outer ring */}
        <circle
          cx="150"
          cy="150"
          r="80"
          fill="none"
          stroke={locked ? "#00FF88" : "#EBFA1D"}
          strokeWidth="1.5"
          opacity="0.6"
          filter="url(#reticleGlow)"
          className={styles.outerRing}
        />

        {/* Inner ring */}
        <circle
          cx="150"
          cy="150"
          r="50"
          fill="none"
          stroke={locked ? "#00FF88" : "#EBFA1D"}
          strokeWidth="1"
          opacity="0.4"
          className={styles.innerRing}
        />

        {/* Crosshair lines */}
        <g className={styles.crosshair}>
          {/* Top */}
          <line
            x1="150"
            y1="70"
            x2="150"
            y2="100"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            opacity="0.8"
          />
          {/* Bottom */}
          <line
            x1="150"
            y1="200"
            x2="150"
            y2="230"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            opacity="0.8"
          />
          {/* Left */}
          <line
            x1="70"
            y1="150"
            x2="100"
            y2="150"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            opacity="0.8"
          />
          {/* Right */}
          <line
            x1="200"
            y1="150"
            x2="230"
            y2="150"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            opacity="0.8"
          />
        </g>

        {/* Corner brackets */}
        <g className={styles.corners}>
          {/* Top-left */}
          <path
            d="M 90 90 L 90 110 M 90 90 L 110 90"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            fill="none"
            opacity="0.7"
          />
          {/* Top-right */}
          <path
            d="M 210 90 L 210 110 M 210 90 L 190 90"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            fill="none"
            opacity="0.7"
          />
          {/* Bottom-left */}
          <path
            d="M 90 210 L 90 190 M 90 210 L 110 210"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            fill="none"
            opacity="0.7"
          />
          {/* Bottom-right */}
          <path
            d="M 210 210 L 210 190 M 210 210 L 190 210"
            stroke={locked ? "#00FF88" : "#EBFA1D"}
            strokeWidth="2"
            fill="none"
            opacity="0.7"
          />
        </g>

        {/* Center dot */}
        <circle
          cx="150"
          cy="150"
          r="3"
          fill={locked ? "#00FF88" : "#EBFA1D"}
          opacity="0.9"
          filter="url(#reticleGlow)"
        >
          {locked && (
            <animate
              attributeName="r"
              values="3;5;3"
              dur="1s"
              repeatCount="indefinite"
            />
          )}
        </circle>

        {/* Scanning arc (only when not locked) */}
        {!locked && (
          <circle
            cx="150"
            cy="150"
            r="65"
            fill="none"
            stroke="#EBFA1D"
            strokeWidth="1"
            strokeDasharray="5 10"
            opacity="0.5"
            className={styles.scanningArc}
          />
        )}
      </svg>

      {/* Status text */}
      <div
        className={styles.status}
        style={{ color: locked ? "#00FF88" : "#EBFA1D" }}
      >
        {locked ? "LOCKED" : "SCANNING"}
      </div>
    </div>
  );
}
