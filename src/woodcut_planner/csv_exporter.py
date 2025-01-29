from typing import List, Dict, Any

from .models import WoodPiece, Settings, CalculationResult


def generate_purchase_order(
    result: CalculationResult, settings: Settings
) -> List[List[str]]:
    """Generate CSV data for the purchase order."""
    csv_data = []
    csv_data.append(
        ["Wood Type", "Unit Length (cm)", "Units", "Cost per Unit", "Total Cost"]
    )

    for wood_type, units in result.total_units.items():
        unit_length = settings.wood_types[wood_type].unit_length
        total_cost = result.costs[wood_type]
        cost_per_unit = settings.wood_types[wood_type].price
        csv_data.append(
            [
                wood_type,
                unit_length,
                units,
                f"{cost_per_unit:.2f}{settings.currency}",
                f"{total_cost:.2f}{settings.currency}",
            ]
        )

    return csv_data


def generate_arrangements(
    result: CalculationResult, pieces: List[WoodPiece], settings: Settings
) -> List[List[str]]:
    """Generate CSV data for the cutting arrangements."""
    csv_data = []
    csv_data.append(
        [
            "Wood Type",
            "Unit Number",
            "Piece Length (cm)",
            "Piece Count",
            "Start Position (cm)",
        ]
    )

    for arr in result.arrangements:
        for unit in arr.units:
            for length, count in unit.pieces.items():
                positions = [pos for pos in unit.positions if pos.length == length]
                for pos in positions:
                    csv_data.append(
                        [
                            arr.wood_type,
                            unit.unit_number,
                            length,
                            count,
                            f"{pos.start_position:.1f}",
                        ]
                    )

    return csv_data


def generate_waste_analysis(
    result: CalculationResult, settings: Settings
) -> List[List[str]]:
    """Generate CSV data for the waste analysis."""
    stats = result.waste_statistics
    csv_data = []

    # Overall statistics
    csv_data.append(["Overall Statistics"])
    csv_data.append(["Total Wood Used (cm)", "Total Waste (cm)", "Overall Waste %"])
    csv_data.append(
        [
            f"{stats.total_wood_used:.1f}",
            f"{stats.total_waste:.1f}",
            f"{stats.waste_percentage:.1f}%",
        ]
    )
    csv_data.append([])

    # Per type statistics
    csv_data.append(["Waste by Type"])
    csv_data.append(["Wood Type", "Total Waste (cm)", "Waste %", "Suggestion"])
    for wood_type in stats.waste_by_type:
        type_waste = stats.waste_by_type[wood_type]
        type_total = (
            result.total_units[wood_type] * settings.wood_types[wood_type].unit_length
        )
        waste_percentage = (type_waste / type_total) * 100
        csv_data.append(
            [
                wood_type,
                f"{type_waste:.1f}",
                f"{waste_percentage:.1f}%",
                stats.potential_savings[wood_type],
            ]
        )
    csv_data.append([])

    # Waste distribution
    csv_data.append(["Waste Distribution"])
    csv_data.append(["Wood Type", "Unit Number", "Waste Length (cm)"])
    for wood_type, waste_lengths in stats.waste_distribution.items():
        for i, waste in enumerate(waste_lengths, 1):
            csv_data.append([wood_type, i, f"{waste:.1f}"])

    return csv_data


def generate_cutting_plan(
    result: CalculationResult, settings: Settings
) -> List[List[str]]:
    """Generate CSV data for the cutting plan showing cuts needed from each unit."""
    csv_data = []
    csv_data.append(["Wood Type", "Unit Number", "Cuts Required"])

    # Generate cutting plan for each wood type
    for arr in result.arrangements:
        wood_type = arr.wood_type
        unit_length = settings.wood_types[wood_type].unit_length

        # Add wood type header
        csv_data.append([])
        csv_data.append([f"{wood_type} (Unit Length: {unit_length}cm)"])
        csv_data.append([])

        # For each unit, show the cuts needed
        for unit in arr.units:
            # Add unit header
            csv_data.append([wood_type, f"Unit {unit.unit_number}:"])

            # Add cuts for this unit, sorted by length
            for length in sorted(unit.pieces.keys(), reverse=True):
                count = unit.pieces[length]
                cut_description = f"{count}x {length:.1f}cm"
                csv_data.append(["", "", cut_description])

            # Add waste information
            if unit.waste > 0:
                csv_data.append(["", "", f"Remaining: {unit.waste:.1f}cm"])
            csv_data.append([])

    return csv_data
