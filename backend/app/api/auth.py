import hmac
from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.user import User
from app.database.enums import UserRole
from app.core.config import get_settings

# Define the API Key header scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def _get_hmac_secret() -> bytes:
    """
    Return the HMAC key used for API key hashing.
    
    Reads from settings.SECRET_KEY. If the default value is detected,
    logs a warning encouraging a production secret to be set.
    """
    settings = get_settings()
    secret = settings.SECRET_KEY
    if secret == "change-this-in-production":
        import logging
        logging.getLogger(__name__).warning(
            "HMAC authentication is using the default SECRET_KEY. "
            "Set a strong SECRET_KEY in .env for production use."
        )
    return secret.encode()


def get_current_user(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates the API key from the header using HMAC-based authentication.
    
    API Key format: ats_<key_prefix>_<secret>
    - Extracts the prefix for fast database lookup
    - Hashes the provided secret with HMAC-SHA256
    - Uses constant-time comparison to prevent timing attacks
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    
    # Extract prefix from API key (format: ats_<prefix>_<secret>)
    parts = api_key.split("_")
    if len(parts) < 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key format",
        )
    
    key_prefix = "_".join(parts[:2]) if len(parts) >= 3 else parts[1]
    
    # Fast lookup by prefix
    user = db.query(User).filter(User.key_prefix == key_prefix).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    # Hash the incoming secret and compare with stored hash
    _hmac_secret = _get_hmac_secret()
    key_hash = hmac.new(_hmac_secret, api_key.encode(), "sha256").hexdigest()
    if not hmac.compare_digest(user.key_hash, key_hash):
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
