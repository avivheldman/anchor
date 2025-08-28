from typing import Dict, Optional
from Models.sheet import Sheet


class SheetRepository:
    def __init__(self):
        self._sheets: Dict[str, Sheet] = {}
    
    def save(self, sheet: Sheet) -> str:
        self._sheets[sheet.id] = sheet
        return sheet.id
    
    def get_by_id(self, sheet_id: str) -> Optional[Sheet]:
        return self._sheets.get(sheet_id)
    
    def exists(self, sheet_id: str) -> bool:
        return sheet_id in self._sheets
    
    def delete(self, sheet_id: str) -> bool:
        if sheet_id in self._sheets:
            del self._sheets[sheet_id]
            return True
        return False
    
    def get_all_ids(self) -> list:
        return list(self._sheets.keys())