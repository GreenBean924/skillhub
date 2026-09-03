import { getSkillBySlugAPI } from "@/lib/api";
import { notFound } from "next/navigation";
import { SecurityReport } from "@/components/SecurityReport";
import { InstallGuide } from "@/components/InstallGuide";
import { SecurityBadge } from "@/components/SecurityBadge";

export default async function SkillDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let skill;
  try {
    skill = await getSkillBySlugAPI(slug);
  } catch {
    notFound();
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-4 pt-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="font-mono text-2xl font-bold text-foreground tracking-tight">
                {skill.name}
              </h1>
              <p className="text-sm font-mono text-muted mt-1">
                by{" "}
                <span className="text-neon-cyan/70">{skill.author}</span>
                {" · "}
                {skill.downloads.toLocaleString()} downloads
                {" · "}
                {skill.stars} stars
              </p>
            </div>
            <SecurityBadge
              level={skill.security.level}
              score={skill.security.score}
              size="lg"
            />
          </div>

          <p className="text-sm text-zinc-400 leading-relaxed max-w-2xl">
            {skill.description}
          </p>

          <div className="flex flex-wrap gap-2">
            {skill.tags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 rounded-lg bg-surface-elevated border border-border text-xs font-mono text-muted"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Capabilities */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="font-mono text-sm font-semibold text-foreground mb-3">
            能力
          </h2>
          <div className="flex flex-wrap gap-2">
            {skill.capabilities.map((cap) => (
              <span
                key={cap}
                className="px-3 py-1.5 rounded-lg bg-neon-magenta/5 border border-neon-magenta/20 text-xs font-mono text-neon-magenta/80"
              >
                {cap}
              </span>
            ))}
          </div>
        </div>

        {/* Security Report */}
        <SecurityReport report={skill.security} />

        {/* Install Guide */}
        <InstallGuide command={skill.installCommand} />

        {/* Content Preview */}
        {skill.content && (
          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-border flex items-center justify-between">
              <h2 className="font-mono text-sm font-semibold text-foreground">
                源码预览
              </h2>
              <span className="text-[10px] font-mono text-muted px-2 py-0.5 rounded bg-surface-elevated border border-border">
                只读
              </span>
            </div>
            <pre className="p-5 text-xs font-mono text-zinc-400 leading-relaxed overflow-x-auto">
              {skill.content}
            </pre>
          </div>
        )}

        {/* Back link */}
        <div className="pb-8">
          <a
            href="/"
            className="inline-flex items-center gap-2 text-xs font-mono text-muted hover:text-neon-cyan transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path
                d="M9 3L5 7L9 11"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            返回技能列表
          </a>
        </div>
      </div>
    </div>
  );
}
