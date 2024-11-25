from typing import TypedDict


class WordpairWordType(TypedDict):
    word: str
    transcription: str | None


class WordpairTranslationType(TypedDict):
    translation: str
    transcription: str | None


class WordpairType(TypedDict):
    words: list[WordpairWordType]
    translations: list[WordpairTranslationType]
    annotation: str | None


class WordpairInfoType(TypedDict):
    id: int
    words: list[WordpairWordType]
    translations: list[WordpairTranslationType]
    annotation: str | None
    number_errors: int
