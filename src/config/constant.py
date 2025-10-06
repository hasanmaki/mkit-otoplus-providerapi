"""group all constants here."""

from enum import StrEnum


class ResponseMessage(StrEnum):
    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "primitive payload"
    INTERNAL_ERROR = "internal response handler error"
    EMPTY_BODY = "NONE"
