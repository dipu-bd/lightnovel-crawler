export interface ProgressiveValue<T> {
  data?: T;
  error?: any;
  loading: boolean;
  startedAt: number;
  finishedAt?: number;
}
