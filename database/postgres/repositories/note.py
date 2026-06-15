from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import Note
from logic.repositories.notes import BaseNoteRepository


@cache
class NoteRepository(PostgresBaseRepository[Note], BaseNoteRepository, ):
    model = Note
