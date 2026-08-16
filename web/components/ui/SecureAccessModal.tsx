"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { validateAccessCode } from "@/utils/accessConfig";
import styles from "./SecureAccessModal.module.css";

interface SecureAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetUrl: string;
  title?: string;
  validCodes?: string[];
  onAuthenticated?: () => void;
}

// Default access codes - can be overridden via props or environment
const DEFAULT_ACCESS_CODES = [
  "UNDERGROWTH",
  "TERR4R1UM",
  "CYB3RN3T1C",
  "SW4RM",
  "ECLIPSE",
];

export default function SecureAccessModal({
  isOpen,
  onClose,
  targetUrl,
  title = "ACCESS REQUIRED",
  validCodes = DEFAULT_ACCESS_CODES,
  onAuthenticated,
}: SecureAccessModalProps) {
  const [accessCode, setAccessCode] = useState("");
  const [error, setError] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (isOpen) {
      setAccessCode("");
      setError("");
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsValidating(true);

    // Simulate validation delay for effect
    await new Promise((resolve) => setTimeout(resolve, 600));

    if (validateAccessCode(accessCode, validCodes)) {
      // Success - set cookie
      document.cookie = `terrarium_auth=valid; path=/; max-age=86400; SameSite=Lax`;

      // Call onAuthenticated callback if provided, otherwise redirect
      if (onAuthenticated) {
        onAuthenticated();
      } else {
        router.push(targetUrl);
      }
      onClose();
    } else {
      setError("INVALID ACCESS CODE");
      setAccessCode("");
    }

    setIsValidating(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={styles.modal}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        {/* Corner Brackets */}
        <div className={styles.cornerTL} />
        <div className={styles.cornerTR} />
        <div className={styles.cornerBL} />
        <div className={styles.cornerBR} />

        {/* Close Button */}
        <button
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>

        {/* Content */}
        <div className={styles.content}>
          <h2 className={styles.title}>{title}</h2>

          <div className={styles.glitchLine} />

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                placeholder="ENTER ACCESS CODE"
                className={styles.input}
                autoFocus
                disabled={isValidating}
                maxLength={20}
              />
              <div className={styles.inputBorder} />
            </div>

            {error && (
              <div className={styles.error}>
                <span className={styles.errorIcon}>⚠</span>
                {error}
              </div>
            )}

            <button
              type="submit"
              className={styles.submitBtn}
              disabled={!accessCode || isValidating}
            >
              <span className={styles.submitText}>
                {isValidating ? "VALIDATING..." : "GRANT ACCESS"}
              </span>
              <div className={styles.btnCornerTL} />
              <div className={styles.btnCornerTR} />
              <div className={styles.btnCornerBL} />
              <div className={styles.btnCornerBR} />
            </button>
          </form>

          <p className={styles.hint}>ENTER CLEARANCE CODE TO PROCEED</p>
        </div>
      </div>
    </div>
  );
}
