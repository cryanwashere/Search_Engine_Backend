from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageRequest(_message.Message):
    __slots__ = ("image_bytes",)
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    image_bytes: bytes
    def __init__(self, image_bytes: _Optional[bytes] = ...) -> None: ...

class TextRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ("image_url", "page_url", "text_section_idx", "text_preview")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    TEXT_SECTION_IDX_FIELD_NUMBER: _ClassVar[int]
    TEXT_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    page_url: str
    text_section_idx: int
    text_preview: str
    def __init__(self, image_url: _Optional[str] = ..., page_url: _Optional[str] = ..., text_section_idx: _Optional[int] = ..., text_preview: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SearchResult]
    def __init__(self, results: _Optional[_Iterable[_Union[SearchResult, _Mapping]]] = ...) -> None: ...
