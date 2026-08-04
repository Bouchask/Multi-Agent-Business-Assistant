from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.file_record import FileRecord
from backend.app.schemas.file import FileRecordCreate

class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, file_id: int) -> Optional[FileRecord]:
        return self.db.query(FileRecord).filter(FileRecord.id == file_id).first()

    def get_all(self, project_id: Optional[int] = None, uploaded_by_id: Optional[int] = None) -> List[FileRecord]:
        query = self.db.query(FileRecord)
        if project_id:
            query = query.filter(FileRecord.project_id == project_id)
        if uploaded_by_id:
            query = query.filter(FileRecord.uploaded_by_id == uploaded_by_id)
        return query.all()

    def create(self, file_in: FileRecordCreate, uploaded_by_id: int) -> FileRecord:
        db_file = FileRecord(**file_in.model_dump(), uploaded_by_id=uploaded_by_id)
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def delete(self, db_file: FileRecord) -> None:
        self.db.delete(db_file)
        self.db.commit()
