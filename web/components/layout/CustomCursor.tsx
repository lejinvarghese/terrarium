"use client";

import { useEffect, useState, useRef } from "react";
import styles from "./CustomCursor.module.css";

export default function CustomCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const positionRef = useRef({ x: 0, y: 0 });
  const rafRef = useRef<number>();
  const [isHovering, setIsHovering] = useState(false);
  const [isClicking, setIsClicking] = useState(false);

  useEffect(() => {
    let needsUpdate = false;

    const updatePosition = (e: MouseEvent) => {
      // Store position without triggering re-render
      positionRef.current = { x: e.clientX, y: e.clientY };

      // Request animation frame only if one isn't already scheduled
      if (!needsUpdate) {
        needsUpdate = true;
        rafRef.current = requestAnimationFrame(() => {
          if (cursorRef.current) {
            // Use GPU-accelerated transform instead of left/top
            // Combine position with -50% centering offset
            cursorRef.current.style.transform = `translate(calc(${positionRef.current.x}px - 50%), calc(${positionRef.current.y}px - 50%))`;
          }
          needsUpdate = false;
        });
      }
    };

    const handleMouseDown = () => setIsClicking(true);
    const handleMouseUp = () => setIsClicking(false);

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "A" ||
        target.tagName === "BUTTON" ||
        target.classList.contains("cursor-hover")
      ) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    document.addEventListener("mousemove", updatePosition);
    document.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("mouseup", handleMouseUp);
    document.addEventListener("mouseover", handleMouseOver);

    return () => {
      document.removeEventListener("mousemove", updatePosition);
      document.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("mouseup", handleMouseUp);
      document.removeEventListener("mouseover", handleMouseOver);

      // Cancel pending animation frame
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, []);

  return (
    <div
      ref={cursorRef}
      className={`${styles.cursor} ${isHovering ? styles.hovering : ""} ${
        isClicking ? styles.clicking : ""
      }`}
      style={{
        // Initial position, will be updated via transform
        transform: "translate(0px, 0px)",
      }}
    >
      <div className={styles.dot} />
      <div className={styles.lineTop} />
      <div className={styles.lineBottom} />
      <div className={styles.lineLeft} />
      <div className={styles.lineRight} />
    </div>
  );
}
