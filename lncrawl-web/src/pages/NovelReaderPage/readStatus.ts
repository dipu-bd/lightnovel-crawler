import { get, set } from 'idb-keyval';

export async function getChapterReadStatus(
  novelId: string,
  chapterId: number
): Promise<boolean> {
  const value = await get(`${novelId}:${chapterId}`);
  return Boolean(value);
}

export async function setChapterReadStatus(
  novelId: string,
  chapterId: number
): Promise<void> {
  await set(`${novelId}:${chapterId}`, true);
}
