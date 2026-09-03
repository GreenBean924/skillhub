import { searchSkillsAPI } from "@/lib/api";
import type { Skill } from "@/data/mock";
import { SearchBar } from "@/components/SearchBar";
import { SkillCard } from "@/components/SkillCard";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const query = typeof params.q === "string" ? params.q : "";

  let skills: Skill[] = [];
  let parsedTags: string[] = [];
  let parsedCapabilities: string[] = [];

  if (query) {
    try {
      const res = await searchSkillsAPI(query);
      skills = res.data;
      parsedTags = res.query_understanding?.tags ?? [];
      parsedCapabilities = res.query_understanding?.capabilities ?? [];
    } catch {
      // API unavailable, show empty results
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="pt-8 space-y-4">
          <h1 className="font-mono text-2xl font-bold text-foreground tracking-tight">
            搜索技能
          </h1>
          <SearchBar defaultValue={query} large />
        </div>

        {query && (
          <>
            {/* Query Understanding */}
            {(parsedCapabilities.length > 0 || parsedTags.length > 0) && (
              <div className="bg-surface border border-border rounded-xl p-5 space-y-3">
                <h2 className="font-mono text-xs font-semibold text-muted uppercase tracking-wider">
                  查询理解
                </h2>
                {parsedTags.length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-mono text-muted">标签:</span>
                    {[...new Set(parsedTags)].map((tag) => (
                      <span
                        key={tag}
                        className="px-2.5 py-1 rounded-lg bg-neon-cyan/10 border border-neon-cyan/20 text-xs font-mono text-neon-cyan"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                {parsedCapabilities.length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-mono text-muted">
                      能力:
                    </span>
                    {[...new Set(parsedCapabilities)].map((cap) => (
                      <span
                        key={cap}
                        className="px-2.5 py-1 rounded-lg bg-neon-magenta/10 border border-neon-magenta/20 text-xs font-mono text-neon-magenta"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Results */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-mono text-sm font-semibold text-foreground">
                  找到 {skills.length} 个结果 &quot;
                  <span className="text-neon-cyan">{query}</span>&quot;
                </h2>
              </div>

              {skills.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {skills.map((skill) => (
                    <SkillCard key={skill.slug} skill={skill} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-16 space-y-3">
                  <div className="text-4xl font-mono text-border">∅</div>
                  <p className="text-sm font-mono text-muted">
                    没有找到匹配 &quot;{query}&quot; 的技能
                  </p>
                  <p className="text-xs font-mono text-muted/60">
                    试试其他关键词，或从首页浏览所有技能
                  </p>
                </div>
              )}
            </div>
          </>
        )}

        {!query && (
          <div className="text-center py-20 space-y-3">
            <p className="text-sm font-mono text-muted">
              输入关键词搜索技能
            </p>
            <p className="text-xs font-mono text-muted/60">
              支持按名称、标签或能力搜索
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
