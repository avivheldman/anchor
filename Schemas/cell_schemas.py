from pydantic import BaseModel
from typing import Any

class SetCellRequest(BaseModel):
    column: str
    row: int
    value: Any

class SetCellResponse(BaseModel):
    message: str