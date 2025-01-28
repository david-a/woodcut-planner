from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import WoodPiece, Settings, CalculationResult
from .calculator import calculate_wood_arrangement

app = FastAPI(
    title="Wood Calculator API",
    description="API for calculating optimal wood cutting arrangements",
    version="1.0.0",
)

# Enable CORS for the Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Default SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalculationRequest(BaseModel):
    pieces: List[WoodPiece]
    settings: Settings


@app.post("/api/calculate", response_model=CalculationResult)
async def calculate(request: CalculationRequest) -> CalculationResult:
    """Calculate optimal wood cutting arrangement."""
    try:
        result = calculate_wood_arrangement(request.pieces, request.settings)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/export/cutting-list")
async def export_cutting_list(request: CalculationRequest) -> dict:
    """Generate a CSV export of the cutting list."""
    result = calculate_wood_arrangement(request.pieces, request.settings)

    # Generate CSV data for cutting list
    csv_data = []
    csv_data.append(["Wood Type", "Length (cm)", "Count"])

    for piece in request.pieces:
        csv_data.append([piece.type, piece.length, piece.count])

    return {"filename": "cutting_list.csv", "data": csv_data}


@app.post("/api/export/arrangements")
async def export_arrangements(request: CalculationRequest) -> dict:
    """Generate a CSV export of the cutting arrangements."""
    result = calculate_wood_arrangement(request.pieces, request.settings)

    # Generate CSV data for arrangements
    csv_data = []
    csv_data.append(
        [
            "Wood Type",
            "Unit Number",
            "Piece Length (cm)",
            "Piece Count",
            "Start Position (cm)",
            "Waste (cm)",
            "Unit Waste %",
            "Suggestion",
        ]
    )

    for arr in result.arrangements:
        wood_type = arr.wood_type
        wood_settings = request.settings.wood_types[wood_type]
        unit_length = wood_settings.unit_length

        for unit in arr.units:
            unit_waste_percentage = (unit.waste / unit_length) * 100
            for length, count in unit.pieces.items():
                positions = [pos for pos in unit.positions if pos.length == length]
                for pos in positions:
                    csv_data.append(
                        [
                            arr.wood_type,
                            unit.unit_number,
                            length,
                            count,
                            pos.start_position,
                            unit.waste if pos == positions[-1] else 0,
                            (
                                f"{unit_waste_percentage:.1f}%"
                                if pos == positions[-1]
                                else ""
                            ),
                            (
                                result.waste_statistics.potential_savings[wood_type]
                                if pos == positions[-1]
                                else ""
                            ),
                        ]
                    )

    return {"filename": "arrangements.csv", "data": csv_data}


@app.post("/api/export/waste-analysis")
async def export_waste_analysis(request: CalculationRequest) -> dict:
    """Generate a CSV export of the waste analysis."""
    result = calculate_wood_arrangement(request.pieces, request.settings)
    stats = result.waste_statistics

    # Generate CSV data for waste analysis
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
            result.total_units[wood_type]
            * request.settings.wood_types[wood_type].unit_length
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

    return {"filename": "waste_analysis.csv", "data": csv_data}


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
