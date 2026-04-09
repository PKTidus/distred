import grpc
import os

from generated import vote_pb2, vote_pb2_grpc

VOTE_SERVICE_HOST = os.getenv("VOTE_SERVICE_HOST", "localhost")
VOTE_SERVICE_PORT = os.getenv("VOTE_SERVICE_PORT", "5000")


def get_channel():
    return grpc.insecure_channel(f"{VOTE_SERVICE_HOST}:{VOTE_SERVICE_PORT}")


def get_stub():
    return vote_pb2_grpc.VoteServiceStub(get_channel())


def cast_vote(post_id: str, user_id: str, value: int) -> vote_pb2.VoteResponse:
    stub = get_stub()
    response = stub.CastVote(
        vote_pb2.CastVoteRequest(post_id=post_id, user_id=user_id, value=value)
    )
    return response


def remove_vote(post_id: str, user_id: str) -> vote_pb2.VoteResponse:
    stub = get_stub()
    response = stub.RemoveVote(
        vote_pb2.RemoveVoteRequest(post_id=post_id, user_id=user_id)
    )
    return response
