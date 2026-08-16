"use client";

import { useState } from "react";
import { Service } from "@/data/services";
import SecureAccessModal from "@/components/ui/SecureAccessModal";
import styles from "./ServiceCard.module.css";

interface ServiceCardProps {
  service: Service;
  index: number;
}

// Services that require secure access
const SECURE_SERVICES = ["dome", "archive", "incubator"];

// Single access title for all secured services
const ACCESS_TITLE = "ACCESS";

export default function ServiceCard({ service, index }: ServiceCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const requiresAuth = SECURE_SERVICES.includes(service.id);

  const handleClick = (e: React.MouseEvent) => {
    if (requiresAuth) {
      e.preventDefault();
      setIsModalOpen(true);
    }
    // For non-secure services, let the default anchor behavior work
  };

  return (
    <>
      <a
        href={service.url}
        className={`${styles.card} cursor-hover`}
        onClick={handleClick}
        style={{
          animationDelay: `${index * 0.15}s`,
          color: service.color,
        }}
      >
        <div className={styles.cardHeader}>
          <span className={styles.prefix} style={{ color: service.color }}>
            {service.prefix}
          </span>
          <span className={styles.status} data-status={service.status}>
            {service.status.toUpperCase()}
          </span>
        </div>
        <h3 className={styles.cardTitle}>{service.name}</h3>
        <p className={styles.cardTagline}>{service.tagline}</p>
        <p className={styles.cardDescription}>{service.description}</p>
        <div className={styles.features}>
          {service.features.slice(0, 3).map((feature, i) => (
            <span key={i} className={styles.feature}>
              {feature}
            </span>
          ))}
        </div>

        {requiresAuth && (
          <div className={styles.secureBadge}>SECURE ACCESS</div>
        )}
      </a>

      {requiresAuth && service.url && (
        <SecureAccessModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          targetUrl={service.url}
          title={ACCESS_TITLE}
        />
      )}
    </>
  );
}
