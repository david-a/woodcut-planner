from typing import List, Dict, Tuple
from collections import defaultdict
from itertools import combinations

from .models import (
    WoodPiece,
    Settings,
    CalculationResult,
    WoodUnit,
    WoodArrangement,
    PiecePlacement,
    WasteStatistics,
)


def _calculate_remaining_space(
    unit: WoodUnit, unit_length: float, saw_width: float
) -> float:
    """Calculate actual remaining space in a unit, accounting for saw width between pieces."""
    if not unit.positions:
        return unit_length

    # Calculate space used including saw width between pieces
    used_space = 0
    for piece in unit.positions:
        used_space += piece.length

    # Add saw width for gaps between pieces
    used_space += (len(unit.positions) - 1) * saw_width

    return unit_length - used_space


def _try_add_piece(
    piece: WoodPiece, unit: WoodUnit, unit_length: float, saw_width: float
) -> bool:
    """Try to add a piece to a unit. Returns True if successful."""
    # Calculate current position (end of last piece + saw width if needed)
    current_position = 0
    if unit.positions:
        last_piece = max(unit.positions, key=lambda p: p.start_position + p.length)
        current_position = last_piece.start_position + last_piece.length + saw_width

    # Check if piece fits
    if current_position + piece.length <= unit_length:
        # Add piece
        unit.pieces[piece.length] = unit.pieces.get(piece.length, 0) + 1
        unit.positions.append(
            PiecePlacement(length=piece.length, start_position=current_position)
        )
        # Update waste
        unit.waste = _calculate_remaining_space(unit, unit_length, saw_width)
        return True

    return False


def _arrange_pieces(
    pieces: List[WoodPiece], unit_length: float, saw_width: float
) -> List[WoodUnit]:
    """Arrange pieces optimally, minimizing the number of units and waste."""
    # Sort pieces by length (longest first) for initial placement
    remaining_pieces = sorted(pieces, key=lambda p: (-p.length, p.type))
    units: List[WoodUnit] = []
    current_unit_number = 1

    while remaining_pieces:
        # Try to fit piece in existing units first
        piece = remaining_pieces[0]
        piece_placed = False

        # Sort units by most remaining space for better filling
        for unit in sorted(units, key=lambda u: u.waste, reverse=True):
            if _try_add_piece(piece, unit, unit_length, saw_width):
                remaining_pieces.pop(0)
                piece_placed = True
                break

        if not piece_placed:
            # Create new unit
            new_unit = WoodUnit(
                unit_number=current_unit_number,
                pieces={},
                positions=[],
                waste=unit_length,
            )

            # Add piece to new unit
            if _try_add_piece(piece, new_unit, unit_length, saw_width):
                units.append(new_unit)
                current_unit_number += 1
                remaining_pieces.pop(0)
            else:
                raise ValueError(
                    f"Piece {piece} too long for unit length {unit_length}"
                )

    return units


def _calculate_waste_statistics(
    arrangements: List[WoodArrangement],
    settings: Settings,
) -> WasteStatistics:
    """Calculate detailed waste statistics for the arrangements."""
    total_waste = 0
    waste_by_type = {}
    total_wood_used = 0
    waste_distribution = defaultdict(list)
    potential_savings = {}

    for arr in arrangements:
        wood_type = arr.wood_type
        wood_settings = settings.wood_types[wood_type]
        type_waste = sum(unit.waste for unit in arr.units)
        type_total = len(arr.units) * wood_settings.unit_length

        # Calculate waste for this type
        waste_by_type[wood_type] = type_waste
        total_waste += type_waste
        total_wood_used += type_total

        # Record waste distribution
        waste_distribution[wood_type] = [unit.waste for unit in arr.units]

        # Generate saving suggestions
        avg_waste = type_waste / len(arr.units) if arr.units else 0
        if avg_waste > wood_settings.unit_length * 0.1:  # More than 10% waste
            potential_savings[wood_type] = (
                "Consider combining orders or finding smaller pieces to fill gaps"
            )
        elif len(arr.units) > 1 and any(
            unit.waste > wood_settings.unit_length * 0.2 for unit in arr.units
        ):
            potential_savings[wood_type] = (
                "Large waste in some units - consider rearranging pieces"
            )
        else:
            potential_savings[wood_type] = "Waste is within acceptable range"

    # Calculate overall waste percentage
    waste_percentage = (
        (total_waste / total_wood_used * 100) if total_wood_used > 0 else 0
    )

    return WasteStatistics(
        total_waste=total_waste,
        waste_by_type=waste_by_type,
        total_wood_used=total_wood_used,
        waste_percentage=waste_percentage,
        waste_distribution=dict(waste_distribution),
        potential_savings=potential_savings,
    )


def calculate_wood_arrangement(
    pieces: List[WoodPiece], settings: Settings
) -> CalculationResult:
    """Calculate optimal wood cutting arrangement."""
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

    # Calculate waste statistics
    waste_statistics = _calculate_waste_statistics(arrangements, settings)

    return CalculationResult(
        arrangements=arrangements,
        total_units=total_units,
        costs=costs,
        total_cost=total_cost,
        waste_statistics=waste_statistics,
    )
