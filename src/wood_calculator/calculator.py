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
)


def _try_arrangement(
    pieces: List[WoodPiece], unit_length: float, saw_width: float
) -> List[WoodUnit]:
    """Try to arrange pieces with the current sorting strategy."""
    units: List[WoodUnit] = []
    current_unit = None
    current_position = 0
    unit_number = 1

    for piece in pieces:
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


def _evaluate_arrangement(units: List[WoodUnit]) -> Tuple[float, float]:
    """Evaluate arrangement quality based on total waste and waste distribution.
    Returns (total_waste, longest_waste_piece)"""
    total_waste = sum(unit.waste for unit in units)
    longest_waste = max((unit.waste for unit in units), default=0)
    return total_waste, longest_waste


def _arrange_pieces(
    pieces: List[WoodPiece], unit_length: float, saw_width: float
) -> List[WoodUnit]:
    """Arrange pieces optimally, preferring arrangements with longer waste pieces."""

    # Create different piece arrangements to try
    arrangements_to_try = []

    # 1. Basic length-descending sort
    desc_sorted = sorted(pieces, key=lambda x: x.length, reverse=True)
    arrangements_to_try.append(desc_sorted)

    # 2. Group similar lengths together
    grouped_by_length = []
    length_groups = defaultdict(list)
    for p in pieces:
        length_groups[p.length].append(p)
    for length in sorted(length_groups.keys(), reverse=True):
        grouped_by_length.extend(length_groups[length])
    arrangements_to_try.append(grouped_by_length)

    # 3. Try to pair long pieces with short ones
    paired = pieces.copy()
    long_pieces = sorted(pieces, key=lambda x: x.length, reverse=True)
    short_pieces = sorted(pieces, key=lambda x: x.length)

    # Pair longest with shortest until we run out of pieces
    paired = []
    long_idx = 0
    short_idx = 0
    while long_idx < len(long_pieces) and short_idx < len(short_pieces):
        if (
            long_pieces[long_idx].length + short_pieces[short_idx].length + saw_width
            <= unit_length
        ):
            paired.extend([long_pieces[long_idx], short_pieces[short_idx]])
            long_idx += 1
            short_idx += 1
        else:
            paired.append(long_pieces[long_idx])
            long_idx += 1

    # Add remaining pieces
    paired.extend(long_pieces[long_idx:])
    paired.extend(short_pieces[short_idx:])
    arrangements_to_try.append(paired)

    # Try each arrangement and evaluate results
    best_arrangement = None
    best_score = (float("inf"), 0)  # (total_waste, longest_waste)

    for arrangement in arrangements_to_try:
        units = _try_arrangement(arrangement, unit_length, saw_width)
        score = _evaluate_arrangement(units)

        # Better if total waste is less, or if total waste is same but longest waste piece is longer
        if score[0] < best_score[0] or (
            score[0] == best_score[0] and score[1] > best_score[1]
        ):
            best_arrangement = units
            best_score = score

    return best_arrangement


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
