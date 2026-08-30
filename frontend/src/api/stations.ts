import { cachedGet, clearCache } from "./client";

export interface Station {
  station_id: string;
  name: string;
  line_id?: string | null;
  line_name?: string | null;
  station_type?: string | null;
  status?: string | null;
  sequence_number?: number | null;
  [key: string]: unknown;
}

const STATIONS_CACHE_KEY = "stations";

export async function getStations(
  forceRefresh = false,
): Promise<Station[]> {
  const data = await cachedGet<
    Station[] | { results: Station[] }
  >(
    STATIONS_CACHE_KEY,
    "/stations/",
    forceRefresh,
  );

  return Array.isArray(data) ? data : data.results;
}

export async function getStation(
  stationId: string,
  forceRefresh = false,
): Promise<Station> {
  return cachedGet<Station>(
    `station:${stationId}`,
    `/stations/${stationId}/`,
    forceRefresh,
  );
}

export async function getStationTwin(
  stationId: string,
  forceRefresh = false,
): Promise<Record<string, unknown>> {
  return cachedGet<Record<string, unknown>>(
    `station-twin:${stationId}`,
    `/twin/stations/${stationId}/`,
    forceRefresh,
  );
}

export function clearStationsCache(): void {
  clearCache(STATIONS_CACHE_KEY);
}