"use client";

import styles from "./HolographicOverlay.module.css";

export default function HolographicOverlay() {
  return (
    <div className={styles.container}>
      {/* Grid Pattern */}
      <div className={styles.grid}>
        <svg width="100%" height="100%" shapeRendering="crispEdges">
          <defs>
            <pattern
              id="grid"
              width="50"
              height="50"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 50 0 L 0 0 0 50"
                fill="none"
                stroke="rgba(235, 250, 29, 0.15)"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Scan Lines */}
      <div className={styles.scanLines}>
        <div className={styles.scanLine} style={{ animationDelay: "0s" }} />
        <div className={styles.scanLine} style={{ animationDelay: "2s" }} />
        <div className={styles.scanLine} style={{ animationDelay: "4s" }} />
      </div>

      {/* Glass Effect */}
      <div className={styles.glass} />

      {/* Corner Grids */}
      <div className={styles.cornerGrid} style={{ top: 0, left: 0 }}>
        <svg
          width="200"
          height="200"
          viewBox="0 0 200 200"
          shapeRendering="crispEdges"
        >
          <defs>
            <pattern
              id="cornerGridTL"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="#00FF88"
                strokeWidth="0.5"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#cornerGridTL)" />
        </svg>
      </div>

      <div className={styles.cornerGrid} style={{ top: 0, right: 0 }}>
        <svg
          width="200"
          height="200"
          viewBox="0 0 200 200"
          shapeRendering="crispEdges"
        >
          <defs>
            <pattern
              id="cornerGridTR"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="#00FF88"
                strokeWidth="0.5"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#cornerGridTR)" />
        </svg>
      </div>

      <div className={styles.cornerGrid} style={{ bottom: 0, left: 0 }}>
        <svg
          width="200"
          height="200"
          viewBox="0 0 200 200"
          shapeRendering="crispEdges"
        >
          <defs>
            <pattern
              id="cornerGridBL"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="#00FF88"
                strokeWidth="0.5"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#cornerGridBL)" />
        </svg>
      </div>

      <div className={styles.cornerGrid} style={{ bottom: 0, right: 0 }}>
        <svg
          width="200"
          height="200"
          viewBox="0 0 200 200"
          shapeRendering="crispEdges"
        >
          <defs>
            <pattern
              id="cornerGridBR"
              width="20"
              height="20"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="#00FF88"
                strokeWidth="0.5"
                opacity="0.3"
              />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#cornerGridBR)" />
        </svg>
      </div>

      {/* Holographic Noise/Flicker */}
      <div className={styles.noise} />
    </div>
  );
}
