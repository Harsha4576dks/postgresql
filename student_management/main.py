from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated,Optional
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

class UpdateStudent(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

class UpdateCourse(BaseModel):
    course_name: Optional[str] = None
    duration: Optional[str] = None

class UpdateEnrollment(BaseModel):
    student_id:Optional[str] = None
    course_id:Optional[str] = None


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

@app.patch("/students/{student_id}")
async def update_student_details(student_id:int, student:UpdateStudent, db:db_dependency):
     db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
     if db_student is None:
         raise HTTPException(status_code=404, detail="student not found")
   
     update_data = student.model_dump(exclude_unset=True)
     print(update_data)
     for key, value in update_data.items():
         setattr(db_student, key, value)

     db.commit()
     db.refresh(db_student)
     return db_student

@app.patch("/courses/{course_id}")
async def update_course_details(course_id:int, course:UpdateCourse, db:db_dependency):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="course not found")
    
    update_data = course.model_dump(exclude_unset=True)
    print(update_data)
    for key, value in update_data.items():
        setattr(db_course, key, value)

        db.commit()
        db.refresh(db_course)
        return db_course
    
@app.patch("/enrollments/{enrollment_id}")
async def update_enrollment_details(enrollment_id:int, enrollment:UpdateEnrollment, db:db_dependency):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="no enrollments found")
    
    update_data = enrollment.model_dump(exclude_unset=True)
    print(update_data)
    for key, value in update_data.items():
        setattr(db_enrollment, key, value)

        db.commit()
        db.refresh(db_enrollment)
        return db_enrollment

@app.delete("/attendance/{attendance_id}")
async def delete_attendance(attendance_id:int, db:db_dependency):
    db_attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="attendance record  not found")
    db.delete(db_attendance)
    db.commit()
    return {"message":"attendance details deleted successfullly", "deleted_attendance":db_attendance.id}

@app.delete("/enrollment/{enrollment_id}")
async def delete_enrollment(enrollment_id:int, db:db_dependency):
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="no enrollments found on this id")
    db.delete(db_enrollment)
    db.commit()
    return {"message":"enrollments on this id is deleted successfully", "deleted_enrollment":db_enrollment.id}

@app.delete("/courses/{course_id}")
async def delete_course(course_id:int, db:db_dependency):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if db_course is None:
        raise HTTPException(status_code=400, detail = "course is not found")
    
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.course_id == course_id).first()
    if db_enrollment is not None:
        raise HTTPException(status_code=400, detail = "delete enrollments for this course first")
    
    db_attendance = db.query(models.Attendance).filter(models.Attendance.course_id == course_id).first()
    if db_attendance is not None:
        raise HTTPException(status_code=404, detail=" delete attendance for this course first")
    
    db.delete(db_course)
    db.commit()
    return {"message":"course deleted succesfully", "deleted_course":db_course.id}

@app.delete("/students/{student_id}")
async def delete_student(student_id:int, db:db_dependency):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="student not found")
    
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).first()
    if db_enrollment is not None:
        raise HTTPException(status_code=400, detail = "delete enrollments for this student first")
    
    db_attendance = db.query(models.Attendance).filter(models.Attendance.sttudent_id == student_id).first()
    if db_attendance is not None:
        raise HTTPException(status_code=404, detail=" delete attendance for this student first")
        
    db.delete(db_student)
    db.commit()
    return {"message":"student deleted successfully", "deleted_student":db_student.id}
