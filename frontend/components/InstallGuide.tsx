"use client";

import { useState } from "react";

export function InstallGuide({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-mono font-semibold text-foreground text-sm">
          安装方式
        </h2>
        <span className="text-[10px] font-mono text-muted px-2 py-0.5 rounded bg-surface-elevated border border-border">
          通过 SkillHub CLI
        </span>
      </div>
      <div className="flex items-center gap-3 bg-background rounded-lg border border-border px-4 py-3">
        <span className="text-neon-green font-mono text-sm select-none">$</span>
        <code className="flex-1 font-mono text-sm text-foreground">{command}</code>
        <button
          onClick={handleCopy}
          className="shrink-0 px-3 py-1 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan font-mono text-xs hover:bg-neon-cyan/20 transition-all"
        >
          {copied ? "已复制!" : "复制"}
        </button>
      </div>
      <p className="text-xs text-muted mt-3 font-mono">
        还没有 SkillHub CLI? 使用{" "}
        <code className="text-neon-cyan/70">pip install skillhub-cli</code>{" "}
        安装
      </p>
    </div>
  );
}
