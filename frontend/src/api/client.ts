import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

/*
 * Small frontend cache.
 *
 * This is intentionally kept in memory:
 * - no localStorage
 * - no stale persistence across browser sessions
 * - backend remains the source of truth
 * - navigation between pages becomes instant
 */

type CacheEntry<T> = {
  data: T;
  timestamp: number;
};

const cache = new Map<string, CacheEntry<unknown>>();

const CACHE_TTL = 30_000; // 30 seconds

export function getCached<T>(key: string): T | null {
  const entry = cache.get(key);

  if (!entry) {
    return null;
  }

  if (Date.now() - entry.timestamp > CACHE_TTL) {
    cache.delete(key);
    return null;
  }

  return entry.data as T;
}

export function setCached<T>(key: string, data: T): void {
  cache.set(key, {
    data,
    timestamp: Date.now(),
  });
}

export function clearCache(key?: string): void {
  if (key) {
    cache.delete(key);
  } else {
    cache.clear();
  }
}

export async function cachedGet<T>(
  key: string,
  url: string,
  forceRefresh = false,
): Promise<T> {
  if (!forceRefresh) {
    const cached = getCached<T>(key);

    if (cached !== null) {
      return cached;
    }
  }

  const response = await apiClient.get<T>(url);

  setCached(key, response.data);

  return response.data;
}

export default apiClient;