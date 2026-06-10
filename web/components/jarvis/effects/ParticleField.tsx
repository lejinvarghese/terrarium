'use client';

import { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import styles from './ParticleField.module.css';

interface ParticlesProps {
  isActive: boolean;
}

function Particles({ isActive }: ParticlesProps) {
  const ref = useRef<THREE.Points>(null);

  // Generate random particle positions
  const particles = useMemo(() => {
    const count = 400; // Reduced for better performance
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      // Distribute particles in a sphere around the center
      const radius = Math.random() * 25 + 5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);

      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi);
    }

    return positions;
  }, []);

  // Animate particles
  useFrame((state) => {
    if (!ref.current) return;

    const time = state.clock.getElapsedTime();

    // Slow rotation
    ref.current.rotation.y = time * 0.05;
    ref.current.rotation.x = time * 0.02;

    // If active, particles move toward center
    if (isActive) {
      const positions = ref.current.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < positions.length; i += 3) {
        const distance = Math.sqrt(
          positions[i] ** 2 + positions[i + 1] ** 2 + positions[i + 2] ** 2
        );

        if (distance > 1) {
          positions[i] *= 0.99;
          positions[i + 1] *= 0.99;
          positions[i + 2] *= 0.99;
        }
      }
      ref.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={ref} positions={particles} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#EBFA1D"
        size={0.08}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.6}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

interface ParticleFieldProps {
  isActive: boolean;
}

export default function ParticleField({ isActive }: ParticleFieldProps) {
  const [hasWebGL, setHasWebGL] = useState(true);

  useEffect(() => {
    // Check for WebGL support on client side
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) {
        console.warn('WebGL not supported, ParticleField disabled');
        setHasWebGL(false);
      }
    } catch (e) {
      console.warn('WebGL check failed:', e);
      setHasWebGL(false);
    }
  }, []);

  if (!hasWebGL) return null;

  return (
    <div className={styles.container}>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 75 }}
        gl={{
          alpha: true,
          antialias: false, // Disable for better performance
          powerPreference: 'high-performance',
          failIfMajorPerformanceCaveat: false,
        }}
        dpr={Math.min(window.devicePixelRatio || 1, 2)} // Cap at 2x for performance
        performance={{ min: 0.5 }} // Allow degradation for performance
      >
        <ambientLight intensity={0.5} />
        <Particles isActive={isActive} />
      </Canvas>
    </div>
  );
}
