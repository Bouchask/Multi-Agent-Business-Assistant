from typing import List
from sqlalchemy.orm import Session
from backend.app.repositories.meeting_repo import MeetingRepository
from backend.app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse
from backend.app.core.exceptions import NotFoundException, ForbiddenException
from backend.app.models.user import User

class MeetingService:
    def __init__(self, db: Session):
        self.repo = MeetingRepository(db)

    def get_all_meetings(self, user: User) -> List[MeetingResponse]:
        meetings = self.repo.get_all()
        return [MeetingResponse.model_validate(m) for m in meetings]

    def get_meeting_by_id(self, meeting_id: int) -> MeetingResponse:
        m = self.repo.get_by_id(meeting_id)
        if not m:
            raise NotFoundException("Meeting")
        return MeetingResponse.model_validate(m)

    def create_meeting(self, data: MeetingCreate, user: User) -> MeetingResponse:
        m = self.repo.create(data, organizer_id=user.id)
        return MeetingResponse.model_validate(m)

    def update_meeting(self, meeting_id: int, data: MeetingUpdate, user: User) -> MeetingResponse:
        m = self.repo.get_by_id(meeting_id)
        if not m:
            raise NotFoundException("Meeting")
        if m.organizer_id != user.id and user.role.name != "ADMIN":
            raise ForbiddenException("You did not organize this meeting")
        updated = self.repo.update(m, data)
        return MeetingResponse.model_validate(updated)

    def delete_meeting(self, meeting_id: int, user: User) -> dict:
        m = self.repo.get_by_id(meeting_id)
        if not m:
            raise NotFoundException("Meeting")
        if m.organizer_id != user.id and user.role.name != "ADMIN":
            raise ForbiddenException("You did not organize this meeting")
        self.repo.delete(m)
        return {"success": True, "message": f"Meeting {meeting_id} deleted successfully"}
