import { cachedGet, clearCache } from "./client";
import type { Plant } from "../types/api";

const PLANTS_CACHE_KEY = "plants";

export async function getPlants(
  forceRefresh = false,
): Promise<Plant[]> {
  return cachedGet<Plant[]>(
    PLANTS_CACHE_KEY,
    "/plants/",
    forceRefresh,
  );
}

export function clearPlantsCache(): void {
  clearCache(PLANTS_CACHE_KEY);
}