from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.user import User
from app.database.enums import UserRole

# Define the API Key header scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_current_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates the API key from the header and returns the active User.
    For this MVP, we match the raw api_key string. In production, this should compare hashes.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
        
    user = db.query(User).filter(User.api_key_hash == api_key).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
        
    return user


def require_role(allowed_roles: list[UserRole]):
    """
    Dependency generator for Role-Based Access Control (RBAC).
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
        
    return role_checker
