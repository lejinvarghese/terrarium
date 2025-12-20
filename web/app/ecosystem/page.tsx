'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import dynamic from 'next/dynamic';
import { bots } from '@/data/bots';
import styles from './ecosystem.module.css';

const GridTrail = dynamic(() => import('@/components/effects/GridTrail'), {
  ssr: false,
});

export default function EcosystemPage() {
  const [selectedBot, setSelectedBot] = useState<string | null>(null);

  const openBotModal = (botId: string) => {
    setSelectedBot(botId);
  };

  const closeBotModal = () => {
    setSelectedBot(null);
  };

  const activeBotData = bots.find((bot) => bot.id === selectedBot);

  return (
    <main className={styles.main}>
      <GridTrail
        cellSize={50}
        trailColor="#EBFA1D"
        fadeSpeed={0.05}
        trailRadius={3}
      />

      {/* Header */}
      <header className={styles.header}>
        <Link href="/" className={`${styles.backLink} cursor-hover`}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 4L6 10L12 16" stroke="currentColor" strokeWidth="2" />
          </svg>
          Back
        </Link>
        <h1 className={styles.title}>
          <span className={styles.titlePrefix}>{'//'}</span>the swarm
        </h1>
        <p className={styles.tagline}>
          These cybernetic minds form a distributed intelligence, each tending to our terrarium with a purpose and emergent behavior.
        </p>
      </header>

      {/* Horizontal Profile Cards */}
      <section className={styles.profilesHeader}>
        <div className={styles.profilesScroll}>
          {bots.map((bot) => (
            <div
              key={`profile-${bot.id}`}
              className={`${styles.profileCard} cursor-hover`}
              onClick={() => openBotModal(bot.id)}
              style={
                {
                  '--bot-color': bot.color,
                } as React.CSSProperties
              }
            >
              <div className={styles.profileCardInner}>
                <Image
                  src={bot.image}
                  alt={`${bot.name} profile`}
                  width={200}
                  height={250}
                  className={styles.profileCardImage}
                />
                <div className={styles.profileOverlay}>
                  <div className={styles.overlayText}>
                    <span className={styles.overlayName}>{bot.name}</span>
                    <span className={styles.overlayRole}>{bot.role}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bots Grid */}
      <section className={styles.botsGrid}>
        {bots.map((bot, index) => (
          <div
            key={bot.id}
            className={`${styles.botCard} cursor-hover`}
            style={{
              animationDelay: `${index * 0.1}s`,
              borderColor: bot.color,
            }}
            onClick={() => openBotModal(bot.id)}
          >
            <div className={styles.botImage}>
              <Image
                src={bot.image}
                alt={`${bot.name} profile`}
                width={200}
                height={250}
                className={styles.profileImg}
              />
            </div>
            <h3 className={styles.botName} style={{ color: bot.color }}>
              {bot.name}
            </h3>
            <p className={styles.botRole}>{bot.role}</p>
            <p className={styles.botTagline}>{bot.tagline}</p>
            <div className={styles.botDomains}>
              {bot.domains.slice(0, 3).map((domain) => (
                <span key={domain} className={styles.domainTag}>
                  {domain}
                </span>
              ))}
            </div>
          </div>
        ))}
      </section>

      {/* Bot Detail Modal */}
      {selectedBot && activeBotData && (
        <div className={styles.modal} onClick={closeBotModal}>
          <div
            className={styles.modalContent}
            onClick={(e) => e.stopPropagation()}
            style={{ borderColor: activeBotData.color }}
          >
            <button
              className={`${styles.closeButton} cursor-hover`}
              onClick={closeBotModal}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M18 6L6 18M6 6L18 18"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
            </button>

            <div className={styles.modalHeader}>
              <div className={styles.modalImage}>
                <Image
                  src={activeBotData.image}
                  alt={`${activeBotData.name} profile`}
                  width={150}
                  height={188}
                  className={styles.profileImg}
                />
              </div>
              <div>
                <h2
                  className={styles.modalTitle}
                  style={{ color: activeBotData.color }}
                >
                  {activeBotData.name}
                </h2>
                <p className={styles.modalRole}>{activeBotData.role}</p>
              </div>
            </div>

            <p className={styles.modalTagline}>{activeBotData.tagline}</p>
            <p className={styles.modalDescription}>
              {activeBotData.description}
            </p>

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Personality</h3>
              <ul className={styles.modalList}>
                {activeBotData.personality.map((trait) => (
                  <li key={trait}>{trait}</li>
                ))}
              </ul>
            </div>

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Core Capabilities</h3>
              <ul className={styles.modalList}>
                {activeBotData.capabilities.map((capability) => (
                  <li key={capability}>{capability}</li>
                ))}
              </ul>
            </div>

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Domains of Expertise</h3>
              <div className={styles.modalDomains}>
                {activeBotData.domains.map((domain) => (
                  <span
                    key={domain}
                    className={styles.modalDomainTag}
                    style={{ borderColor: activeBotData.color }}
                  >
                    {domain}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
