from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.role import Role

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email: str, full_name: str, hashed_password: str, role_id: int) -> User:
        db_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role_id=role_id,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_or_create_role(self, role_name: str) -> Role:
        role = self.db.query(Role).filter(Role.name == role_name.upper()).first()
        if not role:
            is_admin = (role_name.upper() == "ADMIN")
            is_manager = (role_name.upper() == "MANAGER")
            role = Role(
                name=role_name.upper(),
                description=f"Standard role for {role_name}",
                can_manage_users=is_admin,
                can_manage_projects=is_admin or is_manager,
                can_invoke_agents=True
            )
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
        return role
