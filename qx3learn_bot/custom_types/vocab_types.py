from typing import TypedDict


class VocabDataType(TypedDict):
    id: int
    name: str
    description: str | None
    number_errors: int
    created_at: str
    wordpairs_count: int
