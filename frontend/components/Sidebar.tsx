"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const navLinks = [
  { href: "/", label: "首页", icon: HomeIcon },
  { href: "/search?q=", label: "搜索", icon: SearchIcon },
  { href: "/#categories", label: "分类", icon: GridIcon },
  { href: "/#about", label: "关于", icon: InfoIcon },
];

export function Sidebar() {
  const pathname = usePathname();
  const [stats, setStats] = useState({ totalSkills: 0, safeSkills: 0, totalDownloads: 0 });

  useEffect(() => {
    fetch(`${API_BASE}/stats`)
      .then((res) => res.json())
      .then((data) =>
        setStats({
          totalSkills: data.total_skills,
          safeSkills: data.safe_skills,
          totalDownloads: data.total_downloads,
        })
      )
      .catch(() => {});
  }, []);

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface border-r border-border flex flex-col z-50">
      <div className="p-6 border-b border-border">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30 flex items-center justify-center glow-cyan-sm">
            <span className="text-neon-cyan font-mono font-bold text-sm">S</span>
          </div>
          <div>
            <h1 className="font-mono font-bold text-lg text-foreground tracking-tight group-hover:text-neon-cyan transition-colors">
              SkillHub
            </h1>
            <p className="text-[10px] font-mono text-muted tracking-widest uppercase">
              Agent Skills
            </p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navLinks.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/"
              ? pathname === "/"
              : pathname.startsWith(href.replace(/\/$/, ""));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-mono text-sm transition-all ${
                isActive
                  ? "bg-neon-cyan/10 text-neon-cyan border-glow"
                  : "text-muted hover:text-foreground hover:bg-surface-elevated"
              }`}
            >
              <Icon active={isActive} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border space-y-3">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-muted">技能数</span>
          <span className="text-neon-cyan">{stats.totalSkills}</span>
        </div>
        <div className="flex justify-between text-xs font-mono">
          <span className="text-muted">已验证</span>
          <span className="text-neon-green">{stats.safeSkills}</span>
        </div>
        <div className="flex justify-between text-xs font-mono">
          <span className="text-muted">下载量</span>
          <span className="text-foreground">
            {stats.totalDownloads >= 1000
              ? `${(stats.totalDownloads / 1000).toFixed(1)}k`
              : stats.totalDownloads}
          </span>
        </div>
        <div className="pt-2 text-[10px] font-mono text-muted/50 text-center">
          v0.1.0-demo
        </div>
      </div>
    </aside>
  );
}

function HomeIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={active ? "text-neon-cyan" : "text-muted"}
    >
      <path
        d="M2 8.5L8 3L14 8.5V13C14 13.5523 13.5523 14 13 14H3C2.44772 14 2 13.5523 2 13V8.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6 14V9H10V14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SearchIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={active ? "text-neon-cyan" : "text-muted"}
    >
      <circle cx="7" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M10.5 10.5L14 14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

function GridIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={active ? "text-neon-cyan" : "text-muted"}
    >
      <rect
        x="2"
        y="2"
        width="5"
        height="5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="9"
        y="2"
        width="5"
        height="5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="2"
        y="9"
        width="5"
        height="5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <rect
        x="9"
        y="9"
        width="5"
        height="5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

function InfoIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={active ? "text-neon-cyan" : "text-muted"}
    >
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M8 7V11"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <circle cx="8" cy="5" r="0.75" fill="currentColor" />
    </svg>
  );
}
