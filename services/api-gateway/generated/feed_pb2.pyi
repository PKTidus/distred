from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeedRequest(_message.Message):
    __slots__ = ("sort", "subreddit", "limit", "offset", "user_id")
    SORT_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    sort: str
    subreddit: str
    limit: int
    offset: int
    user_id: int
    def __init__(self, sort: _Optional[str] = ..., subreddit: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class FeedItem(_message.Message):
    __slots__ = ("post_id", "title", "subreddit", "username", "score", "user_vote", "created_at", "body")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    USER_VOTE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    title: str
    subreddit: str
    username: str
    score: int
    user_vote: int
    created_at: int
    body: str
    def __init__(self, post_id: _Optional[str] = ..., title: _Optional[str] = ..., subreddit: _Optional[str] = ..., username: _Optional[str] = ..., score: _Optional[int] = ..., user_vote: _Optional[int] = ..., created_at: _Optional[int] = ..., body: _Optional[str] = ...) -> None: ...

class FeedResponse(_message.Message):
    __slots__ = ("items", "total")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[FeedItem]
    total: int
    def __init__(self, items: _Optional[_Iterable[_Union[FeedItem, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...
