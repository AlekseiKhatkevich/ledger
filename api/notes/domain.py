import datetime
import enum
from dataclasses import dataclass


@dataclass
class NoteOut:
    id: int
    note: str
    created_at: str
    snippet: str | None
    score: float | None


class SearchMethod(enum.StrEnum):
    MATCH_ALL = 'match_all'
    MATCH_ANY = 'match_any'
    PHRASE = 'phrase'
