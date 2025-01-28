from fastapi.testclient import TestClient
import pytest
from woodcut_planner.api import app
from woodcut_planner.models import WoodPiece, Settings, WoodType

client = TestClient(app)


@pytest.fixture
def sample_request():
    return {
        "pieces": [
            {"type": "pine 5x10", "length": 250, "count": 2},
            {"type": "pine 5x10", "length": 180, "count": 1},
        ],
        "settings": {
            "wood_types": {"pine 5x10": {"unit_length": 480, "price": 50}},
            "saw_width": 0.3,
            "currency": " ILS",
        },
    }


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculate(sample_request):
    response = client.post("/api/calculate", json=sample_request)
    assert response.status_code == 200
    result = response.json()

    # Check basic structure
    assert "arrangements" in result
    assert "total_units" in result
    assert "costs" in result
    assert "total_cost" in result

    # Check specific values
    assert result["total_units"]["pine 5x10"] > 0
    assert result["total_cost"] > 0


def test_export_cutting_list(sample_request):
    response = client.post("/api/export/cutting-list", json=sample_request)
    assert response.status_code == 200
    result = response.json()

    assert "filename" in result
    assert "data" in result
    assert result["filename"] == "cutting_list.csv"
    assert len(result["data"]) > 1  # Header + at least one row
    assert result["data"][0] == ["Wood Type", "Length (cm)", "Count"]


def test_export_arrangements(sample_request):
    response = client.post("/api/export/arrangements", json=sample_request)
    assert response.status_code == 200
    result = response.json()

    assert "filename" in result
    assert "data" in result
    assert result["filename"] == "arrangements.csv"
    assert len(result["data"]) > 1  # Header + at least one row
    assert result["data"][0] == [
        "Wood Type",
        "Unit Number",
        "Piece Length (cm)",
        "Piece Count",
        "Start Position (cm)",
        "Waste (cm)",
    ]


def test_invalid_wood_type(sample_request):
    # Modify request to include invalid wood type
    sample_request["pieces"][0]["type"] = "invalid_wood"

    response = client.post("/api/calculate", json=sample_request)
    assert response.status_code == 400
    assert "Unknown wood type" in response.json()["detail"]
