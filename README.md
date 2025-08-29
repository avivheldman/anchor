# Spreadsheet API

A FastAPI-based HTTP server that manages spreadsheets with support for different data types and lookup functions with cycle detection.

## Features

- **Sheet Management**: Create and retrieve spreadsheets with typed columns (boolean, int, double, string)
- **Cell Operations**: Set cell values with automatic type validation
- **Lookup Functions**: Reference other cells with `lookup(column, row)` syntax
- **Cycle Detection**: Prevents circular references of any size using DFS algorithm
- **Type Safety**: Ensures lookup targets match expected column types

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd anchor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server with:
```bash
python main.py
```

The server will start on `http://localhost:8000`


## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### Create Sheet
```http
POST /sheets
Content-Type: application/json

{
  "columns": [
    {"name": "A", "type": "string"},
    {"name": "B", "type": "int"},
    {"name": "C", "type": "boolean"}
  ]
}
```

### Get Sheet
```http
GET /sheets/{sheet_id}
```

### Set Cell Value
```http
PUT /cells/sheets/{sheet_id}
Content-Type: application/json

{
  "column": "A",
  "row": 1,
  "value": "hello"
}
```

### Set Lookup Cell
```http
PUT /cells/sheets/{sheet_id}
Content-Type: application/json

{
  "column": "B", 
  "row": 1,
  "value": "lookup(A,1)"
}
```

## Example Usage

1. **Create a sheet:**
```bash
curl -X POST "http://localhost:8000/sheets" \
  -H "Content-Type: application/json" \
  -d '{"columns": [{"name": "A", "type": "string"}, {"name": "B", "type": "string"}]}'
```

2. **Set a cell value:**
```bash
curl -X PUT "http://localhost:8000/cells/sheets/{sheet_id}" \
  -H "Content-Type: application/json" \
  -d '{"column": "A", "row": 1, "value": "hello"}'
```

3. **Set a lookup cell:**
```bash
curl -X PUT "http://localhost:8000/cells/sheets/{sheet_id}" \
  -H "Content-Type: application/json" \
  -d '{"column": "B", "row": 1, "value": "lookup(A,1)"}'
```

4. **Get the sheet:**
```bash
curl "http://localhost:8000/sheets/{sheet_id}"
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit/
```

### Run Integration Tests Only
```bash
pytest tests/integration/
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_cell_service.py -v
```

### Key Test Areas:
- Type validation for all column types
- Lookup function parsing and resolution
- Cycle detection (prevents circular references)
- Error handling and edge cases
- End-to-end API workflows

## Project Structure

```
anchor/
├── Models/
│   └── sheet.py              # Data models (Sheet, Cell, Column)
├── Repository/
│   └── sheet_repository.py   # Data access layer
├── Services/
│   ├── sheet_service.py      # Sheet business logic
│   └── cell_service.py       # Cell operations & lookup logic
├── Routers/
│   ├── sheet_router.py       # Sheet API endpoints
│   └── cell_router.py        # Cell API endpoints
├── Schemas/
│   ├── sheet_schemas.py      # Request/response schemas
│   └── cell_schemas.py       # Cell schemas
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── main.py                   # FastAPI application entry point
├── dependencies.py           # Dependency injection
├── exceptions.py            # Custom exceptions
├── requirements.txt         # Production dependencies
└── README.md               # This file
```

## Architecture Notes

- **Architecture**: Separation of concerns with layers (Router → Service → Repository)
- **Dependency Injection**: FastAPI's built-in DI system
- **In-Memory Storage**: Data is stored in memory (not persisted)
- **Type Safety**: Pydantic models ensure request/response validation
- **Cycle Detection**: DFS algorithm prevents infinite lookup chains

## Lookup Function Details

The lookup function supports the format: `lookup(column, row)`

### Examples:
- `lookup(A,1)` - References cell A1
- `lookup(B,10)` - References cell B10
- Case-insensitive: `lookup(a,1)` becomes `lookup(A,1)`

### Restrictions:
- **Type matching**: Lookup target must match column type
- **No cycles**: Circular references are detected and prevented
- **Valid syntax**: Must match exact `lookup(column,row)` format

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **404**: Sheet or column not found
- **422**: Validation error (type mismatch, cycles, invalid format)
- **500**: Internal server error

## Development

### Adding New Features
1. Add models in `Models/`
2. Add business logic in `Services/`
3. Add API endpoints in `Routers/`
4. Add request/response schemas in `Schemas/`
5. Write tests in `tests/`

## Assumptions Made

- **In-memory storage**: Data is not persisted between server restarts
- **Single-threaded**: No concurrent access considerations
- **Column names**: Expected to be single letters (A, B, C, etc.)
- **Case handling**: Column names normalized to uppercase