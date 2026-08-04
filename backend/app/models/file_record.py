import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(String(50), nullable=True)  # PDF, DOCX, XLSX, TXT
    extracted_text = Column(Text, nullable=True)   # Stored text for offline RAG vector indexing
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    project = relationship("Project", back_populates="files")
    uploader = relationship("User")
