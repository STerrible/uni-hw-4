# Домашнее задание 5 — FastAPI сервис с аутентификацией

Проект реализует CRUD-логику для модели `students.csv` с FastAPI + SQLAlchemy + Alembic, а также маршрутизатор `/auth` для регистрации/входа/выхода.

## Что реализовано

- Аутентификация (`/auth`):
  - `POST /auth/register` — регистрация пользователя.
  - `POST /auth/login` — вход (авторизация по идентификатору пользователя).
  - `POST /auth/logout` — выход (завершение сессии).
- Все основные CRUD/отчетные/импорт-экспорт эндпоинты защищены.
  - Для доступа после логина нужно передавать заголовок `X-User-Id`.
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
- Выгрузка данных в CSV:
  - `GET /export/csv`

## Структура модели

Таблицы:

- `users` — пользователи сервиса (`username`, `password_hash`)
- `faculties` — факультеты
- `students` — студенты (`last_name`, `first_name`, `faculty_id`)
- `subjects` — предметы (в CSV столбец `Курс`)
- `student_grades` — оценка студента по предмету

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
python load_students.py
uvicorn app.main:app --reload
```

## Быстрая проверка авторизации

1. Зарегистрируйтесь:
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"secret123"}'
```

2. Выполните вход (получите `user_id`):
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"secret123"}'
```

3. Доступ к защищенным роутам:
```bash
curl http://127.0.0.1:8000/students -H "X-User-Id: 1"
```
