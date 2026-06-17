import datetime
import enum
from dataclasses import dataclass


@dataclass
class NoteOut:
    id: int
    note: str
    created_at: str
    score: float
    snippet: str | None = None


class SearchMethod(enum.StrEnum):
    MATCH_ALL = 'match_all'
    MATCH_ANY = 'match_any'
    PHRASE = 'phrase'
