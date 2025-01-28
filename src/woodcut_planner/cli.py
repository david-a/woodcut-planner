import json
from typing import List
import click
from tabulate import tabulate

from .models import WoodPiece, Settings
from .calculator import calculate_wood_arrangement
from .visualization import create_arrangement_diagram


def print_separator(char="=", length=50):
    click.echo(char * length)


def format_currency(amount: float, currency: str) -> str:
    return f"{amount:.2f}{currency}"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"


@click.command()
@click.argument("pieces_file", type=click.Path(exists=True))
@click.argument("settings_file", type=click.Path(exists=True))
def calculate(pieces_file: str, settings_file: str):
    """Calculate optimal wood cutting arrangement.

    PIECES_FILE: JSON file containing list of required pieces
    SETTINGS_FILE: JSON file containing wood types and settings
    """
    # Load input files
    with open(pieces_file) as f:
        pieces_data = json.load(f)

    with open(settings_file) as f:
        settings_data = json.load(f)

    # Parse input data
    pieces = [WoodPiece(**piece) for piece in pieces_data]
    settings = Settings(**settings_data)

    # Calculate arrangement
    result = calculate_wood_arrangement(pieces, settings)

    # Output results
    click.echo("\nWood Cutting Arrangement")
    print_separator()
    click.echo()

    summary_data = []

    for arr in result.arrangements:
        wood_type = arr.wood_type
        units_needed = result.total_units[wood_type]
        cost = result.costs[wood_type]
        wood_waste = result.waste_statistics.waste_by_type[wood_type]

        # Add to summary data
        summary_data.append(
            [
                wood_type,
                units_needed,
                format_currency(cost, settings.currency),
                f"{wood_waste:.1f}cm",
                format_percentage(
                    wood_waste
                    / (units_needed * settings.wood_types[wood_type].unit_length)
                    * 100
                ),
            ]
        )

        # Detailed arrangement output
        click.echo(f"Wood Type: {wood_type}")
        click.echo(f"Number of units needed: {units_needed}")
        click.echo(f"Cost: {format_currency(cost, settings.currency)}")
        click.echo(f"Total waste: {wood_waste:.1f}cm")
        click.echo(
            f"Suggestion: {result.waste_statistics.potential_savings[wood_type]}"
        )
        click.echo()

        # Display cutting diagram
        click.echo(
            create_arrangement_diagram(
                wood_type, arr.units, settings.wood_types[wood_type].unit_length
            )
        )

        print_separator()
        click.echo()

    # Print summary table
    click.echo("\nOrder Summary")
    print_separator()
    click.echo()

    headers = ["Wood Type", "Units", "Cost", "Waste", "Waste %"]
    click.echo(tabulate(summary_data, headers=headers, tablefmt="grid"))
    click.echo()

    # Print waste statistics
    click.echo("\nWaste Analysis")
    print_separator()
    click.echo()

    click.echo(f"Total Wood Used: {result.waste_statistics.total_wood_used:.1f}cm")
    click.echo(f"Total Waste: {result.waste_statistics.total_waste:.1f}cm")
    click.echo(
        f"Overall Waste Percentage: {format_percentage(result.waste_statistics.waste_percentage)}"
    )
    click.echo()

    click.echo("Waste Distribution by Type:")
    for wood_type, waste_lengths in result.waste_statistics.waste_distribution.items():
        if waste_lengths:
            avg_waste = sum(waste_lengths) / len(waste_lengths)
            max_waste = max(waste_lengths)
            click.echo(f"  {wood_type}:")
            click.echo(f"    Average waste per unit: {avg_waste:.1f}cm")
            click.echo(f"    Largest waste piece: {max_waste:.1f}cm")
    click.echo()

    click.echo(f"Total Cost: {format_currency(result.total_cost, settings.currency)}")
    print_separator()


if __name__ == "__main__":
    calculate()
