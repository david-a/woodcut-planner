from typing import Dict, List
from pydantic import BaseModel, Field, NonNegativeFloat, PositiveFloat


class WoodType(BaseModel):
    unit_length: PositiveFloat
    price: NonNegativeFloat


class WoodPiece(BaseModel):
    type: str
    length: PositiveFloat
    count: int = Field(default=1, ge=1)


class Settings(BaseModel):
    wood_types: Dict[str, WoodType]
    saw_width: NonNegativeFloat = Field(default=0.3)  # cm
    currency: str = Field(default=" ILS")


class PiecePlacement(BaseModel):
    length: PositiveFloat
    start_position: NonNegativeFloat


class WoodUnit(BaseModel):
    unit_number: int
    pieces: Dict[float, int]  # length -> count
    positions: List[PiecePlacement]
    waste: NonNegativeFloat


class WoodArrangement(BaseModel):
    wood_type: str
    units: List[WoodUnit]


class CalculationResult(BaseModel):
    arrangements: List[WoodArrangement]
    total_units: Dict[str, int]
    costs: Dict[str, float]
    total_cost: float
