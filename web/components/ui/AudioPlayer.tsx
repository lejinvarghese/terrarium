'use client';

import { useEffect, useRef, useState } from 'react';
import styles from './AudioPlayer.module.css';

interface AudioPlayerProps {
  audioSrc?: string;
  autoPlay?: boolean;
  volume?: number;
}

export default function AudioPlayer({
  audioSrc = '/assets/sounds/ambient.mp3',
  autoPlay = false,
  volume = 0.3,
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      audioRef.current.loop = true;

      if (autoPlay) {
        // Try to autoplay with user interaction
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => setIsPlaying(true))
            .catch(() => setIsPlaying(false));
        }
      }
    }
  }, [autoPlay, volume]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  return (
    <div className={styles.audioPlayer}>
      <audio ref={audioRef} src={audioSrc} />

      <button
        onClick={togglePlay}
        className={`${styles.button} cursor-hover`}
        aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
      >
        {isPlaying ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="4" y="3" width="2" height="10" fill="currentColor" />
            <rect x="10" y="3" width="2" height="10" fill="currentColor" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M5 3L13 8L5 13V3Z" fill="currentColor" />
          </svg>
        )}
      </button>

      <button
        onClick={toggleMute}
        className={`${styles.button} cursor-hover`}
        aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
      >
        {isMuted ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3L5 6H2v4h3l3 3V3zm6 2l-2 2 2 2-1 1-2-2-2 2-1-1 2-2-2-2 1-1 2 2 2-2 1 1z" fill="currentColor" />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3L5 6H2v4h3l3 3V3zm3.5 5c0-1-0.5-2-1.5-2.5v5c1-0.5 1.5-1.5 1.5-2.5zm1.5 0c0 1.5-0.7 3-2 4v1.5c2-1 3.5-3 3.5-5.5S12 3.5 10 2.5V4c1.3 1 2 2.5 2 4z" fill="currentColor" />
          </svg>
        )}
      </button>

      <div className={styles.label}>
        {isPlaying ? 'Sound On' : 'Sound Off'}
      </div>
    </div>
  );
}
