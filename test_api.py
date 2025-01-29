import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_response(response: requests.Response) -> None:
    """Print formatted response."""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("\n" + "=" * 50 + "\n")


def test_health() -> None:
    """Test health check endpoint."""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response)


def test_calculate(data: Dict[str, Any]) -> None:
    """Test calculate endpoint."""
    print("Testing calculate endpoint...")
    response = requests.post(f"{BASE_URL}/api/calculate", json=data)
    print_response(response)


def test_export_purchase_order(data: Dict[str, Any]) -> None:
    """Test purchase order export endpoint."""
    print("Testing export purchase order endpoint...")
    response = requests.post(f"{BASE_URL}/api/export/purchase-order", json=data)
    print_response(response)


def test_export_arrangements(data: Dict[str, Any]) -> None:
    """Test arrangements export endpoint."""
    print("Testing export arrangements endpoint...")
    response = requests.post(f"{BASE_URL}/api/export/arrangements", json=data)
    print_response(response)


def main():
    # Sample data
    test_data = {
        "pieces": [
            {"type": "pine 2x10", "length": 30, "count": 110},
            {"type": "pine 2x10", "length": 10, "count": 110},
            {"type": "pine 2x15", "length": 30, "count": 55},
        ],
        "settings": {
            "wood_types": {
                "pine 2x15": {"unit_length": 480, "price": 60},
                "pine 2x10": {"unit_length": 480, "price": 50},
            },
            "saw_width": 0.3,
            "currency": " ILS",
        },
    }

    # Run tests
    test_health()
    test_calculate(test_data)
    test_export_purchase_order(test_data)
    test_export_arrangements(test_data)


if __name__ == "__main__":
    main()
