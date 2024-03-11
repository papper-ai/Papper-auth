import typing
from abc import ABC, abstractmethod

import uuid

from src.config import settings
from pydantic import EmailStr
from src.repositories import models
from sqlalchemy import pool, select
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

engine = create_async_engine(settings.database_url, poolclass=pool.AsyncAdaptedQueuePool,
                             pool_size=8, max_overflow=4, pool_pre_ping=True)

Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False)


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self, entity):
        raise NotImplementedError

    @abstractmethod
    async def get(self, entity_id):
        raise NotImplementedError


class UserRepository(AbstractRepository):
    def __init__(self):
        self.session = Session()

    async def add(self, entity):
        async with self.session as session:
            async with session.begin():
                session.add(entity)

    async def get(self, email: EmailStr) -> typing.Union[models.User, None]:  # works only with PK
        async with self.session as session:
            user = await session.get(models.User, email)
            return user

    async def get_user_by_login(self, login: str) -> typing.Union[models.User, None]:
        async with self.session as session:
            query = select(models.User).where(models.User.login == login)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user


class SecretRepository(AbstractRepository):
    def __init__(self):
        self.session = Session()

    async def add(self, entity):
        async with self.session as session:
            async with session.begin():
                session.add(entity)

    async def get(self, secret_id) -> typing.Union[models.Secret, None]:
        async with self.session as session:
            async with session.begin():
                secret = await session.get(models.Secret, secret_id)
                return secret
