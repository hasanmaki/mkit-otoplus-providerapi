"""group all constants here."""

from enum import StrEnum


class ResponseMessage(StrEnum):
    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITVE"
    INTERNAL_ERROR = "ERROR"
    EMPTY_BODY = "NONE"
    UNKNOWN = "UNKNOWN"
