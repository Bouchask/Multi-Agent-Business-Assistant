from sqlalchemy.orm import Session
from backend.app.repositories.user_repo import UserRepository
from backend.app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from backend.app.auth.security import get_password_hash, verify_password
from backend.app.auth.jwt import create_access_token, create_refresh_token, verify_token
from backend.app.core.exceptions import UnauthorizedException, DuplicateEntityException, NotFoundException

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> TokenResponse:
        existing = self.user_repo.get_by_email(user_data.email)
        if existing:
            raise DuplicateEntityException("User with this email already registered")

        role = self.user_repo.get_or_create_role(user_data.role_name or "EMPLOYEE")
        hashed_pw = get_password_hash(user_data.password)
        new_user = self.user_repo.create_user(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_pw,
            role_id=role.id
        )

        access_token = create_access_token(subject=new_user.id)
        refresh_token = create_refresh_token(subject=new_user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(new_user)
        )

    def login_user(self, credentials: UserLogin) -> TokenResponse:
        user = self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException("Inactive user account")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user)
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = int(payload["sub"])
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User associated with token")

        new_access = create_access_token(subject=user.id)
        new_refresh = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user=UserResponse.model_validate(user)
        )
