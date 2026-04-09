import os
from concurrent import futures
import grpc
from sqlalchemy import func, case
from generated import vote_pb2, vote_pb2_grpc
from db import Vote
from config import SessionLocal, init_db


class VoteService(vote_pb2_grpc.VoteServiceServicer):
    def _get_post_score(self, db, post_id):
        try:
            p_id = int(post_id)
        except ValueError:
            return 0, 0, 0

        result = (
            db.query(
                func.sum(Vote.score).label("score"),
                func.sum(case((Vote.score == 1, 1), else_=0)).label("upvotes"),
                func.sum(case((Vote.score == -1, 1), else_=0)).label("downvotes"),
            )
            .filter(Vote.post_id == p_id)
            .one()
        )
        return (
            int(result.score or 0),
            int(result.upvotes or 0),
            int(result.downvotes or 0),
        )

    def CastVote(self, request: vote_pb2.CastVoteRequest, context):
        db = SessionLocal()
        try:
            p_id = int(request.post_id)
            u_id = int(request.user_id)
            val = int(request.value)

            existing = (
                db.query(Vote)
                .filter(
                    Vote.post_id == p_id,
                    Vote.user_id == u_id,
                )
                .first()
            )
            if existing:
                existing.score = val
            else:
                db.add(
                    Vote(
                        post_id=p_id,
                        user_id=u_id,
                        score=val,
                    )
                )
            db.commit()
            new_score, _, _ = self._get_post_score(db, request.post_id)
            return vote_pb2.VoteResponse(success=True, new_score=new_score)
        except Exception as e:
            print(f"Error in CastVote: {e}")
            db.rollback()
            return vote_pb2.VoteResponse(success=False)
        finally:
            db.close()

    def RemoveVote(self, request: vote_pb2.RemoveVoteRequest, context):
        db = SessionLocal()
        try:
            p_id = int(request.post_id)
            u_id = int(request.user_id)

            vote = (
                db.query(Vote)
                .filter(Vote.post_id == p_id, Vote.user_id == u_id)
                .first()
            )

            if vote:
                db.delete(vote)
                db.commit()

            new_score, _, _ = self._get_post_score(db, request.post_id)
            return vote_pb2.VoteResponse(
                success=True,
                new_score=new_score,
            )
        except Exception as e:
            print(f"Error in RemoveVote: {e}")
            db.rollback()
            return vote_pb2.VoteResponse(success=False)
        finally:
            db.close()

    def GetScore(self, request: vote_pb2.GetScoreRequest, context):
        db = SessionLocal()
        try:
            score, upvotes, downvotes = self._get_post_score(db, request.post_id)
            return vote_pb2.ScoreResponse(
                post_id=request.post_id,
                score=score,
                upvotes=upvotes,
                downvotes=downvotes,
            )
        except Exception as e:
            print(f"Error in GetScore: {e}")
            return vote_pb2.ScoreResponse(
                post_id=request.post_id, score=0, upvotes=0, downvotes=0
            )
        finally:
            db.close()

    def GetScores(
        self, request: vote_pb2.GetScoresRequest, context
    ) -> vote_pb2.GetScoresResponse:
        db = SessionLocal()
        try:
            p_ids = [int(pid) for pid in request.post_ids]
            results = (
                db.query(
                    Vote.post_id,
                    func.sum(Vote.score).label("score"),
                    func.sum(case((Vote.score == 1, 1), else_=0)).label("upvotes"),
                    func.sum(case((Vote.score == -1, 1), else_=0)).label("downvotes"),
                )
                .filter(Vote.post_id.in_(p_ids))
                .group_by(Vote.post_id)
                .all()
            )

            score_map = {str(r.post_id): r for r in results}
            scores = []
            for pid in request.post_ids:
                if pid in score_map:
                    r = score_map[pid]
                    scores.append(
                        vote_pb2.PostScore(
                            post_id=pid,
                            score=int(r.score or 0),
                            upvotes=int(r.upvotes or 0),
                            downvotes=int(r.downvotes or 0),
                        )
                    )
                else:
                    scores.append(
                        vote_pb2.PostScore(post_id=pid, score=0, upvotes=0, downvotes=0)
                    )

            return vote_pb2.GetScoresResponse(scores=scores)
        except Exception as e:
            print(f"Error in GetScores: {e}")
            return vote_pb2.GetScoresResponse(scores=[])
        finally:
            db.close()

    def GetUserVote(
        self, request: vote_pb2.GetUserVoteRequest, context
    ) -> vote_pb2.UserVoteResponse:
        db = SessionLocal()
        try:
            p_id = int(request.post_id)
            u_id = int(request.user_id)

            vote = (
                db.query(Vote)
                .filter(
                    Vote.post_id == p_id,
                    Vote.user_id == u_id,
                )
                .first()
            )
            if vote:
                return vote_pb2.UserVoteResponse(voted=True, value=vote.score)
            return vote_pb2.UserVoteResponse(voted=False, value=0)
        except Exception as e:
            print(f"Error in GetUserVote: {e}")
            return vote_pb2.UserVoteResponse(voted=False, value=0)
        finally:
            db.close()


if __name__ == "__main__":
    init_db()
    port = os.getenv("PORT", "5000")
    print(f"Vote Service listening on port {port}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vote_pb2_grpc.add_VoteServiceServicer_to_server(VoteService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()
