from concurrent import futures
import grpc
from generated import subreddit_pb2, subreddit_pb2_grpc


class SubredditService(subreddit_pb2_grpc.SubredditServiceServicer):
    pass


if __name__ == "__main__":
    print("Subreddit Service listening on port 5001...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    subreddit_pb2_grpc.add_SubredditServiceServicer_to_server(
        SubredditService(), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
