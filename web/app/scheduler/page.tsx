'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import dynamic from 'next/dynamic';
import { bots } from '@/data/bots';
import SchedulerCalendar from '@/components/scheduler/SchedulerCalendar';
import styles from './scheduler.module.css';

// Import LiveTerminal dynamically to avoid SSR issues with xterm.js
const LiveTerminal = dynamic(() => import('@/components/LiveTerminal').then(mod => ({ default: mod.LiveTerminal })), {
  ssr: false,
  loading: () => <div style={{ padding: '1rem', color: '#EBFA1D' }}>Loading terminal...</div>
});

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
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

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

    return relativeTime;
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
    return taskName.replace(/^.*?\s+-\s+/, '');
  };

  const parseCron = (task: ScheduledTask): string => {
    // Use humanReadable if available, otherwise use the original schedule
    return task.humanReadable || task.schedule;
  };

  // Check if task runs on a specific date (same logic as calendar)
  const taskRunsOnDate = (task: ScheduledTask, date: Date): boolean => {
    const schedule = (task.humanReadable || task.schedule).toLowerCase();
    const dayOfWeek = date.getDay();

    // Daily tasks
    if (schedule.includes('every day') || schedule.includes('daily')) {
      return true;
    }

    // Weekly tasks
    if (schedule.includes('monday') && dayOfWeek === 1) return true;
    if (schedule.includes('tuesday') && dayOfWeek === 2) return true;
    if (schedule.includes('wednesday') && dayOfWeek === 3) return true;
    if (schedule.includes('thursday') && dayOfWeek === 4) return true;
    if (schedule.includes('friday') && dayOfWeek === 5) return true;
    if (schedule.includes('saturday') && dayOfWeek === 6) return true;
    if (schedule.includes('sunday') && dayOfWeek === 0) return true;

    // Bi-weekly
    if (schedule.includes('every 2 weeks') || schedule.includes('bi-weekly')) {
      const nextRun = new Date(task.nextRun);
      if (dayOfWeek === nextRun.getDay()) {
        const weeksDiff = Math.floor((date.getTime() - nextRun.getTime()) / (7 * 24 * 60 * 60 * 1000));
        return weeksDiff % 2 === 0;
      }
      return false;
    }

    // Every 4 weeks
    if (schedule.includes('every 4 weeks')) {
      const nextRun = new Date(task.nextRun);
      if (dayOfWeek === nextRun.getDay()) {
        const weeksDiff = Math.floor((date.getTime() - nextRun.getTime()) / (7 * 24 * 60 * 60 * 1000));
        return weeksDiff % 4 === 0;
      }
      return false;
    }

    // Default: check exact date match
    const nextRun = new Date(task.nextRun);
    return (
      date.getDate() === nextRun.getDate() &&
      date.getMonth() === nextRun.getMonth() &&
      date.getFullYear() === nextRun.getFullYear()
    );
  };

  // Filter tasks based on selected date
  const filteredTasks = selectedDate
    ? tasks.filter((task) => taskRunsOnDate(task, selectedDate))
    : tasks;

  const handleDateSelect = (date: Date | null) => {
    setSelectedDate(date);
  };

  const clearDateFilter = () => {
    setSelectedDate(null);
  };

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
          Back
        </Link>
        <div className={styles.headerInfo}>
          <h1 className={styles.title}>The Engine</h1>
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
          <div className={styles.statLabel}>Total Routines</div>
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

      {/* Calendar View */}
      <section className={styles.calendarSection}>
        <h2 className={styles.sectionTitle}>Swarm Synchronization</h2>
        <SchedulerCalendar
          tasks={tasks}
          onDateSelect={handleDateSelect}
          selectedDate={selectedDate}
        />
      </section>

      <section className={styles.tasks}>
        <div className={styles.tasksHeader}>
          <h2 className={styles.sectionTitle}>
            Swarm Routines
            {selectedDate && (
              <span className={styles.filterIndicator}>
                {' '}
                · {selectedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </span>
            )}
          </h2>
          {selectedDate && (
            <button
              className={`${styles.clearFilterBtn} cursor-hover`}
              onClick={clearDateFilter}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M12 4L4 12M4 4L12 12"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>
              Clear Filter
            </button>
          )}
        </div>
        {filteredTasks.length === 0 && selectedDate ? (
          <div className={styles.noTasks}>
            <p>No swarm activity scheduled for {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</p>
          </div>
        ) : (
          <div className={styles.taskList}>
            {filteredTasks.map((task) => {
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
              </div>
            </div>
            );
          })}
          </div>
        )}
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
          {showTerminal ? 'Hide' : 'Show'} Engine Heartbeat
        </button>

        {showTerminal && (
          <LiveTerminal
            sessionName="terrarium-engine"
            title="The Engine · Live Activity"
            height="500px"
            updateInterval={1000}
            maxLines={100}
          />
        )}
      </section>
    </div>
  );
}
