import grpc
import os

from generated import user_pb2, user_pb2_grpc

USER_SERVICE_HOST = os.getenv("USER_SERVICE_HOST", "localhost")
USER_SERVICE_PORT = os.getenv("USER_SERVICE_PORT", "50051")


def get_channel():
    return grpc.insecure_channel(f"{USER_SERVICE_HOST}:{USER_SERVICE_PORT}")


def get_stub():
    return user_pb2_grpc.UserServiceStub(get_channel())


def grpc_login(username: str, password: str) -> dict:
    stub = get_stub()
    response = stub.Login(user_pb2.LoginRequest(username=username, password=password))
    if response.error:
        return {"error": response.error}
    return {"access_token": response.access_token, "token_type": response.token_type}


def grpc_register(username: str, password: str) -> dict:
    stub = get_stub()
    response = stub.Register(
        user_pb2.RegisterRequest(username=username, password=password)
    )
    if not response.success:
        return {"error": response.error}
    return {"success": True}


def grpc_validate_token(token: str) -> dict:
    stub = get_stub()
    response = stub.ValidateToken(user_pb2.ValidateTokenRequest(token=token))
    return {
        "valid": response.valid,
        "username": response.username,
        "error": response.error,
    }


def grpc_get_current_user(token: str) -> dict:
    stub = get_stub()
    response = stub.GetCurrentUser(user_pb2.GetCurrentUserRequest(token=token))
    if response.error:
        return {"error": response.error}
    return {"id": response.id, "name": response.name, "username": response.username}


def grpc_logout(token: str) -> dict:
    stub = get_stub()
    response = stub.Logout(user_pb2.LogoutRequest(token=token))
    if not response.success:
        return {"error": response.error}
    return {"success": True}
