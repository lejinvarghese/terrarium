"use client";

import Link from "next/link";
import styles from "./Navigation.module.css";

export default function Navigation() {
  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoPrefix}>{"//"}</span>
          terrarium
        </Link>

        <div className={styles.links}>
          <Link href="/undergrowth" className={styles.link}>
            <span className={styles.linkPrefix}>01</span>
            undergrowth
          </Link>
          <a
            href="https://fern.mutatedterrarium.com"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.link}
          >
            <span className={styles.linkPrefix}>02</span>
            fern
          </a>
          <a
            href="https://jarvis.mutatedterrarium.com"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.link}
          >
            <span className={styles.linkPrefix}>03</span>
            jarvis
          </a>
        </div>
      </div>
    </nav>
  );
}
