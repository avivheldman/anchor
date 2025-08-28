from Repository.sheet_repository import SheetRepository

sheet_repository = SheetRepository()

def get_sheet_repository() -> SheetRepository:
    return sheet_repository