from concurrent import futures
import grpc
from sqlalchemy import func
from generated import vote_pb2, vote_pb2_grpc
from db import Vote
from config import SessionLocal, init_db


class VoteService(vote_pb2_grpc.VoteServiceServicer):
    def _get_post_score(self, db, post_id):
        result = (
            db.query(
                func.sum(Vote.score).label("score"),
                func.count(Vote.score).filter(Vote.score == 1).label("upvotes"),
                func.count(Vote.score).filter(Vote.score == -1).label("downvotes"),
            )
            .filter(Vote.post_id == post_id)
            .one()
        )
        return result.score or 0, result.upvotes or 0, result.downvotes or 0

    def CastVote(self, request: vote_pb2.CastVoteRequest, context):
        db = SessionLocal()
        try:
            existing = (
                db.query(Vote)
                .filter(
                    Vote.post_id == request.post_id,
                    Vote.user_id == request.user_id,
                )
                .first()
            )
            if existing:
                existing.score = request.score
            else:
                db.add(
                    Vote(
                        post_id=request.post_id,
                        user_id=request.user_id,
                        score=request.score,
                    )
                )
            db.commit()
            new_score, _, _ = self._get_post_score(db, request.post_id)
            return vote_pb2.VoteResponse(success=True, new_score=new_score)
        except Exception as e:
            db.rollback()
            return vote_pb2.VoteResponse(success=False)
        finally:
            db.close()

    def RemoveVote(self, request: vote_pb2.RemoveVoteRequest, context):
        db = SessionLocal()
        try:
            vote = db.query(Vote).filter(Vote.id == request.vote_id).first()
            if not vote:
                return vote_pb2.VoteResponse(success=False)
            db.delete(vote)
            db.commit()
            new_score, _, _ = self._get_post_score(db, request.post_id)
            return vote_pb2.VoteResponse(
                success=True,
                new_score=new_score,
            )
        except Exception as e:
            db.rollback()
            return vote_pb2.VoteResponse(success=False)
        finally:
            db.close()

    def GetScore(self, request: vote_pb2.GetScoreRequest, context):
        db = SessionLocal()
        try:
            score, upvotes, downvotes = self._get_post_score(db, request.post_id)
            return vote_pb2.ScoreResponse(
                score=score, upvotes=upvotes, downvotes=downvotes
            )
        except Exception:
            return vote_pb2.ScoreResponse(score=0, upvotes=0, downvotes=0)
        finally:
            db.close()

    def GetScores(
        self, request: vote_pb2.GetScoresRequest, context
    ) -> vote_pb2.GetScoresResponse:
        db = SessionLocal()
        try:
            results = (
                db.query(
                    Vote.post_id,
                    func.sum(Vote.score).label("score"),
                    func.count(Vote.score).filter(Vote.score == 1).label("upvotes"),
                    func.count(Vote.score).filter(Vote.score == -1).label("downvotes"),
                )
                .filter(Vote.post_id.in_(request.post_ids))
                .group_by(Vote.post_id)
                .all()
            )

            score_map = {r.post_id: r for r in results}
            scores = [
                vote_pb2.ScoreResponse(
                    score=score_map[pid].score if pid in score_map else 0,
                    upvotes=score_map[pid].upvotes if pid in score_map else 0,
                    downvotes=score_map[pid].downvotes if pid in score_map else 0,
                )
                for pid in request.post_ids
            ]
            return vote_pb2.GetScoresResponse(scores=scores)
        except Exception:
            return vote_pb2.GetScoresResponse(scores=[])
        finally:
            db.close()

    def GetUserVote(
        self, request: vote_pb2.GetUserVoteRequest, context
    ) -> vote_pb2.UserVoteResponse:
        db = SessionLocal()
        try:
            vote = (
                db.query(Vote)
                .filter(
                    Vote.post_id == request.post_id,
                    Vote.user_id == request.user_id,
                )
                .first()
            )
            if vote:
                return vote_pb2.UserVoteResponse(voted=True, score=vote.score)
            return vote_pb2.UserVoteResponse(voted=False, score=0)
        except Exception:
            return vote_pb2.UserVoteResponse(voted=False, score=0)
        finally:
            db.close()


if __name__ == "__main__":
    init_db()
    port = "5000"
    print(f"Vote Service listening on port {port}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vote_pb2_grpc.add_VoteServiceServicer_to_server(VoteService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()
