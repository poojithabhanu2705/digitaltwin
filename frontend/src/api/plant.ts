import apiClient from "./client";

export interface Plant {
  plant_id: string;
  name: string;
}

export async function getPlants(): Promise<Plant[]> {
  const response = await apiClient.get<Plant[]>("/plants/");
  return response.data;
}

export async function getPlant(plantId: string): Promise<Plant> {
  const response = await apiClient.get<Plant>(`/plants/${plantId}/`);
  return response.data;
}