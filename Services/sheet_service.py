from typing import List, Dict
from Models.sheet import Sheet
from Repository.sheet_repository import SheetRepository

class SheetService:
    def __init__(self, sheet_repository: SheetRepository):
        self.sheet_repository = sheet_repository
    
    def create_sheet(self, columns: List[Dict[str, str]]) -> str:
        sheet = Sheet(columns)
        sheet_id = self.sheet_repository.save(sheet)
        return sheet_id