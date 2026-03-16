import uuid

from database.postgres.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func


class User(Base):
    __tablename__ = 'user'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.uuidv7())
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column() # email validation here


    def __repr__(self) -> str:
        return self.name
