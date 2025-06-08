import { AxiosError } from 'axios';

export function stringifyError(
  err: any,
  _default: string = 'Oops! Something went wrong.'
) {
  if (err instanceof AxiosError) {
    if (err.response?.status === 403) {
      return 'Not authorized';
    }
    const data = err.response?.data;
    if (data?.name === 'ER_DUP_ENTRY') {
      return 'Duplicate entry';
    }
    if (data?.detail && typeof data?.detail === 'string') {
      return data.detail;
    }
  }

  return _default || '' + err;
}
