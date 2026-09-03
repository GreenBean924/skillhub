export function TagChip({
  tag,
  active = false,
  onClick,
}: {
  tag: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg font-mono text-xs border transition-all ${
        active
          ? "bg-neon-magenta/10 border-neon-magenta/40 text-neon-magenta"
          : "bg-surface-elevated border-border text-muted hover:text-foreground hover:border-neon-cyan/30"
      }`}
    >
      {tag}
    </button>
  );
}
