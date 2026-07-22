'use client';

import styles from './HomeButton.module.css';

export default function HomeButton() {
  return (
    <a
      href="https://mutatedterrarium.com"
      className={styles.homeButton}
      title="Return to Terrarium"
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
        <polyline points="9 22 9 12 15 12 15 22" />
      </svg>
      <span className={styles.label}>terrarium</span>
    </a>
  );
}
