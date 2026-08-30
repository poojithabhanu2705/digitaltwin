import apiClient from "./client";

export interface ProductionLine {
  line_id: string;
  plant_id: string;
  plant_name: string;
  name: string;
  line_type: string;
  description: string;
  status: string;
}

export async function getLines(): Promise<ProductionLine[]> {
  const response = await apiClient.get<ProductionLine[]>("/lines/");
  return response.data;
}

export async function getLine(
  lineId: string,
): Promise<ProductionLine> {
  const response = await apiClient.get<ProductionLine>(
    `/lines/${lineId}/`,
  );

  return response.data;
}
