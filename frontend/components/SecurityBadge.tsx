import type { SecurityLevel } from "@/data/mock";

const levelConfig: Record<
  SecurityLevel,
  { label: string; color: string; bg: string; border: string; dot: string }
> = {
  safe: {
    label: "安全",
    color: "text-neon-green",
    bg: "bg-neon-green/10",
    border: "border-neon-green/30",
    dot: "bg-neon-green",
  },
  low: {
    label: "低风险",
    color: "text-neon-cyan",
    bg: "bg-neon-cyan/10",
    border: "border-neon-cyan/30",
    dot: "bg-neon-cyan",
  },
  medium: {
    label: "中等风险",
    color: "text-neon-orange",
    bg: "bg-neon-orange/10",
    border: "border-neon-orange/30",
    dot: "bg-neon-orange",
  },
  high: {
    label: "高风险",
    color: "text-neon-red",
    bg: "bg-neon-red/10",
    border: "border-neon-red/30",
    dot: "bg-neon-red",
  },
  critical: {
    label: "极高风险",
    color: "text-red-400",
    bg: "bg-red-400/10",
    border: "border-red-400/30",
    dot: "bg-red-400",
  },
  pending: {
    label: "待审查",
    color: "text-zinc-400",
    bg: "bg-zinc-400/10",
    border: "border-zinc-400/30",
    dot: "bg-zinc-400",
  },
};

export function SecurityBadge({
  level,
  score,
  size = "sm",
}: {
  level: SecurityLevel;
  score: number;
  size?: "sm" | "lg";
}) {
  const config = levelConfig[level];

  if (size === "lg") {
    return (
      <div
        className={`inline-flex items-center gap-2.5 px-4 py-2 rounded-xl border font-mono ${config.color} ${config.bg} ${config.border}`}
      >
        <span
          className={`w-2.5 h-2.5 rounded-full ${config.dot} animate-pulse-glow`}
        />
        <span className="text-sm font-semibold">{config.label}</span>
        <span className="text-xs opacity-60">Score: {score}/100</span>
      </div>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono ${config.color} ${config.bg} ${config.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
}
