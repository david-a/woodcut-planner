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
                            pos.start_position,
                            unit.waste if pos == positions[-1] else 0,
                        ]
                    )

    return {"filename": "arrangements.csv", "data": csv_data}


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
