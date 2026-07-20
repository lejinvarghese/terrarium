'use client';

import Link from 'next/link';
import { services } from '@/data/services';
import dynamic from 'next/dynamic';
import ServiceCard from '@/components/sections/ServiceCard';
import styles from './page.module.css';

const GridTrail = dynamic(() => import('@/components/effects/GridTrail'), {
  ssr: false,
});

// Multiplex Network visualization - can be easily removed by commenting out
// Shows Layer 0 (physical/carbon beings) and Layer 1 (digital/silicon agents)
const MultiplexNetwork = dynamic(() => import('@/components/visualizations/MultiplexNetwork'), {
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
            A digital home where cybernetic minds swarm, grow, and tend to your ecosystem.
            Step through the glass—where technology and life merge as one.
          </p>
          <Link href="/ecosystem" className={`${styles.cta} cursor-hover`}>
            Explore
          </Link>
        </div>
      </section>

      {/* Services Grid Section */}
      <section className={styles.services}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.titlePrefix}>{'//'}</span>substations
          </h2>
          <div className={styles.grid}>
            {services.map((service, index) => (
              <ServiceCard
                key={service.id}
                service={service}
                index={index}
              />
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className={styles.about}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.titlePrefix}>{'//'}</span>the swarm
          </h2>
          <p className={styles.aboutText}>
            The terrarium is a living ecosystem, home to a mosaic of cybernetic and physical minds, each a distinct node in the swarm, together shaping unique landscapes of thought, culture, and experience within this sprawling cyberpunk-organic domain. Subcultures and intelligences flourish in its interconnected strata, co-evolving as a distributed swarm.
          </p>
        </div>
      </section>

      {/* ========================================
          Multiplex Network Visualization
          Layer 0: Physical beings (humans, dog, plants)
          Layer 1: Digital beings (AI landscapes)
          Comment out this entire section to remove
          ======================================== */}
      <section className={styles.landscapes}>
        <MultiplexNetwork />
      </section>
      {/* ======================================== */}

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <p>site by starscream · powered by open source</p>
        </div>
      </footer>
    </main>
  );
}
