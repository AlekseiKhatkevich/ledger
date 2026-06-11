import datetime
from dataclasses import dataclass


@dataclass
class NoteOut:
    id: int
    note: str
    created_at: datetime.datetime
    snippet: str
    score: float
