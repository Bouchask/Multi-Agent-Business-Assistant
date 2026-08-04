from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.services.project_service import ProjectService
from backend.app.middleware.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ProjectService(db)
    return service.get_all_projects()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ProjectService(db)
    return service.create_project(data, user)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ProjectService(db)
    return service.get_project_by_id(project_id)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ProjectService(db)
    return service.update_project(project_id, data, user)

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ProjectService(db)
    return service.delete_project(project_id, user)
