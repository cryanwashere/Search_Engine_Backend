from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ImageEmbeddingRequest(_message.Message):
    __slots__ = ("image_bytes",)
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    image_bytes: bytes
    def __init__(self, image_bytes: _Optional[bytes] = ...) -> None: ...

class TextEmbeddingRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("values", "dim")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    DIM_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    dim: int
    def __init__(self, values: _Optional[_Iterable[float]] = ..., dim: _Optional[int] = ...) -> None: ...
