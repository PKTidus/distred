from concurrent import futures
import threading
import time

import grpc

from generated import health_check_pb2
from generated import health_check_pb2_grpc
import psutil

cpu_percent = 0.0
mem_percent = 0.0


def update_metrics():
    global cpu_percent, mem_percent
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem_percent = psutil.virtual_memory().percent
        time.sleep(1)


class HealthCheckService(health_check_pb2_grpc.HealthCheckServiceServicer):
    def Check(
        self, request: health_check_pb2.HealthCheckRequest, context
    ) -> health_check_pb2.HealthCheckResponse:
        global cpu_percent, mem_percent
        return health_check_pb2.HealthCheckResponse(
            cpu_usage=cpu_percent, memory_usage=mem_percent
        )


if __name__ == "__main__":
    threading.Thread(target=update_metrics, daemon=True).start()
    print("Health Check Service listening on port 5000...")
    port = "5000"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    health_check_pb2_grpc.add_HealthCheckServiceServicer_to_server(
        HealthCheckService(), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
