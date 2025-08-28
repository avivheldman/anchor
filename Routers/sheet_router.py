from fastapi import APIRouter, HTTPException, Depends
from Schemas.sheet_schemas import CreateSheetRequest, CreateSheetResponse
from Services.sheet_service import SheetService
from Repository.sheet_repository import SheetRepository

router = APIRouter(prefix="/sheets", tags=["sheets"])

def get_sheet_service() -> SheetService:
    sheet_repository = SheetRepository()
    return SheetService(sheet_repository)

@router.post("", response_model=CreateSheetResponse)
def create_sheet(
    request: CreateSheetRequest, 
    sheet_service: SheetService = Depends(get_sheet_service)
):
    try:
        # Convert to the format expected by service
        columns_dict = [{"name": col.name, "type": col.type} for col in request.columns]
        
        sheet_id = sheet_service.create_sheet(columns_dict)
        
        return CreateSheetResponse(
            sheet_id=sheet_id,
            message="Sheet created successfully"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))