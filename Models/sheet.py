from typing import Dict, List, Any, Optional
import uuid
from enum import Enum
from dataclasses import dataclass
class ColumnType(Enum):
    BOOLEAN ="boolean"
    INT = "int"
    DOUBLE = "double"
    STRING = "string"

@dataclass
class Column:
    name:str
    type:ColumnType

@dataclass
class Cell:
    value:Any
    is_lookup: bool = False
    lookup_column: Optional[str] = None
    lookup_row: Optional[str] = None
    dependents: List[tuple]  = None

    def __post_init__(self):
        if self.dependents is None:
            self.dependents = []

class Sheet:
    def __init__(self, columns: List[Dict[str, str]]):
        self.id = str(uuid.uuid4())
        self.columns = columns
        self.cells = {}
    
    def get_id(self) -> str:
        return self.id
    
    def get_columns(self) -> List[Dict[str, str]]:
        return self.columns