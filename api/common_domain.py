from dataclasses import dataclass

from pydantic import HttpUrl


@dataclass
class CommonErrorResponse:
    detail: str
    status_code: str


@dataclass
class ProblemDetailResponse:
    type: HttpUrl
    title: str
    detail: str
    instance: HttpUrl
    extra: dict | None
    status_code: int