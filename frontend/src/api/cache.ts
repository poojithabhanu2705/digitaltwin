type CacheEntry<T> = {
  data: T;
  timestamp: number;
};

const cache = new Map<string, CacheEntry<unknown>>();
const pending = new Map<string, Promise<unknown>>();

const CACHE_TTL = 30_000; // 30 seconds

export async function cachedRequest<T>(
  key: string,
  request: () => Promise<T>,
  forceRefresh = false,
): Promise<T> {
  const now = Date.now();
  const existing = cache.get(key) as CacheEntry<T> | undefined;

  if (!forceRefresh && existing && now - existing.timestamp < CACHE_TTL) {
    return existing.data;
  }

  const existingRequest = pending.get(key) as Promise<T> | undefined;

  if (!forceRefresh && existingRequest) {
    return existingRequest;
  }

  const requestPromise = request()
    .then((data) => {
      cache.set(key, {
        data,
        timestamp: Date.now(),
      });

      return data;
    })
    .finally(() => {
      pending.delete(key);
    });

  pending.set(key, requestPromise);

  return requestPromise;
}

export function clearApiCache() {
  cache.clear();
  pending.clear();
}