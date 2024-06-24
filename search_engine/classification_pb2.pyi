from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageClassificationRequest(_message.Message):
    __slots__ = ("image_bytes",)
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    image_bytes: bytes
    def __init__(self, image_bytes: _Optional[bytes] = ...) -> None: ...

class ClassificationResult(_message.Message):
    __slots__ = ("class_name", "class_id", "class_metadata", "confidence")
    CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    CLASS_METADATA_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    class_name: str
    class_id: int
    class_metadata: str
    confidence: float
    def __init__(self, class_name: _Optional[str] = ..., class_id: _Optional[int] = ..., class_metadata: _Optional[str] = ..., confidence: _Optional[float] = ...) -> None: ...

class ClassificationResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ClassificationResult]
    def __init__(self, results: _Optional[_Iterable[_Union[ClassificationResult, _Mapping]]] = ...) -> None: ...
