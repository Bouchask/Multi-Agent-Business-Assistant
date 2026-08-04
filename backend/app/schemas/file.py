from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FileRecordBase(BaseModel):
    filename: str
    file_type: Optional[str] = None
    project_id: Optional[int] = None

class FileRecordCreate(FileRecordBase):
    file_path: str
    extracted_text: Optional[str] = None

class FileRecordResponse(FileRecordBase):
    id: int
    file_path: str
    extracted_text: Optional[str] = None
    uploaded_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
