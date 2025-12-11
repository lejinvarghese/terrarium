'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { bots } from '@/data/bots';
import styles from './scheduler.module.css';

interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  schedule: string;
  cronExpression?: string;
  humanReadable?: string;
  nextRun: string;
  lastRun?: string;
  status: 'active' | 'paused' | 'failed';
  service: string;
  command?: string;
}

export default function SchedulerPage() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState<string>('');

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Fetch schedule data from API
    const fetchSchedule = async () => {
      try {
        const response = await fetch('/api/schedule');
        const data = await response.json();
        setTasks(data.tasks || []);
      } catch (error) {
        console.error('Failed to load schedule:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  const formatDateMMDDYYYY = (date: Date) => {
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
  };

  const formatDateTimeMMDDYYYY = (date: Date) => {
    const dateStr = formatDateMMDDYYYY(date);
    const time = date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
    return `${dateStr} ${time}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    let relativeTime = '';
    if (diffMins < 1) relativeTime = 'in < 1 min';
    else if (diffMins < 60) relativeTime = `in ${diffMins} mins`;
    else if (diffHours < 24) relativeTime = `in ${diffHours}h ${diffMins % 60}m`;
    else relativeTime = `in ${diffDays}d ${diffHours % 24}h`;

    return `${relativeTime} (${formatDateTimeMMDDYYYY(date)})`;
  };

  const getBotFromTaskName = (taskName: string) => {
    // Extract bot name from task name (e.g., "🌅 Cassia - Morning Briefing" -> "Cassia")
    const match = taskName.match(/[🌅🌶️🍝🎨🚀💪🧙👻🎵]\s+(\w+)/);
    if (match) {
      const botName = match[1].toLowerCase();
      return bots.find((bot) => bot.id === botName);
    }
    return null;
  };

  const getCleanTaskName = (taskName: string) => {
    // Remove everything up to and including " - " (emoji and bot name prefix)
    // e.g., "🌅 Cassia - Morning Briefing" -> "Morning Briefing"
    return taskName.replace(/^.*?\s+-\s+/, '');
  };

  const parseCron = (task: ScheduledTask): string => {
    // Use humanReadable if available, otherwise use the original schedule
    return task.humanReadable || task.schedule;
  };

  // Poll tmux output from terrarium-engine session when terminal is visible
  useEffect(() => {
    if (!showTerminal) return;

    const fetchTerminalOutput = async () => {
      try {
        const response = await fetch('/api/tmux/terrarium-engine?lines=50');
        if (response.ok) {
          const output = await response.text();
          setTerminalOutput(output);
        }
      } catch (error) {
        console.error('Failed to fetch tmux output:', error);
        setTerminalOutput('Error: Unable to connect to scheduler session');
      }
    };

    // Fetch immediately
    fetchTerminalOutput();

    // Poll every 2 seconds
    const interval = setInterval(fetchTerminalOutput, 2000);

    return () => clearInterval(interval);
  }, [showTerminal]);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading schedule...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <Link href="/" className={styles.backLink}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 4L6 10L12 16" stroke="currentColor" strokeWidth="2" />
          </svg>
          Back to Home
        </Link>
        <div className={styles.headerInfo}>
          <h1 className={styles.title}>Scheduler</h1>
          <div className={styles.clock}>
            <span className={styles.time}>{formatTime(currentTime)}</span>
            <span className={styles.date}>
              {formatDateMMDDYYYY(currentTime)}
            </span>
          </div>
        </div>
      </header>

      <div className={styles.stats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{tasks.length}</div>
          <div className={styles.statLabel}>Total Tasks</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {tasks.filter((t) => t.status === 'active').length}
          </div>
          <div className={styles.statLabel}>Active</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {tasks.filter((t) => t.status === 'paused').length}
          </div>
          <div className={styles.statLabel}>Paused</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {tasks.filter((t) => t.status === 'failed').length}
          </div>
          <div className={styles.statLabel}>Failed</div>
        </div>
      </div>

      <section className={styles.tasks}>
        <h2 className={styles.sectionTitle}>Scheduled Tasks</h2>
        <div className={styles.taskList}>
          {tasks.map((task) => {
            const bot = getBotFromTaskName(task.name);
            const cleanName = getCleanTaskName(task.name);

            return (
              <div key={task.id} className={styles.taskCard}>
                <div className={styles.taskHeader}>
                  <div className={styles.taskTitleRow}>
                    {bot && (
                      <div className={styles.botProfile}>
                        <Image
                          src={bot.image}
                          alt={`${bot.name} profile`}
                          width={40}
                          height={50}
                          className={styles.botAvatar}
                        />
                      </div>
                    )}
                    <div className={styles.taskInfo}>
                      <h3 className={styles.taskName}>{cleanName}</h3>
                      {bot && (
                        <span className={styles.botName} style={{ color: bot.color }}>
                          {bot.name}
                        </span>
                      )}
                    </div>
                    <span
                      className={styles.taskStatus}
                      data-status={task.status}
                    >
                      {task.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                <p className={styles.taskDescription}>{task.description}</p>

              <div className={styles.taskSchedule}>
                <div className={styles.scheduleItem}>
                  <span className={styles.scheduleLabel}>Schedule:</span>
                  <span className={styles.scheduleValue}>
                    {parseCron(task)}
                  </span>
                </div>
                <div className={styles.scheduleItem}>
                  <span className={styles.scheduleLabel}>Next Run:</span>
                  <span className={styles.scheduleValue}>
                    {formatDate(task.nextRun)}
                  </span>
                </div>
                {task.lastRun && (
                  <div className={styles.scheduleItem}>
                    <span className={styles.scheduleLabel}>Last Run:</span>
                    <span className={styles.scheduleValue}>
                      {formatDateTimeMMDDYYYY(new Date(task.lastRun))}
                    </span>
                  </div>
                )}
              </div>
            </div>
            );
          })}
        </div>
      </section>

      {/* Scheduler Terminal Section */}
      <section className={styles.terminalSection}>
        <button
          className={`${styles.terminalToggle} cursor-hover`}
          onClick={() => setShowTerminal(!showTerminal)}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M2 4L6 8L2 12M8 12H14"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          {showTerminal ? 'Hide' : 'Show'} Terminal [terrarium-engine]
        </button>

        {showTerminal && (
          <div className={styles.terminal}>
            <div className={styles.terminalHeader}>
              <span className={styles.terminalTitle}>
                tmux session: terrarium-engine
              </span>
              <span className={styles.terminalUpdate}>
                updating every 2s • last 50 lines
              </span>
            </div>
            <pre className={styles.terminalOutput}>
              {terminalOutput || 'Loading terminal output...'}
            </pre>
          </div>
        )}
      </section>
    </div>
  );
}
