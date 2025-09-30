from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from database import Base

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)  # ← BIGINT
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Income(Base):
    __tablename__ = "income"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)  # ← BIGINT
    amount = Column(Float, nullable=False)
    source = Column(String)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
