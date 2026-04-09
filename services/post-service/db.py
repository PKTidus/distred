import time
from sqlalchemy import Column, Integer, String, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    subreddit = Column(String(100), nullable=False)
    author_id = Column(Integer, nullable=False)
    created_at = Column(BigInteger, default=lambda: int(time.time()))

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', subreddit='{self.subreddit}')>"
