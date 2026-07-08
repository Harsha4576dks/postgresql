from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from . import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import date


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    name:str
    salary:int
    
class ExpenseBase(BaseModel):
    date:date
    description:str
    payment_method:str
    amount_spent:int
    user_id:int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency  = Annotated[Session, Depends(get_db)]

@app.post("/users/")
async def create_users(user:UserBase, db:db_dependency):
    db_user = models.User(name=user.name, salary=user.salary)
    db.add(db_user)    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/expenses/")
async def create_expense(expense:ExpenseBase, db:db_dependency):
    db_user = db.query(models.User).filter(models.User.id == expense.user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    
    db_expense = models.Expense(date=expense.date, description=expense.description, payment_method=expense.payment_method, amount_spent=expense.amount_spent, user_id=expense.user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense