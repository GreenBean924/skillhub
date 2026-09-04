import Link from "next/link";

export function TagChip({
  tag,
  active = false,
  href,
  onClick,
}: {
  tag: string;
  active?: boolean;
  href?: string;
  onClick?: () => void;
}) {
  const className = `px-3 py-1.5 rounded-lg font-mono text-xs border transition-all ${
    active
      ? "bg-neon-magenta/10 border-neon-magenta/40 text-neon-magenta"
      : "bg-surface-elevated border-border text-muted hover:text-foreground hover:border-neon-cyan/30"
  }`;

  if (href) {
    return (
      <Link href={href} className={className}>
        {tag}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={className}>
      {tag}
    </button>
  );
}
