from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePostRequest(_message.Message):
    __slots__ = ("title", "subreddit", "author_id")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    title: str
    subreddit: str
    author_id: str
    def __init__(self, title: _Optional[str] = ..., subreddit: _Optional[str] = ..., author_id: _Optional[str] = ...) -> None: ...

class GetPostRequest(_message.Message):
    __slots__ = ("post_id",)
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    def __init__(self, post_id: _Optional[str] = ...) -> None: ...

class ListPostsRequest(_message.Message):
    __slots__ = ("subreddit", "limit", "offset")
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    subreddit: str
    limit: int
    offset: int
    def __init__(self, subreddit: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class DeletePostRequest(_message.Message):
    __slots__ = ("post_id", "author_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    author_id: str
    def __init__(self, post_id: _Optional[str] = ..., author_id: _Optional[str] = ...) -> None: ...

class PostResponse(_message.Message):
    __slots__ = ("post_id", "title", "subreddit", "author_id", "username", "created_at")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    title: str
    subreddit: str
    author_id: str
    username: str
    created_at: int
    def __init__(self, post_id: _Optional[str] = ..., title: _Optional[str] = ..., subreddit: _Optional[str] = ..., author_id: _Optional[str] = ..., username: _Optional[str] = ..., created_at: _Optional[int] = ...) -> None: ...

class ListPostsResponse(_message.Message):
    __slots__ = ("posts", "total")
    POSTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    posts: _containers.RepeatedCompositeFieldContainer[PostResponse]
    total: int
    def __init__(self, posts: _Optional[_Iterable[_Union[PostResponse, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class DeletePostResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
