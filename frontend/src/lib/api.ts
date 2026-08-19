import { EntityDetail, SearchJobResponse, SearchResultItem, APIKeyItem } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL !== undefined 
  ? process.env.NEXT_PUBLIC_API_URL 
  : typeof window !== "undefined" ? "" : "http://localhost:8000";

export async function createSearchJob(query: string, sources: string[] = ["auto"]): Promise<SearchJobResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, sources, limit: 50 }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error?.message || "Failed to initiate discovery job");
  }
  return res.json();
}

export async function getSearchJobStatus(searchId: string): Promise<SearchJobResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/search/${searchId}`);
  if (!res.ok) throw new Error("Failed to fetch search job status");
  return res.json();
}

export async function getSearchResults(searchId: string, qualifiedOnly: boolean = false): Promise<SearchResultItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/search/${searchId}/results?qualified_only=${qualifiedOnly}`);
  if (!res.ok) throw new Error("Failed to fetch search job results");
  return res.json();
}

export async function getEntityDetail(entityId: string): Promise<EntityDetail> {
  const res = await fetch(`${API_BASE_URL}/api/v1/entities/${entityId}`);
  if (!res.ok) throw new Error("Failed to fetch entity details");
  return res.json();
}

export async function listAPIKeys(): Promise<APIKeyItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/api-keys`);
  if (!res.ok) return [];
  return res.json();
}

export async function createAPIKey(name: string): Promise<{ raw_api_key: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/api-keys`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error("Failed to create API Key");
  return res.json();
}

export function getExportUrl(searchId: string, format: 'csv' | 'json'): string {
  return `${API_BASE_URL}/api/v1/export/${searchId}?format=${format}`;
}
