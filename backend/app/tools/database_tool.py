from typing import Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
from backend.app.db.session import SessionLocal
from backend.app.models.project import Project
from backend.app.models.task import Task

class DatabaseAnalyticsTool:
    @staticmethod
    def get_project_statistics() -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            total_projects = db.query(Project).count()
            total_tasks = db.query(Task).count()
            in_progress_tasks = db.query(Task).filter(Task.status == "IN_PROGRESS").count()
            done_tasks = db.query(Task).filter(Task.status == "DONE").count()
            return {
                "success": True,
                "total_projects": total_projects,
                "total_tasks": total_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": done_tasks
            }
        except Exception as e:
            logger.error(f"Database analytics error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()
