from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse
from backend.app.services.meeting_service import MeetingService
from backend.app.middleware.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/v1/meetings", tags=["Meetings"])

@router.get("", response_model=List[MeetingResponse])
def get_meetings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = MeetingService(db)
    return service.get_all_meetings(user)

@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(data: MeetingCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = MeetingService(db)
    return service.create_meeting(data, user)

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = MeetingService(db)
    return service.get_meeting_by_id(meeting_id)

@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(meeting_id: int, data: MeetingUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = MeetingService(db)
    return service.update_meeting(meeting_id, data, user)

@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = MeetingService(db)
    return service.delete_meeting(meeting_id, user)
