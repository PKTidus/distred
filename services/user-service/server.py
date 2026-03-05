from concurrent import futures
import grpc
from generated import user_pb2, user_pb2_grpc


class UserService(user_pb2_grpc.UserServiceServicer):
    pass


if __name__ == "__main__":
    print("User Service listening on port 5001...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
