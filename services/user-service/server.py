from concurrent import futures
import grpc
from generated import user_pb2, user_pb2_grpc
from datetime import timedelta

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from config import SessionLocal, init_db
from db import User
from db import TokenBlacklist


class UserService(user_pb2_grpc.UserServiceServicer):
    def _get_db(self):
        return SessionLocal()

    def Register(self, request, context):
        db = self._get_db()
        try:
            existing = db.query(User).filter(User.username == request.username).first()
            if existing:
                return user_pb2.RegisterResponse(
                    success=False, error="Username already exists"
                )
            user = User(
                name=request.name,
                username=request.username,
                hashed_password=get_password_hash(request.password),
            )
            db.add(user)
            db.commit()
            return user_pb2.RegisterResponse(success=True)
        except Exception as e:
            db.rollback()
            return user_pb2.RegisterResponse(success=False, error=str(e))
        finally:
            db.close()

    def Login(self, request, context):
        db = self._get_db()
        try:
            user = db.query(User).filter(User.username == request.username).first()

            if not user:
                return user_pb2.LoginResponse(error="Incorrect username or password")

            if not verify_password(request.password, str(user.hashed_password)):
                return user_pb2.LoginResponse(error="Incorrect username or password")

            access_token = create_access_token(
                data={"sub": user.username},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            return user_pb2.LoginResponse(
                access_token=access_token, token_type="bearer"
            )
        finally:
            db.close()

    # ------------------------------------------------------------------
    # ValidateToken → used by gateway to guard protected routes
    # ------------------------------------------------------------------
    def ValidateToken(self, request, context):
        username = decode_token(request.token)

        if not username:
            return user_pb2.ValidateTokenResponse(
                valid=False, error="Invalid or expired token"
            )
        return user_pb2.ValidateTokenResponse(valid=True, username=username)

    def GetCurrentUser(self, request, context):
        username = decode_token(request.token)
        if not username:
            return user_pb2.UserResponse(error="Invalid or expired token")

        db = self._get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return user_pb2.UserResponse(error="User not found")
            return user_pb2.UserResponse(
                id=int(user.id),  # type: ignore
                username=str(user.username),
            )
        finally:
            db.close()

    def Logout(self, request: user_pb2.LogoutRequest, context):
        token = request.token
        db = self._get_db()
        try:
            blacklisted = TokenBlacklist(token=token)
            db.add(blacklisted)
            db.commit()
        except Exception as e:
            db.rollback()
            return user_pb2.LogoutResponse(success=False, error=str(e))
        finally:
            db.close()

        return user_pb2.LogoutResponse(success=True)


if __name__ == "__main__":
    print("User Service listening on port 5001...")
    port = "5000"
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()
