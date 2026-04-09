import os

import grpc

from generated import subreddit_pb2, subreddit_pb2_grpc
from clients import user_client
from middleware import extract_bearer_token

SUBREDDIT_SERVICE_HOST = os.getenv("SUBREDDIT_SERVICE_HOST", "localhost")
SUBREDDIT_SERVICE_PORT = os.getenv("SUBREDDIT_SERVICE_PORT", "50051")


def get_channel():
    return grpc.insecure_channel(f"{SUBREDDIT_SERVICE_HOST}:{SUBREDDIT_SERVICE_PORT}")


def get_stub():
    return subreddit_pb2_grpc.SubredditServiceStub(get_channel())


def get_subreddits() -> subreddit_pb2.ListSubredditsResponse:
    stub = get_stub()
    response = stub.ListSubreddits(subreddit_pb2.ListSubredditsRequest())
    return response


def create_subreddit(name: str, description: str) -> subreddit_pb2.SubredditResponse:
    stub = get_stub()
    user_id = user_client.get_current_user(extract_bearer_token() or "").id
    response = stub.CreateSubreddit(
        subreddit_pb2.CreateSubredditRequest(
            name=name, description=description, user_id=user_id
        )
    )
    return response


def get_subreddit(name: str) -> subreddit_pb2.SubredditResponse:
    stub = get_stub()
    response = stub.GetSubreddit(subreddit_pb2.GetSubredditRequest(name=name))
    return response
