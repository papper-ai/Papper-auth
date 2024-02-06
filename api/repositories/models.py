import uuid
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    email = mapped_column(String, primary_key=True)
    password = mapped_column(String)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    uuid = mapped_column(String, default=str(uuid.uuid4()), nullable=False)
