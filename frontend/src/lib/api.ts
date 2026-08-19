import { EntityDetail, SearchJobResponse, SearchResultItem, APIKeyItem } from "@/types";

const getApiBaseUrl = (): string => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (typeof window !== "undefined") {
    // If browser is on HTTPS, force relative URL to use Next.js HTTPS proxy rewrite
    if (window.location.protocol === "https:") {
      return "";
    }
    return envUrl !== undefined ? envUrl : "";
  }
  return envUrl || "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

export async function createSearchJob(query: string, sources: string[] = ["auto"]): Promise<SearchJobResponse> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/search`, {
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
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/search/${searchId}`);
  if (!res.ok) throw new Error("Failed to fetch search job status");
  return res.json();
}

export async function getSearchResults(searchId: string, qualifiedOnly: boolean = false): Promise<SearchResultItem[]> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/search/${searchId}/results?qualified_only=${qualifiedOnly}`);
  if (!res.ok) throw new Error("Failed to fetch search job results");
  return res.json();
}

export async function getEntityDetail(entityId: string): Promise<EntityDetail> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/entities/${entityId}`);
  if (!res.ok) throw new Error("Failed to fetch entity details");
  return res.json();
}

export async function listAPIKeys(): Promise<APIKeyItem[]> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/api-keys`);
  if (!res.ok) return [];
  return res.json();
}

export async function createAPIKey(name: string): Promise<{ raw_api_key: string }> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/v1/api-keys`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error("Failed to create API Key");
  return res.json();
}

export function getExportUrl(searchId: string, format: 'csv' | 'json'): string {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}/api/v1/export/${searchId}?format=${format}`;
}
