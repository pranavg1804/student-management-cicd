import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_payload():
    return {
        "name": "Asha Verma",
        "email": "asha@example.com",
        "course": "Computer Science",
        "year": 3,
    }
