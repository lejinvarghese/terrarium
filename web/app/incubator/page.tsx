'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import SecureAccessModal from '@/components/ui/SecureAccessModal';
import styles from './incubator.module.css';

const GridTrail = dynamic(() => import('@/components/effects/GridTrail'), {
  ssr: false,
});

interface Observation {
  id: number;
  agentId: string;
  episodeId: string;
  timestamp: string;
  observationText: string;
  actionCode: string | null;
  outcome: string | null;
  reward: number;
  modelCheckpoint: string;
}

export default function IncubatorPage() {
  const [showAccessModal, setShowAccessModal] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [agents, setAgents] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedObservation, setSelectedObservation] = useState<Observation | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const router = useRouter();

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

  // Fetch logs
  const fetchLogs = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const url = selectedAgent
        ? `/api/incubator/logs?agent_id=${selectedAgent}&limit=100`
        : '/api/incubator/logs?limit=100';

      console.log('Fetching logs from:', url);
      const response = await fetch(url);
      const data = await response.json();
      console.log('Received data:', { observationCount: data.observations?.length, agents: data.agents });

      if (data.observations) {
        setObservations(data.observations);
      }
      if (data.agents) {
        setAgents(data.agents);
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, selectedAgent]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh || !isAuthenticated) return;

    const interval = setInterval(() => {
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh, isAuthenticated, fetchLogs]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getRewardColor = (reward: number) => {
    if (reward > 0.5) return '#00ff41';
    if (reward < 0) return '#ff0051';
    return '#EBFA1D';
  };

  const truncateText = (text: string, maxLength: number = 200) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatAction = (actionCode: string | null) => {
    if (!actionCode) return '';

    // Extract text from environment.run(...) wrapper
    const match = actionCode.match(/environment\.run\((.*)\)/);
    const text = match ? match[1] : actionCode;

    // Convert to title case
    return text
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

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
            <div className={styles.lockIcon}>🔒</div>
            <h1 className={styles.lockedTitle}>RESTRICTED ACCESS</h1>
            <p className={styles.lockedMessage}>
              This area contains classified incubator logs.
              <br />
              Clearance required to proceed.
            </p>
          </div>
        </div>
        <SecureAccessModal
          isOpen={showAccessModal}
          onClose={() => router.push('/')}
          targetUrl="/incubator"
          title="ACCESS"
        />
      </>
    );
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading incubator logs...</div>
      </div>
    );
  }

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
        <div className={styles.headerInfo}>
          <h1 className={styles.title}>
            <span className={styles.titlePrefix}>//</span>the incubator
          </h1>
          <p className={styles.subtitle}>exploration logs · undergrowth landscape</p>
        </div>
      </header>

      {/* Controls */}
      <div className={styles.controls}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Agent:</label>
          <select
            className={`${styles.filterSelect} cursor-hover`}
            value={selectedAgent || ''}
            onChange={(e) => setSelectedAgent(e.target.value || null)}
          >
            <option value="">All Agents</option>
            {agents.map((agentId) => (
              <option key={agentId} value={agentId}>
                {agentId}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.toggleGroup}>
          <label className={styles.toggleLabel}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className={styles.toggleCheckbox}
            />
            <span className={styles.toggleText}>Auto-refresh</span>
          </label>
        </div>

        <button
          className={`${styles.refreshBtn} cursor-hover`}
          onClick={fetchLogs}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M14 8C14 4.686 11.314 2 8 2C4.686 2 2 4.686 2 8C2 11.314 4.686 14 8 14"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <path d="M14 8L12 6M14 8L12 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className={styles.stats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{observations.length}</div>
          <div className={styles.statLabel}>Total Episodes</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{agents.length}</div>
          <div className={styles.statLabel}>Active Agents</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {observations.filter((o) => o.reward > 0.5).length}
          </div>
          <div className={styles.statLabel}>Successful</div>
        </div>
        <div className={styles.statCard}>
          <div
            className={styles.statValue}
            style={{ color: getRewardColor(
              observations.reduce((sum, o) => sum + o.reward, 0) / observations.length || 0
            )}}
          >
            {observations.length > 0
              ? (observations.reduce((sum, o) => sum + o.reward, 0) / observations.length).toFixed(2)
              : '0.00'}
          </div>
          <div className={styles.statLabel}>Avg Reward</div>
        </div>
      </div>

      {/* Observations List */}
      <section className={styles.logsSection}>
        <h2 className={styles.sectionTitle}>Recent Exploration Logs</h2>
        <div className={styles.logsList}>
          {observations.length === 0 ? (
            <div className={styles.noLogs}>
              <p>No exploration logs found.</p>
            </div>
          ) : (
            observations.map((obs) => (
              <div
                key={obs.id}
                className={`${styles.logCard} cursor-hover`}
                onClick={() => setSelectedObservation(obs)}
              >
                <div className={styles.logHeader}>
                  <div className={styles.logAgent}>{obs.agentId}</div>
                  <div className={styles.logMeta}>
                    <span className={styles.logTimestamp}>
                      {formatTimestamp(obs.timestamp)}
                    </span>
                    <span
                      className={styles.logReward}
                      style={{ color: getRewardColor(obs.reward) }}
                    >
                      +{obs.reward.toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className={styles.logEpisode}>Episode: {obs.episodeId}</div>
                <div className={styles.logPreview}>
                  {truncateText(obs.observationText)}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Detail Modal */}
      {selectedObservation && (
        <div className={styles.modal} onClick={() => setSelectedObservation(null)}>
          <div
            className={styles.modalContent}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className={`${styles.closeButton} cursor-hover`}
              onClick={() => setSelectedObservation(null)}
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
              <h2 className={styles.modalTitle}>{selectedObservation.agentId}</h2>
              <div className={styles.modalMeta}>
                <span>{formatTimestamp(selectedObservation.timestamp)}</span>
                <span
                  style={{ color: getRewardColor(selectedObservation.reward) }}
                >
                  Reward: +{selectedObservation.reward.toFixed(2)}
                </span>
              </div>
            </div>

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Episode ID</h3>
              <code className={styles.modalCode}>{selectedObservation.episodeId}</code>
            </div>

            {selectedObservation.actionCode && (
              <div className={styles.modalSection}>
                <h3 className={styles.modalSectionTitle}>Action</h3>
                <div className={styles.modalText}>{formatAction(selectedObservation.actionCode)}</div>
              </div>
            )}

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Observation</h3>
              <div className={styles.modalText}>
                {selectedObservation.observationText}
              </div>
            </div>

            {selectedObservation.outcome && (
              <div className={styles.modalSection}>
                <h3 className={styles.modalSectionTitle}>Outcome</h3>
                <div className={styles.modalText}>
                  {selectedObservation.outcome}
                </div>
              </div>
            )}

            <div className={styles.modalSection}>
              <h3 className={styles.modalSectionTitle}>Checkpoint</h3>
              <code className={styles.modalCode}>{selectedObservation.modelCheckpoint}</code>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
