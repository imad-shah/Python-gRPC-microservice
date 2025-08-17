from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Book(_message.Message):
    __slots__ = ("checked_out", "due_by")
    CHECKED_OUT_FIELD_NUMBER: _ClassVar[int]
    RETURN_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_FIELD_NUMBER: _ClassVar[int]
    checked_out: bool
    due_by: str
    def __init__(self, checked_out: bool = ..., due_by: _Optional[str] = ..., **kwargs) -> None: ...
