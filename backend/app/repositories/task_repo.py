from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.task import Task
from backend.app.schemas.task import TaskCreate, TaskUpdate

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all(self, project_id: Optional[int] = None, assignee_id: Optional[int] = None) -> List[Task]:
        query = self.db.query(Task)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        return query.all()

    def create(self, task_in: TaskCreate, default_assignee_id: int) -> Task:
        data = task_in.model_dump()
        if data.get("assignee_id") is None:
            data["assignee_id"] = default_assignee_id
        db_task = Task(**data)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update(self, db_task: Task, task_update: TaskUpdate) -> Task:
        update_data = task_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        self.db.delete(db_task)
        self.db.commit()
