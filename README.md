# Wood Calculator

A Python tool for optimizing wood cutting arrangements and calculating costs.

## Installation

```bash
poetry install
```

## Usage

The calculator can be used in three ways:

1. Command Line Interface (CLI)
2. Python API
3. HTTP API Server

### Command Line Usage

The CLI provides several commands:

1. Calculate cutting arrangements:

```bash
woodcut-planner calculate --pieces test-pieces.json --settings test-settings.json
# Or using short options:
woodcut-planner calculate -p test-pieces.json -s test-settings.json
```

2. Export purchase order to CSV:

```bash
woodcut-planner export-purchase-order --pieces test-pieces.json --settings test-settings.json --output purchase-order.csv
# Or using short options:
woodcut-planner export-purchase-order -p test-pieces.json -s test-settings.json -o purchase-order.csv
```

3. Export cutting arrangements to CSV:

```bash
woodcut-planner export-arrangements --pieces test-pieces.json --settings test-settings.json --output arrangements.csv
# Or using short options:
woodcut-planner export-arrangements -p test-pieces.json -s test-settings.json -o arrangements.csv
```

4. Export waste analysis to CSV:

```bash
woodcut-planner export-waste-analysis --pieces test-pieces.json --settings test-settings.json --output waste-analysis.csv
# Or using short options:
woodcut-planner export-waste-analysis -p test-pieces.json -s test-settings.json -o waste-analysis.csv
```

5. Export all data to CSV files:

```bash
woodcut-planner export-all --pieces test-pieces.json --settings test-settings.json --output-dir exports/
# Or using short options:
woodcut-planner export-all -p test-pieces.json -s test-settings.json -o exports/
```

This will create three files in the specified directory:

- `purchase_order.csv`: List of wood types to purchase with quantities and costs
- `arrangements.csv`: Detailed cutting arrangements for each wood unit
- `waste_analysis.csv`: Waste statistics and analysis

### Python API Usage

```python
from woodcut_planner import WoodPiece, Settings, calculate_wood_arrangement

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

### HTTP API Server

The project includes a FastAPI server that provides HTTP endpoints for wood cutting calculations.

#### Starting the Server

```bash
poetry run woodcut-server
```

The server will start on `http://localhost:8000` with auto-reload enabled for development.

#### API Endpoints

1. **Health Check**

   ```http
   GET /api/health
   ```

   Returns server status.

2. **Calculate Arrangements**

   ```http
   POST /api/calculate
   ```

   Calculate optimal wood cutting arrangements.

   Request body:

   ```json
   {
     "pieces": [
       {
         "type": "pine 2x10",
         "length": 30,
         "count": 110
       }
     ],
     "settings": {
       "wood_types": {
         "pine 2x10": {
           "unit_length": 480,
           "price": 50
         }
       },
       "saw_width": 0.3,
       "currency": "USD"
     }
   }
   ```

3. **Export Purchase Order**

   ```http
   POST /api/export/purchase-order
   ```

   Generate a CSV file with the purchase order, including unit lengths, quantities, and costs.

   Uses the same request format as the calculate endpoint.

4. **Export Arrangements**

   ```http
   POST /api/export/arrangements
   ```

   Generate a CSV file with detailed cutting arrangements.

   Uses the same request format as the calculate endpoint.

5. **Export Waste Analysis**

   ```http
   POST /api/export/waste-analysis
   ```

   Generate a CSV file with waste statistics and analysis.

   Uses the same request format as the calculate endpoint.

#### API Documentation

The API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Testing the API

Two test scripts are provided to validate the API functionality:

1. Python Test Script:

   ```bash
   poetry run python test_api.py
   ```

2. Shell Test Script:
   ```bash
   ./test_api.sh
   ```

## Features

- Optimizes wood cutting arrangements to minimize waste
- Accounts for saw width in calculations
- Supports multiple wood types
- Calculates costs per type and total
- Provides detailed arrangement information
- Multiple interfaces: CLI, Python API, and HTTP API
- Export results in CSV format
- Interactive API documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
