from sqlalchemy import Boolean, String, Column, ForeignKey, Integer, Date
from sqlalchemy .orm import relationship
from .database import Base

class Student(Base):
    __tablename__ = 'student_details'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    phone = Column(String, index=True)
    enrollments = relationship("Enrollment", back_populates="student")

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, index=True)
    duration = Column(String, index=True)
    enrollments = relationship("Enrollment", back_populates="course")

class Enrollment(Base):
    __tablename__ = 'enrollment_details'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_details.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_details.id"))
    status =  Column(String, index=True)
    date =  Column(Date, index=True)
    course_id =  Column(Integer, ForeignKey("courses.id"))