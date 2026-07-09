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

@app.get("/users/{user_id}")
async def read_user(user_id:int, db:db_dependency):
    result = db.query(models.User).filter(models.User.id == user_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='user  not found')
    return result

@app.get("/expenses/{expense_id}")
async def read_expense(expense_id:int, db:db_dependency):
    result = db.query(models.Expense).filter(models.Expense.id == expense_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='expenses not found')
    return result

@app.put("/expenses/{expense_id}")
async def update_expense(expense_id:int, expense:ExpenseBase, db:db_dependency):
    db_user = db.query(models.User).filter(models.User.id == expense.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='expense not found')
    
    
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if db_expense is None:
        raise HTTPException(status_code=404, detail='expense not found')
    
    db_expense.date=expense.date, 
    db_expense.description=expense.description,
    db_expense.payment_method=expense.payment_method,
    db_expense.amount_spent=expense.amount_spent,
    db_expense.user_id=expense.user_id

    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id:int, db:db_dependency):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if db_expense is None:
        raise HTTPException(status_code=404, detail='expense does not exist')
    db.delete(db_expense)
    db.commit()
    return {"message":"expenses deleted successfully", "deleted_expense_id":db_expense.id}

@app.delete("/users/{user_id}")
async def delete_user(user_id:int, db:db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='user not found')
    
    db_expense = db.query(models.Expense).filter(models.Expense.user_id == user_id).first()
    if db_expense is not None:
        raise HTTPException(status_code=404, detail='This user has expense delete the expenses first')
    
    db.delete(db_user)
    db.commit()
    return {"message":"user deleted successfully", "deleted_user_id":db_user.id}
