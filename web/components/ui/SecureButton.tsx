"use client";

import { useState } from "react";
import styles from "./SecureButton.module.css";
import SecureAccessModal from "./SecureAccessModal";

interface SecureButtonProps {
  label: string;
  targetUrl: string;
  modalTitle?: string;
  validCodes?: string[];
  variant?: "primary" | "secondary";
  size?: "medium" | "large";
  className?: string;
}

export default function SecureButton({
  label,
  targetUrl,
  modalTitle,
  validCodes,
  variant = "primary",
  size = "medium",
  className = "",
}: SecureButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleClick = () => {
    setIsModalOpen(true);
  };

  return (
    <>
      <button
        onClick={handleClick}
        className={`${styles.button} ${styles[variant]} ${styles[size]} ${className}`}
      >
        <span className={styles.label}>{label}</span>

        {/* Corner Brackets */}
        <div className={styles.cornerTL} />
        <div className={styles.cornerTR} />
        <div className={styles.cornerBL} />
        <div className={styles.cornerBR} />

        {/* Glow effect */}
        <div className={styles.glow} />
      </button>

      <SecureAccessModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        targetUrl={targetUrl}
        title={modalTitle}
        validCodes={validCodes}
      />
    </>
  );
}
