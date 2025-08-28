from typing import Any
from Repository.sheet_repository import SheetRepository
from Models.sheet import ColumnType, Cell

class CellService:
    def __init__(self, sheet_repository: SheetRepository):
        self.sheet_repository = sheet_repository
    
    def set_cell_value(self, sheet_id: str, column: str, row: int, value: Any) -> str:
        sheet = self.sheet_repository.get_by_id(sheet_id)
        print(self.sheet_repository._sheets)
        print(sheet)
        if not sheet:
            raise ValueError(f"Sheet with id {sheet_id} not found")

        column_def = None
        for col in sheet.columns:
            if col["name"] == column:
                column_def = col
                break
        
        if not column_def:
            raise ValueError(f"Column '{column}' not found in sheet")
        
        # Validate value type
        expected_type = ColumnType(column_def["type"])
        if not self._validate_value_type(value, expected_type):
            raise ValueError(f"Value type mismatch. Expected {expected_type.value}, got {type(value).__name__}")

        # Set the cell value
        cell_key = f"{column}_{row}"
        sheet.cells[cell_key] = Cell(value=value)

        self.sheet_repository.save(sheet)
        
        return "Cell value set successfully"
    
    def _validate_value_type(self, value: Any, expected_type: ColumnType) -> bool:
        if expected_type == ColumnType.BOOLEAN:
            return isinstance(value, bool)
        elif expected_type == ColumnType.INT:
            return isinstance(value, int)
        elif expected_type == ColumnType.DOUBLE:
            return isinstance(value, (int, float))
        elif expected_type == ColumnType.STRING:
            return isinstance(value, str)
        return False