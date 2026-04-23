'use client';

import { useState, useEffect } from 'react';
import CircularHUD from '../hud/CircularHUD';
import RadarDisplay from '../hud/RadarDisplay';
import CircularGauge from '../hud/CircularGauge';
import TargetingReticle from '../hud/TargetingReticle';
import DataPanel from '../ui/DataPanel';
import ParticleField from '../effects/ParticleField';
import HolographicOverlay from '../effects/HolographicOverlay';
import styles from './JarvisInterface.module.css';

type JarvisState = 'idle' | 'listening' | 'processing' | 'responding';

export default function JarvisInterface() {
  const [state, setState] = useState<JarvisState>('listening');
  const [isActive, setIsActive] = useState(true);
  const [cpuUsage, setCpuUsage] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);
  const [temperature, setTemperature] = useState(0);

  // Simulate system metrics
  useEffect(() => {
    if (!isActive) {
      setCpuUsage(0);
      setMemoryUsage(0);
      setTemperature(0);
      return;
    }

    // Initial values
    setCpuUsage(Math.random() * 30 + 20);
    setMemoryUsage(Math.random() * 40 + 30);
    setTemperature(Math.random() * 10 + 35);

    // Update periodically
    const interval = setInterval(() => {
      setCpuUsage((prev) => Math.min(100, Math.max(0, prev + (Math.random() - 0.5) * 10)));
      setMemoryUsage((prev) => Math.min(100, Math.max(0, prev + (Math.random() - 0.5) * 5)));
      setTemperature((prev) => Math.min(100, Math.max(20, prev + (Math.random() - 0.5) * 2)));
    }, 2000);

    return () => clearInterval(interval);
  }, [isActive]);

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
        handleActivate();
      }
      if (e.key === 'f' || e.key === 'F') {
        handleFullscreen();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isActive]);

  return (
    <div className={styles.interface}>
      {/* 3D Particle Background */}
      <ParticleField isActive={isActive} />

      {/* Holographic Grid Overlay */}
      <HolographicOverlay />

      {/* Main HUD Container */}
      <div className={styles.hudContainer}>
        {/* Central Circular HUD */}
        <CircularHUD state={state} isActive={isActive} />

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
            value={cpuUsage}
            max={100}
            unit="%"
            color="yellow"
            isActive={isActive}
          />
          <CircularGauge
            label="MEMORY"
            value={memoryUsage}
            max={100}
            unit="%"
            color="green"
            isActive={isActive}
          />
          <CircularGauge
            label="TEMP"
            value={temperature}
            max={100}
            unit="°C"
            color="cyan"
            isActive={isActive}
          />
        </div>

        {/* Data Panels */}
        <DataPanel title="SYSTEM STATUS" position="left" isActive={isActive} />
        <DataPanel title="DIAGNOSTICS" position="right" isActive={isActive} />

        {/* Status Display */}
        <div className={styles.statusDisplay}>
          <div className={styles.statusText}>
            {state === 'idle' && 'STANDBY'}
            {state === 'listening' && 'LISTENING...'}
            {state === 'processing' && 'PROCESSING...'}
            {state === 'responding' && 'JARVIS ONLINE'}
          </div>
        </div>

        {/* Activation Button (temporary until voice is added) */}
        <button
          className={`${styles.activationButton} ${isActive ? styles.active : ''}`}
          onClick={handleActivate}
        >
          {isActive ? 'DEACTIVATE' : 'ACTIVATE JARVIS'}
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
