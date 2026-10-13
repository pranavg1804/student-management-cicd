def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Management System" in response.data


def test_add_student_via_form(client, student_payload):
    response = client.post("/add", data=student_payload, follow_redirects=True)
    assert response.status_code == 200
    assert b"Student added successfully." in response.data
    assert b"Asha Verma" in response.data


def test_add_student_invalid_form_shows_errors(client):
    response = client.post("/add", data={"name": "", "email": "x", "course": "", "year": ""})
    assert response.status_code == 400
    assert b"Name is required." in response.data


def test_search_filters_results(client, student_payload):
    client.post("/add", data=student_payload)
    other = dict(student_payload, name="Rohan Mehta", email="rohan@example.com")
    client.post("/add", data=other)

    response = client.get("/?q=Rohan")
    assert b"Rohan Mehta" in response.data
    assert b"Asha Verma" not in response.data


def test_delete_student_via_form(client, student_payload):
    client.post("/add", data=student_payload)
    response = client.post("/delete/1", follow_redirects=True)
    assert b"Student deleted." in response.data
    assert b"Asha Verma" not in response.data