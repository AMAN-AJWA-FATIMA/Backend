from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    # Nullable only to preserve legacy records created before authentication.
    # New registrations always provide an Argon2id hash.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="student",
        server_default="student",
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=True,
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
