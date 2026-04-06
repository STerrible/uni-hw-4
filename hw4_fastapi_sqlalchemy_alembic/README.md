# Домашнее задание 4 — REST API CRUD на FastAPI

Проект реализует CRUD-логику для модели `students.csv` с FastAPI + SQLAlchemy + Alembic.

## Что реализовано

- CRUD для студентов:
  - `POST /students`
  - `GET /students`
  - `GET /students/{student_id}`
  - `PUT /students/{student_id}`
  - `DELETE /students/{student_id}`
- CRUD для оценок студента по предметам:
  - `POST /students/{student_id}/grades`
  - `PUT /students/{student_id}/grades/{subject_name}`
  - `DELETE /students/{student_id}/grades/{subject_name}`
- Импорт данных из `students.csv`:
  - `POST /import/csv`
- Отчеты:
  - студенты по факультету: `GET /report/students-by-faculty?faculty_name=...`
  - уникальные курсы: `GET /report/unique-courses`
  - студенты по курсу с оценкой ниже порога: `GET /report/low-scores?subject_name=...&threshold=30`
  - средний балл по факультету: `GET /report/faculty-average?faculty_name=...`
- Выгрузка данных в CSV (доп. задание):
  - `GET /export/csv`

## Структура модели

Таблицы:

- `faculties` — факультеты
- `students` — студенты (`last_name`, `first_name`, `faculty_id`)
- `subjects` — предметы (в CSV столбец `Курс`)
- `student_grades` — оценка студента по предмету

Ограничения:

- уникальный студент в рамках факультета (`uq_students_full_name_faculty`)
- уникальная пара студент+предмет (`uq_student_subject`)
- диапазон оценки `0..100` (`ck_grade_range`)

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
python load_students.py
uvicorn app.main:app --reload
```

## Проверка

- `GET /` — сервис запущен
- `GET /docs` — Swagger UI
