# Wood Calculator

A Python tool for optimizing wood cutting arrangements and calculating costs.

## Installation

```bash
poetry install
```

## Usage

The calculator takes two JSON files as input:

1. A pieces file containing the list of required wood pieces:

```json
[
  {
    "type": "pine 5x10",
    "length": 250,
    "count": 2
  },
  {
    "type": "pine 5x10",
    "length": 180,
    "count": 1
  }
]
```

2. A settings file containing wood types and configuration:

```json
{
  "wood_types": {
    "pine 5x10": {
      "unit_length": 480,
      "price": 50
    }
  },
  "saw_width": 0.3
}
```

### Command Line Usage

```bash
poetry run python -m wood_calculator.cli pieces.json settings.json
```

### Python API Usage

```python
from wood_calculator import WoodPiece, Settings, calculate_wood_arrangement

pieces = [
    WoodPiece(type="pine 5x10", length=250, count=2),
    WoodPiece(type="pine 5x10", length=180, count=1),
]

settings = Settings(
    wood_types={
        "pine 5x10": {
            "unit_length": 480,
            "price": 50
        }
    },
    saw_width=0.3
)

result = calculate_wood_arrangement(pieces, settings)
print(f"Total cost: ${result.total_cost:.2f}")
```

## Features

- Optimizes wood cutting arrangements to minimize waste
- Accounts for saw width in calculations
- Supports multiple wood types
- Calculates costs per type and total
- Provides detailed arrangement information
- Simple CLI and Python API
