import json
import csv
from pathlib import Path
from typing import List
import click
from tabulate import tabulate

from .models import WoodPiece, Settings
from .calculator import calculate_wood_arrangement
from .csv_exporter import (
    generate_purchase_order,
    generate_arrangements,
    generate_waste_analysis,
)


def print_separator(char="=", length=50):
    click.echo(char * length)


def format_currency(amount: float, currency: str) -> str:
    return f"{amount:.2f}{currency}"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"


def save_csv(data: List[List[str]], output_file: str):
    """Save data to a CSV file."""
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    click.echo(f"CSV file saved to: {output_file}")


def load_input_files(
    pieces_file: str, settings_file: str
) -> tuple[List[WoodPiece], Settings]:
    """Load and parse input files."""
    with open(pieces_file) as f:
        pieces_data = json.load(f)
    with open(settings_file) as f:
        settings_data = json.load(f)

    pieces = [WoodPiece(**piece) for piece in pieces_data]
    settings = Settings(**settings_data)
    return pieces, settings


@click.group()
def cli():
    """Wood Calculator CLI."""
    pass


@cli.command()
@click.option(
    "--pieces",
    "-p",
    "pieces_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing list of required pieces",
)
@click.option(
    "--settings",
    "-s",
    "settings_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing wood types and settings",
)
def calculate(pieces_file: str, settings_file: str):
    """Calculate optimal wood cutting arrangement."""
    pieces, settings = load_input_files(pieces_file, settings_file)
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
        unit_length = settings.wood_types[wood_type].unit_length

        # Add to summary data
        summary_data.append(
            [
                wood_type,
                unit_length,
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
        click.echo(f"Unit Length: {unit_length}cm")
        click.echo(f"Number of units needed: {units_needed}")
        click.echo(f"Cost: {format_currency(cost, settings.currency)}")
        click.echo(f"Total waste: {wood_waste:.1f}cm")
        click.echo(
            f"Suggestion: {result.waste_statistics.potential_savings[wood_type]}"
        )
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

    headers = ["Wood Type", "Unit Length (cm)", "Units", "Cost", "Waste", "Waste %"]
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


@cli.command()
@click.option(
    "--pieces",
    "-p",
    "pieces_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing list of required pieces",
)
@click.option(
    "--settings",
    "-s",
    "settings_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing wood types and settings",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    required=True,
    help="Path to save the CSV file",
)
def export_purchase_order(pieces_file: str, settings_file: str, output_file: str):
    """Export purchase order to CSV."""
    pieces, settings = load_input_files(pieces_file, settings_file)
    result = calculate_wood_arrangement(pieces, settings)
    csv_data = generate_purchase_order(result, settings)
    save_csv(csv_data, output_file)


@cli.command()
@click.option(
    "--pieces",
    "-p",
    "pieces_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing list of required pieces",
)
@click.option(
    "--settings",
    "-s",
    "settings_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing wood types and settings",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    required=True,
    help="Path to save the CSV file",
)
def export_arrangements(pieces_file: str, settings_file: str, output_file: str):
    """Export cutting arrangements to CSV."""
    pieces, settings = load_input_files(pieces_file, settings_file)
    result = calculate_wood_arrangement(pieces, settings)
    csv_data = generate_arrangements(result, pieces, settings)
    save_csv(csv_data, output_file)


@cli.command()
@click.option(
    "--pieces",
    "-p",
    "pieces_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing list of required pieces",
)
@click.option(
    "--settings",
    "-s",
    "settings_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing wood types and settings",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    required=True,
    help="Path to save the CSV file",
)
def export_waste_analysis(pieces_file: str, settings_file: str, output_file: str):
    """Export waste analysis to CSV."""
    pieces, settings = load_input_files(pieces_file, settings_file)
    result = calculate_wood_arrangement(pieces, settings)
    csv_data = generate_waste_analysis(result, settings)
    save_csv(csv_data, output_file)


@cli.command()
@click.option(
    "--pieces",
    "-p",
    "pieces_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing list of required pieces",
)
@click.option(
    "--settings",
    "-s",
    "settings_file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file containing wood types and settings",
)
@click.option(
    "--output-dir",
    "-o",
    "output_dir",
    type=click.Path(),
    required=True,
    help="Directory to save the CSV files",
)
def export_all(pieces_file: str, settings_file: str, output_dir: str):
    """Export all data to CSV files in the specified directory."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pieces, settings = load_input_files(pieces_file, settings_file)
    result = calculate_wood_arrangement(pieces, settings)

    # Export purchase order
    csv_data = generate_purchase_order(result, settings)
    save_csv(csv_data, output_path / "purchase_order.csv")

    # Export arrangements
    csv_data = generate_arrangements(result, pieces, settings)
    save_csv(csv_data, output_path / "arrangements.csv")

    # Export waste analysis
    csv_data = generate_waste_analysis(result, settings)
    save_csv(csv_data, output_path / "waste_analysis.csv")


if __name__ == "__main__":
    cli()
