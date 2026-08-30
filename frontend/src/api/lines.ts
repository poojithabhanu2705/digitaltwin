import { cachedGet, clearCache } from "./client";

export interface ProductionLine {
  line_id: string;
  plant_id: string;
  plant_name: string;
  name: string;
  line_type: string;
  description: string;
  status: string;
}

const LINES_CACHE_KEY = "lines";

export async function getLines(
  forceRefresh = false,
): Promise<ProductionLine[]> {
  return cachedGet<ProductionLine[]>(
    LINES_CACHE_KEY,
    "/lines/",
    forceRefresh,
  );
}

export async function getLine(
  lineId: string,
  forceRefresh = false,
): Promise<ProductionLine> {
  return cachedGet<ProductionLine>(
    `line:${lineId}`,
    `/lines/${lineId}/`,
    forceRefresh,
  );
}

export function clearLinesCache(): void {
  clearCache(LINES_CACHE_KEY);
}