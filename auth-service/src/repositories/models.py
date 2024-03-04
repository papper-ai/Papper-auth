import uuid
from sqlalchemy import DateTime, String, func, Boolean, ForeignKey, Integer, UUID, text
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


def uuid_default():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = mapped_column(UUID(as_uuid=True), default=uuid_default, primary_key=True)
    login = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)

    name = mapped_column(String, nullable=False)
    surname = mapped_column(String, nullable=False)

    used_secret = mapped_column(ForeignKey("secrets.secret"), nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active = mapped_column(Boolean, default=True)
    
    secrets = relationship("Secret", back_populates="users")


class Secret(Base):
    __tablename__ = "secrets"

    secret = mapped_column(UUID(as_uuid=True), default=uuid_default, primary_key=True)

    created_by = mapped_column(String, nullable=False)
    used_by = mapped_column(UUID(as_uuid=True))
    is_used = mapped_column(Boolean, server_default='false')

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="secrets")
    

