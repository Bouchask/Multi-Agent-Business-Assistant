from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.repositories.file_repo import FileRepository
from backend.app.schemas.file import FileRecordCreate, FileRecordResponse
from backend.app.core.exceptions import NotFoundException, ForbiddenException
from backend.app.models.user import User

class FileService:
    def __init__(self, db: Session):
        self.repo = FileRepository(db)

    def get_all_files(self, project_id: Optional[int] = None) -> List[FileRecordResponse]:
        files = self.repo.get_all(project_id=project_id)
        return [FileRecordResponse.model_validate(f) for f in files]

    def record_file_upload(self, data: FileRecordCreate, user: User) -> FileRecordResponse:
        f = self.repo.create(data, uploaded_by_id=user.id)
        return FileRecordResponse.model_validate(f)

    def delete_file(self, file_id: int, user: User) -> dict:
        f = self.repo.get_by_id(file_id)
        if not f:
            raise NotFoundException("File")
        if f.uploaded_by_id != user.id and user.role.name != "ADMIN":
            raise ForbiddenException("You did not upload this file")
        self.repo.delete(f)
        return {"success": True, "message": f"File record {file_id} removed"}
