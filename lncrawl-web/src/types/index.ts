import type {
  JobPriority,
  JobStatus,
  OutputFormat,
  RunState,
  UserRole,
  UserTier,
} from './enums';

export * from './enums';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  tier: UserTier;
  is_active: boolean;
  created_at: number;
  updated_at: number;
}

export interface AuthLoginResponse {
  token: string;
  user: User;
  is_verified: boolean;
}

export interface PaginatiedResponse<T> {
  total: number;
  offset: number;
  limit: number;
  items: T[];
}

export interface Novel {
  id: string;
  created_at: number;
  updated_at: number;
  url: string;
  title: string;
  orphan: boolean;
  authors: string;
  synopsis: string;
  tags: string[];
  volume_count: number;
  chapter_count: number;
}

export interface Job {
  id: string;
  created_at: number;
  updated_at: number;
  user_id: string;
  novel_id: string;
  url: string;
  priority: JobPriority;
  status: JobStatus;
  run_state: RunState;
  progress: number;
  error: string;
  started_at: number;
  finished_at: number;
}

export interface Artifact {
  id: string;
  format: OutputFormat;
  created_at: number;
  updated_at: number;
  novel_id: string;
  file_name: string;
  file_size?: number;
  is_available: boolean;
}

export interface RunnerHistoryItem {
  time: number;
  job_id: string;
  user_id: string;
  novel_id: string;
  status: JobStatus;
  run_state: RunState;
}

export interface RunnerStatus {
  running: boolean;
  history: RunnerHistoryItem[];
}

export interface JobDetails {
  job: Job;
  novel: Novel;
  user: User;
  artifacts: Artifact[];
}

export interface SupportedSource {
  url: string;
  domain: string;
  has_manga: boolean;
  has_mtl: boolean;
  language: string;
  is_disabled: boolean;
  disable_reason?: string;
  can_search: boolean;
  can_login: boolean;
  can_logout: boolean;
}

export interface Chapter {
  id: number;
  hash: string;
  title: string;
  isRead?: boolean;
}

export interface Volume {
  id: number;
  title: string;
  chapters: Chapter[];
  isRead?: boolean;
}

export interface ChapterBody {
  id: number;
  title: string;
  body: string;
  volume_id: number;
  volume: string;
  prev?: Chapter;
  next?: Chapter;
}
