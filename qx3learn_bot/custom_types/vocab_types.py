from datetime import datetime
from typing import TypedDict

from sqlalchemy import Column


class VocabDataType(TypedDict):
    id: Column[int]
    name: Column[str]
    description: Column[str] | None
    number_errors: Column[int]
    created_at: Column[datetime]
    wordpairs_count: int
