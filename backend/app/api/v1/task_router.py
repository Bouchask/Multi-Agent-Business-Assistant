from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.app.services.task_service import TaskService
from backend.app.middleware.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
def get_tasks(project_id: Optional[int] = Query(None), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.get_all_tasks(project_id=project_id)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.create_task(data, user)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.get_task_by_id(task_id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.update_task(task_id, data)

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = TaskService(db)
    return service.delete_task(task_id)
