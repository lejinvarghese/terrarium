'use client';

import { useState, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import JarvisInterface from '@/components/jarvis/core/JarvisInterface';
import SecureAccessModal from '@/components/ui/SecureAccessModal';
import '@/styles/jarvis/variables.css';
import '@/styles/jarvis/animations.css';
import styles from './jarvis.module.css';

const GridTrail = dynamic(() => import('@/components/effects/GridTrail'), {
  ssr: false,
});

export default function JarvisPage() {
  const [showAccessModal, setShowAccessModal] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = () => {
      const cookies = document.cookie.split(';');
      const authCookie = cookies.find((c) => c.trim().startsWith('terrarium_auth='));
      if (authCookie?.includes('valid')) {
        setIsAuthenticated(true);
        setShowAccessModal(false);
      }
    };
    checkAuth();
  }, []);

  if (!isAuthenticated) {
    return (
      <>
        <div className={styles.lockedContainer}>
          <GridTrail
            cellSize={50}
            trailColor="#EBFA1D"
            fadeSpeed={0.05}
            trailRadius={3}
          />
          <div className={styles.lockedContent}>
            <h1 className={styles.lockedTitle}>RESTRICTED ACCESS</h1>
          </div>
        </div>
        <SecureAccessModal
          isOpen={showAccessModal}
          onClose={() => setShowAccessModal(false)}
          targetUrl="/jarvis"
          title="ACCESS REQUIRED"
          onAuthenticated={() => {
            setIsAuthenticated(true);
            setShowAccessModal(false);
          }}
        />
      </>
    );
  }

  return (
    <main className={styles.container}>
      <Suspense fallback={<div className={styles.loading}>INITIALIZING</div>}>
        <JarvisInterface />
      </Suspense>
    </main>
  );
}
