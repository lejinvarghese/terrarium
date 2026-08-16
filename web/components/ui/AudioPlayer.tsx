"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./AudioPlayer.module.css";

interface AudioPlayerProps {
  audioSrc?: string;
  autoPlay?: boolean;
  volume?: number;
}

export default function AudioPlayer({
  audioSrc = "/assets/sounds/ambient.mp3?v=2",
  autoPlay = false,
  volume = 0.3,
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const attemptedAutoPlay = useRef(false);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      audioRef.current.loop = true;

      if (autoPlay && !attemptedAutoPlay.current) {
        attemptedAutoPlay.current = true;
        // Try to autoplay
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => setIsPlaying(true))
            .catch(() => {
              // Autoplay blocked - will need user interaction
              setIsPlaying(false);
            });
        }
      }
    }
  }, [autoPlay, volume]);

  // Listen for user interaction to enable autoplay if it was blocked
  useEffect(() => {
    if (!autoPlay || !audioRef.current) return;

    const tryPlayAfterInteraction = () => {
      if (audioRef.current && !isPlaying && autoPlay) {
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.then(() => setIsPlaying(true)).catch(() => {}); // Silently fail if still blocked
        }
      }
    };

    // Try to play after any user interaction
    document.addEventListener("click", tryPlayAfterInteraction, { once: true });
    document.addEventListener("keydown", tryPlayAfterInteraction, {
      once: true,
    });

    return () => {
      document.removeEventListener("click", tryPlayAfterInteraction);
      document.removeEventListener("keydown", tryPlayAfterInteraction);
    };
  }, [autoPlay, isPlaying]);

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
    <div className={styles.audioPlayer} data-playing={isPlaying}>
      <audio ref={audioRef} src={audioSrc} />

      <button
        onClick={togglePlay}
        className={`${styles.button} ${isPlaying ? styles.playing : ""} cursor-hover`}
        aria-label={isPlaying ? "Pause audio" : "Play audio"}
      >
        {isPlaying ? (
          <div className={styles.soundWaves}>
            <span className={styles.wave}></span>
            <span className={styles.wave}></span>
            <span className={styles.wave}></span>
            <span className={styles.wave}></span>
          </div>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M5 3L13 8L5 13V3Z" fill="currentColor" />
          </svg>
        )}
      </button>

      <button
        onClick={toggleMute}
        className={`${styles.button} cursor-hover`}
        aria-label={isMuted ? "Unmute audio" : "Mute audio"}
      >
        {isMuted ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M8 3L5 6H2v4h3l3 3V3zm6 2l-2 2 2 2-1 1-2-2-2 2-1-1 2-2-2-2 1-1 2 2 2-2 1 1z"
              fill="currentColor"
            />
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M8 3L5 6H2v4h3l3 3V3zm3.5 5c0-1-0.5-2-1.5-2.5v5c1-0.5 1.5-1.5 1.5-2.5zm1.5 0c0 1.5-0.7 3-2 4v1.5c2-1 3.5-3 3.5-5.5S12 3.5 10 2.5V4c1.3 1 2 2.5 2 4z"
              fill="currentColor"
            />
          </svg>
        )}
      </button>
    </div>
  );
}
