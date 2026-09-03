"use client";

import { useState } from "react";
import type { SecurityReport as SecurityReportType } from "@/data/mock";
import { SecurityBadge } from "./SecurityBadge";

const severityColors: Record<string, { text: string; bg: string; border: string }> = {
  critical: { text: "text-neon-red", bg: "bg-neon-red/10", border: "border-neon-red/30" },
  high: { text: "text-neon-red", bg: "bg-neon-red/8", border: "border-neon-red/20" },
  medium: { text: "text-neon-orange", bg: "bg-neon-orange/8", border: "border-neon-orange/20" },
  low: { text: "text-neon-cyan", bg: "bg-neon-cyan/8", border: "border-neon-cyan/20" },
  info: { text: "text-muted", bg: "bg-surface-elevated", border: "border-border" },
};

export function SecurityReport({ report }: { report: SecurityReportType }) {
  const [expanded, setExpanded] = useState(true);

  const counts = report.findings.reduce(
    (acc, f) => {
      acc[f.severity] = (acc[f.severity] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="bg-surface border border-border rounded-xl overflow-hidden">
      <div className="p-5 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h2 className="font-mono font-semibold text-foreground">安全报告</h2>
            <SecurityBadge level={report.level} score={report.score} />
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs font-mono text-muted hover:text-foreground transition-colors"
          >
            {expanded ? "收起" : "展开"}
          </button>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {Object.entries(counts).map(([severity, count]) => {
            const colors = severityColors[severity];
            return (
              <span
                key={severity}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono border ${colors.text} ${colors.bg} ${colors.border}`}
              >
                {severity}: {count}
              </span>
            );
          })}
          <span className="text-xs font-mono text-muted ml-auto">
            扫描时间: {new Date(report.scannedAt).toLocaleDateString("zh-CN")}
          </span>
        </div>
      </div>

      {expanded && (
        <div className="divide-y divide-border/50">
          {report.findings.map((finding) => {
            const colors = severityColors[finding.severity];
            return (
              <div key={finding.id} className="p-5">
                <div className="flex items-start gap-3">
                  <span
                    className={`shrink-0 mt-0.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${colors.text} ${colors.bg} ${colors.border}`}
                  >
                    {finding.severity}
                  </span>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-mono text-sm font-semibold text-foreground">
                      {finding.title}
                    </h3>
                    <p className="text-sm text-zinc-400 mt-1.5 leading-relaxed">
                      {finding.description}
                    </p>
                    {finding.evidence && (
                      <pre className="mt-3 p-3 rounded-lg bg-background border border-border text-xs font-mono text-neon-cyan/80 overflow-x-auto">
                        {finding.evidence}
                      </pre>
                    )}
                    <div className="mt-3 flex items-start gap-2">
                      <span className="text-neon-green text-xs mt-0.5">&#x2713;</span>
                      <p className="text-xs text-zinc-400 leading-relaxed">
                        <span className="text-neon-green font-mono font-semibold">
                          建议:{" "}
                        </span>
                        {finding.recommendation}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
