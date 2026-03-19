import { existsSync } from 'fs';
import { cp, mkdir, readFile, readdir, rm, stat, writeFile } from 'fs/promises';

export async function pathExists(targetPath: string): Promise<boolean> {
  try {
    await stat(targetPath);
    return true;
  } catch {
    return false;
  }
}

export function pathExistsSync(targetPath: string): boolean {
  return existsSync(targetPath);
}

export async function ensureDir(targetPath: string): Promise<void> {
  await mkdir(targetPath, { recursive: true });
}

export async function readJson<T>(targetPath: string): Promise<T> {
  const content = await readFile(targetPath, 'utf-8');
  return JSON.parse(content) as T;
}

export async function copyPath(sourcePath: string, targetPath: string): Promise<void> {
  await cp(sourcePath, targetPath, { recursive: true, force: true });
}

export async function removePath(targetPath: string): Promise<void> {
  await rm(targetPath, { recursive: true, force: true });
}

export { readFile, readdir, stat, writeFile };
