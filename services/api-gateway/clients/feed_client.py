import grpc
import os

from generated import feed_pb2, feed_pb2_grpc

FEED_SERVICE_HOST = os.getenv("FEED_SERVICE_HOST", "localhost")
FEED_SERVICE_PORT = os.getenv("FEED_SERVICE_PORT", "50051")


def get_channel():
    return grpc.insecure_channel(f"{FEED_SERVICE_HOST}:{FEED_SERVICE_PORT}")


def get_stub():
    return feed_pb2_grpc.FeedServiceStub(get_channel())


def get_home_feed(
    sort: str, page: int, per_page: int, user_id: int
) -> feed_pb2.FeedResponse:
    stub = get_stub()
    response = stub.GetHomeFeed(
        feed_pb2.FeedRequest(
            subreddit="",
            limit=per_page,
            sort=sort,
            offset=(page - 1) * per_page,
            user_id=user_id,
        )
    )
    return response


def get_subreddit_feed(
    subreddit: str, sort: str, page: int, per_page: int, user_id: int
) -> feed_pb2.FeedResponse:
    stub = get_stub()
    response = stub.GetSubredditFeed(
        feed_pb2.FeedRequest(
            subreddit=subreddit,
            sort=sort,
            limit=per_page,
            offset=(page - 1) * per_page,
            user_id=user_id,
        )
    )
    return response
