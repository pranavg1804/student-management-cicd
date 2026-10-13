def test_list_is_empty_initially(client):
    response = client.get("/api/students")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_student(client, student_payload):
    response = client.post("/api/students", json=student_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["email"] == "asha@example.com"


def test_get_student(client, student_payload):
    client.post("/api/students", json=student_payload)
    response = client.get("/api/students/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Asha Verma"


def test_get_missing_student_returns_404(client):
    assert client.get("/api/students/999").status_code == 404


def test_update_student(client, student_payload):
    client.post("/api/students", json=student_payload)
    updated = dict(student_payload, course="Data Science", year=4)
    response = client.put("/api/students/1", json=updated)
    assert response.status_code == 200
    assert response.get_json()["course"] == "Data Science"
    assert response.get_json()["year"] == 4


def test_delete_student(client, student_payload):
    client.post("/api/students", json=student_payload)
    assert client.delete("/api/students/1").status_code == 200
    assert client.get("/api/students/1").status_code == 404


def test_duplicate_email_rejected(client, student_payload):
    client.post("/api/students", json=student_payload)
    response = client.post("/api/students", json=student_payload)
    assert response.status_code == 400
    assert "already exists" in response.get_json()["errors"][0]


def test_invalid_input_rejected(client):
    bad = {"name": "", "email": "not-an-email", "course": "", "year": 99}
    response = client.post("/api/students", json=bad)
    assert response.status_code == 400
    assert len(response.get_json()["errors"]) == 4