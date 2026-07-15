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
    phone:str

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

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/students/")
async def create_students(student:StudentBase, db:db_dependency):
    db_student = models.Student(name=student.name, email=student.email, department=student.department, phone=student.phone)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.post("/courses/")
async def create_courses(course:CourseBase, db:db_dependency):
    db_course = models.Course(course_name=course.course_name, duration=course.duration)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.post("/enrollments/")
async def create_enrollments(enrollment:EnrollmentBase, db:db_dependency):
    
    db_student = db.query(models.Student).filter(models.Student.id == enrollment.student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="student not found")
    
    db_course = db.query(models.Course).filter(models.Course.id == enrollment.course_id).first()
    if db_course is None:
        raise HTTPException(status_code=400, detail="course not found")
    
    existing_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == enrollment.student_id, 
        models.Enrollment.course_id == enrollment.course_id).first()
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="This student is already enrolled in this course")
    
    db_enrollment = models.Enrollment(student_id=enrollment.student_id, course_id=enrollment.course_id)
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

@app.post("/attendances/")
async def create_attendance(attendance:AttendanceBase, db:db_dependency):

    db_student = db.query(models.Student).filter(models.Student.id == attendance.student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="student not found")
    
    db_course = db.query(models.Course).filter(models.Course.id == attendance.course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="student is not enrolled in this course")
    
    db_enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == attendance.student_id,
        models.Enrollment.course_id == attendance.course_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="not present")
    
    existing_attendance = db.query(models.Attendance).filter(
    models.Attendance.student_id == attendance.student_id,
    models.Attendance.course_id == attendance.course_id,
    models.Attendance.date == attendance.date).first()
    if existing_attendance:
        raise HTTPException(status_code=404, detail="attendance already marked for this date")
    
    db_attendance = models.Attendance(
    student_id=attendance.student_id,
    course_id=attendance.course_id,
    date=attendance.date,
    status=attendance.status)

    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return (db_attendance)

@app.get("/students/{student_id}")
async def get_student(student_id:int, db:db_dependency ):
    result = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="student not found")
    return result

@app.get("/students/search/")
async def search_by_name(student_name:str, db:db_dependency):
    result = db.query(models.Student).filter(models.Student.name == student_name).all()
    if not result:
         raise HTTPException(status_code=404, detail="student not found")
    return result

@app.get("/courses/{course_id}")
async def get_course(course_id:int, db:db_dependency):
    result = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not result:
         raise HTTPException(status_code=404, detail="course not found")
    return result

@app.get("/course/search/")
async def search_by_name(course_name:str, db:db_dependency):
    result =  db.query(models.Course).filter(models.Course.course_name == course_name).all()
    if not result:
         raise HTTPException(status_code=404, detail="course not found")
    return result

@app.get("/enrollments/search/")
async def search_by_enrollment(student_id:int, db:db_dependency):
    result = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    if not result:
         raise HTTPException(status_code=404, detail="no enrollments found on this id")
    return result

@app.get("/attendances/search/")
async def search_by_specification(student_id:int,course_id:int, db:db_dependency):
    result = db.query(models.Attendance).filter(models.Attendance.student_id == student_id , models.Attendance.course_id == course_id).first()
    if not result:
         raise HTTPException(status_code=404, detail="No attendance found for this student on this course")
    return result

