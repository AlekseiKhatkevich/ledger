from dataclasses import dataclass
from typing import Iterator

from temporalio.client import Schedule


@dataclass
class TemporalSchedule:
    id: str
    schedule: Schedule
    workflow: object

    def __iter__(self) -> Iterator:
        return iter((self.id, self. schedule))
