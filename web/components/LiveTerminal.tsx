'use client';

import { useEffect, useRef, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import styles from './LiveTerminal.module.css';

interface LiveTerminalProps {
  sessionName: string;
  title?: string;
  height?: string;
  updateInterval?: number;
  maxLines?: number;
}

export function LiveTerminal({
  sessionName,
  title = 'Terminal',
  height = '400px',
  updateInterval = 1000,
  maxLines = 100
}: LiveTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize xterm.js with cyberpunk theme
    const term = new Terminal({
      cursorBlink: false,
      disableStdin: true, // READ-ONLY: no user input
      convertEol: true,
      fontSize: 12,
      fontFamily: 'JetBrains Mono, monospace',
      theme: {
        background: '#000000',
        foreground: '#ffffff',
        cursor: '#EBFA1D',
        selectionBackground: 'rgba(235, 250, 29, 0.3)',
        // ANSI colors for terminal output
        black: '#000000',
        red: '#ff5555',
        green: '#50fa7b',
        yellow: '#f1fa8c',
        blue: '#bd93f9',
        magenta: '#ff79c6',
        cyan: '#8be9fd',
        white: '#bfbfbf',
        brightBlack: '#4d4d4d',
        brightRed: '#ff6e67',
        brightGreen: '#5af78e',
        brightYellow: '#f4f99d',
        brightBlue: '#caa9fa',
        brightMagenta: '#ff92d0',
        brightCyan: '#9aedfe',
        brightWhite: '#e6e6e6',
      },
      scrollback: 1000,
      allowTransparency: true,
      drawBoldTextInBrightColors: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);

    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    // Fetch terminal output from tmux
    const fetchOutput = async () => {
      try {
        const response = await fetch(`/api/tmux/${sessionName}?lines=${maxLines}`);
        if (response.ok) {
          const output = await response.text();
          term.clear();
          term.write(output);
          setIsConnected(true);
          setLastUpdate(new Date());
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        console.error('Failed to fetch terminal output:', error);
        setIsConnected(false);
      }
    };

    fetchOutput();
    const interval = setInterval(fetchOutput, updateInterval);

    // Handle window resize
    const handleResize = () => {
      if (fitAddonRef.current) {
        fitAddonRef.current.fit();
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
      term.dispose();
    };
  }, [sessionName, updateInterval, maxLines]);

  return (
    <div className={styles.terminalContainer}>
      {/* Cyberpunk Header */}
      <div className={styles.terminalHeader}>
        <div className={styles.headerLeft}>
          <div className={styles.windowButtons}>
            <span className={styles.dot} style={{ background: '#ff5555' }}></span>
            <span className={styles.dot} style={{ background: '#f1fa8c' }}></span>
            <span className={styles.dot} style={{ background: '#50fa7b' }}></span>
          </div>
          <span className={styles.terminalTitle}>{title}</span>
        </div>
        <div className={styles.headerRight}>
          <span className={styles.statusIndicator}>
            <span
              className={`${styles.statusDot} ${isConnected ? styles.connected : styles.disconnected}`}
            ></span>
            {isConnected ? 'LIVE' : 'DISCONNECTED'}
          </span>
          {lastUpdate && (
            <span className={styles.timestamp}>
              {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div
        ref={terminalRef}
        className={styles.terminal}
        style={{ height }}
      />

      {/* Cyberpunk Footer */}
      <div className={styles.terminalFooter}>
        <span className={styles.footerText}>
          {sessionName} · Read-only · Updates every {updateInterval/1000}s
        </span>
        <span className={styles.footerInfo}>
          Last {maxLines} lines
        </span>
      </div>
    </div>
  );
}
