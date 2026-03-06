from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSubredditRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class ListSubredditsRequest(_message.Message):
    __slots__ = ("limit", "offset")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class CreateSubredditRequest(_message.Message):
    __slots__ = ("name", "description", "user_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    user_id: int
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class SubredditResponse(_message.Message):
    __slots__ = ("subreddit_id", "name", "description", "created_by", "created_at")
    SUBREDDIT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    subreddit_id: str
    name: str
    description: str
    created_by: str
    created_at: int
    def __init__(self, subreddit_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_by: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class ListSubredditsResponse(_message.Message):
    __slots__ = ("subreddits",)
    SUBREDDITS_FIELD_NUMBER: _ClassVar[int]
    subreddits: _containers.RepeatedCompositeFieldContainer[SubredditResponse]
    def __init__(self, subreddits: _Optional[_Iterable[_Union[SubredditResponse, _Mapping]]] = ...) -> None: ...
