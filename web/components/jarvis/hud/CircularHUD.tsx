"use client";

import { useEffect, useRef } from "react";
import styles from "./CircularHUD.module.css";

interface CircularHUDProps {
  state: "idle" | "listening" | "processing" | "responding";
  isActive: boolean;
  cpuUsage?: number;
  memoryUsage?: number;
  gpuUtilization?: number;
  gpuMemory?: number;
  temperature?: number;
}

export default function CircularHUD({
  state,
  isActive,
  cpuUsage = 0,
  memoryUsage = 0,
  gpuUtilization = 0,
  gpuMemory = 0,
  temperature = 0,
}: CircularHUDProps) {
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

  // Create arc path for thick filled rings
  const createRingPath = (
    radius: number,
    thickness: number,
    percentage: number,
  ) => {
    const innerRadius = radius - thickness / 2;
    const outerRadius = radius + thickness / 2;
    const angle = (percentage / 100) * 360;

    if (percentage === 0) return "";
    if (percentage >= 100) {
      // Full circle
      return `
        M ${1000 + outerRadius} 1000
        A ${outerRadius} ${outerRadius} 0 1 1 ${1000 + outerRadius - 0.001} 1000
        L ${1000 + innerRadius - 0.001} 1000
        A ${innerRadius} ${innerRadius} 0 1 0 ${1000 + innerRadius} 1000
        Z
      `;
    }

    const endAngle = angle - 90; // Start from top
    const largeArc = angle > 180 ? 1 : 0;

    const outerEndX = 1000 + outerRadius * Math.cos((endAngle * Math.PI) / 180);
    const outerEndY = 1000 + outerRadius * Math.sin((endAngle * Math.PI) / 180);
    const innerEndX = 1000 + innerRadius * Math.cos((endAngle * Math.PI) / 180);
    const innerEndY = 1000 + innerRadius * Math.sin((endAngle * Math.PI) / 180);

    return `
      M 1000 ${1000 - outerRadius}
      A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${outerEndX} ${outerEndY}
      L ${innerEndX} ${innerEndY}
      A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 1000 ${1000 - innerRadius}
      Z
    `;
  };

  // Color with opacity for diffused effect
  const getMetricColor = (
    value: number,
    type: "cpu" | "memory" | "temp",
    opacity = 0.6,
  ) => {
    let baseColor;
    if (type === "temp") {
      if (value > 80) baseColor = "255, 68, 68";
      else if (value > 70) baseColor = "255, 184, 0";
      else baseColor = "0, 255, 136";
    } else {
      if (value > 80) baseColor = "255, 68, 68";
      else if (value > 60) baseColor = "255, 184, 0";
      else baseColor = "0, 255, 136";
    }
    return `rgba(${baseColor}, ${opacity})`;
  };

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
          {/* Core Glow Filter - Enhanced */}
          <filter id="coreGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="40" result="blur" />
            <feFlood floodColor="#EBFA1D" floodOpacity="1" />
            <feComposite in2="blur" operator="in" result="glow" />
            <feMerge>
              <feMergeNode in="glow" />
              <feMergeNode in="glow" />
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
          className={`${styles.core} ${isActive ? styles.coreActive : ""}`}
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

        {/* Ring 1 - CPU Usage */}
        <circle
          cx="1000"
          cy="1000"
          r="190"
          fill="none"
          stroke="rgba(235, 250, 29, 0.08)"
          strokeWidth="50"
        />
        <path
          d={createRingPath(190, 50, cpuUsage)}
          fill={getMetricColor(cpuUsage, "cpu", 0.5)}
          filter="url(#ringGlow)"
          style={{ transition: "all 0.8s ease" }}
        />
        <text
          x="1000"
          y="795"
          textAnchor="middle"
          fill="rgba(235, 250, 29, 0.5)"
          fontSize="11"
          fontFamily="JetBrains Mono, monospace"
          letterSpacing="3"
          fontWeight="300"
        >
          CPU
        </text>

        {/* Ring 2 - Memory Usage */}
        <circle
          cx="1000"
          cy="1000"
          r="270"
          fill="none"
          stroke="rgba(0, 255, 136, 0.08)"
          strokeWidth="50"
        />
        <path
          d={createRingPath(270, 50, memoryUsage)}
          fill={getMetricColor(memoryUsage, "memory", 0.5)}
          filter="url(#ringGlow)"
          style={{ transition: "all 0.8s ease" }}
        />
        <text
          x="1000"
          y="715"
          textAnchor="middle"
          fill="rgba(0, 255, 136, 0.5)"
          fontSize="11"
          fontFamily="JetBrains Mono, monospace"
          letterSpacing="3"
          fontWeight="300"
        >
          MEM
        </text>

        {/* Ring 3 - GPU Utilization */}
        <circle
          cx="1000"
          cy="1000"
          r="350"
          fill="none"
          stroke="rgba(255, 184, 0, 0.08)"
          strokeWidth="50"
        />
        <path
          d={createRingPath(350, 50, gpuUtilization)}
          fill={getMetricColor(gpuUtilization, "cpu", 0.5)}
          filter="url(#ringGlow)"
          style={{ transition: "all 0.8s ease" }}
        />
        <text
          x="1000"
          y="635"
          textAnchor="middle"
          fill="rgba(255, 184, 0, 0.5)"
          fontSize="11"
          fontFamily="JetBrains Mono, monospace"
          letterSpacing="3"
          fontWeight="300"
        >
          GPU
        </text>

        {/* Ring 4 - GPU Memory */}
        <circle
          cx="1000"
          cy="1000"
          r="430"
          fill="none"
          stroke="rgba(255, 100, 200, 0.08)"
          strokeWidth="50"
        />
        <path
          d={createRingPath(430, 50, gpuMemory)}
          fill={getMetricColor(gpuMemory, "memory", 0.5)}
          filter="url(#ringGlow)"
          style={{ transition: "all 0.8s ease" }}
        />
        <text
          x="1000"
          y="555"
          textAnchor="middle"
          fill="rgba(255, 100, 200, 0.5)"
          fontSize="11"
          fontFamily="JetBrains Mono, monospace"
          letterSpacing="3"
          fontWeight="300"
        >
          VRAM
        </text>

        {/* Ring 5 - Temperature */}
        <circle
          cx="1000"
          cy="1000"
          r="510"
          fill="none"
          stroke="rgba(0, 255, 242, 0.08)"
          strokeWidth="50"
        />
        <path
          d={createRingPath(510, 50, temperature)}
          fill={getMetricColor(temperature, "temp", 0.5)}
          filter="url(#ringGlow)"
          style={{ transition: "all 0.8s ease" }}
        />
        <text
          x="1000"
          y="475"
          textAnchor="middle"
          fill="rgba(0, 255, 242, 0.5)"
          fontSize="11"
          fontFamily="JetBrains Mono, monospace"
          letterSpacing="3"
          fontWeight="300"
        >
          TEMP
        </text>

        {/* Ring 6 - Voice Activity (reserved for voice integration) */}
        <circle
          cx="1000"
          cy="1000"
          r="590"
          fill="none"
          stroke="#EBFA1D"
          strokeWidth="4"
          opacity={state === "listening" || state === "processing" ? 0.8 : 0.3}
          filter="url(#ringGlow)"
          className={
            state === "listening" || state === "processing"
              ? styles.voiceActive
              : styles.voiceIdle
          }
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
        <line
          x1="1000"
          y1="450"
          x2="1000"
          y2="550"
          stroke="#EBFA1D"
          strokeWidth="2"
          opacity="0.5"
        />
        <line
          x1="1000"
          y1="1450"
          x2="1000"
          y2="1550"
          stroke="#EBFA1D"
          strokeWidth="2"
          opacity="0.5"
        />
        <line
          x1="450"
          y1="1000"
          x2="550"
          y2="1000"
          stroke="#EBFA1D"
          strokeWidth="2"
          opacity="0.5"
        />
        <line
          x1="1450"
          y1="1000"
          x2="1550"
          y2="1000"
          stroke="#EBFA1D"
          strokeWidth="2"
          opacity="0.5"
        />

        {/* Corner Brackets */}
        <g className={styles.corners}>
          {/* Top Left */}
          <path
            d="M 625 625 L 625 700"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />
          <path
            d="M 625 625 L 700 625"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />

          {/* Top Right */}
          <path
            d="M 1375 625 L 1375 700"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />
          <path
            d="M 1375 625 L 1300 625"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />

          {/* Bottom Left */}
          <path
            d="M 625 1375 L 625 1300"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />
          <path
            d="M 625 1375 L 700 1375"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />

          {/* Bottom Right */}
          <path
            d="M 1375 1375 L 1375 1300"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />
          <path
            d="M 1375 1375 L 1300 1375"
            stroke="#00FFF2"
            strokeWidth="4"
            opacity="0.7"
          />
        </g>

        {/* Data Points */}
        <g className={styles.dataPoints}>
          <circle cx="750" cy="750" r="8" fill="#EBFA1D" opacity="0.8">
            <animate
              attributeName="opacity"
              values="0.3;1;0.3"
              dur="2s"
              repeatCount="indefinite"
            />
          </circle>
          <circle cx="1250" cy="750" r="8" fill="#00FF88" opacity="0.8">
            <animate
              attributeName="opacity"
              values="0.3;1;0.3"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          <circle cx="750" cy="1250" r="8" fill="#00FFF2" opacity="0.8">
            <animate
              attributeName="opacity"
              values="0.3;1;0.3"
              dur="3s"
              repeatCount="indefinite"
            />
          </circle>
          <circle cx="1250" cy="1250" r="8" fill="#EBFA1D" opacity="0.8">
            <animate
              attributeName="opacity"
              values="0.3;1;0.3"
              dur="2.2s"
              repeatCount="indefinite"
            />
          </circle>
        </g>
      </svg>

      {/* Floating Info Panels */}
      <div className={styles.infoPanel} style={{ top: "10%", left: "5%" }}>
        <div className={styles.panelTitle}>SYSTEM</div>
        <div className={styles.panelValue}>ONLINE</div>
      </div>

      <div className={styles.infoPanel} style={{ top: "10%", right: "5%" }}>
        <div className={styles.panelTitle}>STATUS</div>
        <div className={styles.panelValue}>{state.toUpperCase()}</div>
      </div>

      <div className={styles.infoPanel} style={{ bottom: "10%", left: "5%" }}>
        <div className={styles.panelTitle}>CORE</div>
        <div className={styles.panelValue}>{isActive ? "100%" : "0%"}</div>
      </div>

      <div className={styles.infoPanel} style={{ bottom: "10%", right: "5%" }}>
        <div className={styles.panelTitle}>MODE</div>
        <div className={styles.panelValue}>STANDBY</div>
      </div>
    </div>
  );
}
