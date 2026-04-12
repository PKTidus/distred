import time
from sqlalchemy import Column, Integer, String, BigInteger, Text, Index
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    subreddit = Column(String(100), nullable=False)
    author_id = Column(Integer, nullable=False)
    score = Column(Integer, default=0)
    created_at = Column(BigInteger, default=lambda: int(time.time()))

    __table_args__ = (
        Index("ix_posts_subreddit_score", "subreddit", "score"),
        Index("ix_posts_subreddit_created_at", "subreddit", "created_at"),
        Index("ix_posts_author_id", "author_id"),
        Index("ix_posts_created_at", "created_at"),
        Index("ix_posts_score", "score"),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', subreddit='{self.subreddit}')>"
