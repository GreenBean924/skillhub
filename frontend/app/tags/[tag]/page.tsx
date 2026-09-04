import { getSkillsByTag } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { SkillCard } from "@/components/SkillCard";
import Link from "next/link";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ tag: string }>;
}) {
  const { tag } = await params;
  const decoded = decodeURIComponent(tag);
  return {
    title: `${decoded} Skills — SkillHub`,
    description: `Browse AI agent skills tagged with "${decoded}". Discover, audit, and install with confidence.`,
  };
}

export default async function TagPage({
  params,
}: {
  params: Promise<{ tag: string }>;
}) {
  const { tag } = await params;
  const decoded = decodeURIComponent(tag);

  let skills: Awaited<ReturnType<typeof getSkillsByTag>>["data"] = [];
  let total = 0;

  try {
    const res = await getSkillsByTag(decoded);
    skills = res.data;
    total = res.meta.total;
  } catch {
    // API unavailable
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="pt-8 space-y-4">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="text-xs font-mono text-muted hover:text-neon-cyan transition-colors"
            >
              Home
            </Link>
            <span className="text-muted text-xs">/</span>
            <span className="text-xs font-mono text-neon-cyan">tags</span>
            <span className="text-muted text-xs">/</span>
            <span className="text-xs font-mono text-foreground">{decoded}</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="px-3 py-1.5 rounded-lg bg-neon-magenta/10 border border-neon-magenta/30 text-sm font-mono text-neon-magenta">
              {decoded}
            </span>
            <span className="text-xs font-mono text-muted">
              {total} 个技能
            </span>
          </div>

          <SearchBar large />
        </div>

        {skills.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((skill) => (
              <SkillCard key={skill.slug} skill={skill} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 space-y-3">
            <div className="text-4xl font-mono text-border">∅</div>
            <p className="text-sm font-mono text-muted">
              没有找到标签为 &quot;{decoded}&quot; 的技能
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
