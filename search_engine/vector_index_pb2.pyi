from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VectorPayload(_message.Message):
    __slots__ = ("text_section_idx", "image_url", "page_url")
    TEXT_SECTION_IDX_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    text_section_idx: int
    image_url: str
    page_url: str
    def __init__(self, text_section_idx: _Optional[int] = ..., image_url: _Optional[str] = ..., page_url: _Optional[str] = ...) -> None: ...

class UpsertRequest(_message.Message):
    __slots__ = ("payload", "nparray_bytes")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    NPARRAY_BYTES_FIELD_NUMBER: _ClassVar[int]
    payload: VectorPayload
    nparray_bytes: bytes
    def __init__(self, payload: _Optional[_Union[VectorPayload, _Mapping]] = ..., nparray_bytes: _Optional[bytes] = ...) -> None: ...

class UpsertResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("nparray_bytes",)
    NPARRAY_BYTES_FIELD_NUMBER: _ClassVar[int]
    nparray_bytes: bytes
    def __init__(self, nparray_bytes: _Optional[bytes] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SearchResult]
    def __init__(self, results: _Optional[_Iterable[_Union[SearchResult, _Mapping]]] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ("payload", "score")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    payload: VectorPayload
    score: float
    def __init__(self, payload: _Optional[_Union[VectorPayload, _Mapping]] = ..., score: _Optional[float] = ...) -> None: ...
