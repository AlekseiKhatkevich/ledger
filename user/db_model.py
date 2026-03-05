import uuid

from database.postgres.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(30))


    def __repr__(self) -> str:
        return self.name
