/**
 * TypeScript types for spec-ai-writer Frontend
 *
 * Matches FastAPI backend models
 */

export type PhaseStatus = 'not_started' | 'in_progress' | 'completed';

export type MessageRole = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface Project {
  project_id: string;
  display_name: string;
  current_phase: number;
  phase_status: Record<number, PhaseStatus>;
  created_at: string;
  updated_at: string;
  total_qa_pairs: number;
}

export interface ProjectCreate {
  display_name: string;
  llm_provider?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface PhaseInfo {
  phase_num: number;
  phase_name: string;
  description: string;
  status: PhaseStatus;
  qa_count: number;
  required_fields: string[];
  filename: string;
}

export interface ProjectStatusResponse {
  project_id: string;
  current_phase: number;
  phases: PhaseInfo[];
  overall_progress: number;
}

export interface InterviewStartRequest {
  project_id: string;
  phase_num?: number;
}

export interface InterviewStartResponse {
  project_id: string;
  display_name: string;
  phase_num: number;
  phase_name: string;
  initial_message: string;
  all_complete?: boolean;
  chat_history?: ChatMessage[];
}

export interface UserAnswerRequest {
  project_id: string;
  answer?: string;
}

export interface AssistantQuestionResponse {
  question: string;
  phase_complete: boolean;
  phase_num: number;
  qa_count: number;
}

export interface SpecificationResponse {
  project_id: string;
  phase_num: number;
  phase_name: string;
  filename: string;
  content: string;
  generated_at: string;
}

export interface SpecificationListItem {
  phase_num: number;
  phase_name: string;
  filename: string;
  file_size?: number;
  generated_at?: string;
  exists: boolean;
}

export interface SpecificationListResponse {
  project_id: string;
  specifications: SpecificationListItem[];
}

// ---------- Settings ----------

export type LLMProvider =
  | 'claude'
  | 'openai'
  | 'openrouter'
  | 'ollama'
  | 'lmstudio'
  | 'kimi'
  | 'bedrock';

export type SettingsSource = 'json' | 'env' | 'default';

export interface ProviderSettingsResponse {
  model: string;
  api_key_masked: string;
  base_url: string;
  aws_access_key_id_masked: string;
  aws_secret_access_key_masked: string;
  aws_region: string;
}

export type EffortSetting = "auto" | "low" | "medium" | "high" | "xhigh" | "max";

export interface GenerationParamsResponse {
  model: string;
  temperature_supported: boolean;
  effort_levels: string[];
}

export interface SettingsResponse {
  active_provider: LLMProvider;
  temperature: number;
  effort: EffortSetting;
  providers: Record<LLMProvider, ProviderSettingsResponse>;
  /** e.g. "kimi.model" → "json" | "env" | "default" */
  sources: Record<string, SettingsSource>;
}

export interface ProviderUpdate {
  model?: string;
  api_key?: string;
  clear_api_key?: boolean;
  base_url?: string;
  aws_access_key_id?: string;
  aws_secret_access_key?: string;
  aws_region?: string;
}

/** Payload for PUT /api/settings. All fields optional (partial update). */
export interface SettingsUpdateRequest {
  active_provider?: LLMProvider;
  temperature?: number;
  effort?: EffortSetting;
  providers?: Partial<Record<LLMProvider, ProviderUpdate>>;
}
