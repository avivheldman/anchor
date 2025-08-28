from pydantic import BaseModel
from typing import Any

class CellBase(BaseModel):
    column: str
    row: int
    value: Any

class SetCellRequest(CellBase):
    pass

class SetCellResponse(BaseModel):
    message: str

class CellData(CellBase):
    pass