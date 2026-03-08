from sqlalchemy import Column, Integer, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

    __table_args__ = (
        # Prevents duplicate votes from the same user on the same post
        UniqueConstraint("post_id", "user_id", name="uq_vote_post_user"),
        Index("ix_votes_post_id", "post_id"),
        Index("ix_votes_user_id_post_id", "user_id", "post_id"),
    )

    def __repr__(self):
        return f"<Vote(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, score={self.score})>"
