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

        cells = []
        for cell_key, cell in sheet.cells.items():
            column_name, row_str = cell_key.split("_")
            cells.append(CellData(
                column=column_name,
                row=int(row_str),
                value=cell.value
            ))
        
        return GetSheetResponse(
            sheet_id=sheet.id,
            columns=columns,
            cells=cells
        )