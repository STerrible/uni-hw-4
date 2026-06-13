def create_student(client, last_name="Иванов", first_name="Иван", faculty_name="ИТ"):
    response = client.post(
        "/students",
        json={"last_name": last_name, "first_name": first_name, "faculty_name": faculty_name},
    )
    assert response.status_code == 200
    return response.json()


# POST /students

def test_create_student_success(client):
    response = client.post(
        "/students",
        json={"last_name": "Петров", "first_name": "Петр", "faculty_name": "Физика"},
    )

    assert response.status_code == 200
    assert response.json()["last_name"] == "Петров"
    assert response.json()["faculty"] == "Физика"


def test_create_student_validation_error_for_empty_last_name(client):
    response = client.post(
        "/students",
        json={"last_name": "", "first_name": "Петр", "faculty_name": "Физика"},
    )

    assert response.status_code == 422


# GET /students/{student_id}

def test_get_student_success(client):
    student = create_student(client)

    response = client.get(f"/students/{student['id']}")

    assert response.status_code == 200
    assert response.json() == student


def test_get_student_not_found(client):
    response = client.get("/students/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Студент не найден"


# PUT /students/{student_id}

def test_update_student_success(client):
    student = create_student(client)

    response = client.put(
        f"/students/{student['id']}",
        json={"first_name": "Сергей", "faculty_name": "Математика"},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Сергей"
    assert response.json()["faculty"] == "Математика"


def test_update_student_not_found(client):
    response = client.put("/students/999", json={"first_name": "Сергей"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Студент не найден"


# POST /students/{student_id}/grades

def test_create_grade_success(client):
    student = create_student(client)

    response = client.post(
        f"/students/{student['id']}/grades",
        json={"subject_name": "Python", "grade": 95},
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == student["id"]
    assert response.json()["grade"] == 95


def test_create_grade_for_missing_student_returns_404(client):
    response = client.post(
        "/students/999/grades",
        json={"subject_name": "Python", "grade": 95},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Студент не найден"


# GET /report/faculty-average

def test_report_faculty_average_success(client):
    student = create_student(client, faculty_name="ИТ")
    client.post(f"/students/{student['id']}/grades", json={"subject_name": "Python", "grade": 80})
    client.post(f"/students/{student['id']}/grades", json={"subject_name": "SQL", "grade": 90})

    response = client.get("/report/faculty-average", params={"faculty_name": "ИТ"})

    assert response.status_code == 200
    assert response.json() == {"faculty": "ИТ", "average_grade": 85.0}


def test_report_faculty_average_without_grades_returns_404(client):
    create_student(client, faculty_name="ИТ")

    response = client.get("/report/faculty-average", params={"faculty_name": "ИТ"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Нет данных по факультету"
