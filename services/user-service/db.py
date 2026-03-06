from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)

    def __repr__(self):
        return f"<TokenBlacklist(id={self.id}, token='{self.token}')>"
