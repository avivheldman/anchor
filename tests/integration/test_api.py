import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestSheetAPI:
    def test_create_sheet_with_valid_data(self):
        request_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "int"},
                {"name": "C", "type": "boolean"}
            ]
        }
        
        response = client.post("/sheets", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "sheet_id" in data
        assert data["message"] == "Sheet created successfully"

    def test_create_sheet_with_invalid_column_type(self):
        request_data = {
            "columns": [
                {"name": "A", "type": "invalid_type"}
            ]
        }
        
        response = client.post("/sheets", json=request_data)
        
        assert response.status_code == 422

    def test_get_sheet_returns_created_sheet(self):
        create_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "int"}
            ]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]

        response = client.get(f"/sheets/{sheet_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sheet_id"] == sheet_id
        assert len(data["columns"]) == 2
        assert data["columns"][0]["name"] == "A"
        assert data["columns"][0]["type"] == "string"
        assert data["columns"][1]["name"] == "B"  
        assert data["columns"][1]["type"] == "int"
        assert data["cells"] == []

    def test_get_nonexistent_sheet_returns_404(self):
        response = client.get("/sheets/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCellAPI:
    def test_set_cell_with_valid_data(self):
        create_data = {
            "columns": [{"name": "A", "type": "string"}]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]
        
        # Set a cell value
        cell_data = {
            "column": "A",
            "row": 1,
            "value": "hello"
        }
        response = client.put(f"/cells/sheets/{sheet_id}", json=cell_data)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Cell value set successfully"

    def test_set_cell_with_wrong_type_returns_422(self):
        create_data = {
            "columns": [{"name": "A", "type": "boolean"}]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]

        cell_data = {
            "column": "A", 
            "row": 1,
            "value": "not_boolean"
        }
        response = client.put(f"/cells/sheets/{sheet_id}", json=cell_data)
        
        assert response.status_code == 422
        assert "type mismatch" in response.json()["detail"].lower()

    def test_set_cell_in_nonexistent_sheet_returns_404(self):
        cell_data = {
            "column": "A",
            "row": 1, 
            "value": "test"
        }
        response = client.put("/cells/sheets/nonexistent-id", json=cell_data)
        
        assert response.status_code == 404

    def test_set_cell_in_nonexistent_column_returns_404(self):
        create_data = {
            "columns": [{"name": "A", "type": "string"}]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]

        cell_data = {
            "column": "B",
            "row": 1,
            "value": "test"
        }
        response = client.put(f"/cells/sheets/{sheet_id}", json=cell_data)
        
        assert response.status_code == 404
        assert "column" in response.json()["detail"].lower()


class TestLookupIntegration:
    def test_set_lookup_cell_and_resolve_value(self):
        create_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "string"}
            ]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]

        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "A", "row": 1, "value": "hello"
        })

        response = client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "B", "row": 1, "value": "lookup(A,1)"
        })
        assert response.status_code == 200

        get_response = client.get(f"/sheets/{sheet_id}")
        data = get_response.json()
        
        cell_values = {(cell["column"], cell["row"]): cell["value"] for cell in data["cells"]}
        assert cell_values[("A", 1)] == "hello"
        assert cell_values[("B", 1)] == "hello"  # Should resolve to A1's value

    def test_lookup_type_mismatch_returns_422(self):
        # Create sheet with string and boolean columns
        create_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "boolean"}
            ]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]
        
        response = client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "B", "row": 1, "value": "lookup(A,1)"
        })
        
        assert response.status_code == 422
        assert "type mismatch" in response.json()["detail"].lower()

    def test_cycle_detection_returns_422(self):
        create_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "string"}
            ]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]
        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "A", "row": 1, "value": "lookup(B,1)"
        })
        response = client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "B", "row": 1, "value": "lookup(A,1)"
        })
        
        assert response.status_code == 422
        assert "cycle" in response.json()["detail"].lower()


class TestEndToEndFlow:
    def test_complete_spreadsheet_workflow_with_lookups(self):
        # 1. Create sheet
        create_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "string"},
                {"name": "C", "type": "int"}
            ]
        }
        create_response = client.post("/sheets", json=create_data)
        sheet_id = create_response.json()["sheet_id"]
        
        # 2. Set some cell values and lookups
        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "A", "row": 1, "value": "original"
        })
        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "B", "row": 1, "value": "lookup(A,1)"  # B1 -> A1
        })
        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "C", "row": 1, "value": 42
        })
        
        # 3. Get sheet and verify all data
        response = client.get(f"/sheets/{sheet_id}")
        data = response.json()
        
        assert len(data["cells"]) == 3
        cell_values = {(cell["column"], cell["row"]): cell["value"] for cell in data["cells"]}
        
        assert cell_values[("A", 1)] == "original"
        assert cell_values[("B", 1)] == "original"  # Should resolve lookup
        assert cell_values[("C", 1)] == 42
        
        # 4. Update A1 and verify B1 reflects the change
        client.put(f"/cells/sheets/{sheet_id}", json={
            "column": "A", "row": 1, "value": "updated"
        })
        
        response = client.get(f"/sheets/{sheet_id}")
        data = response.json()
        cell_values = {(cell["column"], cell["row"]): cell["value"] for cell in data["cells"]}
        
        assert cell_values[("A", 1)] == "updated"
        assert cell_values[("B", 1)] == "updated"  # Should reflect the update