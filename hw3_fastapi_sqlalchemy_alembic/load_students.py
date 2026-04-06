import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Faculty, Student, StudentGrade, Subject


CSV_PATH = Path(__file__).resolve().parent / "students.csv"


def main() -> None:
    session: Session = SessionLocal()

    try:
        session.query(StudentGrade).delete()
        session.query(Student).delete()
        session.query(Subject).delete()
        session.query(Faculty).delete()
        session.commit()

        faculties: dict[str, Faculty] = {}
        subjects: dict[str, Subject] = {}
        students: dict[tuple[str, str, str], Student] = {}
        grades: dict[tuple[int, int], StudentGrade] = {}

        with CSV_PATH.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                last_name = row["Фамилия"].strip()
                first_name = row["Имя"].strip()
                faculty_name = row["Факультет"].strip()
                subject_name = row["Курс"].strip()
                grade = int(row["Оценка"])

                faculty = faculties.get(faculty_name)
                if faculty is None:
                    faculty = Faculty(name=faculty_name)
                    session.add(faculty)
                    session.flush()
                    faculties[faculty_name] = faculty

                student_key = (last_name, first_name, faculty_name)
                student = students.get(student_key)
                if student is None:
                    student = Student(
                        last_name=last_name,
                        first_name=first_name,
                        faculty_id=faculty.id,
                    )
                    session.add(student)
                    session.flush()
                    students[student_key] = student

                subject = subjects.get(subject_name)
                if subject is None:
                    subject = Subject(name=subject_name)
                    session.add(subject)
                    session.flush()
                    subjects[subject_name] = subject

                grade_key = (student.id, subject.id)
                student_grade = grades.get(grade_key)
                if student_grade is None:
                    student_grade = StudentGrade(
                        student_id=student.id,
                        subject_id=subject.id,
                        grade=grade,
                    )
                    session.add(student_grade)
                    grades[grade_key] = student_grade
                else:
                    student_grade.grade = grade

        session.commit()
        print("Данные успешно загружены")

    except Exception as exc:  # noqa: BLE001
        session.rollback()
        print(f"Ошибка при загрузке данных: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
