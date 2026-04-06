from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    students = relationship("Student", back_populates="faculty", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("last_name", "first_name", "faculty_id", name="uq_students_full_name_faculty"),
    )

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)

    faculty = relationship("Faculty", back_populates="students")
    grades = relationship("StudentGrade", back_populates="student", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    grades = relationship("StudentGrade", back_populates="subject", cascade="all, delete-orphan")


class StudentGrade(Base):
    __tablename__ = "student_grades"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
        CheckConstraint("grade >= 0 AND grade <= 100", name="ck_grade_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    grade = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
