from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.meeting import Meeting
from backend.app.schemas.meeting import MeetingCreate, MeetingUpdate

class MeetingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, meeting_id: int) -> Optional[Meeting]:
        return self.db.query(Meeting).filter(Meeting.id == meeting_id).first()

    def get_all(self, organizer_id: Optional[int] = None) -> List[Meeting]:
        query = self.db.query(Meeting)
        if organizer_id:
            query = query.filter(Meeting.organizer_id == organizer_id)
        return query.order_by(Meeting.start_time.asc()).all()

    def create(self, meeting_in: MeetingCreate, organizer_id: int) -> Meeting:
        db_meet = Meeting(**meeting_in.model_dump(), organizer_id=organizer_id)
        self.db.add(db_meet)
        self.db.commit()
        self.db.refresh(db_meet)
        return db_meet

    def update(self, db_meet: Meeting, meeting_update: MeetingUpdate) -> Meeting:
        update_data = meeting_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_meet, key, value)
        self.db.commit()
        self.db.refresh(db_meet)
        return db_meet

    def delete(self, db_meet: Meeting) -> None:
        self.db.delete(db_meet)
        self.db.commit()
