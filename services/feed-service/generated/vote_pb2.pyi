from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CastVoteRequest(_message.Message):
    __slots__ = ("post_id", "user_id", "value")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    user_id: str
    value: int
    def __init__(self, post_id: _Optional[str] = ..., user_id: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...

class RemoveVoteRequest(_message.Message):
    __slots__ = ("post_id", "user_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    user_id: str
    def __init__(self, post_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetUserVoteRequest(_message.Message):
    __slots__ = ("post_id", "user_id")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    user_id: str
    def __init__(self, post_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("success", "new_score")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    NEW_SCORE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    new_score: int
    def __init__(self, success: bool = ..., new_score: _Optional[int] = ...) -> None: ...

class ScoreResponse(_message.Message):
    __slots__ = ("post_id", "score", "upvotes", "downvotes")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    UPVOTES_FIELD_NUMBER: _ClassVar[int]
    DOWNVOTES_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    score: int
    upvotes: int
    downvotes: int
    def __init__(self, post_id: _Optional[str] = ..., score: _Optional[int] = ..., upvotes: _Optional[int] = ..., downvotes: _Optional[int] = ...) -> None: ...

class PostScore(_message.Message):
    __slots__ = ("post_id", "score", "upvotes", "downvotes")
    POST_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    UPVOTES_FIELD_NUMBER: _ClassVar[int]
    DOWNVOTES_FIELD_NUMBER: _ClassVar[int]
    post_id: str
    score: int
    upvotes: int
    downvotes: int
    def __init__(self, post_id: _Optional[str] = ..., score: _Optional[int] = ..., upvotes: _Optional[int] = ..., downvotes: _Optional[int] = ...) -> None: ...

class UserVoteResponse(_message.Message):
    __slots__ = ("voted", "value")
    VOTED_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    voted: bool
    value: int
    def __init__(self, voted: bool = ..., value: _Optional[int] = ...) -> None: ...
