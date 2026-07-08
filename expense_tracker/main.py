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
