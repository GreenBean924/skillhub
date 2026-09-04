import { getSkills, getTags, getRecommendations } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { SkillCard } from "@/components/SkillCard";
import { TagChip } from "@/components/TagChip";

export default async function Home() {
  const [skillsRes, tags] = await Promise.all([getSkills(1, 50), getTags()]);
  const allSkills = skillsRes.data;
  const popularTags = tags.slice(0, 10).map((t) => t.name);

  let recommended = allSkills
    .sort((a, b) => b.stars - a.stars)
    .slice(0, 6);

  try {
    const apiRecs = await getRecommendations(6);
    if (apiRecs.length > 0) {
      recommended = apiRecs;
    }
  } catch {
    // fallback to stars-based sorting
  }

  const latest = [...allSkills]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Hero / Search */}
        <section className="pt-12 pb-4 space-y-6">
          <div className="space-y-2">
            <h1 className="font-mono text-3xl font-bold text-foreground tracking-tight">
              发现{" "}
              <span className="text-neon-cyan text-glow-cyan">Agent Skills</span>
            </h1>
            <p className="text-sm text-muted font-mono max-w-lg">
              搜索、审查和安装 AI Agent 技能。所有技能均经过安全扫描和验证。
            </p>
          </div>
          <SearchBar large />
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono text-muted mr-1">热门标签:</span>
            {popularTags.slice(0, 8).map((tag) => (
              <TagChip key={tag} tag={tag} href={`/tags/${tag}`} />
            ))}
          </div>
        </section>

        {/* Recommended Skills */}
        <section className="space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="font-mono text-lg font-semibold text-foreground flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-neon-cyan" />
              推荐技能
            </h2>
            <span className="text-xs font-mono text-muted">
              共 {allSkills.length} 个技能
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommended.map((skill) => (
              <SkillCard key={skill.slug} skill={skill} />
            ))}
          </div>
        </section>

        {/* Latest Updates */}
        <section className="space-y-5 pb-12">
          <h2 className="font-mono text-lg font-semibold text-foreground flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neon-magenta" />
            最近更新
          </h2>
          <div className="space-y-2">
            {latest.map((skill) => (
              <a
                key={skill.slug}
                href={`/skills/${skill.slug}`}
                className="flex items-center gap-4 p-4 rounded-xl bg-surface border border-border hover:border-neon-cyan/30 transition-all group"
              >
                <div className="flex-1 min-w-0">
                  <h3 className="font-mono text-sm font-semibold text-foreground group-hover:text-neon-cyan transition-colors truncate">
                    {skill.name}
                  </h3>
                  <p className="text-xs text-muted mt-0.5 truncate">
                    {skill.description}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      skill.security.level === "safe"
                        ? "bg-neon-green"
                        : skill.security.level === "low"
                          ? "bg-neon-cyan"
                          : skill.security.level === "medium"
                            ? "bg-neon-orange"
                            : "bg-neon-red"
                    }`}
                  />
                  <span className="text-xs font-mono text-muted">
                    {new Date(skill.updatedAt).toLocaleDateString()}
                  </span>
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 14 14"
                    fill="none"
                    className="text-muted group-hover:text-neon-cyan transition-colors"
                  >
                    <path
                      d="M5 3L9 7L5 11"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              </a>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
