from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal
from app.models import Student

app = FastAPI(title="Students API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Students service is running"}


@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).options(joinedload(Student.faculty)).all()

    return [
        {
            "id": student.id,
            "last_name": student.last_name,
            "first_name": student.first_name,
            "faculty": student.faculty.name,
        }
        for student in students
    ]
