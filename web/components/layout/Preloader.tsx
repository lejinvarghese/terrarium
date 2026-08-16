"use client";

import { useEffect, useState } from "react";
import styles from "./Preloader.module.css";

const PRELOADER_DURATION = 3600; // 3.6 seconds
const SESSION_KEY = "terrarium_preloader_shown";

export default function Preloader() {
  const [isVisible, setIsVisible] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Check if preloader was already shown in this session
    const hasShown = sessionStorage.getItem(SESSION_KEY);

    if (hasShown) {
      setIsVisible(false);
      return;
    }

    // Animate progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 100 / (PRELOADER_DURATION / 50); // Update every 50ms
      });
    }, 50);

    // Hide preloader after duration
    const hideTimer = setTimeout(() => {
      setIsVisible(false);
      sessionStorage.setItem(SESSION_KEY, "true");
    }, PRELOADER_DURATION);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(hideTimer);
    };
  }, []);

  if (!isVisible) return null;

  return (
    <div className={styles.preloader}>
      <div className={styles.content}>
        <div className={styles.logo}>
          <div className={styles.logoGrid}>
            {Array.from({ length: 9 }).map((_, i) => (
              <div
                key={i}
                className={styles.logoCell}
                style={{
                  animationDelay: `${i * 0.1}s`,
                }}
              />
            ))}
          </div>
        </div>

        <h1 className={styles.title}>TERRARIUM</h1>
        <p className={styles.subtitle}>Spawning</p>

        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className={styles.loadingText}>
          Initializing systems. {Math.floor(progress)}%
        </p>
      </div>
    </div>
  );
}
