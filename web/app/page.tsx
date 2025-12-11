'use client';

import Link from 'next/link';
import { services } from '@/data/services';
import dynamic from 'next/dynamic';
import styles from './page.module.css';

const GridTrail = dynamic(() => import('@/components/effects/GridTrail'), {
  ssr: false,
});

export default function Home() {
  return (
    <main className={styles.main}>
      <GridTrail cellSize={50} trailColor="#EBFA1D" fadeSpeed={0.05} trailRadius={3} />
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className="container">
          <h1 className={styles.title}>terrarium</h1>
          <p className={styles.tagline}>
            Embark on a visionary journey where AI agents and innovation converge,
            crafting a future where technology transcends boundaries.
          </p>
          <Link href="/ecosystem" className={`${styles.cta} cursor-hover`}>
            Explore the Ecosystem
          </Link>
        </div>
      </section>

      {/* Services Grid Section */}
      <section className={styles.services}>
        <div className="container">
          <h2 className={styles.sectionTitle}>//the ai ecosystem</h2>
          <div className={styles.grid}>
            {services.map((service, index) => (
              <a
                key={service.id}
                href={service.url}
                className={`${styles.card} cursor-hover`}
                style={{
                  animationDelay: `${index * 0.15}s`,
                  color: service.color,
                }}
              >
                <div className={styles.cardHeader}>
                  <span className={styles.prefix} style={{ color: service.color }}>
                    {service.prefix}
                  </span>
                  <span
                    className={styles.status}
                    data-status={service.status}
                  >
                    {service.status.toUpperCase()}
                  </span>
                </div>
                <h3 className={styles.cardTitle}>{service.name}</h3>
                <p className={styles.cardTagline}>{service.tagline}</p>
                <p className={styles.cardDescription}>{service.description}</p>
                <div className={styles.features}>
                  {service.features.slice(0, 3).map((feature, i) => (
                    <span key={i} className={styles.feature}>
                      {feature}
                    </span>
                  ))}
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className={styles.about}>
        <div className="container">
          <h2 className={styles.sectionTitle}>Inspired by open innovation</h2>
          <p className={styles.aboutText}>
            Terrarium is a comprehensive meta-project that orchestrates multiple
            AI services into a cohesive ecosystem. Powered by the latest in AI technology,
            our platform offers a unique exploration of machine learning, natural language,
            and tomorrow's possibilities—entirely self-hosted.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <p>site by starscream · powered by open source</p>
        </div>
      </footer>
    </main>
  );
}
