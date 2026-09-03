import Link from "next/link";
import type { Skill } from "@/data/mock";
import { SecurityBadge } from "./SecurityBadge";

export function SkillCard({ skill }: { skill: Skill }) {
  return (
    <Link href={`/skills/${skill.slug}`}>
      <div className="card-hover bg-surface border border-border rounded-xl p-5 flex flex-col gap-4 h-full">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="font-mono font-semibold text-foreground truncate group-hover:text-neon-cyan transition-colors">
              {skill.name}
            </h3>
            <p className="text-xs font-mono text-muted mt-1">by {skill.author}</p>
          </div>
          <SecurityBadge level={skill.security.level} score={skill.security.score} />
        </div>

        <p className="text-sm text-zinc-400 leading-relaxed line-clamp-2 flex-1">
          {skill.description}
        </p>

        <div className="flex flex-wrap gap-1.5">
          {skill.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 rounded bg-surface-elevated border border-border text-[10px] font-mono text-muted"
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-4 pt-2 border-t border-border/50">
          <span className="text-xs font-mono text-muted flex items-center gap-1.5">
            <DownloadIcon />
            {skill.downloads >= 1000
              ? `${(skill.downloads / 1000).toFixed(1)}k`
              : skill.downloads}
          </span>
          <span className="text-xs font-mono text-muted flex items-center gap-1.5">
            <StarIcon />
            {skill.stars}
          </span>
          <span className="text-xs font-mono text-muted ml-auto">
            {timeAgo(skill.updatedAt)}
          </span>
        </div>
      </div>
    </Link>
  );
}

function DownloadIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path
        d="M6 1.5V8M6 8L3 5M6 8L9 5M2 10.5H10"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path
        d="M6 1L7.5 4.1L11 4.6L8.5 7L9.1 10.5L6 8.9L2.9 10.5L3.5 7L1 4.6L4.5 4.1L6 1Z"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function timeAgo(dateStr: string): string {
  const now = new Date("2026-09-03");
  const date = new Date(dateStr);
  const days = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (days < 1) return "today";
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}
