'use client';

import { Suspense } from 'react';
import JarvisInterface from '@/components/jarvis/core/JarvisInterface';
import '@/styles/jarvis/variables.css';
import '@/styles/jarvis/animations.css';
import styles from './jarvis.module.css';

export default function JarvisPage() {
  return (
    <main className={styles.container}>
      <Suspense fallback={<div className={styles.loading}>INITIALIZING JARVIS...</div>}>
        <JarvisInterface />
      </Suspense>
    </main>
  );
}
