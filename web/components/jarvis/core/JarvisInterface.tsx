'use client';

import { useState, useEffect } from 'react';
import CircularHUD from '../hud/CircularHUD';
import ParticleField from '../effects/ParticleField';
import HolographicOverlay from '../effects/HolographicOverlay';
import styles from './JarvisInterface.module.css';

type JarvisState = 'idle' | 'listening' | 'processing' | 'responding';

export default function JarvisInterface() {
  const [state, setState] = useState<JarvisState>('idle');
  const [isActive, setIsActive] = useState(false);

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
