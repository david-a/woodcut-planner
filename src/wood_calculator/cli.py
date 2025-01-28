import json
from typing import List
import click
from tabulate import tabulate

from .models import WoodPiece, Settings
from .calculator import calculate_wood_arrangement


def print_separator(char="=", length=50):
    click.echo(char * length)


def format_currency(amount: float, currency: str) -> str:
    return f"{amount:.2f}{currency}"


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

    # Track total waste for summary
    total_waste = 0
    total_units = 0
    summary_data = []

    for arr in result.arrangements:
        wood_type = arr.wood_type
        units_needed = result.total_units[wood_type]
        cost = result.costs[wood_type]
        wood_waste = sum(unit.waste for unit in arr.units)
        total_waste += wood_waste
        total_units += units_needed

        # Add to summary data
        summary_data.append(
            [
                wood_type,
                units_needed,
                format_currency(cost, settings.currency),
                f"{wood_waste:.1f}cm",
            ]
        )

        # Detailed arrangement output
        click.echo(f"Wood Type: {wood_type}")
        click.echo(f"Number of units needed: {units_needed}")
        click.echo(f"Cost: {format_currency(cost, settings.currency)}")
        click.echo(f"Total waste: {wood_waste:.1f}cm")
        click.echo()

        for unit in arr.units:
            click.echo(f"  Unit {unit.unit_number}")
            print_separator("-", 30)
            click.echo("  Pieces:")
            for length, count in unit.pieces.items():
                click.echo(f"    - {count}x {length}cm")
            click.echo(f"  Waste: {unit.waste:.1f}cm")
            print_separator("-", 30)
            click.echo()

        print_separator()
        click.echo()

    # Print summary table
    click.echo("\nOrder Summary")
    print_separator()
    click.echo()

    headers = ["Wood Type", "Units", "Cost", "Waste"]
    click.echo(tabulate(summary_data, headers=headers, tablefmt="grid"))
    click.echo()

    click.echo(f"Total Units: {total_units}")
    click.echo(f"Total Waste: {total_waste:.1f}cm")
    click.echo(f"Total Cost: {format_currency(result.total_cost, settings.currency)}")
    print_separator()


if __name__ == "__main__":
    calculate()
