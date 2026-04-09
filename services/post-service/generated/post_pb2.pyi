from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePostRequest(_message.Message):
    __slots__ = ("title", "subreddit", "author_id", "body")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    title: str
    subreddit: str
    author_id: int
    body: str
    def __init__(self, title: _Optional[str] = ..., subreddit: _Optional[str] = ..., author_id: _Optional[int] = ..., body: _Optional[str] = ...) -> None: ...

class GetPostRequest(_message.Message):
    __slots__ = ("post_id", "user_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    user_id: int
    def __init__(self, post_id: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class ListPostsRequest(_message.Message):
    __slots__ = ("subreddit", "limit", "offset", "user_id", "sort")
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    subreddit: str
    limit: int
    offset: int
    user_id: int
    sort: str
    def __init__(self, subreddit: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., user_id: _Optional[int] = ..., sort: _Optional[str] = ...) -> None: ...

class UpdateScoreRequest(_message.Message):
    __slots__ = ("post_id", "new_score")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_SCORE_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    new_score: int
    def __init__(self, post_id: _Optional[str] = ..., new_score: _Optional[int] = ...) -> None: ...

class UpdateScoreResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DeletePostRequest(_message.Message):
    __slots__ = ("post_id", "author_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    author_id: int
    def __init__(self, post_id: _Optional[str] = ..., author_id: _Optional[int] = ...) -> None: ...

class PostResponse(_message.Message):
    __slots__ = ("post_id", "title", "subreddit", "author_id", "username", "score", "user_vote", "created_at", "body", "error")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBREDDIT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    USER_VOTE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    title: str
    subreddit: str
    author_id: int
    username: str
    score: int
    user_vote: int
    created_at: int
    body: str
    error: str
    def __init__(self, post_id: _Optional[str] = ..., title: _Optional[str] = ..., subreddit: _Optional[str] = ..., author_id: _Optional[int] = ..., username: _Optional[str] = ..., score: _Optional[int] = ..., user_vote: _Optional[int] = ..., created_at: _Optional[int] = ..., body: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ListPostsResponse(_message.Message):
    __slots__ = ("posts", "total")
    POSTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    posts: _containers.RepeatedCompositeFieldContainer[PostResponse]
    total: int
    def __init__(self, posts: _Optional[_Iterable[_Union[PostResponse, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class DeletePostResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    def __init__(self, success: bool = ..., error: _Optional[str] = ...) -> None: ...
