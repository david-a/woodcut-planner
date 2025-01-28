from typing import List, Dict
from collections import defaultdict

from .models import (
    WoodPiece,
    Settings,
    CalculationResult,
    WoodUnit,
    WoodArrangement,
    PiecePlacement,
)


def calculate_wood_arrangement(
    pieces: List[WoodPiece], settings: Settings
) -> CalculationResult:
    # Group pieces by wood type
    pieces_by_type: Dict[str, List[WoodPiece]] = defaultdict(list)
    for piece in pieces:
        pieces_by_type[piece.type].extend([piece] * piece.count)

    arrangements = []
    total_units = {}
    costs = {}
    total_cost = 0

    for wood_type, type_pieces in pieces_by_type.items():
        if wood_type not in settings.wood_types:
            raise ValueError(f"Unknown wood type: {wood_type}")

        wood_settings = settings.wood_types[wood_type]
        arrangement = _arrange_pieces(
            type_pieces, wood_settings.unit_length, settings.saw_width
        )

        units_needed = len(arrangement)
        type_cost = units_needed * wood_settings.price

        arrangements.append(WoodArrangement(wood_type=wood_type, units=arrangement))
        total_units[wood_type] = units_needed
        costs[wood_type] = type_cost
        total_cost += type_cost

    return CalculationResult(
        arrangements=arrangements,
        total_units=total_units,
        costs=costs,
        total_cost=total_cost,
    )


def _arrange_pieces(
    pieces: List[WoodPiece], unit_length: float, saw_width: float
) -> List[WoodUnit]:
    # Sort pieces by length in descending order for better packing
    sorted_pieces = sorted(pieces, key=lambda x: x.length, reverse=True)

    units: List[WoodUnit] = []
    current_unit = None
    current_position = 0
    unit_number = 1

    for piece in sorted_pieces:
        if current_unit is None:
            current_unit = WoodUnit(
                unit_number=unit_number, pieces={}, positions=[], waste=0
            )
            current_position = 0

        # Check if piece fits in current unit
        if current_position + piece.length + saw_width <= unit_length:
            # Add piece to current unit
            current_unit.pieces[piece.length] = (
                current_unit.pieces.get(piece.length, 0) + 1
            )
            current_unit.positions.append(
                PiecePlacement(length=piece.length, start_position=current_position)
            )
            current_position += piece.length + saw_width
        else:
            # Calculate waste for current unit
            current_unit.waste = unit_length - current_position
            units.append(current_unit)

            # Start new unit
            unit_number += 1
            current_unit = WoodUnit(
                unit_number=unit_number,
                pieces={piece.length: 1},
                positions=[PiecePlacement(length=piece.length, start_position=0)],
                waste=0,
            )
            current_position = piece.length + saw_width

    # Add last unit if not empty
    if current_unit is not None:
        current_unit.waste = unit_length - current_position
        units.append(current_unit)

    return units
