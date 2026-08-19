export interface SearchJobResponse {
  search_id: string;
  status: 'queued' | 'planning' | 'discovering' | 'normalizing' | 'deduplicating' | 'enriching' | 'qualifying' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  discovered: number;
  qualified: number;
  created_at: string;
  finished_at?: string;
  structured_plan?: any;
  error_message?: string;
}

export interface SearchResultItem {
  entity_id: string;
  rank: number;
  name: string;
  entity_type: string;
  website?: string;
  email?: string;
  phone?: string;
  location_summary?: string;
  description?: string;
  match_score: number;
  is_qualified: boolean;
  qualification_reasons: string[];
  attributes: Record<string, any>;
}

export interface EntityProvenance {
  id: string;
  field_name: string;
  value_raw?: string;
  source_url: string;
  source_type: string;
  collected_at: string;
  verification_status: 'observed' | 'inferred' | 'third_party_verified';
}

export interface EntityDetail {
  id: string;
  entity_type: string;
  name: string;
  description?: string;
  website?: string;
  email?: string;
  phone?: string;
  location_summary?: string;
  attributes: Record<string, any>;
  created_at: string;
  updated_at: string;
  sources: EntityProvenance[];
}

export interface APIKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  created_at: string;
  last_used_at?: string;
}
