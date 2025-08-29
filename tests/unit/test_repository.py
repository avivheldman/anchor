import pytest
from Repository.sheet_repository import SheetRepository
from Models.sheet import Sheet


class TestSheetRepository:
    def test_save_stores_sheet_and_returns_id(self):
        repo = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        
        returned_id = repo.save(sheet)
        
        assert returned_id == sheet.id
        assert repo.exists(sheet.id)

    def test_get_by_id_returns_existing_sheet(self):
        repo = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        repo.save(sheet)
        retrieved_sheet = repo.get_by_id(sheet.id)
        assert retrieved_sheet is sheet

    def test_get_by_id_returns_none_for_nonexistent_sheet(self):
        repo = SheetRepository()
        result = repo.get_by_id("nonexistent-id")
        assert result is None

    def test_exists_returns_true_for_existing_sheet(self):
        repo = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        repo.save(sheet)
        
        assert repo.exists(sheet.id) is True

    def test_exists_returns_false_for_nonexistent_sheet(self):
        repo = SheetRepository()
        
        assert repo.exists("nonexistent-id") is False

    def test_delete_removes_existing_sheet_and_returns_true(self):
        repo = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        repo.save(sheet)
        
        result = repo.delete(sheet.id)
        
        assert result is True
        assert not repo.exists(sheet.id)
        assert repo.get_by_id(sheet.id) is None

    def test_delete_returns_false_for_nonexistent_sheet(self):
        repo = SheetRepository()
        result = repo.delete("nonexistent-id")
        assert result is False

    def test_get_all_ids_returns_empty_list_when_no_sheets(self):
        repo = SheetRepository()
        result = repo.get_all_ids()
        assert result == []

    def test_get_all_ids_returns_all_stored_sheet_ids(self):
        repo = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        
        sheet1 = Sheet(columns)
        sheet2 = Sheet(columns)
        sheet3 = Sheet(columns)
        
        repo.save(sheet1)
        repo.save(sheet2)
        repo.save(sheet3)
        
        all_ids = repo.get_all_ids()
        
        assert len(all_ids) == 3
        assert sheet1.id in all_ids
        assert sheet2.id in all_ids
        assert sheet3.id in all_ids

    def test_repository_isolation_between_instances(self):
        repo1 = SheetRepository()
        repo2 = SheetRepository()
        columns = [{"name": "A", "type": "string"}]
        sheet = Sheet(columns)
        
        repo1.save(sheet)
        
        assert repo1.exists(sheet.id)
        assert not repo2.exists(sheet.id)