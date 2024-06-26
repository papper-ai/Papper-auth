import uuid

from sqladmin import ModelView
from sqlalchemy import DateTime, String, func, Boolean, ForeignKey, Integer, UUID, text
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


def uuid_default():
    return str(uuid.uuid4())


class StrMixin:
    def __str__(self):
        # Получаем словарь всех атрибутов объекта, исключая приватные и защищенные
        fields = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        # Создаем строковое представление
        fields_str = ', '.join(f"{key}={value}" for key, value in fields.items())
        return f"{self.__class__.__name__}({fields_str})"


class Base(DeclarativeBase, StrMixin):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = mapped_column(UUID(as_uuid=False), default=uuid_default, primary_key=True)
    login = mapped_column(String, nullable=False, unique=True)
    password = mapped_column(String, nullable=False)
    has_face_id = mapped_column(Boolean, default=False)

    name = mapped_column(String, nullable=False)
    surname = mapped_column(String, nullable=False)

    used_secret = mapped_column(ForeignKey("secrets.secret"), nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active = mapped_column(Boolean, default=True)
    
    secrets = relationship("Secret", back_populates="users")


class Secret(Base):
    __tablename__ = "secrets"

    secret = mapped_column(UUID(as_uuid=False), default=uuid_default, primary_key=True)

    created_by = mapped_column(String, nullable=False)
    used_by = mapped_column(UUID(as_uuid=False))
    is_used = mapped_column(Boolean, server_default='false')

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="secrets")

    # def __repr__(self):
    #     return f"Secret(secret={self.secret!r}, created_by={self.created_by!r}, used_by={self.used_by!r}, is_used={self.is_used!r}, created_at={self.created_at!r})"
    #


class SecretsAdmin(ModelView, model=Secret):
    column_list = [Secret.secret, Secret.created_by, Secret.used_by, Secret.is_used, Secret.created_at]


class UsersAdmin(ModelView, model=User):
    column_list = [User.user_id, User.login, User.name, User.surname, User.used_secret, User.created_at, User.is_active]

