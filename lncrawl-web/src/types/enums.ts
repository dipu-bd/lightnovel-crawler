export const UserRole = {
  USER: 'user',
  ADMIN: 'admin',
};
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserTier = {
  BASIC: 0,
  PREMIUM: 1,
  VIP: 2,
};
export type UserTier = (typeof UserTier)[keyof typeof UserTier];

export const JobPriority = {
  LOW: 0,
  NORMAL: 1,
  HIGH: 2,
};
export type JobPriority = (typeof JobPriority)[keyof typeof JobPriority];

export const JobStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'done',
};
export type JobStatus = (typeof JobStatus)[keyof typeof JobStatus];

export const RunState = {
  FAILED: 0,
  SUCCESS: 1,
  CANCELED: 2,
  FETCHING_NOVEL: 3,
  FETCHING_CONTENT: 4,
  CREATING_ARTIFACTS: 5,
};
export type RunState = (typeof RunState)[keyof typeof RunState];

export const OutputFormat = {
  json: 'json',
  epub: 'epub',
  text: 'text',
  web: 'web',
  docx: 'docx',
  mobi: 'mobi',
  pdf: 'pdf',
  rtf: 'rtf',
  txt: 'txt',
  azw3: 'azw3',
  fb2: 'fb2',
  lit: 'lit',
  lrf: 'lrf',
  oeb: 'oeb',
  pdb: 'pdb',
  rb: 'rb',
  snb: 'snb',
  tcr: 'tcr',
};
export type OutputFormat = (typeof OutputFormat)[keyof typeof OutputFormat];
