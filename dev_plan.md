# Wood Order Calculator - Development Plan

## Project Overview

A calculator that helps optimize wood cutting by efficiently arranging required lengths into standard wood units, considering saw width and providing cost calculations.

## Project Structure

```
wood-calculator/
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── models.py        # Data models and type definitions
│   ├── calculator.py    # Core calculation logic
│   ├── settings.py      # Settings management
│   └── utils.py         # Helper functions
└── tests/
    ├── __init__.py
    ├── test_calculator.py
    └── test_utils.py
```

## Development Steps

### 1. Project Setup ✅

- [x] Initialize Python project with `pyproject.toml`
- [x] Set up virtual environment
- [x] Configure basic dependencies (pydantic for models, pytest for testing)
- [x] Create project structure

### 2. Data Models Implementation (`models.py`) ✅

- [x] Create `WoodType` model for wood specifications
- [x] Create `WoodPiece` model for required lengths
- [x] Create `Settings` model for configuration
- [x] Create `CutPlan` model for output arrangement
- [x] Create `CalculationResult` model for final output

### 3. Settings Management ✅

- [x] Implement settings loading mechanism
- [x] Add validation for wood types and their properties
- [x] Add validation for delimiter (saw width) settings

### 4. Core Calculation Logic (`calculator.py`) ✅

- [x] Implement input validation and preprocessing
- [x] Create function to group pieces by wood type
- [x] Implement the arrangement algorithm:
  - [x] Sort pieces by length (descending)
  - [x] Implement First-Fit Decreasing algorithm for bin packing
  - [x] Account for saw width between cuts
- [x] Calculate required units per wood type
- [x] Calculate costs (per type and total)

### 5. Helper Functions (`utils.py`) 🔄

- [ ] Implement length conversion utilities
- [ ] Create formatting functions for output
- [ ] Add validation helpers

### 6. Testing ⏳

- [ ] Write unit tests for models
- [ ] Write unit tests for calculator logic
- [ ] Write unit tests for arrangement algorithm
- [ ] Add integration tests
- [ ] Add test cases for edge cases:
  - Empty input
  - Single very long piece
  - Many small pieces
  - Mixed piece sizes

### 7. Documentation ✅

- [x] Write README with setup and usage instructions
- [x] Add docstrings to all functions
- [x] Add type hints
- [x] Include example usage

### 8. CLI Interface ✅

- [x] Add CLI interface for command-line usage
- [x] Implement input file reading (JSON/YAML)
- [x] Add output formatting options

### 9. Optimization Improvements ⏳

- [ ] Enhance arrangement algorithm to minimize overall waste
- [ ] Implement preference for longer waste pieces over multiple shorter ones
- [ ] Add waste statistics to output:
  - Total waste length per wood type
  - Waste piece lengths distribution
  - Waste percentage of total wood used
- [ ] Add visual representation of cuts and waste (ASCII diagram)

## Implementation Notes

### Optimization Strategy

The arrangement algorithm should be enhanced to:

1. Minimize the total waste across all units
2. Prefer arrangements that result in fewer, longer waste pieces over multiple shorter ones
3. Consider combining shorter pieces with longer ones to maximize the usability of waste pieces
4. Track and report waste statistics for better decision making

### Data Structures

```python
# Example input format
input_pieces = [
    {"type": "pine 5x10", "length": 250},
    {"type": "pine 5x10", "length": 180},
    # ...
]

# Example settings format
settings = {
    "wood_types": {
        "pine 5x10": {
            "unit_length": 480,
            "price": 50
        }
    },
    "saw_width": 0.3  # cm
}

# Example output format
output = {
    "arrangements": [
        {
            "wood_type": "pine 5x10",
            "units": [
                {
                    "unit_number": 1,
                    "pieces": {
                        "250": 1,
                        "90": 2
                    },
                    "positions": [
                        {"length": 250, "start_position": 0},
                        {"length": 90, "start_position": 250.3},
                        {"length": 90, "start_position": 340.6}
                    ],
                    "waste": 49.4
                }
            ]
        }
    ],
    "total_units": {"pine 5x10": 1},
    "costs": {
        "per_type": {"pine 5x10": 50},
        "total": 50
    },
    "waste_statistics": {
        "total_waste": 49.4,
        "waste_pieces": [49.4],
        "waste_percentage": 10.3
    }
}
```

### Original Prompt

create a simple dev plan for a wood order calculator with the following requirements:

1. input: list of required lengths for a project { "type": str e.g. "pine 5x10", "length": number, "count": number }.
2. types can repeat multiple times
3. All lengths in cm
4. Settings should include an object of known types with their unit length and price per unit. e.g. "pine 5x10": { "unit_length": 480, "price": 50 }
5. Settings should include a delimeter length to compensate for the saw width.
6. calculate and output how long each wood type is needed in net, how many units of each wood type are needed taking into account all the above and arranging the required lenths in the most efficient way possible.
7. output the arrengement that was used to calculate the units - a list of wood units and the lengths that fit into them.
8. output the line and total price.

Write the dev plan in the best way to easily implement it step by step here, to a file named "dev_plan.md"
