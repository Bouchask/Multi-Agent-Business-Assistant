from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class RoleEnum(str, PyEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    GUEST = "GUEST"

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    can_manage_users = Column(Boolean, default=False)
    can_manage_projects = Column(Boolean, default=False)
    can_invoke_agents = Column(Boolean, default=True)

    users = relationship("User", back_populates="role")
