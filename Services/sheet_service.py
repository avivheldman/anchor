from typing import List, Dict
from Models.sheet import Sheet
from Repository.sheet_repository import SheetRepository
from Schemas.sheet_schemas import GetSheetResponse, ColumnRequest
from Schemas.cell_schemas import CellData
from exceptions import NotFoundError

class SheetService:
    def __init__(self, sheet_repository: SheetRepository):
        self.sheet_repository = sheet_repository
    
    def create_sheet(self, columns: List[Dict[str, str]]) -> str:
        sheet = Sheet(columns)
        sheet_id = self.sheet_repository.save(sheet)
        return sheet_id
    
    def get_sheet_by_id(self, sheet_id: str) -> GetSheetResponse:
        sheet = self.sheet_repository.get_by_id(sheet_id)
        if not sheet:
            raise NotFoundError(f"Sheet with id {sheet_id} not found")

        columns = [ColumnRequest(name=col["name"], type=col["type"]) for col in sheet.columns]

        # Convert cells to CellData format with resolved values
        cell_service = self._get_cell_service()
        
        cells = []
        for cell_key, cell in sheet.cells.items():
            column_name, row_str = cell_key.split("_")
            
            # Resolve the actual value (follows lookup chains)
            resolved_value = cell_service._resolve_cell_value(sheet, column_name, int(row_str))
            
            cells.append(CellData(
                column=column_name,
                row=int(row_str),
                value=resolved_value
            ))
        
        return GetSheetResponse(
            sheet_id=sheet.id,
            columns=columns,
            cells=cells
        )
    
    def _get_cell_service(self):
        """Create a CellService instance to avoid circular imports. couldnt find a better solution :( """
        from Services.cell_service import CellService
        return CellService(self.sheet_repository)