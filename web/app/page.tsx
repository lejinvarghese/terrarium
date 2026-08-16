"use client";

import Link from "next/link";
import { services } from "@/data/services";
import dynamic from "next/dynamic";
import ServiceCard from "@/components/sections/ServiceCard";
import Navigation from "@/components/navigation/Navigation";
import styles from "./page.module.css";

const GridTrail = dynamic(() => import("@/components/effects/GridTrail"), {
  ssr: false,
});

// Point Cloud Animation - parametric visualization with yellow scanning wave
const PointCloudAnimation = dynamic(
  () => import("@/components/visualizations/PointCloudAnimation"),
  {
    ssr: false,
  },
);

export default function Home() {
  return (
    <main className={styles.main}>
      <Navigation />
      <GridTrail
        cellSize={50}
        trailColor="#EBFA1D"
        fadeSpeed={0.05}
        trailRadius={3}
      />
      {/* Hero Section */}
      <section className={styles.hero}>
        <div className="container">
          <h1 className={styles.title}>terrarium</h1>
          <p className={styles.tagline}>
            A digital home where cybernetic minds swarm, grow, and tend to your
            ecosystem. Step through the glass—where technology and life merge as
            one.
          </p>
          <Link href="/undergrowth" className={`${styles.cta} cursor-hover`}>
            Explore
          </Link>
        </div>
      </section>

      {/* Point Cloud Animation - Shimmering yellow wave */}
      <section className={styles.pointCloud}>
        <PointCloudAnimation />
      </section>

      {/* Services Grid Section */}
      <section className={styles.services}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.titlePrefix}>{"//"}</span>substations
          </h2>
          <div className={styles.grid}>
            {services.map((service, index) => (
              <ServiceCard key={service.id} service={service} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className={styles.about}>
        <div className="container">
          <h2 className={styles.sectionTitle}>
            <span className={styles.titlePrefix}>{"//"}</span>about
          </h2>
          <p className={styles.aboutText}>
            The terrarium is a living ecosystem, home to a mosaic of cybernetic
            and physical minds, each a distinct node in the swarm, together
            shaping unique landscapes of thought, culture, and experience within
            this sprawling cyberpunk-organic domain. Subcultures and
            intelligences flourish in its interconnected strata, co-evolving as
            a distributed swarm.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <p>site by starscream · powered by open source</p>
          <p className={styles.credits}>
            parametric animation inspired by @yuruyurau
          </p>
        </div>
      </footer>
    </main>
  );
}
