from concurrent import futures
import grpc
from generated import feed_pb2, feed_pb2_grpc


class FeedService(feed_pb2_grpc.FeedServiceServicer):
    pass


if __name__ == "__main__":
    print("Feed Service listening on port 5001...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feed_pb2_grpc.add_FeedServiceServicer_to_server(FeedService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
