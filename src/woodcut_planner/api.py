from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from .models import WoodPiece, Settings, CalculationResult
from .calculator import calculate_wood_arrangement
from .csv_exporter import (
    generate_purchase_order,
    generate_arrangements,
    generate_waste_analysis,
    generate_cutting_plan,
)

app = FastAPI(
    title="Wood Calculator API",
    description="API for calculating optimal wood cutting arrangements",
    version="1.0.0",
)

# Get allowed origins from environment or use default for local development
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:4173",  # Dev and preview servers
    ).split(",")
]

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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


@app.post("/api/export/purchase-order")
async def export_purchase_order(request: CalculationRequest) -> dict:
    """Generate a CSV export of the purchase order."""
    result = calculate_wood_arrangement(request.pieces, request.settings)
    csv_data = generate_purchase_order(result, request.settings)
    return {"filename": "purchase_order.csv", "data": csv_data}


@app.post("/api/export/arrangements")
async def export_arrangements(request: CalculationRequest) -> dict:
    """Generate a CSV export of the cutting arrangements."""
    result = calculate_wood_arrangement(request.pieces, request.settings)
    csv_data = generate_arrangements(result, request.pieces, request.settings)
    return {"filename": "arrangements.csv", "data": csv_data}


@app.post("/api/export/waste-analysis")
async def export_waste_analysis(request: CalculationRequest) -> dict:
    """Generate a CSV export of the waste analysis."""
    result = calculate_wood_arrangement(request.pieces, request.settings)
    csv_data = generate_waste_analysis(result, request.settings)
    return {"filename": "waste_analysis.csv", "data": csv_data}


@app.post("/api/export/cutting-plan")
async def export_cutting_plan(request: CalculationRequest) -> dict:
    """Generate a CSV export of the aggregated cutting plan."""
    result = calculate_wood_arrangement(request.pieces, request.settings)
    csv_data = generate_cutting_plan(result, request.settings)
    return {"filename": "cutting_plan.csv", "data": csv_data}


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
