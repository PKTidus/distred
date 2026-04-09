import os
from concurrent import futures
import grpc
from generated import post_pb2, post_pb2_grpc
from generated import user_pb2, user_pb2_grpc
from generated import vote_pb2, vote_pb2_grpc
from config import SessionLocal, init_db
from db import Post


USER_SERVICE_HOST = os.getenv("USER_SERVICE_HOST", "localhost")
USER_SERVICE_PORT = os.getenv("USER_SERVICE_PORT", "5000")
VOTE_SERVICE_HOST = os.getenv("VOTE_SERVICE_HOST", "localhost")
VOTE_SERVICE_PORT = os.getenv("VOTE_SERVICE_PORT", "5000")


class PostService(post_pb2_grpc.PostServiceServicer):
    def _get_db(self):
        return SessionLocal()

    def _get_user_stub(self):
        channel = grpc.insecure_channel(f"{USER_SERVICE_HOST}:{USER_SERVICE_PORT}")
        return user_pb2_grpc.UserServiceStub(channel)

    def _get_vote_stub(self):
        channel = grpc.insecure_channel(f"{VOTE_SERVICE_HOST}:{VOTE_SERVICE_PORT}")
        return vote_pb2_grpc.VoteServiceStub(channel)

    def _get_username(self, author_id):
        try:
            user_stub = self._get_user_stub()
            user_resp = user_stub.GetUser(user_pb2.GetUserRequest(user_id=author_id))
            if not user_resp.error:
                return user_resp.username
        except Exception:
            pass
        return "unknown"

    def CreatePost(self, request, context):
        db = self._get_db()
        try:
            post = Post(
                title=request.title,
                body=request.body,
                subreddit=request.subreddit,
                author_id=request.author_id,
            )
            db.add(post)
            db.commit()
            db.refresh(post)

            username = self._get_username(post.author_id)
            
            # Automatically upvote
            try:
                vote_stub = self._get_vote_stub()
                vote_stub.CastVote(vote_pb2.CastVoteRequest(
                    post_id=str(post.id),
                    user_id=str(post.author_id),
                    value=1
                ))
            except Exception:
                pass

            return post_pb2.PostResponse(
                post_id=str(post.id),
                title=post.title,
                body=post.body or "",
                subreddit=post.subreddit,
                author_id=post.author_id,
                username=username,
                score=1,
                user_vote=1,
                created_at=post.created_at,
            )
        except Exception as e:
            db.rollback()
            return post_pb2.PostResponse(error=str(e))
        finally:
            db.close()

    def GetPost(self, request, context):
        db = self._get_db()
        try:
            post = db.query(Post).filter(Post.id == int(request.post_id)).first()
            if not post:
                return post_pb2.PostResponse(error="Post not found")

            # Fetch additional info
            username = self._get_username(post.author_id)
            score = 0
            user_vote = 0

            # Fetch score
            try:
                vote_stub = self._get_vote_stub()
                score_resp = vote_stub.GetScore(vote_pb2.GetScoreRequest(post_id=request.post_id))
                score = score_resp.score
            except Exception:
                pass

            # Fetch user vote if authenticated
            if request.user_id != 0:
                try:
                    vote_stub = self._get_vote_stub()
                    uv_resp = vote_stub.GetUserVote(vote_pb2.GetUserVoteRequest(
                        post_id=request.post_id, user_id=str(request.user_id)
                    ))
                    user_vote = uv_resp.value
                except Exception:
                    pass

            return post_pb2.PostResponse(
                post_id=str(post.id),
                title=post.title,
                body=post.body or "",
                subreddit=post.subreddit,
                author_id=post.author_id,
                username=username,
                score=score,
                user_vote=user_vote,
                created_at=post.created_at,
            )
        finally:
            db.close()

    def ListPosts(self, request, context):
        db = self._get_db()
        try:
            query = db.query(Post)
            if request.subreddit:
                query = query.filter(Post.subreddit == request.subreddit)

            total = query.count()
            posts = query.order_by(Post.created_at.desc()).offset(request.offset).limit(request.limit).all()

            # Batch fetch scores
            post_ids = [str(p.id) for p in posts]
            scores_dict = {}
            try:
                vote_stub = self._get_vote_stub()
                scores_resp = vote_stub.GetScores(vote_pb2.GetScoresRequest(post_ids=post_ids))
                for ps in scores_resp.scores:
                    scores_dict[ps.post_id] = ps.score
            except Exception:
                pass

            # Cache usernames for this request
            author_usernames = {}

            res_posts = []
            for p in posts:
                p_id_str = str(p.id)
                u_vote = 0
                if request.user_id != 0:
                    try:
                        vote_stub = self._get_vote_stub()
                        uv_resp = vote_stub.GetUserVote(vote_pb2.GetUserVoteRequest(
                            post_id=p_id_str, user_id=str(request.user_id)
                        ))
                        u_vote = uv_resp.value
                    except Exception:
                        pass

                if p.author_id not in author_usernames:
                    author_usernames[p.author_id] = self._get_username(p.author_id)

                res_posts.append(post_pb2.PostResponse(
                    post_id=p_id_str,
                    title=p.title,
                    body=p.body or "",
                    subreddit=p.subreddit,
                    author_id=p.author_id,
                    username=author_usernames[p.author_id],
                    score=scores_dict.get(p_id_str, 0),
                    user_vote=u_vote,
                    created_at=p.created_at,
                ))

            return post_pb2.ListPostsResponse(posts=res_posts, total=total)
        finally:
            db.close()

    def DeletePost(self, request, context):
        db = self._get_db()
        try:
            post = db.query(Post).filter(Post.id == int(request.post_id)).first()
            if not post:
                return post_pb2.DeletePostResponse(success=False, error="Post not found")

            if post.author_id != request.author_id:
                return post_pb2.DeletePostResponse(success=False, error="Unauthorized")

            db.delete(post)
            db.commit()
            return post_pb2.DeletePostResponse(success=True)
        except Exception as e:
            db.rollback()
            return post_pb2.DeletePostResponse(success=False, error=str(e))
        finally:
            db.close()

    def UpdateScore(self, request, context):
        db = self._get_db()
        try:
            post = db.query(Post).filter(Post.id == int(request.post_id)).first()
            if not post:
                return post_pb2.UpdateScoreResponse(success=False)
            
            post.score = request.new_score
            db.commit()
            return post_pb2.UpdateScoreResponse(success=True)
        except Exception:
            db.rollback()
            return post_pb2.UpdateScoreResponse(success=False)
        finally:
            db.close()


if __name__ == "__main__":
    port = os.getenv("PORT", "5000")
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Post Service started, listening on {port}")
    server.wait_for_termination()
