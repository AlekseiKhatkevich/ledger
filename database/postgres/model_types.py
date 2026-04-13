from typing import Annotated

from sqlalchemy import BIGINT, Identity
from sqlalchemy.orm import mapped_column


bigint_pk = Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True,)]
