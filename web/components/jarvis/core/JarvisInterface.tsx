'use client';

import { useState, useEffect } from 'react';
import CircularHUD from '../hud/CircularHUD';
import RadarDisplay from '../hud/RadarDisplay';
import CircularGauge from '../hud/CircularGauge';
import TargetingReticle from '../hud/TargetingReticle';
import DataPanel from '../ui/DataPanel';
import ParticleField from '../effects/ParticleField';
import HolographicOverlay from '../effects/HolographicOverlay';
import { useSystemMetrics } from '@/hooks/jarvis/useSystemMetrics';
import styles from './JarvisInterface.module.css';

type JarvisState = 'idle' | 'listening' | 'processing' | 'responding';

export default function JarvisInterface() {
  const [state, setState] = useState<JarvisState>('listening');
  const [isActive, setIsActive] = useState(true);

  // Fetch real system metrics
  const { metrics } = useSystemMetrics(isActive);

  // Activation handler (will be replaced with voice activation later)
  const handleActivate = () => {
    setIsActive(!isActive);
    setState(isActive ? 'idle' : 'listening');
  };

  // Handle fullscreen toggle
  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === ' ') {
        e.preventDefault();
        setIsActive(prev => !prev);
        setState(prev => prev === 'idle' ? 'listening' : 'idle');
      }
      if (e.key === 'f' || e.key === 'F') {
        handleFullscreen();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  return (
    <div className={styles.interface}>
      {/* 3D Particle Background - Disabled for GPU performance */}
      {/* <ParticleField isActive={isActive} /> */}

      {/* Holographic Grid Overlay - Disabled for performance */}
      {/* <HolographicOverlay /> */}

      {/* Main HUD Container */}
      <div className={styles.hudContainer}>
        {/* Central Circular HUD */}
        <CircularHUD
          state={state}
          isActive={isActive}
          cpuUsage={metrics.cpu}
          memoryUsage={metrics.memory}
          gpuUtilization={metrics.gpuUtilization}
          gpuMemory={metrics.gpuMemory}
          temperature={metrics.temperature}
        />

        {/* Targeting Reticle - Top Center */}
        <div className={styles.targetingReticle}>
          <TargetingReticle isActive={isActive} />
        </div>

        {/* Radar Display - Bottom Left */}
        <div className={styles.radar}>
          <RadarDisplay isActive={isActive} />
        </div>

        {/* Circular Gauges - Bottom Right */}
        <div className={styles.gauges}>
          <CircularGauge
            label="CPU"
            value={metrics.cpu}
            max={100}
            unit="%"
            color="yellow"
            isActive={isActive}
          />
          <CircularGauge
            label="MEMORY"
            value={metrics.memory}
            max={100}
            unit="%"
            color="green"
            isActive={isActive}
          />
          <CircularGauge
            label="TEMP"
            value={metrics.temperature}
            max={100}
            unit="°C"
            color="cyan"
            isActive={isActive}
          />
        </div>

        {/* Data Panels - Removed for cleaner UX (redundant with center HUD) */}
        {/* <DataPanel title="SYSTEM STATUS" position="left" isActive={isActive} /> */}
        {/* <DataPanel title="DIAGNOSTICS" position="right" isActive={isActive} /> */}

        {/* Activation Button (temporary until voice is added) */}
        <button
          className={`${styles.activationButton} ${isActive ? styles.active : ''}`}
          onClick={handleActivate}
        >
          {isActive ? 'DEACTIVATE' : 'ACTIVATE'}
        </button>

        {/* Controls Help */}
        <div className={styles.controls}>
          <div className={styles.controlItem}>SPACE: Activate</div>
          <div className={styles.controlItem}>F: Fullscreen</div>
        </div>
      </div>
    </div>
  );
}
