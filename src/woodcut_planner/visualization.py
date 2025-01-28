"""Module for generating visual representations of wood cutting arrangements."""

from typing import List, Dict
from .models import WoodUnit, PiecePlacement


def _scale_length(length: float, unit_length: float, max_width: int = 60) -> int:
    """Scale a length to fit within max_width characters."""
    return int((length / unit_length) * max_width)


def _create_unit_diagram(
    unit: WoodUnit, unit_length: float, max_width: int = 60
) -> List[str]:
    """Create an ASCII diagram for a single wood unit."""
    # Scale all lengths to fit in max_width
    scaled_positions = [
        (
            _scale_length(pos.start_position, unit_length, max_width),
            _scale_length(pos.length, unit_length, max_width),
        )
        for pos in unit.positions
    ]
    scaled_waste = _scale_length(unit.waste, unit_length, max_width)

    # Create the basic diagram structure
    diagram = []

    # Top border
    diagram.append("+" + "-" * max_width + "+")

    # Middle section with pieces and labels
    pieces_line = [" " for _ in range(max_width)]
    labels_line = [" " for _ in range(max_width)]
    cuts_line = [" " for _ in range(max_width)]

    # Fill in pieces
    for i, (start, length) in enumerate(scaled_positions):
        # Fill piece area with a distinct character
        for j in range(start, start + length):
            if j < max_width:
                pieces_line[j] = "█"

        # Add cut marker at the end of each piece except the last one
        if i < len(scaled_positions) - 1:
            cut_pos = start + length
            if cut_pos < max_width:
                cuts_line[cut_pos] = "┊"

        # Add length label in the middle of the piece
        label = f"{unit.positions[i].length:.1f}"
        label_start = start + (length - len(label)) // 2
        if label_start >= 0 and label_start + len(label) <= max_width:
            for k, char in enumerate(label):
                labels_line[label_start + k] = char

    # Add waste area if there's waste
    if unit.waste > 0:
        waste_start = sum(p[1] for p in scaled_positions)
        waste_end = waste_start + scaled_waste

        # Fill waste area with different pattern
        for j in range(waste_start, min(waste_end, max_width)):
            pieces_line[j] = "░"

        # Add waste label
        waste_label = f"W:{unit.waste:.1f}"
        waste_label_start = waste_start + (scaled_waste - len(waste_label)) // 2
        if waste_label_start >= 0 and waste_label_start + len(waste_label) <= max_width:
            for k, char in enumerate(waste_label):
                labels_line[waste_label_start + k] = char

    diagram.append("|" + "".join(pieces_line) + "|")
    diagram.append("|" + "".join(labels_line) + "|")
    diagram.append("|" + "".join(cuts_line) + "|")

    # Bottom border
    diagram.append("+" + "-" * max_width + "+")

    # Add unit number, total length and utilization
    used_length = unit_length - unit.waste
    utilization = (used_length / unit_length) * 100
    diagram.append(
        f"Unit {unit.unit_number} (Length: {unit_length:.1f}cm, Used: {used_length:.1f}cm, Utilization: {utilization:.1f}%)"
    )

    return diagram


def create_arrangement_diagram(
    wood_type: str, units: List[WoodUnit], unit_length: float
) -> str:
    """Create an ASCII diagram for a complete wood type arrangement."""
    diagrams = []

    # Add header
    diagrams.append(f"\nCutting Diagram for {wood_type}")
    diagrams.append("=" * (len(diagrams[0]) - 1))
    diagrams.append("Legend: █ = Used wood, ░ = Waste, ┊ = Cut position")
    diagrams.append("")

    # Create diagram for each unit
    for unit in units:
        unit_diagram = _create_unit_diagram(unit, unit_length)
        diagrams.extend(unit_diagram)
        diagrams.append("")  # Add spacing between units

    return "\n".join(diagrams)
