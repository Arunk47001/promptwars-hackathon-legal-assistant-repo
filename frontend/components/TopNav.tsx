"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import LanguageToggle from "@/components/LanguageToggle";
import { useLanguage } from "@/components/LanguageProvider";

const NAV_LINKS = [
  { href: "/", label: "Document" },
  { href: "/compare", label: "Compare" },
  { href: "/law-mapping", label: "Law mapping" },
  { href: "/navigator", label: "Navigator" },
];

export default function TopNav() {
  const pathname = usePathname();
  const { language, setLanguage } = useLanguage();
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .health()
      .then((res) => {
        if (!cancelled) setHealthy(res.status === "ok");
      })
      .catch(() => {
        if (!cancelled) setHealthy(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <nav className="top-nav">
      <div className="top-nav-brand">
        <span className="brand-name">Namma Nyaya</span>
        <span className="brand-kannada">ನಮ್ಮ ನ್ಯಾಯ</span>
      </div>

      <div className="top-nav-links">
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`top-nav-link ${pathname === link.href ? "active" : ""}`}
          >
            {link.label}
          </Link>
        ))}
      </div>

      <div className="top-nav-meta">
        <span className="status-indicator" aria-live="polite">
          <span
            className={`status-dot ${healthy === false ? "status-dot-offline" : ""}`}
            aria-hidden="true"
          />
          {healthy === null ? "Checking service…" : healthy ? "Service online" : "Service unreachable"}
        </span>
        <LanguageToggle value={language} onChange={setLanguage} />
      </div>
    </nav>
  );
}
