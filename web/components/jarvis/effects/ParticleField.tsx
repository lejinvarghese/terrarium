'use client';

import { useRef, useMemo } from 'react';
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
    const count = 2000;
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
        color="#00F0FF"
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
  return (
    <div className={styles.container}>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 75 }}
        gl={{ alpha: true, antialias: true }}
      >
        <ambientLight intensity={0.5} />
        <Particles isActive={isActive} />
      </Canvas>
    </div>
  );
}
