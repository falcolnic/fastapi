from sqlalchemy import Column, Integer, String, DateTime,Boolean,ForeignKey
from src.database import Base
from sqlalchemy.orm import relationship
import datetime


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True, index= True)
    username = Column(String(50),  nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)   
    provider = Column(String, default="local", nullable=True)
    
    tokens = relationship("TokenTable", back_populates="user")

class TokenTable(Base):
    __tablename__ = 'token'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Corrected table name
    access_toke = Column(String, nullable=False)
    refresh_toke = Column(String, nullable=False)
    status = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    
    user = relationship("User", back_populates="tokens")