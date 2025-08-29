import pytest
import uuid
from Models.sheet import Sheet, Cell


class TestCell:
    def test_cell_post_init_creates_empty_dependents_when_none(self):
        """Test the actual logic in __post_init__"""
        cell = Cell(value="test", dependents=None)
        assert cell.dependents == []

    def test_cell_post_init_preserves_existing_dependents(self):
        """Test __post_init__ doesn't overwrite existing dependents"""
        existing_deps = [("A", "1"), ("B", "2")]
        cell = Cell(value="test", dependents=existing_deps)
        assert cell.dependents == existing_deps


class TestSheet:
    def test_sheet_generates_unique_uuid_ids(self):
        columns = [{"name": "A", "type": "string"}]
        sheet1 = Sheet(columns)
        sheet2 = Sheet(columns)
        uuid.UUID(sheet1.id)
        uuid.UUID(sheet2.id)
        
        # Should be different
        assert sheet1.id != sheet2.id

    def test_sheet_stores_columns_reference(self):
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        columns.append({"name": "B", "type": "int"})
        assert len(sheet.get_columns()) == 2

    def test_sheet_initializes_empty_cells_dict(self):
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        
        assert sheet.cells == {}