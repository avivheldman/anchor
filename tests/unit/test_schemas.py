import pytest
from pydantic import ValidationError
from Schemas.sheet_schemas import ColumnRequest, CreateSheetRequest


class TestColumnRequest:
    def test_validate_type_accepts_valid_types(self):
        valid_types = ["boolean", "int", "double", "string"]
        
        for valid_type in valid_types:
            column = ColumnRequest(name="A", type=valid_type)
            assert column.type == valid_type

    def test_validate_type_rejects_invalid_types(self):
        invalid_types = ["integer", "bool", "float", "str", "invalid"]
        
        for invalid_type in invalid_types:
            with pytest.raises(ValidationError) as exc_info:
                ColumnRequest(name="A", type=invalid_type)
            error_message = str(exc_info.value)
            assert invalid_type in error_message


class TestCreateSheetRequest:
    def test_create_sheet_request_with_valid_columns(self):
        request_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "int"},
                {"name": "C", "type": "boolean"}
            ]
        }
        
        request = CreateSheetRequest(**request_data)
        assert len(request.columns) == 3
        assert request.columns[0].name == "A"
        assert request.columns[0].type == "string"

    def test_create_sheet_request_validates_column_types(self):
        request_data = {
            "columns": [
                {"name": "A", "type": "string"},
                {"name": "B", "type": "invalid_type"}  # Invalid type
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateSheetRequest(**request_data)
        assert "invalid_type" in str(exc_info.value)