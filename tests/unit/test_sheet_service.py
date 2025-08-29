import pytest
from unittest.mock import Mock
from Services.sheet_service import SheetService
from Models.sheet import Sheet
from exceptions import NotFoundError


class TestSheetService:
    def test_create_sheet_creates_and_saves_sheet(self):
        mock_repo = Mock()
        mock_repo.save.return_value = "test-sheet-id"
        service = SheetService(mock_repo)
        
        columns = [{"name": "A", "type": "string"}]
        result = service.create_sheet(columns)
        
        assert result == "test-sheet-id"

        # Verify a Sheet was created with the right columns
        saved_sheet = mock_repo.save.call_args[0][0]
        assert isinstance(saved_sheet, Sheet)
        assert saved_sheet.columns == columns

    def test_get_sheet_by_id_raises_not_found_for_missing_sheet(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        service = SheetService(mock_repo)
        
        with pytest.raises(NotFoundError) as exc_info:
            service.get_sheet_by_id("missing-id")
        
        assert "missing-id" in str(exc_info.value)

    def test_get_sheet_by_id_returns_response_for_existing_sheet_with_no_cells(self):
        mock_repo = Mock()
        mock_sheet = Mock()
        mock_sheet.id = "test-id"
        mock_sheet.columns = [{"name": "A", "type": "string"}]
        mock_sheet.cells = {}
        mock_repo.get_by_id.return_value = mock_sheet
        
        service = SheetService(mock_repo)
        response = service.get_sheet_by_id("test-id")
        
        assert response.sheet_id == "test-id"
        assert len(response.columns) == 1
        assert response.columns[0].name == "A"
        assert response.columns[0].type == "string"
        assert response.cells == []
