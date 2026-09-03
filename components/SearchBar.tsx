"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function SearchBar({
  defaultValue = "",
  large = false,
}: {
  defaultValue?: string;
  large?: boolean;
}) {
  const [value, setValue] = useState(defaultValue);
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      router.push(`/search?q=${encodeURIComponent(value.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div
        className={`search-glow flex items-center gap-3 bg-surface-elevated border border-border rounded-xl transition-all ${
          large ? "px-5 py-4" : "px-4 py-3"
        }`}
      >
        <svg
          width={large ? "20" : "16"}
          height={large ? "20" : "16"}
          viewBox="0 0 16 16"
          fill="none"
          className="text-muted shrink-0"
        >
          <circle cx="7" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5" />
          <path
            d="M10.5 10.5L14 14"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="搜索技能名称、标签或能力..."
          className={`w-full bg-transparent outline-none font-mono text-foreground placeholder:text-muted/60 ${
            large ? "text-base" : "text-sm"
          }`}
        />
        {value && (
          <button
            type="button"
            onClick={() => setValue("")}
            className="text-muted hover:text-foreground transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path
                d="M3 3L11 11M11 3L3 11"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </button>
        )}
        <button
          type="submit"
          className="shrink-0 px-4 py-1.5 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan font-mono text-xs hover:bg-neon-cyan/20 transition-all"
        >
          搜索
        </button>
      </div>
    </form>
  );
}
