import apiClient from "./client";
import type { Plant } from "../types/api";

export async function getPlants(): Promise<Plant[]> {
  const response = await apiClient.get<Plant[]>("/plants/");
  return response.data;
}
