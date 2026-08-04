from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.auth.jwt import oauth2_scheme, verify_token
from backend.app.repositories.user_repo import UserRepository
from backend.app.models.user import User
from backend.app.core.exceptions import UnauthorizedException

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise UnauthorizedException("Authentication token is missing")
    
    payload = verify_token(token, token_type="access")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid user token payload")
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id_str))
    if not user or not user.is_active:
        raise UnauthorizedException("User inactive or not found")
    return user
