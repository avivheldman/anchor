from fastapi import APIRouter, HTTPException, Depends
from Schemas.cell_schemas import SetCellRequest, SetCellResponse
from Services.cell_service import CellService
from Repository.sheet_repository import SheetRepository
from dependencies import get_sheet_repository

router = APIRouter(prefix="/cells", tags=["cells"])

def get_cell_service(repo: SheetRepository = Depends(get_sheet_repository)) -> CellService:
    return CellService(repo)


@router.put("/sheets/{sheet_id}", response_model=SetCellResponse)
def set_cell(
        sheet_id: str,
        request: SetCellRequest,
        cell_service: CellService = Depends(get_cell_service)
):
    try:
        message = cell_service.set_cell_value(
            sheet_id=sheet_id,
            column=request.column,
            row=request.row,
            value=request.value
        )
        
        return SetCellResponse(message=message)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))