from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.project import Project
from backend.app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_all(self, owner_id: Optional[int] = None) -> List[Project]:
        query = self.db.query(Project)
        if owner_id:
            query = query.filter(Project.owner_id == owner_id)
        return query.all()

    def create(self, project_in: ProjectCreate, owner_id: int) -> Project:
        db_proj = Project(**project_in.model_dump(), owner_id=owner_id)
        self.db.add(db_proj)
        self.db.commit()
        self.db.refresh(db_proj)
        return db_proj

    def update(self, db_proj: Project, project_update: ProjectUpdate) -> Project:
        update_data = project_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_proj, key, value)
        self.db.commit()
        self.db.refresh(db_proj)
        return db_proj

    def delete(self, db_proj: Project) -> None:
        self.db.delete(db_proj)
        self.db.commit()
