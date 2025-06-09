export function formatFileSize(bytes?: number, decimals = 2): string {
  if (!bytes) {
    return '0 bytes';
  }
  const sizes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'];
  const k = 1024;
  const dm = Math.max(0, decimals);
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}
