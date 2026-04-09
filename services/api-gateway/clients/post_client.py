import os

import grpc

from generated import post_pb2, post_pb2_grpc
from middleware import extract_bearer_token
from clients import user_client

POST_SERVICE_HOST = os.getenv("POST_SERVICE_HOST", "localhost")
POST_SERVICE_PORT = os.getenv("POST_SERVICE_PORT", "5000")


def get_channel():
    return grpc.insecure_channel(f"{POST_SERVICE_HOST}:{POST_SERVICE_PORT}")


def get_stub():
    return post_pb2_grpc.PostServiceStub(get_channel())


def create_post(title: str, subreddit: str) -> post_pb2.PostResponse:
    stub = get_stub()
    user = user_client.get_current_user(extract_bearer_token() or "")
    response = stub.CreatePost(
        post_pb2.CreatePostRequest(title=title, subreddit=subreddit, author_id=user.id)
    )
    return response

def get_post(post_id: str) -> post_pb2.PostResponse:
    stub = get_stub()
    user_id = 0
    token = extract_bearer_token()
    if token:
        user = user_client.get_current_user(token)
        user_id = user.id
    response = stub.GetPost(post_pb2.GetPostRequest(post_id=post_id, user_id=user_id))
    return response

def delete_post(post_id: str) -> post_pb2.DeletePostResponse:
    stub = get_stub()
    user = user_client.get_current_user(extract_bearer_token() or "")
    response = stub.DeletePost(
        post_pb2.DeletePostRequest(post_id=post_id, author_id=user.id)
    )
    return response
