import os
import time
from concurrent import futures
import grpc
from generated import subreddit_pb2, subreddit_pb2_grpc
from config import SessionLocal, init_db
from db import Subreddit


class SubredditService(subreddit_pb2_grpc.SubredditServiceServicer):
    def _get_db(self):
        return SessionLocal()

    def GetSubreddit(self, request, context):
        db = self._get_db()
        try:
            subreddit = db.query(Subreddit).filter(Subreddit.name == request.name).first()
            if not subreddit:
                return subreddit_pb2.SubredditResponse(error=f"Subreddit {request.name} not found")

            return subreddit_pb2.SubredditResponse(
                subreddit_id=str(subreddit.id),
                name=subreddit.name,
                description=subreddit.description or "",
                created_by=str(subreddit.created_by),
                created_at=subreddit.created_at,
            )
        finally:
            db.close()

    def ListSubreddits(self, request, context):
        db = self._get_db()
        try:
            query = db.query(Subreddit)
            if request.limit:
                query = query.limit(request.limit)
            if request.offset:
                query = query.offset(request.offset)
            
            subreddits = query.all()
            
            return subreddit_pb2.ListSubredditsResponse(
                subreddits=[
                    subreddit_pb2.SubredditResponse(
                        subreddit_id=str(s.id),
                        name=s.name,
                        description=s.description or "",
                        created_by=str(s.created_by),
                        created_at=s.created_at,
                    ) for s in subreddits
                ]
            )
        finally:
            db.close()

    def CreateSubreddit(self, request, context):
        db = self._get_db()
        try:
            # Check if exists
            existing = db.query(Subreddit).filter(Subreddit.name == request.name).first()
            if existing:
                return subreddit_pb2.SubredditResponse(error=f"Subreddit {request.name} already exists")

            subreddit = Subreddit(
                name=request.name,
                description=request.description,
                created_by=request.user_id,
            )
            db.add(subreddit)
            db.commit()
            db.refresh(subreddit)

            return subreddit_pb2.SubredditResponse(
                subreddit_id=str(subreddit.id),
                name=subreddit.name,
                description=subreddit.description or "",
                created_by=str(subreddit.created_by),
                created_at=subreddit.created_at,
            )
        except Exception as e:
            db.rollback()
            return subreddit_pb2.SubredditResponse(error=str(e))
        finally:
            db.close()


if __name__ == "__main__":
    port = os.getenv("PORT", "50051")
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    subreddit_pb2_grpc.add_SubredditServiceServicer_to_server(
        SubredditService(), server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Subreddit Service started, listening on {port}")
    server.wait_for_termination()
