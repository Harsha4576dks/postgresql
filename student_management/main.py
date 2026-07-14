from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from . import models
from . database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import date

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class StudentBase(BaseModel):
    name:str
    email:str
    department:str
    phone:int

class CourseBase(BaseModel):
    course_name:str
    duration:str

class AttendanceBase(BaseModel):
    student_id:int
    status:str
    date:date
    course_id:int    

class EnrollmentBase(BaseModel):
    student_id:int
    course_id:int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()