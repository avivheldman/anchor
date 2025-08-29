from pydantic import BaseModel, field_validator
from typing import Any

class CellBase(BaseModel):
    column: str
    row: int
    value: Any
    
    @field_validator('row')
    @classmethod
    def validate_row(cls, v):
        if v <= 0:
            raise ValueError("Row number must be a positive integer (greater than 0)")
        return v

class SetCellRequest(CellBase):
    pass

class SetCellResponse(BaseModel):
    message: str

class CellData(CellBase):
    pass