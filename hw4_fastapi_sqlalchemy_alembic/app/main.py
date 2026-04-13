from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, router as auth_router
from app.crud import DatabaseManager
from app.database import SessionLocal
from app.schemas import GradeCreate, GradeUpdate, StudentCreate, StudentOut, StudentUpdate

CSV_PATH = Path(__file__).resolve().parents[1] / "students.csv"

app = FastAPI(title="Students API")
app.include_router(auth_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def to_student_out(student) -> StudentOut:
    return StudentOut(
        id=student.id,
        last_name=student.last_name,
        first_name=student.first_name,
        faculty=student.faculty.name,
    )


@app.get("/")
def root():
    return {"message": "Students service is running"}


@app.post("/students", response_model=StudentOut)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    try:
        student = manager.create_student(
            last_name=payload.last_name,
            first_name=payload.first_name,
            faculty_name=payload.faculty_name,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Не удалось создать студента: {exc}") from exc
    return to_student_out(manager.get_student(student.id))


@app.get("/students", response_model=list[StudentOut])
def get_students(db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    return [to_student_out(student) for student in manager.list_students()]


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    student = manager.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return to_student_out(student)


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    student = manager.update_student(student_id, **payload.model_dump(exclude_none=True))
    if student is None:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return to_student_out(student)


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    if not manager.delete_student(student_id):
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"status": "deleted", "student_id": student_id}


@app.post("/students/{student_id}/grades")
def create_or_update_grade(
    student_id: int,
    payload: GradeCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    grade = manager.set_student_grade(
        student_id=student_id,
        subject_name=payload.subject_name,
        grade=payload.grade,
    )
    if grade is None:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"student_id": grade.student_id, "subject_id": grade.subject_id, "grade": grade.grade}


@app.put("/students/{student_id}/grades/{subject_name}")
def update_grade(
    student_id: int,
    subject_name: str,
    payload: GradeUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    grade = manager.update_student_grade(student_id=student_id, subject_name=subject_name, grade=payload.grade)
    if grade is None:
        raise HTTPException(status_code=404, detail="Оценка или предмет не найдены")
    return {"student_id": grade.student_id, "subject_id": grade.subject_id, "grade": grade.grade}


@app.delete("/students/{student_id}/grades/{subject_name}")
def delete_grade(
    student_id: int,
    subject_name: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    if not manager.delete_student_grade(student_id=student_id, subject_name=subject_name):
        raise HTTPException(status_code=404, detail="Оценка или предмет не найдены")
    return {"status": "deleted", "student_id": student_id, "subject": subject_name}


@app.post("/import/csv")
def import_students_from_csv(db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail=f"Файл не найден: {CSV_PATH}")
    return manager.load_from_csv(CSV_PATH)


@app.get("/report/students-by-faculty", response_model=list[StudentOut])
def report_students_by_faculty(
    faculty_name: str = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    students = manager.students_by_faculty(faculty_name)
    return [to_student_out(student) for student in students]


@app.get("/report/unique-courses")
def report_unique_courses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    return {"courses": manager.unique_courses()}


@app.get("/report/low-scores")
def report_low_scores(
    subject_name: str = Query(...),
    threshold: int = Query(30, ge=0, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    rows = manager.students_by_course_with_low_grade(subject_name=subject_name, threshold=threshold)
    return [
        {
            "student_id": row.student.id,
            "last_name": row.student.last_name,
            "first_name": row.student.first_name,
            "faculty": row.student.faculty.name,
            "subject": row.subject.name,
            "grade": row.grade,
        }
        for row in rows
    ]


@app.get("/report/faculty-average")
def report_faculty_average(
    faculty_name: str = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    manager = DatabaseManager(db)
    avg_grade = manager.average_grade_by_faculty(faculty_name)
    if avg_grade is None:
        raise HTTPException(status_code=404, detail="Нет данных по факультету")
    return {"faculty": faculty_name, "average_grade": round(avg_grade, 2)}


@app.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db), _=Depends(get_current_user)):
    manager = DatabaseManager(db)
    return manager.export_to_csv_text()
