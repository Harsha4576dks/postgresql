from sqlalchemy import Boolean,Column, ForeignKey, Integer, String, Date
from .database import Base
from sqlalchemy.orm import relationship

class Expense(Base):
    __tablename__='expenses'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    description = Column(String, index=True)
    payment_method = Column(String, index=True)
    amount_spent = Column(Integer, index=True)
    User_id = Column(Integer, ForeignKey("user_data.id"))
    user = relationship("User", back_populates="expenses")

class User(Base):
    __tablename__='user_data'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    salary = Column(Integer, index=True)
    expenses = relationship("Expense", back_populates="user")

    