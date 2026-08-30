export interface Plant {
  plant_id: string;
  name: string;
  location: string;
  timezone: string;
  status: string;
}

export interface ProductionLine {
  line_id: string;
  plant_id: string;
  plant_name: string;
  name: string;
  line_type: string;
  description: string;
  status: string;
}

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
