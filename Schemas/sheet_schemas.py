from pydantic import BaseModel, field_validator
from typing import List, Any, Union
from Models.sheet import ColumnType

class ColumnRequest(BaseModel):
    name: str
    type: str
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = {ct.value for ct in ColumnType}
        if v not in valid_types:
            raise ValueError(f"Invalid column type: {v}. Valid types: {list(valid_types)}")
        return v

class CreateSheetRequest(BaseModel):
    columns: List[ColumnRequest]

class CreateSheetResponse(BaseModel):
    sheet_id: str
    message: str