import json
import click
from typing import List

from .models import WoodPiece, Settings
from .calculator import calculate_wood_arrangement


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
    click.echo("\nWood Cutting Arrangement:")
    click.echo("=======================")

    for arr in result.arrangements:
        click.echo(f"\nWood Type: {arr.wood_type}")
        click.echo(f"Number of units needed: {result.total_units[arr.wood_type]}")
        click.echo(f"Cost: {result.costs[arr.wood_type]:.2f}{settings.currency}")

        for unit in arr.units:
            click.echo(f"\n  Unit {unit.unit_number}:")
            click.echo("  Pieces:")
            for length, count in unit.pieces.items():
                click.echo(f"    - {count}x {length}cm")
            click.echo(f"  Waste: {unit.waste:.1f}cm")

    click.echo(f"\nTotal Cost: {result.total_cost:.2f}{settings.currency}")


if __name__ == "__main__":
    calculate()
