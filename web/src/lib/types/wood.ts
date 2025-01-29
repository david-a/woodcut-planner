export interface WoodType {
  unit_length: number;
  price: number;
}

export interface WoodPiece {
  type: string;
  length: number;
  count: number;
}

export interface Settings {
  wood_types: Record<string, WoodType>;
  saw_width: number;
  currency: string;
}

export interface PiecePosition {
  length: number;
  start_position: number;
}

export interface UnitArrangement {
  unit_number: number;
  pieces: Record<string, number>;
  positions: PiecePosition[];
  waste: number;
}

export interface WoodTypeArrangement {
  wood_type: string;
  units: UnitArrangement[];
}

export interface WasteStatistics {
  total_waste: number;
  waste_pieces: number[];
  waste_percentage: number;
}

export interface CalculationResult {
  arrangements: WoodTypeArrangement[];
  total_units: Record<string, number>;
  costs: {
    per_type: Record<string, number>;
    total: number;
  };
  waste_statistics: WasteStatistics;
}
