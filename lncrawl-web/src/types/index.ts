import type { UserRole, UserTier } from './enums';

export type * from './enums';

export interface AuthUser {
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
  user: AuthUser;
}

export interface PaginationParams extends Record<string, any> {
  limit: number;
  offset: number;
}

export interface Pagination<T> extends PaginationParams {
  total: number;
  items: Array<T>;
}
