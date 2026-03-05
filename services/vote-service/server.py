from concurrent import futures
import grpc
from generated import vote_pb2, vote_pb2_grpc


class VoteService(vote_pb2_grpc.VoteServiceServicer):
    pass


if __name__ == "__main__":
    print("Vote Service listening on port 5001...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vote_pb2_grpc.add_VoteServiceServicer_to_server(VoteService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()