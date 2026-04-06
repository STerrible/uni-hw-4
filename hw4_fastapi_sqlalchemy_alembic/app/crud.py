import csv
import io
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Faculty, Student, StudentGrade, Subject


class DatabaseManager:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_or_create_faculty(self, faculty_name: str) -> Faculty:
        faculty = self.db.query(Faculty).filter(Faculty.name == faculty_name).first()
        if faculty is None:
            faculty = Faculty(name=faculty_name)
            self.db.add(faculty)
            self.db.flush()
        return faculty

    def _get_or_create_subject(self, subject_name: str) -> Subject:
        subject = self.db.query(Subject).filter(Subject.name == subject_name).first()
        if subject is None:
            subject = Subject(name=subject_name)
            self.db.add(subject)
            self.db.flush()
        return subject

    def create_student(self, last_name: str, first_name: str, faculty_name: str) -> Student:
        faculty = self._get_or_create_faculty(faculty_name)
        student = Student(last_name=last_name, first_name=first_name, faculty_id=faculty.id)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_student(self, student_id: int) -> Student | None:
        return (
            self.db.query(Student)
            .options(joinedload(Student.faculty))
            .filter(Student.id == student_id)
            .first()
        )

    def list_students(self) -> list[Student]:
        return self.db.query(Student).options(joinedload(Student.faculty)).all()

    def update_student(self, student_id: int, **kwargs) -> Student | None:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student is None:
            return None

        if kwargs.get("last_name") is not None:
            student.last_name = kwargs["last_name"]
        if kwargs.get("first_name") is not None:
            student.first_name = kwargs["first_name"]
        if kwargs.get("faculty_name") is not None:
            faculty = self._get_or_create_faculty(kwargs["faculty_name"])
            student.faculty_id = faculty.id

        self.db.commit()
        self.db.refresh(student)
        return self.get_student(student.id)

    def delete_student(self, student_id: int) -> bool:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student is None:
            return False
        self.db.delete(student)
        self.db.commit()
        return True

    def set_student_grade(self, student_id: int, subject_name: str, grade: int) -> StudentGrade | None:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student is None:
            return None

        subject = self._get_or_create_subject(subject_name)
        student_grade = (
            self.db.query(StudentGrade)
            .filter(StudentGrade.student_id == student_id, StudentGrade.subject_id == subject.id)
            .first()
        )
        if student_grade is None:
            student_grade = StudentGrade(student_id=student_id, subject_id=subject.id, grade=grade)
            self.db.add(student_grade)
        else:
            student_grade.grade = grade

        self.db.commit()
        self.db.refresh(student_grade)
        return student_grade

    def update_student_grade(self, student_id: int, subject_name: str, grade: int) -> StudentGrade | None:
        subject = self.db.query(Subject).filter(Subject.name == subject_name).first()
        if subject is None:
            return None

        student_grade = (
            self.db.query(StudentGrade)
            .filter(StudentGrade.student_id == student_id, StudentGrade.subject_id == subject.id)
            .first()
        )
        if student_grade is None:
            return None

        student_grade.grade = grade
        self.db.commit()
        self.db.refresh(student_grade)
        return student_grade

    def delete_student_grade(self, student_id: int, subject_name: str) -> bool:
        subject = self.db.query(Subject).filter(Subject.name == subject_name).first()
        if subject is None:
            return False

        student_grade = (
            self.db.query(StudentGrade)
            .filter(StudentGrade.student_id == student_id, StudentGrade.subject_id == subject.id)
            .first()
        )
        if student_grade is None:
            return False

        self.db.delete(student_grade)
        self.db.commit()
        return True

    def students_by_faculty(self, faculty_name: str) -> list[Student]:
        return (
            self.db.query(Student)
            .join(Faculty)
            .options(joinedload(Student.faculty))
            .filter(Faculty.name == faculty_name)
            .all()
        )

    def unique_courses(self) -> list[str]:
        rows = self.db.query(Subject.name).order_by(Subject.name.asc()).all()
        return [row[0] for row in rows]

    def students_by_course_with_low_grade(self, subject_name: str, threshold: int = 30) -> list[StudentGrade]:
        return (
            self.db.query(StudentGrade)
            .join(Subject)
            .join(Student)
            .options(joinedload(StudentGrade.student).joinedload(Student.faculty), joinedload(StudentGrade.subject))
            .filter(Subject.name == subject_name, StudentGrade.grade < threshold)
            .all()
        )

    def average_grade_by_faculty(self, faculty_name: str) -> float | None:
        avg_grade = (
            self.db.query(func.avg(StudentGrade.grade))
            .join(Student, Student.id == StudentGrade.student_id)
            .join(Faculty, Faculty.id == Student.faculty_id)
            .filter(Faculty.name == faculty_name)
            .scalar()
        )
        return float(avg_grade) if avg_grade is not None else None

    def load_from_csv(self, csv_path: Path) -> dict[str, int]:
        self.db.query(StudentGrade).delete()
        self.db.query(Student).delete()
        self.db.query(Subject).delete()
        self.db.query(Faculty).delete()
        self.db.commit()

        faculties: dict[str, Faculty] = {}
        subjects: dict[str, Subject] = {}
        students: dict[tuple[str, str, str], Student] = {}
        grades: dict[tuple[int, int], StudentGrade] = {}

        loaded_rows = 0
        with csv_path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                loaded_rows += 1
                last_name = row["Фамилия"].strip()
                first_name = row["Имя"].strip()
                faculty_name = row["Факультет"].strip()
                subject_name = row["Курс"].strip()
                grade = int(row["Оценка"])

                faculty = faculties.get(faculty_name)
                if faculty is None:
                    faculty = Faculty(name=faculty_name)
                    self.db.add(faculty)
                    self.db.flush()
                    faculties[faculty_name] = faculty

                student_key = (last_name, first_name, faculty_name)
                student = students.get(student_key)
                if student is None:
                    student = Student(last_name=last_name, first_name=first_name, faculty_id=faculty.id)
                    self.db.add(student)
                    self.db.flush()
                    students[student_key] = student

                subject = subjects.get(subject_name)
                if subject is None:
                    subject = Subject(name=subject_name)
                    self.db.add(subject)
                    self.db.flush()
                    subjects[subject_name] = subject

                grade_key = (student.id, subject.id)
                student_grade = grades.get(grade_key)
                if student_grade is None:
                    student_grade = StudentGrade(student_id=student.id, subject_id=subject.id, grade=grade)
                    self.db.add(student_grade)
                    grades[grade_key] = student_grade
                else:
                    student_grade.grade = grade

        self.db.commit()

        students_count = self.db.query(func.count(Student.id)).scalar() or 0
        grades_count = self.db.query(func.count(StudentGrade.id)).scalar() or 0
        return {"rows": loaded_rows, "students": int(students_count), "grades": int(grades_count)}

    def export_to_csv_text(self) -> str:
        rows = (
            self.db.query(StudentGrade)
            .join(Student)
            .join(Faculty)
            .join(Subject)
            .options(joinedload(StudentGrade.student).joinedload(Student.faculty), joinedload(StudentGrade.subject))
            .order_by(Faculty.name, Student.last_name, Student.first_name, Subject.name)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Фамилия", "Имя", "Факультет", "Курс", "Оценка"])
        for student_grade in rows:
            writer.writerow(
                [
                    student_grade.student.last_name,
                    student_grade.student.first_name,
                    student_grade.student.faculty.name,
                    student_grade.subject.name,
                    student_grade.grade,
                ]
            )
        return output.getvalue()
