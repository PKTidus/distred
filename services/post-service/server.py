from concurrent import futures
import grpc
from generated import post_pb2, post_pb2_grpc


class PostService(post_pb2_grpc.PostServiceServicer):
    pass


if __name__ == "__main__":
    print("Post Service listening on port 5001...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
