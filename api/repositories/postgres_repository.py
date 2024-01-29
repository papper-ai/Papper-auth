from abc import ABC, abstractmethod

from config import settings
from pydantic import EmailStr
from repositories import models
from sqlalchemy import pool, select
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

engine = create_async_engine(settings.database_url, poolclass=pool.AsyncAdaptedQueuePool,
                             pool_size=12, max_overflow=4, pool_pre_ping=True)

Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession
)


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

    async def get(self, email: EmailStr) -> models.User or None:  # works only with PK
        async with self.session as session:
            user = await session.get(models.User, email)
            if user:
                return user
            else:
                return None

    async def get_user_by_uuid(self, uuid: str) -> models.User or None:
        async with self.session as session:
            query = select(models.User).where(models.User.uuid == uuid)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user
