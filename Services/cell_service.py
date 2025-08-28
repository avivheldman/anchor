from typing import Any, Tuple, Optional
import re
from Repository.sheet_repository import SheetRepository
from Models.sheet import ColumnType, Cell
from exceptions import NotFoundError, ValidationError

class CellService:
    def __init__(self, sheet_repository: SheetRepository):
        self.sheet_repository = sheet_repository
    
    def set_cell_value(self, sheet_id: str, column: str, row: int, value: Any) -> str:
        sheet = self._get_sheet_or_raise(sheet_id)
        column_def = self._get_column_definition(sheet, column)
        
        if self._is_lookup_string(value):
            self._set_lookup_cell(sheet, column, row, value, column_def)
        else:
            self._set_regular_cell(sheet, column, row, value, column_def)

        self.sheet_repository.save(sheet)
        return "Cell value set successfully"
    
    def _get_sheet_or_raise(self, sheet_id: str):
        sheet = self.sheet_repository.get_by_id(sheet_id)
        if not sheet:
            raise NotFoundError(f"Sheet with id {sheet_id} not found")
        return sheet
    
    def _get_column_definition(self, sheet, column: str):
        for col in sheet.columns:
            if col["name"] == column:
                return col
        raise NotFoundError(f"Column '{column}' not found in sheet")
    
    def _set_regular_cell(self, sheet, column: str, row: int, value: Any, column_def: dict):
        expected_type = ColumnType(column_def["type"])
        if not self._validate_value_type(value, expected_type):
            raise ValidationError(f"Value type mismatch. Expected {expected_type.value}, got {type(value).__name__}")
        
        cell_key = f"{column}_{row}"
        sheet.cells[cell_key] = Cell(value=value)
    
    def _set_lookup_cell(self, sheet, column: str, row: int, value: str, column_def: dict):
        lookup_column, lookup_row = self._parse_lookup_string(value)
        lookup_column_def = self._get_column_definition(sheet, lookup_column)
        self._validate_lookup_types(lookup_column_def, column_def, lookup_column, column)

        cell_key = f"{column}_{row}"
        sheet.cells[cell_key] = Cell(
            value=value,
            is_lookup=True,
            lookup_column=lookup_column,
            lookup_row=str(lookup_row)
        )

        self._add_dependency(sheet, lookup_column, lookup_row, column, row)
    
    def _validate_lookup_types(self, lookup_column_def: dict, target_column_def: dict, lookup_column: str, target_column: str):
        lookup_type = ColumnType(lookup_column_def["type"])
        expected_type = ColumnType(target_column_def["type"])
        if lookup_type != expected_type:
            raise ValidationError(
                f"Type mismatch in lookup. Target column '{lookup_column}' is {lookup_type.value}, "
                f"but current column '{target_column}' expects {expected_type.value}"
            )
    
    def _add_dependency(self, sheet, lookup_column: str, lookup_row: int, dependent_column: str, dependent_row: int):
        target_key = f"{lookup_column}_{lookup_row}"
        if target_key in sheet.cells:
            sheet.cells[target_key].dependents.append((dependent_column, dependent_row))
    
    def _parse_lookup_string(self, value: str) -> Optional[Tuple[str, int]]:
        if not isinstance(value, str):
            return None
        
        pattern = r'^lookup\(([A-Za-z]+),(\d+)\)$'
        match = re.match(pattern, value.strip())
        
        if match:
            column = match.group(1).upper()
            row = int(match.group(2))
            return (column, row)
        
        return None
    
    def _is_lookup_string(self, value: str) -> bool:
        return self._parse_lookup_string(value) is not None
    
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