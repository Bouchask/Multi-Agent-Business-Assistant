from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.file import FileRecordCreate, FileRecordResponse
from backend.app.services.file_service import FileService
from backend.app.middleware.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/v1/files", tags=["Files"])

@router.get("", response_model=List[FileRecordResponse])
def get_files(project_id: Optional[int] = Query(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    return service.get_all_files(project_id=project_id)

@router.post("", response_model=FileRecordResponse, status_code=status.HTTP_201_CREATED)
def upload_file_record(data: FileRecordCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    return service.record_file_upload(data, user)

@router.delete("/{file_id}")
def delete_file_record(file_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = FileService(db)
    return service.delete_file(file_id, user)
