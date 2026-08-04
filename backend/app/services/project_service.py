from typing import List
from sqlalchemy.orm import Session
from backend.app.repositories.project_repo import ProjectRepository
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.core.exceptions import NotFoundException, ForbiddenException
from backend.app.models.user import User

class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def get_all_projects(self) -> List[ProjectResponse]:
        projects = self.repo.get_all()
        return [ProjectResponse.model_validate(p) for p in projects]

    def get_project_by_id(self, project_id: int) -> ProjectResponse:
        p = self.repo.get_by_id(project_id)
        if not p:
            raise NotFoundException("Project")
        return ProjectResponse.model_validate(p)

    def create_project(self, data: ProjectCreate, user: User) -> ProjectResponse:
        p = self.repo.create(data, owner_id=user.id)
        return ProjectResponse.model_validate(p)

    def update_project(self, project_id: int, data: ProjectUpdate, user: User) -> ProjectResponse:
        p = self.repo.get_by_id(project_id)
        if not p:
            raise NotFoundException("Project")
        if p.owner_id != user.id and user.role.name != "ADMIN":
            raise ForbiddenException("You do not own this project")
        updated = self.repo.update(p, data)
        return ProjectResponse.model_validate(updated)

    def delete_project(self, project_id: int, user: User) -> dict:
        p = self.repo.get_by_id(project_id)
        if not p:
            raise NotFoundException("Project")
        if p.owner_id != user.id and user.role.name != "ADMIN":
            raise ForbiddenException("You do not own this project")
        self.repo.delete(p)
        return {"success": True, "message": f"Project {project_id} deleted successfully"}
