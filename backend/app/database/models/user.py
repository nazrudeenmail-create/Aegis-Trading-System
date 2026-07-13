import hmac
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, Boolean
from app.database.base import Base
from app.database.enums import UserRole

# API key prefix constant
API_KEY_PREFIX = "ats_"


class User(Base):
    """
    User account for API access and authentication.
    
    API Key format: ats_<key_prefix>_<secret>
    - key_prefix: stored in database for fast lookups
    - secret: stored as HMAC-SHA256 hash for security
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # HMAC-SHA256 produces 64 hex chars
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=True),
        default=UserRole.READ_ONLY,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"

    @staticmethod
    def hash_secret(secret: str, hmac_key: bytes = b"ats_internal_hmac_key") -> str:
        """
        Hash a secret using HMAC-SHA256 for secure storage.
        
        Args:
            secret: The secret to hash.
            hmac_key: The HMAC key bytes. Must match auth.py at runtime.
                      Defaults to a fallback for backward compatibility;
                      production deployments should pass settings.SECRET_KEY.encode().
        """
        return hmac.new(
            hmac_key,
            secret.encode(),
            "sha256"
        ).hexdigest()
