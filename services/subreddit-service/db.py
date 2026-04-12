import time
from sqlalchemy import Column, Integer, String, BigInteger, Text, Index
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Subreddit(Base):
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(BigInteger, default=lambda: int(time.time()))

    __table_args__ = (
        Index("ix_subreddits_created_by", "created_by"),
    )

    def __repr__(self):
        return f"<Subreddit(id={self.id}, name='{self.name}')>"
