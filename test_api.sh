#!/bin/bash

# Health check
echo "Testing health check endpoint..."
curl -X GET http://localhost:8000/api/health

# Calculate arrangement
echo -e "\n\nTesting calculate endpoint..."
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "pieces": [
      {"type": "pine 2x10", "length": 30, "count": 110},
      {"type": "pine 2x10", "length": 10, "count": 110},
      {"type": "pine 2x15", "length": 30, "count": 55}
    ],
    "settings": {
      "wood_types": {
        "pine 2x15": {
          "unit_length": 480,
          "price": 60
        },
        "pine 2x10": {
          "unit_length": 480,
          "price": 50
        }
      },
      "saw_width": 0.3,
      "currency": " ILS"
    }
  }' | json_pp

# Export cutting list
echo -e "\n\nTesting export cutting list endpoint..."
curl -X POST http://localhost:8000/api/export/cutting-list \
  -H "Content-Type: application/json" \
  -d '{
    "pieces": [
      {"type": "pine 2x10", "length": 30, "count": 110},
      {"type": "pine 2x10", "length": 10, "count": 110},
      {"type": "pine 2x15", "length": 30, "count": 55}
    ],
    "settings": {
      "wood_types": {
        "pine 2x15": {
          "unit_length": 480,
          "price": 60
        },
        "pine 2x10": {
          "unit_length": 480,
          "price": 50
        }
      },
      "saw_width": 0.3,
      "currency": " ILS"
    }
  }' | json_pp

# Export arrangements
echo -e "\n\nTesting export arrangements endpoint..."
curl -X POST http://localhost:8000/api/export/arrangements \
  -H "Content-Type: application/json" \
  -d '{
    "pieces": [
      {"type": "pine 2x10", "length": 30, "count": 110},
      {"type": "pine 2x10", "length": 10, "count": 110},
      {"type": "pine 2x15", "length": 30, "count": 55}
    ],
    "settings": {
      "wood_types": {
        "pine 2x15": {
          "unit_length": 480,
          "price": 60
        },
        "pine 2x10": {
          "unit_length": 480,
          "price": 50
        }
      },
      "saw_width": 0.3,
      "currency": " ILS"
    }
  }' | json_pp 