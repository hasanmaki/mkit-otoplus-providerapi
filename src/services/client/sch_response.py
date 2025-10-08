from enum import StrEnum


class ResponseMessage(StrEnum):
    """Jenis hasil parsing body response."""

    DICT = "DICT"
    LIST = "LIST"
    TEXT = "TEXT"
    PRIMITIVE = "PRIMITIVE"
    EMPTY = "EMPTY"
    ERROR = "ERROR"
