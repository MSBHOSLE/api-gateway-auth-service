from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)  # admin, service, user
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class RouteRule(Base):
    __tablename__ = "route_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path_prefix: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    target_service_url: Mapped[str] = mapped_column(String(255), nullable=False)
    require_auth: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
