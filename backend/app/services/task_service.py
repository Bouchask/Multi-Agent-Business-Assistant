from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.repositories.task_repo import TaskRepository
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.app.core.exceptions import NotFoundException
from backend.app.models.user import User

class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def get_all_tasks(self, project_id: Optional[int] = None) -> List[TaskResponse]:
        tasks = self.repo.get_all(project_id=project_id)
        return [TaskResponse.model_validate(t) for t in tasks]

    def get_task_by_id(self, task_id: int) -> TaskResponse:
        t = self.repo.get_by_id(task_id)
        if not t:
            raise NotFoundException("Task")
        return TaskResponse.model_validate(t)

    def create_task(self, data: TaskCreate, user: User) -> TaskResponse:
        t = self.repo.create(data, default_assignee_id=user.id)
        return TaskResponse.model_validate(t)

    def update_task(self, task_id: int, data: TaskUpdate) -> TaskResponse:
        t = self.repo.get_by_id(task_id)
        if not t:
            raise NotFoundException("Task")
        updated = self.repo.update(t, data)
        return TaskResponse.model_validate(updated)

    def delete_task(self, task_id: int) -> dict:
        t = self.repo.get_by_id(task_id)
        if not t:
            raise NotFoundException("Task")
        self.repo.delete(t)
        return {"success": True, "message": f"Task {task_id} deleted successfully"}
