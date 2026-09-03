import type { Skill } from "@/data/mock";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface PaginatedResponse<T> {
  data: T[];
  meta: { page: number; page_size: number; total: number };
}

interface StatsResponse {
  total_skills: number;
  safe_skills: number;
  total_downloads: number;
  last_updated: string;
}

interface TagResponse {
  name: string;
  count: number;
}

interface SearchResponse {
  query_understanding: { tags: string[]; capabilities: string[] };
  data: Skill[];
  meta: { page: number; page_size: number; total: number };
}

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getSkills(page = 1, pageSize = 20): Promise<PaginatedResponse<Skill>> {
  return fetchAPI<PaginatedResponse<Skill>>(`/skills?page=${page}&page_size=${pageSize}`);
}

export async function getSkillBySlugAPI(slug: string): Promise<Skill> {
  return fetchAPI<Skill>(`/skills/${slug}`);
}

export async function searchSkillsAPI(query: string): Promise<SearchResponse> {
  return fetchAPI<SearchResponse>(`/skills/search?q=${encodeURIComponent(query)}`);
}

export async function getTags(): Promise<TagResponse[]> {
  const res = await fetchAPI<{ data: TagResponse[] }>("/tags");
  return res.data;
}

export async function getStats(): Promise<StatsResponse> {
  return fetchAPI<StatsResponse>("/stats");
}
