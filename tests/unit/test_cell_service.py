import pytest
from unittest.mock import Mock
from Services.cell_service import CellService
from Models.sheet import Sheet, Cell, ColumnType
from exceptions import NotFoundError, ValidationError


class TestCellService:
    def test_set_cell_value_with_valid_regular_value(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "string"}])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)
        result = service.set_cell_value("sheet-id", "A", 1, "hello")
        
        assert result == "Cell value set successfully"
        assert "A_1" in mock_sheet.cells
        assert mock_sheet.cells["A_1"].value == "hello"
        assert mock_sheet.cells["A_1"].is_lookup is False
        mock_repo.save.assert_called_once_with(mock_sheet)

    def test_set_cell_value_raises_not_found_for_missing_sheet(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        
        service = CellService(mock_repo)
        
        with pytest.raises(NotFoundError) as exc_info:
            service.set_cell_value("missing-sheet", "A", 1, "value")
        
        assert "missing-sheet" in str(exc_info.value)

    def test_set_cell_value_raises_not_found_for_missing_column(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "string"}])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)
        
        with pytest.raises(NotFoundError) as exc_info:
            service.set_cell_value("sheet-id", "B", 1, "value")
        
        assert "Column 'B' not found" in str(exc_info.value)

    def test_validate_value_type_with_correct_types(self):
        service = CellService(Mock())
        
        assert service._validate_value_type(True, ColumnType.BOOLEAN) is True
        assert service._validate_value_type(False, ColumnType.BOOLEAN) is True
        assert service._validate_value_type(42, ColumnType.INT) is True
        assert service._validate_value_type(3.14, ColumnType.DOUBLE) is True
        assert service._validate_value_type(5, ColumnType.DOUBLE) is True  # int accepted for double
        assert service._validate_value_type("hello", ColumnType.STRING) is True

    def test_validate_value_type_with_incorrect_types(self):
        service = CellService(Mock())
        
        assert service._validate_value_type("true", ColumnType.BOOLEAN) is False
        assert service._validate_value_type(1, ColumnType.BOOLEAN) is False
        assert service._validate_value_type(3.14, ColumnType.INT) is False
        assert service._validate_value_type("42", ColumnType.INT) is False
        assert service._validate_value_type("3.14", ColumnType.DOUBLE) is False
        assert service._validate_value_type(42, ColumnType.STRING) is False

    def test_set_cell_value_raises_validation_error_for_wrong_type(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "boolean"}])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)
        
        with pytest.raises(ValidationError) as exc_info:
            service.set_cell_value("sheet-id", "A", 1, "not_boolean")
        
        error_msg = str(exc_info.value)
        assert "type mismatch" in error_msg.lower()
        assert "boolean" in error_msg
        assert "str" in error_msg

    def test_parse_lookup_string_with_valid_format(self):
        service = CellService(Mock())
        
        result = service._parse_lookup_string("lookup(A,10)")
        assert result == ("A", 10)
        
        result = service._parse_lookup_string("lookup(B,5)")
        assert result == ("B", 5)
        
        result = service._parse_lookup_string("lookup(abc,1)")
        assert result == ("ABC", 1)  # Should uppercase column

    def test_parse_lookup_string_with_invalid_format(self):
        service = CellService(Mock())
        
        assert service._parse_lookup_string("not_lookup") is None
        assert service._parse_lookup_string("lookup(A)") is None
        assert service._parse_lookup_string("lookup(A,B)") is None
        assert service._parse_lookup_string("LOOKUP(A,1)") is None
        assert service._parse_lookup_string(123) is None

    def test_is_lookup_string(self):
        service = CellService(Mock())
        
        assert service._is_lookup_string("lookup(A,1)") is True
        assert service._is_lookup_string("lookup(B,10)") is True
        assert service._is_lookup_string("regular_value") is False
        assert service._is_lookup_string("LOOKUP(A,1)") is False

    def test_set_lookup_cell_with_valid_types(self):
        mock_repo = Mock()
        mock_sheet = Sheet([
            {"name": "A", "type": "string"},
            {"name": "B", "type": "string"}
        ])
        mock_repo.get_by_id.return_value = mock_sheet
        mock_sheet.cells["A_1"] = Cell(value="hello")
        service = CellService(mock_repo)

        result = service.set_cell_value("sheet-id", "B", 1, "lookup(A,1)")
        
        assert result == "Cell value set successfully"
        assert "B_1" in mock_sheet.cells
        cell = mock_sheet.cells["B_1"]
        assert cell.is_lookup is True
        assert cell.lookup_column == "A"
        assert cell.lookup_row == "1"
        assert cell.value == "lookup(A,1)"

    def test_set_lookup_cell_with_type_mismatch_raises_error(self):
        mock_repo = Mock()
        # Create sheet with string and boolean columns
        mock_sheet = Sheet([
            {"name": "A", "type": "string"},
            {"name": "B", "type": "boolean"}
        ])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)

        with pytest.raises(ValidationError) as exc_info:
            service.set_cell_value("sheet-id", "B", 1, "lookup(A,1)")
        
        error_msg = str(exc_info.value)
        assert "type mismatch" in error_msg.lower()
        assert "string" in error_msg
        assert "boolean" in error_msg

    def test_cycle_detection_size_1_self_reference(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "string"}])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)
        
        with pytest.raises(ValidationError) as exc_info:
            service.set_cell_value("sheet-id", "A", 1, "lookup(A,1)")
        
        assert "cycle of size 1" in str(exc_info.value)

    def test_cycle_detection_size_2(self):
        mock_repo = Mock()
        mock_sheet = Sheet([
            {"name": "A", "type": "string"},
            {"name": "B", "type": "string"}
        ])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)

        service.set_cell_value("sheet-id", "A", 1, "lookup(B,1)")
        
        with pytest.raises(ValidationError) as exc_info:
            service.set_cell_value("sheet-id", "B", 1, "lookup(A,1)")
        
        assert "cycle of size 2" in str(exc_info.value)

    def test_cycle_detection_size_3(self):
        mock_repo = Mock()
        mock_sheet = Sheet([
            {"name": "A", "type": "string"},
            {"name": "B", "type": "string"},
            {"name": "C", "type": "string"}
        ])
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = CellService(mock_repo)
        
        # Set A1 -> B1 -> C1
        service.set_cell_value("sheet-id", "A", 1, "lookup(B,1)")
        service.set_cell_value("sheet-id", "B", 1, "lookup(C,1)")
        
        # Try to set C1 -> A1 - should create cycle of size 3
        with pytest.raises(ValidationError) as exc_info:
            service.set_cell_value("sheet-id", "C", 1, "lookup(A,1)")
        
        assert "cycle of size 3" in str(exc_info.value)

    def test_resolve_cell_value_with_regular_cell(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "string"}])
        mock_sheet.cells["A_1"] = Cell(value="hello")
        
        service = CellService(mock_repo)
        result = service._resolve_cell_value(mock_sheet, "A", 1)
        
        assert result == "hello"

    def test_resolve_cell_value_with_lookup_chain(self):
        mock_repo = Mock()
        mock_sheet = Sheet([
            {"name": "A", "type": "string"},
            {"name": "B", "type": "string"},
            {"name": "C", "type": "string"}
        ])

        mock_sheet.cells["A_1"] = Cell(value="final_value")
        mock_sheet.cells["B_1"] = Cell(
            value="lookup(A,1)",
            is_lookup=True,
            lookup_column="A",
            lookup_row="1"
        )
        
        # C1 looks up B1 (which looks up A1)
        mock_sheet.cells["C_1"] = Cell(
            value="lookup(B,1)",
            is_lookup=True,
            lookup_column="B",
            lookup_row="1"
        )
        
        service = CellService(mock_repo)
        result = service._resolve_cell_value(mock_sheet, "C", 1)
        
        assert result == "final_value"

    def test_resolve_cell_value_for_nonexistent_cell_returns_none(self):
        mock_repo = Mock()
        mock_sheet = Sheet([{"name": "A", "type": "string"}])
        
        service = CellService(mock_repo)
        result = service._resolve_cell_value(mock_sheet, "A", 1)
        
        assert result is None