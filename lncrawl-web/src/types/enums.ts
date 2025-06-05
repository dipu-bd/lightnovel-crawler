export const UserRole = {
  USER: 'user',
  ADMIN: 'admin',
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserTier = {
  BASIC: 0,
  PREMIUM: 1,
  VIP: 2,
} as const;
export type UserTier = (typeof UserTier)[keyof typeof UserTier];
