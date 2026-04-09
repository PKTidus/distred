import os
from concurrent import futures
import grpc
from generated import feed_pb2, feed_pb2_grpc
from generated import post_pb2, post_pb2_grpc


POST_SERVICE_HOST = os.getenv("POST_SERVICE_HOST", "localhost")
POST_SERVICE_PORT = os.getenv("POST_SERVICE_PORT", "5000")


class FeedService(feed_pb2_grpc.FeedServiceServicer):
    def _get_post_stub(self):
        channel = grpc.insecure_channel(f"{POST_SERVICE_HOST}:{POST_SERVICE_PORT}")
        return post_pb2_grpc.PostServiceStub(channel)

    def GetHomeFeed(self, request, context):
        try:
            post_stub = self._get_post_stub()
            # Post service's ListPosts can handle home feed by sending empty subreddit
            post_request = post_pb2.ListPostsRequest(
                subreddit="",
                limit=request.limit,
                offset=request.offset,
                user_id=request.user_id
            )
            post_response = post_stub.ListPosts(post_request)
            
            feed_items = []
            for p in post_response.posts:
                feed_items.append(feed_pb2.FeedItem(
                    post_id=p.post_id,
                    title=p.title,
                    subreddit=p.subreddit,
                    username=p.username,
                    score=p.score,
                    user_vote=p.user_vote,
                    created_at=p.created_at
                ))
                
            return feed_pb2.FeedResponse(items=feed_items, total=post_response.total)
        except Exception as e:
            print(f"Error in GetHomeFeed: {e}")
            return feed_pb2.FeedResponse()

    def GetSubredditFeed(self, request, context):
        try:
            post_stub = self._get_post_stub()
            post_request = post_pb2.ListPostsRequest(
                subreddit=request.subreddit,
                limit=request.limit,
                offset=request.offset,
                user_id=request.user_id
            )
            post_response = post_stub.ListPosts(post_request)
            
            feed_items = []
            for p in post_response.posts:
                feed_items.append(feed_pb2.FeedItem(
                    post_id=p.post_id,
                    title=p.title,
                    subreddit=p.subreddit,
                    username=p.username,
                    score=p.score,
                    user_vote=p.user_vote,
                    created_at=p.created_at
                ))
                
            return feed_pb2.FeedResponse(items=feed_items, total=post_response.total)
        except Exception as e:
            print(f"Error in GetSubredditFeed: {e}")
            return feed_pb2.FeedResponse()


if __name__ == "__main__":
    port = os.getenv("PORT", "5000")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    feed_pb2_grpc.add_FeedServiceServicer_to_server(FeedService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print(f"Feed Service started, listening on {port}")
    server.wait_for_termination()
