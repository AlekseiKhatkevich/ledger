from dataclasses import dataclass


@dataclass
class CommonErrorResponse:
    detail: str
    status_code: str